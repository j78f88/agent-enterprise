"""
Contract Validation Tests

Tests for JSON Schema validation, Rego policies, and FSM transitions.
Phase 1 - Formal Verification

Run with: pytest tests/test_contracts.py -v
"""

import pytest
import json
from pathlib import Path

# Import validators
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "phase1_verification"))

from validator import SubagentReturnValidator, WritePermit, format_validation_errors


class TestSubagentReturnValidation:
    """Test JSON Schema validation for subagent returns."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        schema_dir = Path(__file__).parent.parent / "schemas"
        return SubagentReturnValidator(schema_dir=schema_dir)
    
    def test_tier1_valid(self, validator):
        """Test valid Tier 1 return."""
        data = {
            "tier": 1,
            "agent": "planner",
            "status": "complete",
            "summary": "Analysis complete with no blockers found.",
            "findings": [
                {
                    "severity": "SUGGESTION",
                    "description": "Consider adding integration tests for new API endpoints",
                    "recommendation": "Add test coverage to improve reliability"
                }
            ]
        }
        
        result = validator.validate(json.dumps(data), expected_tier=1)
        assert result.valid
        assert result.tier == 1
        assert len(result.errors) == 0
    
    def test_tier1_missing_summary(self, validator):
        """Test Tier 1 with missing required field."""
        data = {
            "tier": 1,
            "agent": "planner",
            "status": "complete",
            "findings": []
        }
        
        result = validator.validate(json.dumps(data), expected_tier=1)
        assert not result.valid
        assert any("summary" in err.lower() for err in result.errors)
    
    def test_tier1_blocked_requires_reason(self, validator):
        """Test Tier 1 blocked status requires blockerReason."""
        data = {
            "tier": 1,
            "agent": "planner",
            "status": "blocked",
            "summary": "Cannot proceed",
            "findings": []
        }
        
        result = validator.validate(json.dumps(data), expected_tier=1)
        assert not result.valid
        assert any("blockerReason" in err for err in result.errors)
    
    def test_tier2_valid_brainstorm(self, validator):
        """Test valid Tier 2 brainstorm return."""
        data = {
            "tier": 2,
            "agent": "planner",
            "status": "complete",
            "summary": "Brainstorm session complete",
            "artifactPath": "docs/planning/drafts/feature-x-brainstorm.md",
            "artifactType": "brainstorm",
            "findings": []
        }
        
        result = validator.validate(
            json.dumps(data),
            expected_tier=2,
            write_permit=WritePermit.BRAINSTORM
        )
        
        assert result.valid
        assert result.tier == 2
    
    def test_tier2_write_permit_violation(self, validator):
        """Test Tier 2 with wrong path for write permit."""
        data = {
            "tier": 2,
            "agent": "architect",
            "status": "complete",
            "summary": "Architecture document created",
            "artifactPath": "docs/architecture/design.md",  # Wrong for BRAINSTORM
            "artifactType": "architecture",
            "findings": []
        }
        
        result = validator.validate(
            json.dumps(data),
            expected_tier=2,
            write_permit=WritePermit.BRAINSTORM  # Expects drafts/*-brainstorm.md
        )
        
        assert not result.valid
        assert any("Write permit violation" in err for err in result.errors)
    
    def test_tier3_valid_composition(self, validator):
        """Test valid Tier 3 composition return."""
        data = {
            "tier": 3,
            "agent": "planner",
            "status": "complete",
            "summary": "Sprint 042 composition complete with 8 items",
            "sprintNumber": "042",
            "composition": [
                {
                    "itemId": "ITEM-001",
                    "type": "feature",
                    "tier": "P0",
                    "score": 95,
                    "rationale": "Critical security feature"
                },
                {
                    "itemId": "ITEM-002",
                    "type": "bug",
                    "tier": "P0",
                    "score": 90,
                    "rationale": "P0 bug must be included"
                }
            ],
            "excluded": [],
            "constraints": {
                "featurePercent": 65,
                "bugCount": 1,
                "debtPressure": 25,
                "capacityUsed": 85
            }
        }
        
        result = validator.validate(json.dumps(data), expected_tier=3)
        assert result.valid
        assert result.tier == 3
    
    def test_tier3_invalid_sprint_number(self, validator):
        """Test Tier 3 with invalid sprint number format."""
        data = {
            "tier": 3,
            "agent": "planner",
            "status": "complete",
            "summary": "Composition complete",
            "sprintNumber": "42",  # Should be "042" (3-4 digits)
            "composition": [
                {
                    "itemId": "ITEM-001",
                    "type": "feature",
                    "tier": "P0",
                    "score": 95,
                    "rationale": "Test"
                }
            ],
            "constraints": {
                "featurePercent": 65,
                "bugCount": 0,
                "debtPressure": 20,
                "capacityUsed": 80
            }
        }
        
        result = validator.validate(json.dumps(data), expected_tier=3)
        assert not result.valid
        assert any("sprintNumber" in err for err in result.errors)
    
    def test_invalid_json(self, validator):
        """Test invalid JSON input."""
        result = validator.validate("not valid json", expected_tier=1)
        assert not result.valid
        assert any("Invalid JSON" in err for err in result.errors)
    
    def test_tier_mismatch(self, validator):
        """Test tier mismatch warning."""
        data = {
            "tier": 2,
            "agent": "planner",
            "status": "complete",
            "summary": "Test",
            "artifactPath": "test.md",
            "artifactType": "research",
            "findings": []
        }
        
        result = validator.validate(json.dumps(data), expected_tier=1)
        assert any("Tier mismatch" in warn for warn in result.warnings)


class TestFSMTransitions:
    """Test FSM state transitions (basic logic tests without full implementation)."""
    
    def test_valid_transition_sequence(self):
        """Test valid sequence of state transitions."""
        # This would require importing the FSM implementation
        # Placeholder for FSM tests
        pass
    
    def test_invalid_transition_blocked(self):
        """Test invalid transition raises error."""
        pass
    
    def test_terminal_state_no_transitions(self):
        """Test terminal state has no valid transitions."""
        pass


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
