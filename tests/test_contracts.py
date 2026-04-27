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
sys.path.insert(0, str(Path(__file__).parent.parent))

from validator import SubagentReturnValidator, WritePermit, format_validation_errors
from policy_engine import PolicyEngine


class TestSubagentReturnValidation:
    """Test JSON Schema validation for subagent returns."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return SubagentReturnValidator()
    
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


class TestPolicyEngine:
    """Test Rego policy evaluation."""
    
    @pytest.fixture
    def engine(self):
        """Create policy engine instance."""
        try:
            return PolicyEngine()
        except RuntimeError as e:
            pytest.skip(f"OPA not installed: {e}")
    
    def test_composition_valid(self, engine):
        """Test valid composition passes policies."""
        composition = {
            "composition": [
                {"itemId": "ITEM-001", "type": "feature", "tier": "P0", "score": 95, "age": 1, "index": 0},
                {"itemId": "ITEM-002", "type": "bug", "tier": "P0", "score": 90, "age": 0, "index": 1},
                {"itemId": "ITEM-003", "type": "feature", "tier": "P1", "score": 85, "age": 2, "index": 2},
            ],
            "excluded": [],
            "constraints": {
                "featurePercent": 65,
                "bugCount": 1,
                "debtPressure": 25,
                "capacityUsed": 85
            }
        }
        
        result = engine.evaluate_composition(composition)
        assert result.allow
        assert len(result.violations) == 0
    
    def test_composition_priority_violation(self, engine):
        """Test composition with wrong priority order."""
        composition = {
            "composition": [
                {"itemId": "ITEM-001", "type": "feature", "tier": "P1", "score": 85, "age": 1, "index": 0},  # P1 first
                {"itemId": "ITEM-002", "type": "bug", "tier": "P0", "score": 90, "age": 0, "index": 1},     # P0 second (wrong!)
            ],
            "excluded": [],
            "constraints": {
                "featurePercent": 50,
                "bugCount": 1,
                "debtPressure": 20,
                "capacityUsed": 80
            }
        }
        
        result = engine.evaluate_composition(composition)
        assert not result.allow
        assert any("PRIORITY_ORDER" in v for v in result.violations)
    
    def test_composition_capacity_exceeded(self, engine):
        """Test composition exceeding capacity."""
        composition = {
            "composition": [
                {"itemId": "ITEM-001", "type": "feature", "tier": "P0", "score": 95, "age": 1, "index": 0},
            ],
            "excluded": [],
            "constraints": {
                "featurePercent": 50,
                "bugCount": 0,
                "debtPressure": 20,
                "capacityUsed": 105  # Over 100%!
            }
        }
        
        result = engine.evaluate_composition(composition)
        assert not result.allow
        assert any("CAPACITY_EXCEEDED" in v for v in result.violations)
    
    def test_composition_feature_balance_low(self, engine):
        """Test composition with feature allocation too low."""
        composition = {
            "composition": [
                {"itemId": "ITEM-001", "type": "bug", "tier": "P0", "score": 95, "age": 1, "index": 0},
            ],
            "excluded": [],
            "constraints": {
                "featurePercent": 30,  # Below 50% minimum
                "bugCount": 1,
                "debtPressure": 20,
                "capacityUsed": 80
            }
        }
        
        result = engine.evaluate_composition(composition)
        assert not result.allow
        assert any("FEATURE_BALANCE" in v for v in result.violations)
    
    def test_security_valid_config(self, engine):
        """Test valid security configuration."""
        config = {
            "commands": {
                "test": "npm test",
                "build": "npm run build",
                "lint": "eslint ."
            },
            "paths": {
                "sprints": "docs/sprints",
                "backlog": "docs/backlog.md"
            },
            "escalation": {
                "def_kill_threshold": 5,
                "def_p0_threshold": 3
            }
        }
        
        result = engine.evaluate_security(config)
        assert result.allow
        assert len(result.violations) == 0
    
    def test_security_dangerous_command(self, engine):
        """Test security policy detects dangerous command."""
        config = {
            "commands": {
                "test": "npm test; rm -rf /"  # Dangerous!
            },
            "paths": {},
            "escalation": {}
        }
        
        result = engine.evaluate_security(config)
        assert not result.allow
        assert any("DANGEROUS_PATTERN" in v for v in result.violations)
    
    def test_security_path_traversal(self, engine):
        """Test security policy detects path traversal."""
        config = {
            "commands": {},
            "paths": {
                "data": "../../../etc/passwd"  # Path traversal!
            },
            "escalation": {}
        }
        
        result = engine.evaluate_security(config)
        assert not result.allow
        assert any("PATH_TRAVERSAL" in v for v in result.violations)


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
