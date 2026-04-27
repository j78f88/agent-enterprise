"""
Subagent Return Validator

Validates subagent return data against JSON Schema contracts.
Enforces write permit boundaries and provides detailed error messages.

Phase 1 - Formal Verification
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
except ImportError:
    print("❌ jsonschema not installed. Run: pip install jsonschema")
    raise


class ReturnTier(Enum):
    """Subagent return tiers."""
    ANALYSIS = 1
    ARTIFACT = 2
    COMPOSITION = 3


class WritePermit(Enum):
    """Write permit tokens and their allowed paths."""
    BRAINSTORM = ("WRITE:BRAINSTORM", ["docs/planning/drafts/*-brainstorm.md"])
    DRAFT_PLAN = ("WRITE:DRAFT-PLAN", ["docs/planning/drafts/*-draft-plan.md"])
    ANALYSIS_ONLY = ("WRITE:ANALYSIS-ONLY", [])  # No file writes
    VALIDATION = ("WRITE:VALIDATION", ["docs/planning/validation/*-validation.md"])
    RESEARCH = ("WRITE:RESEARCH", ["docs/research/*", "docs/planning/research/*"])
    ARCHITECTURE = ("WRITE:ARCHITECTURE", ["docs/architecture/*"])
    
    def __init__(self, token: str, allowed_patterns: List[str]):
        self.token = token
        self.allowed_patterns = allowed_patterns
    
    @classmethod
    def from_token(cls, token: str) -> Optional['WritePermit']:
        """Get WritePermit from token string."""
        for permit in cls:
            if permit.token == token:
                return permit
        return None


@dataclass
class ValidationResult:
    """Result of subagent return validation."""
    valid: bool
    tier: Optional[int]
    errors: List[str]
    warnings: List[str]
    data: Optional[Dict[str, Any]]
    
    def __bool__(self):
        return self.valid


class SubagentReturnValidator:
    """
    Validates subagent returns against JSON Schema contracts.
    
    Usage:
        validator = SubagentReturnValidator()
        result = validator.validate(return_text, expected_tier=1)
        if result:
            print(f"✓ Valid return: {result.data['summary']}")
        else:
            print(f"❌ Validation failed: {result.errors}")
    """
    
    def __init__(self, schema_dir: Optional[Path] = None):
        """
        Initialize validator with schema directory.
        
        Args:
            schema_dir: Path to directory containing JSON schema files.
                       Defaults to ./schemas/ relative to this file.
        """
        if schema_dir is None:
            schema_dir = Path(__file__).parent / "schemas"
        
        self.schema_dir = Path(schema_dir)
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[int, Draft7Validator]:
        """Load JSON schemas for all return tiers."""
        schemas = {}
        
        for tier in [1, 2, 3]:
            schema_path = self.schema_dir / f"subagent-return-tier{tier}.schema.json"
            
            if not schema_path.exists():
                raise FileNotFoundError(
                    f"Schema file not found: {schema_path}\n"
                    f"Expected schemas in: {self.schema_dir}"
                )
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Create validator with schema
            schemas[tier] = Draft7Validator(schema)
        
        return schemas
    
    def validate(
        self, 
        return_text: str, 
        expected_tier: Optional[int] = None,
        write_permit: Optional[WritePermit] = None
    ) -> ValidationResult:
        """
        Validate subagent return against schema.
        
        Args:
            return_text: Raw text output from subagent
            expected_tier: Expected tier (1-3), or None to auto-detect
            write_permit: Write permit token for path validation (Tier 2 only)
        
        Returns:
            ValidationResult with validation status and details
        """
        errors = []
        warnings = []
        
        # Step 1: Parse JSON
        try:
            data = json.loads(return_text)
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                tier=None,
                errors=[f"Invalid JSON: {e}"],
                warnings=[],
                data=None
            )
        
        # Step 2: Extract tier
        if 'tier' not in data:
            return ValidationResult(
                valid=False,
                tier=None,
                errors=["Missing required field: 'tier'"],
                warnings=[],
                data=data
            )
        
        tier = data['tier']
        
        # Validate tier value
        if tier not in [1, 2, 3]:
            return ValidationResult(
                valid=False,
                tier=tier,
                errors=[f"Invalid tier value: {tier}. Must be 1, 2, or 3."],
                warnings=[],
                data=data
            )
        
        # Check expected tier
        if expected_tier is not None and tier != expected_tier:
            warnings.append(
                f"Tier mismatch: expected {expected_tier}, got {tier}"
            )
        
        # Step 3: Validate against schema
        validator = self.schemas[tier]
        schema_errors = list(validator.iter_errors(data))
        
        if schema_errors:
            for error in schema_errors:
                # Format error message with path
                path = ".".join(str(p) for p in error.path) if error.path else "root"
                errors.append(f"Schema violation at '{path}': {error.message}")
        
        # Step 4: Write permit validation (Tier 2 only)
        if tier == 2 and write_permit is not None:
            artifact_path = data.get('artifactPath', '')
            
            if write_permit == WritePermit.ANALYSIS_ONLY:
                errors.append(
                    f"Write permit violation: {write_permit.token} does not allow "
                    f"file creation, but artifactPath '{artifact_path}' was provided"
                )
            else:
                if not self._check_path_allowed(artifact_path, write_permit):
                    errors.append(
                        f"Write permit violation: Path '{artifact_path}' not allowed "
                        f"by {write_permit.token}. Allowed patterns: {write_permit.allowed_patterns}"
                    )
        
        # Step 5: Cross-field validation
        status = data.get('status')
        if status == 'blocked' and 'blockerReason' not in data:
            errors.append(
                "Missing 'blockerReason' field (required when status='blocked')"
            )
        
        # Return result
        return ValidationResult(
            valid=len(errors) == 0,
            tier=tier,
            errors=errors,
            warnings=warnings,
            data=data
        )
    
    def _check_path_allowed(self, path: str, permit: WritePermit) -> bool:
        """
        Check if a path is allowed by the write permit.
        
        Args:
            path: Relative file path
            permit: Write permit to check against
        
        Returns:
            True if path matches any allowed pattern
        """
        from fnmatch import fnmatch
        
        # Normalize path (forward slashes, no leading slash)
        path = path.replace('\\', '/').lstrip('/')
        
        for pattern in permit.allowed_patterns:
            if fnmatch(path, pattern):
                return True
        
        return False
    
    def validate_with_retry(
        self,
        return_text: str,
        expected_tier: int,
        write_permit: Optional[WritePermit] = None,
        retry_callback=None
    ) -> Tuple[ValidationResult, int]:
        """
        Validate with retry logic per protocol.
        
        If validation fails, invokes retry_callback once to give the subagent
        a chance to correct its output.
        
        Args:
            return_text: Initial return text
            expected_tier: Expected tier
            write_permit: Write permit for path validation
            retry_callback: Function to call on failure: f(error_msg) -> new_return_text
        
        Returns:
            (ValidationResult, attempt_count)
        """
        # First attempt
        result = self.validate(return_text, expected_tier, write_permit)
        
        if result.valid:
            return result, 1
        
        # Retry if callback provided
        if retry_callback is None:
            return result, 1
        
        # Format error message for retry
        error_msg = "; ".join(result.errors)
        retry_prompt = (
            f"[SUBAGENT-MODE] Your previous return failed validation: {error_msg}. "
            f"Return valid JSON per Tier {expected_tier} schema."
        )
        
        # Get retry output
        retry_return_text = retry_callback(retry_prompt)
        
        # Second attempt
        result = self.validate(retry_return_text, expected_tier, write_permit)
        
        return result, 2


def format_validation_errors(result: ValidationResult) -> str:
    """Format validation errors for display."""
    if result.valid:
        return f"✓ Valid Tier {result.tier} return"
    
    lines = [f"❌ Validation failed (Tier {result.tier or 'unknown'}):"]
    
    for error in result.errors:
        lines.append(f"  • {error}")
    
    if result.warnings:
        lines.append("\n⚠ Warnings:")
        for warning in result.warnings:
            lines.append(f"  • {warning}")
    
    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Example Tier 1 return (valid)
    tier1_valid = {
        "tier": 1,
        "agent": "planner",
        "status": "complete",
        "summary": "Analysis complete. No blockers found.",
        "findings": [
            {
                "severity": "SUGGESTION",
                "description": "Consider adding integration tests",
                "recommendation": "Add test coverage for API endpoints"
            }
        ]
    }
    
    # Example Tier 1 return (invalid - missing summary)
    tier1_invalid = {
        "tier": 1,
        "agent": "planner",
        "status": "complete",
        "findings": []
    }
    
    # Validate
    validator = SubagentReturnValidator()
    
    print("=== Valid Tier 1 Return ===")
    result = validator.validate(json.dumps(tier1_valid), expected_tier=1)
    print(format_validation_errors(result))
    
    print("\n=== Invalid Tier 1 Return ===")
    result = validator.validate(json.dumps(tier1_invalid), expected_tier=1)
    print(format_validation_errors(result))
    
    # Example Tier 2 with write permit validation
    tier2_valid = {
        "tier": 2,
        "agent": "planner",
        "status": "complete",
        "summary": "Brainstorm complete",
        "artifactPath": "docs/planning/drafts/feature-x-brainstorm.md",
        "artifactType": "brainstorm",
        "findings": []
    }
    
    print("\n=== Valid Tier 2 Return (with write permit) ===")
    result = validator.validate(
        json.dumps(tier2_valid),
        expected_tier=2,
        write_permit=WritePermit.BRAINSTORM
    )
    print(format_validation_errors(result))
    
    # Example: wrong path for permit
    tier2_wrong_path = tier2_valid.copy()
    tier2_wrong_path['artifactPath'] = "docs/architecture/design.md"  # Wrong path!
    
    print("\n=== Invalid Tier 2 Return (write permit violation) ===")
    result = validator.validate(
        json.dumps(tier2_wrong_path),
        expected_tier=2,
        write_permit=WritePermit.BRAINSTORM
    )
    print(format_validation_errors(result))
