"""Configuration management for Potion Problem integration.

This module handles loading configuration from environment variables and config files,
providing a centralized way to manage paths and settings without hardcoding.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, rely on system environment variables
    pass

logger = logging.getLogger(__name__)


@dataclass
class PotionProblemConfig:
    """Configuration for Potion Problem integration."""
    api_database_path: Path
    workspace_path: Path
    prioritize_sorry_contributions: bool = True
    include_error_patterns: bool = True
    sorry_contribution_weight: float = 2.0


class ConfigManager:
    """Manages configuration loading from environment and config files."""
    
    def __init__(self, config_file_path: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_file_path: Optional path to config file. If not provided,
                            will look for POTION_PROBLEM_CONFIG_PATH env var
                            or default to 'potion_problem_config.yml'
        """
        self.config_file_path = self._resolve_config_path(config_file_path)
        self._config_data = self._load_config_file()
        
    def _resolve_config_path(self, config_file_path: Optional[Path]) -> Path:
        """Resolve the configuration file path."""
        if config_file_path:
            return config_file_path
            
        # Check environment variable
        env_path = os.getenv("POTION_PROBLEM_CONFIG_PATH")
        if env_path:
            return Path(env_path)
            
        # Default to project root
        project_root = Path(__file__).parent.parent.parent.parent
        return project_root / "potion_problem_config.yml"
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_file_path}: {e}")
        return {}
    
    def get_potion_problem_config(self) -> PotionProblemConfig:
        """Get Potion Problem configuration with environment variable overrides."""
        # Start with config file values
        potion_config = self._config_data.get("potion_problem", {})
        
        # Override with environment variables
        workspace_path = os.getenv("POTION_PROBLEM_PATH")
        if not workspace_path and "workspace_path" in potion_config:
            workspace_path = potion_config["workspace_path"]
        if not workspace_path:
            # Default fallback
            workspace_path = "C:/Users/id374/workspace/potion_problem"
            
        db_path = os.getenv("POTION_PROBLEM_DB_PATH")
        if not db_path and "api_database_path" in potion_config:
            db_path = potion_config["api_database_path"]
        if not db_path:
            # Default fallback
            db_path = f"{workspace_path}/api_database/mathlib_apis.db"
        
        # Get search preferences
        search_prefs = potion_config.get("search_preferences", {})
        
        return PotionProblemConfig(
            api_database_path=Path(db_path),
            workspace_path=Path(workspace_path),
            prioritize_sorry_contributions=search_prefs.get("prioritize_sorry_contributions", True),
            include_error_patterns=search_prefs.get("include_error_patterns", True),
            sorry_contribution_weight=search_prefs.get("sorry_contribution_weight", 2.0)
        )
    
    def get_database_url(self) -> str:
        """Get database URL from config."""
        db_config = self._config_data.get("database", {})
        return db_config.get("url", f"sqlite:///{self.get_potion_problem_config().api_database_path}")
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration."""
        return self._config_data.get("search", {})


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_potion_config() -> PotionProblemConfig:
    """Convenience function to get Potion Problem configuration."""
    return get_config_manager().get_potion_problem_config()