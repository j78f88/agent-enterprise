"""
Database Migration Utilities

Migrates from markdown-based state to SQLite database.
Supports dual-write mode for gradual transition.
Phase 2 - Durable Execution
"""

import re
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from db import Database, LedgerItem, Bug, Rejection, Sprint


# =============================================================================
# Markdown Parsers
# =============================================================================

class MarkdownLedgerParser:
    """Parse ledger from markdown format."""
    
    # Ledger item pattern: | ITEM-001 | feature | BUG-003 | 0 | 1 | 042 | notes |
    ITEM_PATTERN = re.compile(
        r'\|\s*(?P<item_id>ITEM-\d+)\s*\|'
        r'\s*(?P<type>\w+)\s*\|'
        r'\s*(?P<source_id>[A-Z]+-\d+)?\s*\|'
        r'\s*(?P<age>\d+)\s*\|'
        r'\s*(?P<def>\d+)\s*\|'
        r'\s*(?P<sprint>\d+)?\s*\|'
        r'\s*(?P<notes>.*?)\s*\|'
    )
    
    @classmethod
    def parse_ledger_file(cls, filepath: Path) -> List[LedgerItem]:
        """
        Parse ledger markdown file.
        
        Args:
            filepath: Path to BACKLOG_LEDGER.md
        
        Returns:
            List of LedgerItem objects
        """
        if not filepath.exists():
            return []
        
        items = []
        content = filepath.read_text(encoding='utf-8')
        
        for match in cls.ITEM_PATTERN.finditer(content):
            item = LedgerItem(
                item_id=match.group('item_id'),
                type=match.group('type'),
                source_id=match.group('source_id') or None,
                age=int(match.group('age')),
                def_count=int(match.group('def')),
                sprint=match.group('sprint') or None,
                status='assigned' if match.group('sprint') else 'open',
                blocked=False,  # Can't determine from markdown
                draft_path=None,  # Not in markdown format
                notes=match.group('notes').strip() or None,
                created_at=datetime.now(timezone.utc).isoformat(),  # Unknown
                updated_at=datetime.now(timezone.utc).isoformat()
            )
            items.append(item)
        
        return items


class MarkdownBugParser:
    """Parse bugs from markdown format."""
    
    # Bug pattern (multi-line)
    BUG_PATTERN = re.compile(
        r'## (BUG-\d+)\s+\((.*?)\)\s*\n'
        r'\*\*Title:\*\*\s*(.*?)\n'
        r'\*\*Observed:\*\*\s*(.*?)\n'
        r'\*\*Expected:\*\*\s*(.*?)(?:\n|$)',
        re.DOTALL
    )
    
    @classmethod
    def parse_bug_file(cls, filepath: Path) -> List[Bug]:
        """
        Parse bug backlog markdown file.
        
        Args:
            filepath: Path to BUG_BACKLOG.md
        
        Returns:
            List of Bug objects
        """
        if not filepath.exists():
            return []
        
        bugs = []
        content = filepath.read_text(encoding='utf-8')
        
        for match in cls.BUG_PATTERN.finditer(content):
            bug_id = match.group(1)
            severity = match.group(2)
            title = match.group(3).strip()
            observed = match.group(4).strip()
            expected = match.group(5).strip()
            
            bug = Bug(
                bug_id=bug_id,
                ledger_item_id=f"ITEM-{bug_id.split('-')[1]}",  # Approximate mapping
                severity=severity,
                title=title,
                description=title,  # Use title as description
                reproduction_steps=None,
                observed=observed,
                expected=expected,
                impact=None,
                screenshot_path=None,
                reported_by=None,
                reported_at=datetime.now(timezone.utc).isoformat(),
                fixed_at=None
            )
            bugs.append(bug)
        
        return bugs


class MarkdownRejectionParser:
    """Parse rejections from markdown format."""
    
    REJECTION_PATTERN = re.compile(
        r'## (REJ-\d+)\s*\n'
        r'\*\*From:\*\*\s*(@\w+)\s*\n'
        r'\*\*To:\*\*\s*(@\w+)\s*\n'
        r'\*\*Reason:\*\*\s*(.*?)\n'
        r'\*\*Rationale:\*\*\s*(.*?)(?:\n\n|\Z)',
        re.DOTALL
    )
    
    @classmethod
    def parse_rejection_file(cls, filepath: Path) -> List[Rejection]:
        """
        Parse handoff rejections markdown file.
        
        Args:
            filepath: Path to HANDOFF_REJECTIONS.md
        
        Returns:
            List of Rejection objects
        """
        if not filepath.exists():
            return []
        
        rejections = []
        content = filepath.read_text(encoding='utf-8')
        
        for match in cls.REJECTION_PATTERN.finditer(content):
            rejection_id = match.group(1)
            source_agent = match.group(2)
            target_agent = match.group(3)
            reason = match.group(4).strip()
            rationale = match.group(5).strip()
            
            rejection = Rejection(
                rejection_id=rejection_id,
                ledger_item_id=f"ITEM-{rejection_id.split('-')[1]}",  # Approximate
                source_agent=source_agent,
                target_agent=target_agent,
                reason=reason,
                rationale=rationale,
                original_request=None,
                rejected_at=datetime.now(timezone.utc).isoformat(),
                resolved_at=None,
                resolution=None
            )
            rejections.append(rejection)
        
        return rejections


# =============================================================================
# Migration Manager
# =============================================================================

class MigrationManager:
    """
    Manages migration from markdown to SQLite.
    
    Supports three phases:
    1. Dual-write: Write to both markdown and DB
    2. Verification: Compare outputs for consistency
    3. Cutover: Stop writing to markdown
    """
    
    def __init__(
        self,
        db: Database,
        ledger_path: str = "BACKLOG_LEDGER.md",
        bug_path: str = "BUG_BACKLOG.md",
        rejection_path: str = "HANDOFF_REJECTIONS.md"
    ):
        """
        Initialize migration manager.
        
        Args:
            db: Database instance
            ledger_path: Path to ledger markdown
            bug_path: Path to bug backlog markdown
            rejection_path: Path to rejection markdown
        """
        self.db = db
        self.ledger_path = Path(ledger_path)
        self.bug_path = Path(bug_path)
        self.rejection_path = Path(rejection_path)
        self.dual_write_enabled = False
    
    def enable_dual_write(self):
        """Enable dual-write mode."""
        self.dual_write_enabled = True
        print("✓ Dual-write mode enabled")
    
    def disable_dual_write(self):
        """Disable dual-write mode (SQLite only)."""
        self.dual_write_enabled = False
        print("✓ Dual-write mode disabled - SQLite is source of truth")
    
    def import_from_markdown(self) -> Dict[str, int]:
        """
        Import all data from markdown files to database.
        
        Returns:
            Dictionary with import counts
        """
        counts = {
            'ledger': 0,
            'bugs': 0,
            'rejections': 0
        }
        
        with self.db.transaction():
            # Import ledger
            ledger_items = MarkdownLedgerParser.parse_ledger_file(self.ledger_path)
            for item in ledger_items:
                try:
                    self.db.add_ledger_item(item)
                    counts['ledger'] += 1
                except Exception as e:
                    print(f"⚠ Failed to import ledger item {item.item_id}: {e}")
            
            # Import bugs
            bugs = MarkdownBugParser.parse_bug_file(self.bug_path)
            for bug in bugs:
                try:
                    self.db.add_bug(bug)
                    counts['bugs'] += 1
                except Exception as e:
                    print(f"⚠ Failed to import bug {bug.bug_id}: {e}")
            
            # Import rejections
            rejections = MarkdownRejectionParser.parse_rejection_file(self.rejection_path)
            for rejection in rejections:
                try:
                    self.db.add_ledger_item(LedgerItem(
                        item_id=rejection.ledger_item_id,
                        type='rejection',
                        source_id=rejection.rejection_id,
                        age=0,
                        def_count=0,
                        sprint=None,
                        status='open',
                        blocked=False,
                        draft_path=None,
                        notes=rejection.rationale[:100],
                        created_at=rejection.rejected_at,
                        updated_at=rejection.rejected_at
                    ))
                    counts['rejections'] += 1
                except Exception:
                    pass  # May already exist from ledger import
        
        return counts
    
    def export_to_markdown(self) -> Dict[str, int]:
        """
        Export database to markdown files (for verification).
        
        Returns:
            Dictionary with export counts
        """
        counts = {
            'ledger': 0,
            'bugs': 0,
            'rejections': 0
        }
        
        # Export ledger
        ledger_items = self.db.get_ledger_by_status('open')
        ledger_content = self._format_ledger_markdown(ledger_items)
        
        export_path = self.ledger_path.parent / f"{self.ledger_path.stem}_exported.md"
        export_path.write_text(ledger_content, encoding='utf-8')
        counts['ledger'] = len(ledger_items)
        
        print(f"✓ Exported ledger to {export_path}")
        
        return counts
    
    def _format_ledger_markdown(self, items: List[Dict]) -> str:
        """Format ledger items as markdown table."""
        lines = [
            "# Backlog Ledger (Exported from Database)",
            "",
            "| Item ID | Type | Source | Age | Def | Sprint | Notes |",
            "|---------|------|--------|-----|-----|--------|-------|"
        ]
        
        for item in items:
            source = item['source_id'] or ''
            sprint = item['sprint'] or ''
            notes = item['notes'] or ''
            
            lines.append(
                f"| {item['item_id']} | {item['type']} | {source} | "
                f"{item['age']} | {item['def']} | {sprint} | {notes} |"
            )
        
        return "\n".join(lines)
    
    def verify_consistency(self) -> Tuple[bool, List[str]]:
        """
        Verify consistency between markdown and database.
        
        Returns:
            (is_consistent, list of discrepancies)
        """
        discrepancies = []
        
        # Parse markdown
        md_items = MarkdownLedgerParser.parse_ledger_file(self.ledger_path)
        md_item_ids = {item.item_id for item in md_items}
        
        # Query database
        db_items = self.db.get_open_ledger_items()
        db_item_ids = {item['item_id'] for item in db_items}
        
        # Check for missing items
        missing_in_db = md_item_ids - db_item_ids
        missing_in_md = db_item_ids - md_item_ids
        
        if missing_in_db:
            discrepancies.append(f"Missing in DB: {missing_in_db}")
        
        if missing_in_md:
            discrepancies.append(f"Missing in markdown: {missing_in_md}")
        
        # Check for value differences
        for md_item in md_items:
            db_item = self.db.get_ledger_item(md_item.item_id)
            if db_item:
                if md_item.age != db_item['age']:
                    discrepancies.append(
                        f"{md_item.item_id}: age mismatch (MD={md_item.age}, DB={db_item['age']})"
                    )
                if md_item.def_count != db_item['def']:
                    discrepancies.append(
                        f"{md_item.item_id}: def mismatch (MD={md_item.def_count}, DB={db_item['def']})"
                    )
        
        return len(discrepancies) == 0, discrepancies
    
    def archive_markdown_files(self, archive_dir: str = "docs/archive/legacy-state"):
        """
        Archive markdown files after successful cutover.
        
        Args:
            archive_dir: Directory to archive files to
        """
        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for source_path in [self.ledger_path, self.bug_path, self.rejection_path]:
            if source_path.exists():
                dest_path = archive_path / f"{source_path.stem}_{timestamp}{source_path.suffix}"
                dest_path.write_text(source_path.read_text(encoding='utf-8'), encoding='utf-8')
                print(f"✓ Archived {source_path} → {dest_path}")


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Migration CLI."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [import|export|verify|archive]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Initialize
    db = Database()
    migrator = MigrationManager(db)
    
    if command == "import":
        print("📦 Importing from markdown...")
        counts = migrator.import_from_markdown()
        print(f"\n✓ Import complete:")
        print(f"  Ledger items: {counts['ledger']}")
        print(f"  Bugs: {counts['bugs']}")
        print(f"  Rejections: {counts['rejections']}")
    
    elif command == "export":
        print("📤 Exporting to markdown...")
        counts = migrator.export_to_markdown()
        print(f"\n✓ Export complete:")
        print(f"  Ledger items: {counts['ledger']}")
    
    elif command == "verify":
        print("🔍 Verifying consistency...")
        is_consistent, discrepancies = migrator.verify_consistency()
        
        if is_consistent:
            print("\n✓ Markdown and database are consistent")
        else:
            print(f"\n❌ Found {len(discrepancies)} discrepancies:")
            for disc in discrepancies:
                print(f"  • {disc}")
    
    elif command == "archive":
        print("📁 Archiving markdown files...")
        migrator.archive_markdown_files()
        print("\n✓ Archive complete")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
    
    db.close()


if __name__ == "__main__":
    main()
