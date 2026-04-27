"""
Policy Engine Integration

Validates configurations and compositions against Rego policies using Open Policy Agent (OPA).
Phase 1 - Formal Verification
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    allow: bool
    violations: List[str]
    warnings: List[str]
    summary: Dict[str, Any]
    
    def __bool__(self):
        return self.allow


class PolicyEngine:
    """
    Evaluates policies using Open Policy Agent (OPA).
    
    Requires OPA to be installed:
        https://www.openpolicyagent.org/docs/latest/#running-opa
    
    Usage:
        engine = PolicyEngine()
        result = engine.evaluate_composition(composition_data)
        if not result:
            print(f"Policy violations: {result.violations}")
    """
    
    def __init__(self, policy_dir: Optional[Path] = None):
        """
        Initialize policy engine.
        
        Args:
            policy_dir: Path to directory containing .rego policy files.
                       Defaults to ./policies/ relative to this file.
        """
        if policy_dir is None:
            policy_dir = Path(__file__).parent / "policies"
        
        self.policy_dir = Path(policy_dir)
        
        # Check if OPA is installed
        if not self._check_opa_installed():
            raise RuntimeError(
                "OPA (Open Policy Agent) not found. Install from:\n"
                "  https://www.openpolicyagent.org/docs/latest/#running-opa\n"
                "Or: brew install opa (macOS), choco install opa (Windows)"
            )
    
    def _check_opa_installed(self) -> bool:
        """Check if OPA is installed and accessible."""
        try:
            result = subprocess.run(
                ["opa", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def evaluate_policy(
        self,
        policy_name: str,
        input_data: Dict[str, Any],
        query: str = "data"
    ) -> PolicyResult:
        """
        Evaluate a policy against input data.
        
        Args:
            policy_name: Name of the policy package (e.g., 'composition', 'security')
            input_data: Data to evaluate against policy
            query: OPA query string (default: 'data' for full result)
        
        Returns:
            PolicyResult with evaluation outcome
        """
        # Construct query for policy result
        full_query = f"data.{policy_name}.result"
        
        # Run OPA eval
        try:
            result = subprocess.run(
                [
                    "opa", "eval",
                    "-d", str(self.policy_dir),
                    "-I",  # Use stdin for input
                    "--format", "json",
                    full_query
                ],
                input=json.dumps(input_data).encode(),
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode()
                raise RuntimeError(f"OPA evaluation failed: {error_msg}")
            
            # Parse result
            output = json.loads(result.stdout.decode())
            
            # Extract policy result from OPA output
            if not output.get("result"):
                raise RuntimeError("OPA returned no results")
            
            policy_result = output["result"][0]["expressions"][0]["value"]
            
            return PolicyResult(
                allow=policy_result.get("allow", False),
                violations=list(policy_result.get("violations", [])),
                warnings=list(policy_result.get("warnings", [])),
                summary=policy_result.get("summary", {})
            )
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("OPA evaluation timed out (>30s)")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in OPA output: {e}")
    
    def evaluate_composition(self, composition_data: Dict[str, Any]) -> PolicyResult:
        """
        Evaluate sprint composition against composition policies.
        
        Args:
            composition_data: Composition data (Tier 3 subagent return)
        
        Returns:
            PolicyResult with violations and warnings
        """
        # Enrich data with indices for ordering checks
        enriched = composition_data.copy()
        if "composition" in enriched:
            for idx, item in enumerate(enriched["composition"]):
                item["index"] = idx
        
        return self.evaluate_policy("composition", enriched)
    
    def evaluate_security(self, config_data: Dict[str, Any]) -> PolicyResult:
        """
        Evaluate configuration against security policies.
        
        Args:
            config_data: Configuration data (project.config.yml contents)
        
        Returns:
            PolicyResult with violations and warnings
        """
        return self.evaluate_policy("security", config_data)
    
    def format_result(self, result: PolicyResult) -> str:
        """Format policy result for display."""
        if result.allow:
            lines = ["✓ Policy validation passed"]
            
            if result.warnings:
                lines.append(f"\n⚠ {len(result.warnings)} warnings:")
                for warning in result.warnings:
                    lines.append(f"  • {warning}")
        else:
            lines = [f"❌ Policy validation failed ({len(result.violations)} violations)"]
            
            for violation in result.violations:
                lines.append(f"  • {violation}")
            
            if result.warnings:
                lines.append(f"\n⚠ {len(result.warnings)} warnings:")
                for warning in result.warnings:
                    lines.append(f"  • {warning}")
        
        # Add summary if available
        if result.summary:
            lines.append("\n📊 Summary:")
            for key, value in result.summary.items():
                lines.append(f"  • {key}: {value}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Example composition data
    composition = {
        "tier": 3,
        "agent": "planner",
        "status": "complete",
        "summary": "Sprint 042 composition complete",
        "sprintNumber": "042",
        "composition": [
            {
                "itemId": "ITEM-001",
                "type": "feature",
                "tier": "P0",
                "score": 95,
                "age": 1,
                "rationale": "Critical security fix"
            },
            {
                "itemId": "ITEM-002",
                "type": "bug",
                "tier": "P0",
                "score": 90,
                "age": 0,
                "rationale": "P0 bug must be included"
            },
            {
                "itemId": "ITEM-003",
                "type": "feature",
                "tier": "P1",
                "score": 85,
                "age": 2,
                "rationale": "High-value feature"
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
    
    # Example security config
    security_config = {
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
    
    try:
        engine = PolicyEngine()
        
        print("=== Composition Policy Evaluation ===")
        result = engine.evaluate_composition(composition)
        print(engine.format_result(result))
        
        print("\n=== Security Policy Evaluation ===")
        result = engine.evaluate_security(security_config)
        print(engine.format_result(result))
        
    except RuntimeError as e:
        print(f"❌ Policy engine error: {e}")
    except FileNotFoundError:
        print("❌ OPA not installed. Install from: https://www.openpolicyagent.org/")
