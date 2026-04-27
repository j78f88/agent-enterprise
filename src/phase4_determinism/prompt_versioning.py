"""
Prompt Versioning System

Tracks prompt changes via SHA256 hashing to detect non-determinism sources.
Enables reproducible agent executions by versioning skill templates.

Phase 4 - Determinism & Replay
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone


# =============================================================================
# Prompt Versioning
# =============================================================================

@dataclass
class PromptVersion:
    """
    Version metadata for a prompt.
    
    Tracks content hash, creation time, and source information.
    """
    
    prompt_hash: str  # SHA256 hash (first 12 chars)
    full_hash: str    # Full SHA256 hash
    skill_name: str
    created_at: str
    content_length: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'prompt_hash': self.prompt_hash,
            'full_hash': self.full_hash,
            'skill_name': self.skill_name,
            'created_at': self.created_at,
            'content_length': self.content_length,
            'metadata': self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PromptVersion':
        """Deserialize from dictionary."""
        return PromptVersion(
            prompt_hash=data['prompt_hash'],
            full_hash=data['full_hash'],
            skill_name=data['skill_name'],
            created_at=data['created_at'],
            content_length=data['content_length'],
            metadata=data.get('metadata', {})
        )


class PromptVersioner:
    """
    Manages prompt versioning via content hashing.
    
    Detects when prompts change between runs, which would affect
    determinism of agent executions.
    
    Usage:
        versioner = PromptVersioner()
        
        # Hash a prompt
        version = versioner.hash_prompt(prompt_text, skill_name="planner")
        
        # Check if prompt changed
        if versioner.has_changed("planner", prompt_text):
            print("⚠️  Prompt changed - replay will differ!")
        
        # Get version history
        history = versioner.get_history("planner")
    """
    
    def __init__(self, state_dir: str = ".agent-state"):
        """
        Initialize prompt versioner.
        
        Args:
            state_dir: Directory for version history storage
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.versions_file = self.state_dir / "prompt-versions.jsonl"
        
        # In-memory cache of current versions
        self._current_versions: Dict[str, PromptVersion] = {}
        self._load_current_versions()
    
    def hash_prompt(
        self,
        prompt: str,
        skill_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptVersion:
        """
        Hash prompt content and create version record.
        
        Args:
            prompt: Prompt text to hash
            skill_name: Name of skill (e.g., "planner", "reviewer")
            metadata: Additional metadata (task ID, context, etc.)
        
        Returns:
            PromptVersion object
        """
        # Compute SHA256 hash
        full_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        prompt_hash = full_hash[:12]  # Short hash for display
        
        # Create version record
        version = PromptVersion(
            prompt_hash=prompt_hash,
            full_hash=full_hash,
            skill_name=skill_name,
            created_at=datetime.now(timezone.utc).isoformat(),
            content_length=len(prompt),
            metadata=metadata or {}
        )
        
        # Update current version
        self._current_versions[skill_name] = version
        
        # Append to version history
        self._append_version(version)
        
        return version
    
    def has_changed(self, skill_name: str, prompt: str) -> bool:
        """
        Check if prompt has changed since last version.
        
        Args:
            skill_name: Name of skill
            prompt: Current prompt text
        
        Returns:
            True if prompt changed, False if identical
        """
        current_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        
        if skill_name not in self._current_versions:
            # No previous version
            return True
        
        previous_version = self._current_versions[skill_name]
        return current_hash != previous_version.full_hash
    
    def get_current_version(self, skill_name: str) -> Optional[PromptVersion]:
        """
        Get current version for skill.
        
        Args:
            skill_name: Name of skill
        
        Returns:
            PromptVersion or None if no version recorded
        """
        return self._current_versions.get(skill_name)
    
    def get_history(self, skill_name: Optional[str] = None) -> List[PromptVersion]:
        """
        Get version history for skill(s).
        
        Args:
            skill_name: Filter by skill name (None = all skills)
        
        Returns:
            List of PromptVersion objects
        """
        if not self.versions_file.exists():
            return []
        
        versions = []
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    version = PromptVersion.from_dict(data)
                    
                    if skill_name is None or version.skill_name == skill_name:
                        versions.append(version)
                except Exception as e:
                    print(f"⚠️  Failed to parse version: {e}")
        
        return versions
    
    def compare_versions(
        self,
        skill_name: str,
        hash1: str,
        hash2: str
    ) -> Dict[str, Any]:
        """
        Compare two prompt versions.
        
        Args:
            skill_name: Name of skill
            hash1: First prompt hash
            hash2: Second prompt hash
        
        Returns:
            Comparison result dictionary
        """
        history = self.get_history(skill_name)
        
        v1 = next((v for v in history if v.prompt_hash == hash1), None)
        v2 = next((v for v in history if v.prompt_hash == hash2), None)
        
        if not v1 or not v2:
            return {'error': 'Version not found'}
        
        return {
            'skill': skill_name,
            'version1': v1.to_dict(),
            'version2': v2.to_dict(),
            'identical': v1.full_hash == v2.full_hash,
            'length_diff': v2.content_length - v1.content_length,
            'time_diff': v2.created_at > v1.created_at
        }
    
    def _append_version(self, version: PromptVersion):
        """Append version to history file."""
        with open(self.versions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(version.to_dict()) + '\n')
    
    def _load_current_versions(self):
        """Load most recent version for each skill."""
        if not self.versions_file.exists():
            return
        
        # Read all versions
        all_versions = self.get_history()
        
        # Keep only most recent per skill
        for version in all_versions:
            skill = version.skill_name
            
            if skill not in self._current_versions:
                self._current_versions[skill] = version
            else:
                # Keep most recent
                current = self._current_versions[skill]
                if version.created_at > current.created_at:
                    self._current_versions[skill] = version


# =============================================================================
# Skill Template Hashing
# =============================================================================

class SkillTemplateHasher:
    """
    Hashes skill template files to detect changes.
    
    Useful for detecting when SKILL.md files change between runs.
    
    Usage:
        hasher = SkillTemplateHasher()
        
        # Hash all skills
        hashes = hasher.hash_all_skills("skills/")
        
        # Compare with previous run
        if hasher.any_changed():
            print("⚠️  Skills changed - replay may differ!")
    """
    
    def __init__(self, state_dir: str = ".agent-state"):
        """
        Initialize skill template hasher.
        
        Args:
            state_dir: Directory for hash storage
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.hashes_file = self.state_dir / "skill-hashes.json"
        
        # Load previous hashes
        self.previous_hashes = self._load_hashes()
        self.current_hashes: Dict[str, str] = {}
    
    def hash_skill_file(self, skill_path: Path) -> str:
        """
        Hash a single skill file.
        
        Args:
            skill_path: Path to SKILL.md file
        
        Returns:
            SHA256 hash (first 12 chars)
        """
        content = skill_path.read_text(encoding='utf-8')
        full_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return full_hash[:12]
    
    def hash_all_skills(self, skills_dir: str) -> Dict[str, str]:
        """
        Hash all skill files in directory.
        
        Args:
            skills_dir: Path to skills directory
        
        Returns:
            Dictionary mapping skill name to hash
        """
        skills_path = Path(skills_dir)
        
        if not skills_path.exists():
            return {}
        
        hashes = {}
        
        # Find all SKILL.md files
        for skill_file in sorted(skills_path.rglob("SKILL.md")):
            # Get skill name from parent directory
            skill_name = skill_file.parent.name
            
            # Hash file
            file_hash = self.hash_skill_file(skill_file)
            hashes[skill_name] = file_hash
        
        self.current_hashes = hashes
        return hashes
    
    def any_changed(self) -> bool:
        """
        Check if any skills changed since last run.
        
        Returns:
            True if any skills changed
        """
        if not self.previous_hashes:
            # No previous run
            return False
        
        # Check for changes
        for skill, current_hash in self.current_hashes.items():
            previous_hash = self.previous_hashes.get(skill)
            
            if previous_hash is None:
                # New skill
                return True
            
            if current_hash != previous_hash:
                # Hash changed
                return True
        
        # Check for deleted skills
        for skill in self.previous_hashes:
            if skill not in self.current_hashes:
                return True
        
        return False
    
    def get_changes(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Get detailed list of skill changes.
        
        Returns:
            Dictionary mapping skill name to change info
        """
        changes = {}
        
        # Check all current skills
        for skill, current_hash in self.current_hashes.items():
            previous_hash = self.previous_hashes.get(skill)
            
            if previous_hash is None:
                changes[skill] = {
                    'status': 'added',
                    'previous': None,
                    'current': current_hash
                }
            elif current_hash != previous_hash:
                changes[skill] = {
                    'status': 'modified',
                    'previous': previous_hash,
                    'current': current_hash
                }
        
        # Check for deleted skills
        for skill, previous_hash in self.previous_hashes.items():
            if skill not in self.current_hashes:
                changes[skill] = {
                    'status': 'deleted',
                    'previous': previous_hash,
                    'current': None
                }
        
        return changes
    
    def save_hashes(self):
        """Save current hashes to disk."""
        with open(self.hashes_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_hashes, f, indent=2)
    
    def _load_hashes(self) -> Dict[str, str]:
        """Load previous hashes from disk."""
        if not self.hashes_file.exists():
            return {}
        
        try:
            with open(self.hashes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load skill hashes: {e}")
            return {}


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== Prompt Versioning Demo ===\n")
    
    # Initialize versioner
    versioner = PromptVersioner(".agent-state")
    
    # Hash some prompts
    print("--- Hashing prompts ---\n")
    
    prompt1 = """
    You are a sprint planner. Analyze the backlog and create a sprint plan.
    
    Constraints:
    - Max 5 items per sprint
    - Total complexity ≤ 13 points
    """
    
    version1 = versioner.hash_prompt(prompt1, skill_name="planner")
    print(f"Planner prompt v1: {version1.prompt_hash}")
    
    # Hash again (same content)
    version1b = versioner.hash_prompt(prompt1, skill_name="planner")
    print(f"Planner prompt v1 (again): {version1b.prompt_hash}")
    print(f"  Changed: {versioner.has_changed('planner', prompt1)}")
    
    # Modify prompt
    prompt2 = prompt1 + "\n- Prioritize bugs over features\n"
    version2 = versioner.hash_prompt(prompt2, skill_name="planner")
    print(f"\nPlanner prompt v2: {version2.prompt_hash}")
    print(f"  Changed: {versioner.has_changed('planner', prompt1)}")
    
    # Get history
    print("\n--- Version history ---\n")
    history = versioner.get_history("planner")
    for v in history:
        print(f"  {v.prompt_hash} - {v.created_at} ({v.content_length} chars)")
    
    # Skill template hashing
    print("\n--- Skill template hashing ---\n")
    
    hasher = SkillTemplateHasher(".agent-state")
    
    # Hash all skills (if directory exists)
    if Path("skills").exists():
        hashes = hasher.hash_all_skills("skills/")
        print(f"Hashed {len(hashes)} skills:")
        for skill, hash_val in hashes.items():
            print(f"  {skill}: {hash_val}")
        
        # Check for changes
        if hasher.any_changed():
            print("\n⚠️  Skills changed since last run!")
            changes = hasher.get_changes()
            for skill, change in changes.items():
                print(f"  {skill}: {change['status']}")
        else:
            print("\n✓ No skill changes detected")
        
        # Save hashes
        hasher.save_hashes()
    else:
        print("  (skills/ directory not found)")
    
    print("\n✓ Demo complete")
