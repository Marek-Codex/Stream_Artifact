"""
Configuration Management for Stream Artifact
Handles settings, persistence, and user preferences
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TwitchConfig:
    """Twitch connection configuration"""
    channel: str = ""
    token: str = ""
    username: str = ""
    client_id: str = ""


@dataclass
class AIConfig:
    """AI/OpenRouter configuration"""
    api_key: str = ""
    model: str = "anthropic/claude-3-haiku"
    personality: str = "You are a friendly, helpful AI assistant for a Twitch stream. You engage naturally with viewers and provide helpful responses."
    memory_enabled: bool = True
    memory_depth: int = 10
    random_reply_chance: float = 0.05
    max_response_length: int = 480


@dataclass
class UIConfig:
    """UI appearance and behavior configuration"""
    theme: str = "cyberpunk"
    window_width: int = 1200
    window_height: int = 800
    always_on_top: bool = False
    minimize_to_tray: bool = True
    glass_effect: bool = True
    glow_intensity: float = 0.3


@dataclass
class AppConfig:
    """Main application configuration"""
    twitch: TwitchConfig
    ai: AIConfig
    ui: UIConfig
    
    def __init__(self):
        self.twitch = TwitchConfig()
        self.ai = AIConfig()
        self.ui = UIConfig()


class Config:
    """Configuration manager for Stream Artifact"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".stream_artifact"
        self.config_file = self.config_dir / "config.json"
        self.config = AppConfig()
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load existing config
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update config with loaded data
                if 'twitch' in data:
                    self.config.twitch = TwitchConfig(**data['twitch'])
                if 'ai' in data:
                    self.config.ai = AIConfig(**data['ai'])
                if 'ui' in data:
                    self.config.ui = UIConfig(**data['ui'])
                
                logger.info("⚙️ Configuration loaded successfully")
            else:
                logger.info("⚙️ Using default configuration")
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            logger.info("⚙️ Using default configuration")
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            config_dict = {
                'twitch': asdict(self.config.twitch),
                'ai': asdict(self.config.ai),
                'ui': asdict(self.config.ui)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=4)
            
            logger.info("💾 Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                value = getattr(value, k)
            
            return value
        except (AttributeError, KeyError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key"""
        try:
            keys = key.split('.')
            obj = self.config
            
            # Navigate to the parent object
            for k in keys[:-1]:
                obj = getattr(obj, k)
            
            # Set the value
            setattr(obj, keys[-1], value)
            
        except (AttributeError, KeyError) as e:
            logger.error(f"❌ Failed to set config value {key}: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = AppConfig()
        logger.info("🔄 Configuration reset to defaults")
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory path"""
        return self.config_dir
    
    @property
    def database_path(self) -> Path:
        """Get the database file path"""
        return self.config_dir / "stream_artifact.db"
    
    @property
    def logs_dir(self) -> Path:
        """Get the logs directory path"""
        logs_dir = self.config_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    def is_first_run(self) -> bool:
        """Check if this is the first run of the application"""
        return not self.config_file.exists() or (
            not self.config.twitch.token and 
            not self.config.ai.api_key
        )
    
    def mark_setup_complete(self) -> None:
        """Mark the initial setup as complete"""
        # Save the current configuration
        self.save()
        logger.info("✅ Initial setup marked as complete")
    
    def has_valid_config(self) -> bool:
        """Check if the configuration has the minimum required settings"""
        return (
            bool(self.config.twitch.token) and
            bool(self.config.twitch.username) and
            bool(self.config.ai.api_key)
        )
