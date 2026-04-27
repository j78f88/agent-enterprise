"""
LLM Configuration Enforcement

Enforces deterministic LLM parameters (temperature=0.0) and validates
configurations to prevent non-deterministic sampling.

Phase 4 - Determinism & Replay
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
from pathlib import Path
from datetime import datetime, timezone


# =============================================================================
# Exceptions
# =============================================================================

class DeterminismViolation(Exception):
    """Raised when non-deterministic LLM parameters are detected."""
    pass


class LLMConfigurationError(Exception):
    """Raised when LLM configuration is invalid."""
    pass


# =============================================================================
# LLM Configuration
# =============================================================================

@dataclass
class LLMConfig:
    """
    LLM configuration with determinism guarantees.
    
    Enforces temperature=0.0 for deterministic sampling.
    """
    
    model: str
    temperature: float = 0.0
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_tokens: Optional[int] = None
    seed: Optional[int] = None  # For providers that support seeding
    
    # Metadata
    provider: str = "openai"  # openai, anthropic, azure, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration on initialization."""
        self.validate()
    
    def validate(self):
        """
        Validate configuration for determinism.
        
        Raises:
            DeterminismViolation: If temperature != 0.0
            LLMConfigurationError: If other parameters invalid
        """
        # CRITICAL: Temperature must be 0.0 for determinism
        if self.temperature != 0.0:
            raise DeterminismViolation(
                f"LLM temperature must be 0.0 for determinism, got {self.temperature}\n"
                "All LLM calls must use temperature=0.0 to ensure reproducible outputs."
            )
        
        # Validate ranges
        if not (0.0 <= self.top_p <= 1.0):
            raise LLMConfigurationError(f"top_p must be in [0.0, 1.0], got {self.top_p}")
        
        if not (-2.0 <= self.frequency_penalty <= 2.0):
            raise LLMConfigurationError(
                f"frequency_penalty must be in [-2.0, 2.0], got {self.frequency_penalty}"
            )
        
        if not (-2.0 <= self.presence_penalty <= 2.0):
            raise LLMConfigurationError(
                f"presence_penalty must be in [-2.0, 2.0], got {self.presence_penalty}"
            )
        
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise LLMConfigurationError(f"max_tokens must be positive, got {self.max_tokens}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'model': self.model,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'max_tokens': self.max_tokens,
            'seed': self.seed,
            'provider': self.provider,
            'metadata': self.metadata
        }
    
    def to_openai_params(self) -> Dict[str, Any]:
        """Convert to OpenAI API parameters."""
        params = {
            'model': self.model,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty
        }
        
        if self.max_tokens is not None:
            params['max_tokens'] = self.max_tokens
        
        if self.seed is not None:
            params['seed'] = self.seed
        
        return params
    
    def to_anthropic_params(self) -> Dict[str, Any]:
        """Convert to Anthropic API parameters."""
        params = {
            'model': self.model,
            'temperature': self.temperature,
            'top_p': self.top_p
        }
        
        if self.max_tokens is not None:
            params['max_tokens'] = self.max_tokens
        
        return params


# =============================================================================
# Configuration Validator
# =============================================================================

class LLMConfigValidator:
    """
    Validates LLM configurations for determinism.
    
    Can be used as a wrapper or decorator to enforce deterministic parameters.
    
    Usage:
        validator = LLMConfigValidator(strict=True)
        
        # Validate parameters before LLM call
        params = {'model': 'gpt-4', 'temperature': 0.0}
        validator.validate_params(params)
        
        # Or use as decorator
        @validator.enforce
        def call_llm(model, temperature, **kwargs):
            # Will raise if temperature != 0.0
            return llm_api.call(model=model, temperature=temperature, **kwargs)
    """
    
    def __init__(
        self,
        strict: bool = True,
        log_violations: bool = True,
        log_path: str = ".agent-state/llm-violations.jsonl"
    ):
        """
        Initialize validator.
        
        Args:
            strict: If True, raise on violations. If False, log warnings only.
            log_violations: If True, log violations to file
            log_path: Path to violations log file
        """
        self.strict = strict
        self.log_violations_enabled = log_violations
        self.log_path = Path(log_path)
        
        if self.log_violations_enabled:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.violations: List[Dict[str, Any]] = []
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate LLM parameters for determinism.
        
        Args:
            params: LLM API parameters
        
        Returns:
            True if valid
        
        Raises:
            DeterminismViolation: If strict=True and temperature != 0.0
        """
        temperature = params.get('temperature', 1.0)
        
        if temperature != 0.0:
            violation = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'non_zero_temperature',
                'temperature': temperature,
                'params': params,
                'message': f"Temperature {temperature} violates determinism requirement"
            }
            
            self.violations.append(violation)
            
            if self.log_violations_enabled:
                self._log_violation(violation)
            
            if self.strict:
                raise DeterminismViolation(
                    f"LLM call with non-zero temperature: {temperature}\n"
                    "All LLM calls must use temperature=0.0 for determinism.\n"
                    f"Full params: {params}"
                )
            else:
                print(f"⚠️  Non-deterministic LLM call: temperature={temperature}")
                return False
        
        return True
    
    def validate_config(self, config: LLMConfig):
        """
        Validate LLMConfig object.
        
        Args:
            config: LLMConfig to validate
        
        Raises:
            DeterminismViolation: If temperature != 0.0
        """
        # LLMConfig already validates on creation
        # This is a no-op but included for API consistency
        config.validate()
    
    def enforce(self, func):
        """
        Decorator to enforce deterministic parameters on LLM calls.
        
        Usage:
            validator = LLMConfigValidator()
            
            @validator.enforce
            def my_llm_call(temperature=0.0, **kwargs):
                return api.call(temperature=temperature, **kwargs)
        """
        def wrapper(*args, **kwargs):
            # Extract temperature from kwargs
            temperature = kwargs.get('temperature', 1.0)
            
            # Validate
            self.validate_params({'temperature': temperature, **kwargs})
            
            # Call original function
            return func(*args, **kwargs)
        
        return wrapper
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all recorded violations."""
        return self.violations
    
    def clear_violations(self):
        """Clear violation history."""
        self.violations.clear()
    
    def _log_violation(self, violation: Dict[str, Any]):
        """Log violation to file."""
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(violation) + '\n')


# =============================================================================
# Configuration Presets
# =============================================================================

class LLMConfigPresets:
    """Predefined LLM configurations for common use cases."""
    
    @staticmethod
    def gpt4_deterministic(max_tokens: Optional[int] = None) -> LLMConfig:
        """GPT-4 with deterministic settings."""
        return LLMConfig(
            model="gpt-4-turbo",
            temperature=0.0,
            max_tokens=max_tokens,
            provider="openai"
        )
    
    @staticmethod
    def gpt4o_deterministic(max_tokens: Optional[int] = None) -> LLMConfig:
        """GPT-4o with deterministic settings."""
        return LLMConfig(
            model="gpt-4o",
            temperature=0.0,
            max_tokens=max_tokens,
            provider="openai"
        )
    
    @staticmethod
    def claude_deterministic(max_tokens: Optional[int] = None) -> LLMConfig:
        """Claude with deterministic settings."""
        return LLMConfig(
            model="claude-3-5-sonnet-20241022",
            temperature=0.0,
            max_tokens=max_tokens,
            provider="anthropic"
        )
    
    @staticmethod
    def custom_deterministic(
        model: str,
        provider: str = "openai",
        max_tokens: Optional[int] = None
    ) -> LLMConfig:
        """Custom model with deterministic settings."""
        return LLMConfig(
            model=model,
            temperature=0.0,
            max_tokens=max_tokens,
            provider=provider
        )


# =============================================================================
# Configuration Manager
# =============================================================================

class LLMConfigManager:
    """
    Manages LLM configurations across agent system.
    
    Ensures all LLM calls use deterministic settings.
    
    Usage:
        manager = LLMConfigManager()
        
        # Get configuration for task
        config = manager.get_config("planner")
        
        # Use in LLM call
        response = llm_api.call(**config.to_openai_params())
    """
    
    def __init__(
        self,
        config_path: str = ".agent-state/llm-config.json",
        validator: Optional[LLMConfigValidator] = None
    ):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
            validator: Optional validator instance
        """
        self.config_path = Path(config_path)
        self.validator = validator or LLMConfigValidator(strict=True)
        
        # Load configurations
        self.configs: Dict[str, LLMConfig] = {}
        self._load_configs()
    
    def get_config(self, task_type: str) -> LLMConfig:
        """
        Get LLM configuration for task type.
        
        Args:
            task_type: Type of task (e.g., "planner", "reviewer", "qa")
        
        Returns:
            LLMConfig
        """
        if task_type in self.configs:
            return self.configs[task_type]
        
        # Default to GPT-4o deterministic
        return LLMConfigPresets.gpt4o_deterministic()
    
    def set_config(self, task_type: str, config: LLMConfig):
        """
        Set configuration for task type.
        
        Args:
            task_type: Type of task
            config: LLM configuration
        """
        # Validate configuration
        self.validator.validate_config(config)
        
        # Store
        self.configs[task_type] = config
        
        # Save to disk
        self._save_configs()
    
    def _load_configs(self):
        """Load configurations from disk."""
        if not self.config_path.exists():
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for task_type, config_dict in data.items():
                try:
                    config = LLMConfig(**config_dict)
                    self.configs[task_type] = config
                except Exception as e:
                    print(f"⚠️  Failed to load config for {task_type}: {e}")
        except Exception as e:
            print(f"⚠️  Failed to load configurations: {e}")
    
    def _save_configs(self):
        """Save configurations to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            task_type: config.to_dict()
            for task_type, config in self.configs.items()
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== LLM Configuration Enforcement Demo ===\n")
    
    # Create deterministic config
    print("--- Creating deterministic config ---\n")
    
    config = LLMConfigPresets.gpt4_deterministic()
    print(f"Model: {config.model}")
    print(f"Temperature: {config.temperature}")
    print(f"Top-p: {config.top_p}")
    
    # Try invalid config (will raise)
    print("\n--- Testing invalid config (should fail) ---\n")
    
    try:
        invalid_config = LLMConfig(
            model="gpt-4",
            temperature=0.7  # Non-zero!
        )
        print("❌ Should have raised DeterminismViolation")
    except DeterminismViolation as e:
        print(f"✓ Caught violation: {str(e)[:60]}...")
    
    # Validator
    print("\n--- Testing validator ---\n")
    
    validator = LLMConfigValidator(strict=True)
    
    # Valid params
    valid_params = {'model': 'gpt-4', 'temperature': 0.0}
    try:
        validator.validate_params(valid_params)
        print("✓ Valid params accepted")
    except DeterminismViolation:
        print("❌ Should not have raised")
    
    # Invalid params
    invalid_params = {'model': 'gpt-4', 'temperature': 0.8}
    try:
        validator.validate_params(invalid_params)
        print("❌ Should have raised DeterminismViolation")
    except DeterminismViolation as e:
        print(f"✓ Invalid params rejected")
    
    # Configuration manager
    print("\n--- Testing configuration manager ---\n")
    
    manager = LLMConfigManager()
    
    # Set config for planner
    planner_config = LLMConfigPresets.gpt4o_deterministic(max_tokens=4000)
    manager.set_config("planner", planner_config)
    
    # Get config
    retrieved_config = manager.get_config("planner")
    print(f"Planner config: {retrieved_config.model}, temp={retrieved_config.temperature}")
    
    # Get default config for unknown task
    default_config = manager.get_config("unknown-task")
    print(f"Default config: {default_config.model}, temp={default_config.temperature}")
    
    print("\n✓ Demo complete")
