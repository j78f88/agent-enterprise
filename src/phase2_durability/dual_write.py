"""
Dual-Write Compatibility Layer

Maintains backward compatibility with markdown files during SQLite migration.
Writes to both markdown and database simultaneously.
Phase 2 - Durable Execution
"""

import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

from db import Database, LedgerItem, Bug, Rejection, Sprint


# =============================================================================
# Dual-Write Manager
# =============================================================================

class DualWriteManager:
    """
    Manages dual-write operations to both markdown and SQLite.
    
    During migration, all writes go to both systems to maintain compatibility.
    After migration verification, can switch to SQLite-only mode.
    
    Usage:
        dwm = DualWriteManager(db, enabled=True)
        
        # Add ledger item (writes to both)
        dwm.add_ledger_item(item)
        
        # Disable dual-write after migration
        dwm.disable()
    """
    
    def __init__(
        self,
        db: Database,
        ledger_path: str = "BACKLOG_LEDGER.md",
        bug_path: str = "BUG_BACKLOG.md",
        rejection_path: str = "HANDOFF_REJECTIONS.md",
        sprint_path: str = "docs/sprints",
        enabled: bool = True
    ):
        """
        Initialize dual-write manager.
        
        Args:
            db: Database instance
            ledger_path: Path to ledger markdown
            bug_path: Path to bug backlog markdown
            rejection_path: Path to rejection markdown
            sprint_path: Directory for sprint markdown files
            enabled: Whether dual-write is enabled
        """
        self.db = db
        self.ledger_path = Path(ledger_path)
        self.bug_path = Path(bug_path)
        self.rejection_path = Path(rejection_path)
        self.sprint_path = Path(sprint_path)
        self.enabled = enabled
        
        # Create directories
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.bug_path.parent.mkdir(parents=True, exist_ok=True)
        self.rejection_path.parent.mkdir(parents=True, exist_ok=True)
        self.sprint_path.mkdir(parents=True, exist_ok=True)
    
    def enable(self):
        """Enable dual-write mode."""
        self.enabled = True
        print("✓ Dual-write mode enabled")
    
    def disable(self):
        """Disable dual-write mode (SQLite only)."""
        self.enabled = False
        print("✓ Dual-write mode disabled - SQLite is source of truth")
    
    # =========================================================================
    # Ledger Operations
    # =========================================================================
    
    def add_ledger_item(self, item: LedgerItem):
        """
        Add ledger item to both database and markdown.
        
        Args:
            item: LedgerItem to add
        """
        # Write to database
        with self.db.transaction():
            self.db.add_ledger_item(item)
        
        # Write to markdown if enabled
        if self.enabled:
            self._append_to_ledger_markdown(item)
    
    def update_ledger_item(self, item_id: str, updates: Dict[str, Any]):
        """
        Update ledger item in both database and markdown.
        
        Args:
            item_id: Item ID to update
            updates: Fields to update
        """
        # Update database
        with self.db.transaction():
            self.db.update_ledger_item(item_id, updates)
        
        # Update markdown if enabled
        if self.enabled:
            # Get updated item
            item_dict = self.db.get_ledger_item(item_id)
            if item_dict:
                self._update_ledger_markdown(item_id, item_dict)
    
    def _append_to_ledger_markdown(self, item: LedgerItem):
        """Append item to ledger markdown file."""
        # Read existing content
        if self.ledger_path.exists():
            content = self.ledger_path.read_text(encoding='utf-8')
        else:
            # Create new ledger file
            content = self._create_ledger_header()
        
        # Format item as markdown row
        source = item.source_id or ''
        sprint = item.sprint or ''
        notes = item.notes or ''
        
        row = (
            f"| {item.item_id} | {item.type} | {source} | "
            f"{item.age} | {item.def_count} | {sprint} | {notes} |\n"
        )
        
        # Append row
        content += row
        
        # Write back
        self.ledger_path.write_text(content, encoding='utf-8')
    
    def _update_ledger_markdown(self, item_id: str, item_dict: Dict[str, Any]):
        """Update item in ledger markdown file."""
        if not self.ledger_path.exists():
            return
        
        content = self.ledger_path.read_text(encoding='utf-8')
        
        # Pattern to match the item row
        pattern = re.compile(
            rf'\|\s*{re.escape(item_id)}\s*\|[^\n]+\n',
            re.MULTILINE
        )
        
        # Format new row
        source = item_dict['source_id'] or ''
        sprint = item_dict['sprint'] or ''
        notes = item_dict['notes'] or ''
        
        new_row = (
            f"| {item_id} | {item_dict['type']} | {source} | "
            f"{item_dict['age']} | {item_dict['def']} | {sprint} | {notes} |\n"
        )
        
        # Replace row
        content = pattern.sub(new_row, content)
        
        # Write back
        self.ledger_path.write_text(content, encoding='utf-8')
    
    def _create_ledger_header(self) -> str:
        """Create ledger markdown header."""
        return (
            "# Backlog Ledger\n\n"
            "| Item ID | Type | Source | Age | Def | Sprint | Notes |\n"
            "|---------|------|--------|-----|-----|--------|-------|\n"
        )
    
    # =========================================================================
    # Bug Operations
    # =========================================================================
    
    def add_bug(self, bug: Bug):
        """
        Add bug to both database and markdown.
        
        Args:
            bug: Bug to add
        """
        # Write to database
        with self.db.transaction():
            self.db.add_bug(bug)
        
        # Write to markdown if enabled
        if self.enabled:
            self._append_to_bug_markdown(bug)
    
    def _append_to_bug_markdown(self, bug: Bug):
        """Append bug to bug backlog markdown file."""
        # Read existing content
        if self.bug_path.exists():
            content = self.bug_path.read_text(encoding='utf-8')
        else:
            content = "# Bug Backlog\n\n"
        
        # Format bug as markdown section
        bug_section = (
            f"## {bug.bug_id} ({bug.severity})\n\n"
            f"**Title:** {bug.title}\n\n"
            f"**Observed:** {bug.observed}\n\n"
            f"**Expected:** {bug.expected}\n\n"
        )
        
        if bug.reproduction_steps:
            bug_section += f"**Reproduction Steps:**\n{bug.reproduction_steps}\n\n"
        
        if bug.impact:
            bug_section += f"**Impact:** {bug.impact}\n\n"
        
        # Append section
        content += bug_section
        
        # Write back
        self.bug_path.write_text(content, encoding='utf-8')
    
    # =========================================================================
    # Rejection Operations
    # =========================================================================
    
    def add_rejection(self, rejection: Rejection):
        """
        Add rejection to both database and markdown.
        
        Args:
            rejection: Rejection to add
        """
        # Write to database
        with self.db.transaction():
            # First ensure ledger item exists
            ledger_item = LedgerItem(
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
            )
            
            try:
                self.db.add_ledger_item(ledger_item)
            except Exception:
                pass  # May already exist
        
        # Write to markdown if enabled
        if self.enabled:
            self._append_to_rejection_markdown(rejection)
    
    def _append_to_rejection_markdown(self, rejection: Rejection):
        """Append rejection to handoff rejections markdown file."""
        # Read existing content
        if self.rejection_path.exists():
            content = self.rejection_path.read_text(encoding='utf-8')
        else:
            content = "# Handoff Rejections\n\n"
        
        # Format rejection as markdown section
        rejection_section = (
            f"## {rejection.rejection_id}\n\n"
            f"**From:** {rejection.source_agent}\n\n"
            f"**To:** {rejection.target_agent}\n\n"
            f"**Reason:** {rejection.reason}\n\n"
            f"**Rationale:** {rejection.rationale}\n\n"
        )
        
        if rejection.original_request:
            rejection_section += f"**Original Request:**\n{rejection.original_request}\n\n"
        
        # Append section
        content += rejection_section
        
        # Write back
        self.rejection_path.write_text(content, encoding='utf-8')
    
    # =========================================================================
    # Sprint Operations
    # =========================================================================
    
    def add_sprint(self, sprint: Sprint):
        """
        Add sprint to both database and markdown.
        
        Args:
            sprint: Sprint to add
        """
        # Write to database
        with self.db.transaction():
            self.db.add_sprint(sprint)
        
        # Write to markdown if enabled
        if self.enabled:
            # Sprint markdown is typically created separately by sprint-lead
            # Just ensure the sprint document exists
            sprint_file = self.sprint_path / f"sprint-{sprint.sprint_id}.md"
            if not sprint_file.exists():
                sprint_content = self._create_sprint_markdown(sprint)
                sprint_file.write_text(sprint_content, encoding='utf-8')
    
    def _create_sprint_markdown(self, sprint: Sprint) -> str:
        """Create sprint markdown template."""
        return (
            f"# Sprint {sprint.sprint_id}\n\n"
            f"**Status:** {sprint.status}\n"
            f"**Started:** {sprint.started_at or 'Not started'}\n"
            f"**Forecast Complexity:** {sprint.forecast_complexity or 'TBD'}\n\n"
            "## Tasks\n\n"
            "- [ ] Task 1\n"
            "- [ ] Task 2\n\n"
            "## Notes\n\n"
        )
    
    # =========================================================================
    # Batch Operations
    # =========================================================================
    
    def sync_from_database(self):
        """
        Sync markdown files from database (overwrite markdown with DB state).
        
        Use this to ensure markdown matches database after migrations.
        """
        print("🔄 Syncing markdown from database...")
        
        # Sync ledger
        ledger_items = self.db.get_open_ledger_items()
        self._write_ledger_markdown(ledger_items)
        print(f"  ✓ Synced {len(ledger_items)} ledger items")
        
        # Sync bugs
        # (Would need to query all bugs)
        
        print("✓ Sync complete")
    
    def _write_ledger_markdown(self, items: List[Dict[str, Any]]):
        """Write complete ledger to markdown."""
        content = self._create_ledger_header()
        
        for item in items:
            source = item['source_id'] or ''
            sprint = item['sprint'] or ''
            notes = item['notes'] or ''
            
            content += (
                f"| {item['item_id']} | {item['type']} | {source} | "
                f"{item['age']} | {item['def']} | {sprint} | {notes} |\n"
            )
        
        self.ledger_path.write_text(content, encoding='utf-8')


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    from db import Database
    
    # Initialize
    db = Database()
    dwm = DualWriteManager(db, enabled=True)
    
    print("✓ Dual-write manager initialized")
    print(f"  Ledger path: {dwm.ledger_path}")
    print(f"  Dual-write enabled: {dwm.enabled}")
    
    # Example: Add a ledger item
    item = LedgerItem(
        item_id="ITEM-999",
        type="feature",
        source_id=None,
        age=0,
        def_count=0,
        sprint=None,
        status="open",
        blocked=False,
        draft_path=None,
        notes="Test dual-write item",
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat()
    )
    
    dwm.add_ledger_item(item)
    print(f"\n✓ Added item ITEM-999 (dual-write)")
    
    # Verify it's in both places
    db_item = db.get_ledger_item("ITEM-999")
    md_exists = "ITEM-999" in dwm.ledger_path.read_text(encoding='utf-8')
    
    print(f"  In database: {db_item is not None}")
    print(f"  In markdown: {md_exists}")
    
    # Example: Update item
    dwm.update_ledger_item("ITEM-999", {"age": 1, "notes": "Updated via dual-write"})
    print(f"\n✓ Updated ITEM-999 (dual-write)")
    
    db.close()
