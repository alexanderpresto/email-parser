"""
Pre-defined configuration profiles for common email processing scenarios.

This module provides a set of pre-configured processing profiles that users
can select for different use cases, from quick processing to comprehensive
analysis.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProcessingProfile:
    """Represents a processing configuration profile."""
    name: str
    display_name: str
    description: str
    settings: Dict[str, Any]
    priority: int = 50  # For sorting in UI
    is_builtin: bool = True
    is_default: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary format."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "settings": self.settings,
            "priority": self.priority,
            "is_builtin": self.is_builtin,
            "is_default": self.is_default
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingProfile':
        """Create profile from dictionary."""
        return cls(
            name=data["name"],
            display_name=data["display_name"],
            description=data["description"],
            settings=data["settings"],
            priority=data.get("priority", 50),
            is_builtin=data.get("is_builtin", False),
            is_default=data.get("is_default", False)
        )


# Built-in profile definitions
BUILTIN_PROFILES = {
    "quick": ProcessingProfile(
        name="quick",
        display_name="🚀 Quick Processing",
        description="Fast processing with minimal conversions - ideal for quick email review",
        priority=10,
        is_default=True,
        settings={
            "processing": {
                "convert_pdf": False,
                "convert_docx": False,
                "convert_excel": True,
                "extract_metadata": True,
                "save_attachments": True
            },
            "pdf_conversion": {
                "enabled": False
            },
            "docx_conversion": {
                "enabled": False
            },
            "excel_conversion": {
                "enabled": True,
                "preserve_formulas": False
            },
            "performance": {
                "parallel_processing": False,
                "max_workers": 1,
                "memory_limit_mb": 256
            }
        }
    ),
    
    "comprehensive": ProcessingProfile(
        name="comprehensive",
        display_name="📊 Comprehensive",
        description="Full processing with all conversions enabled - balanced performance",
        priority=20,
        settings={
            "processing": {
                "convert_pdf": True,
                "convert_docx": True,
                "convert_excel": True,
                "extract_metadata": True,
                "save_attachments": True
            },
            "pdf_conversion": {
                "enabled": True,
                "extraction_mode": "all",
                "extract_images": True,
                "image_quality": 85,
                "use_ocr": True
            },
            "docx_conversion": {
                "enabled": True,
                "output_format": "both",
                "extract_tables": True,
                "extract_images": True,
                "preserve_styles": True,
                "include_comments": True
            },
            "excel_conversion": {
                "enabled": True,
                "convert_all_sheets": True,
                "preserve_formulas": True
            },
            "performance": {
                "parallel_processing": True,
                "max_workers": 4,
                "memory_limit_mb": 512
            }
        }
    ),
    
    "ai_ready": ProcessingProfile(
        name="ai_ready",
        display_name="🤖 AI-Ready",
        description="Optimized for AI/LLM processing with semantic chunking and clean output",
        priority=30,
        settings={
            "processing": {
                "convert_pdf": True,
                "convert_docx": True,
                "convert_excel": True,
                "extract_metadata": True,
                "save_attachments": True
            },
            "pdf_conversion": {
                "enabled": True,
                "extraction_mode": "all",
                "extract_images": True,
                "image_quality": 90,
                "use_ocr": True,
                "optimize_for_llm": True
            },
            "docx_conversion": {
                "enabled": True,
                "output_format": "markdown",
                "extract_tables": True,
                "enable_chunking": True,
                "chunk_strategy": "semantic",
                "max_chunk_tokens": 2000,
                "chunk_overlap": 200,
                "extract_images": True,
                "preserve_styles": False,
                "include_comments": True
            },
            "excel_conversion": {
                "enabled": True,
                "convert_all_sheets": True,
                "preserve_formulas": False,
                "optimize_for_analysis": True
            },
            "performance": {
                "parallel_processing": True,
                "max_workers": 4,
                "memory_limit_mb": 1024
            }
        }
    ),
    
    "archive": ProcessingProfile(
        name="archive",
        display_name="🗄️ Archive Mode",
        description="Preserve everything with maximum quality - ideal for long-term storage",
        priority=40,
        settings={
            "processing": {
                "convert_pdf": True,
                "convert_docx": True,
                "convert_excel": True,
                "extract_metadata": True,
                "save_attachments": True,
                "preserve_original": True
            },
            "pdf_conversion": {
                "enabled": True,
                "extraction_mode": "all",
                "extract_images": True,
                "image_quality": 100,
                "use_ocr": True,
                "create_searchable_pdf": True
            },
            "docx_conversion": {
                "enabled": True,
                "output_format": "both",
                "extract_tables": True,
                "extract_images": True,
                "preserve_styles": True,
                "include_comments": True,
                "extract_metadata": True,
                "preserve_formatting": True
            },
            "excel_conversion": {
                "enabled": True,
                "convert_all_sheets": True,
                "preserve_formulas": True,
                "preserve_formatting": True,
                "extract_charts": True
            },
            "performance": {
                "parallel_processing": True,
                "max_workers": 2,
                "memory_limit_mb": 2048,
                "quality_over_speed": True
            }
        }
    ),
    
    "dev": ProcessingProfile(
        name="dev",
        display_name="🔧 Development",
        description="Development mode with verbose logging and debug information",
        priority=90,
        settings={
            "processing": {
                "convert_pdf": True,
                "convert_docx": True,
                "convert_excel": True,
                "extract_metadata": True,
                "save_attachments": True,
                "debug_mode": True
            },
            "pdf_conversion": {
                "enabled": True,
                "extraction_mode": "all",
                "extract_images": True,
                "image_quality": 85,
                "use_ocr": True,
                "save_debug_info": True
            },
            "docx_conversion": {
                "enabled": True,
                "output_format": "both",
                "extract_tables": True,
                "enable_chunking": True,
                "chunk_strategy": "fixed",
                "max_chunk_tokens": 1000,
                "extract_images": True,
                "preserve_styles": True,
                "include_comments": True,
                "save_intermediate": True
            },
            "excel_conversion": {
                "enabled": True,
                "convert_all_sheets": True,
                "preserve_formulas": True,
                "verbose_logging": True
            },
            "performance": {
                "parallel_processing": False,
                "max_workers": 1,
                "memory_limit_mb": 512,
                "enable_profiling": True,
                "collect_metrics": True
            },
            "logging": {
                "level": "DEBUG",
                "save_logs": True,
                "log_performance": True,
                "log_api_calls": True
            }
        }
    )
}


class ProfileManager:
    """Manages processing profiles including built-in and custom profiles."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the profile manager.
        
        Args:
            config_dir: Directory to store custom profiles
        """
        self.config_dir = config_dir or Path.home() / ".email_parser" / "profiles"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load profiles
        self.profiles: Dict[str, ProcessingProfile] = {}
        self._load_builtin_profiles()
        self._load_custom_profiles()
        
    def _load_builtin_profiles(self):
        """Load built-in profiles."""
        for name, profile in BUILTIN_PROFILES.items():
            self.profiles[name] = profile
            
    def _load_custom_profiles(self):
        """Load custom user-defined profiles from disk."""
        custom_profiles_file = self.config_dir / "custom_profiles.json"
        
        if custom_profiles_file.exists():
            try:
                with open(custom_profiles_file, 'r') as f:
                    custom_data = json.load(f)
                    
                for profile_data in custom_data.get("profiles", []):
                    profile = ProcessingProfile.from_dict(profile_data)
                    profile.is_builtin = False
                    self.profiles[profile.name] = profile
                    
                logger.info(f"Loaded {len(custom_data.get('profiles', []))} custom profiles")
                
            except Exception as e:
                logger.error(f"Failed to load custom profiles: {e}")
                
    def save_custom_profiles(self):
        """Save custom profiles to disk."""
        custom_profiles = {
            name: profile.to_dict()
            for name, profile in self.profiles.items()
            if not profile.is_builtin
        }
        
        custom_profiles_file = self.config_dir / "custom_profiles.json"
        
        try:
            with open(custom_profiles_file, 'w') as f:
                json.dump({"profiles": list(custom_profiles.values())}, f, indent=2)
                
            logger.info(f"Saved {len(custom_profiles)} custom profiles")
            
        except Exception as e:
            logger.error(f"Failed to save custom profiles: {e}")
            
    def get_profile(self, name: str) -> Optional[ProcessingProfile]:
        """
        Get a profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            ProcessingProfile or None if not found
        """
        return self.profiles.get(name)
        
    def get_default_profile(self) -> ProcessingProfile:
        """Get the default profile."""
        # First try to find explicitly marked default
        for profile in self.profiles.values():
            if profile.is_default:
                return profile
                
        # Fall back to 'quick' profile
        return self.profiles.get("quick", next(iter(self.profiles.values())))
        
    def list_profiles(self, include_custom: bool = True) -> List[ProcessingProfile]:
        """
        List all available profiles.
        
        Args:
            include_custom: Whether to include custom profiles
            
        Returns:
            List of profiles sorted by priority
        """
        profiles = []
        
        for profile in self.profiles.values():
            if include_custom or profile.is_builtin:
                profiles.append(profile)
                
        # Sort by priority (lower number = higher priority)
        return sorted(profiles, key=lambda p: p.priority)
        
    def create_profile(
        self, 
        name: str, 
        display_name: str,
        description: str,
        settings: Dict[str, Any],
        base_profile: Optional[str] = None
    ) -> ProcessingProfile:
        """
        Create a new custom profile.
        
        Args:
            name: Unique profile name
            display_name: Display name for UI
            description: Profile description
            settings: Profile settings
            base_profile: Optional base profile to inherit from
            
        Returns:
            Created profile
            
        Raises:
            ValueError: If profile name already exists
        """
        if name in self.profiles:
            raise ValueError(f"Profile '{name}' already exists")
            
        # If base profile specified, merge settings
        if base_profile and base_profile in self.profiles:
            base_settings = self.profiles[base_profile].settings.copy()
            # Deep merge settings
            merged_settings = self._deep_merge(base_settings, settings)
            settings = merged_settings
            
        profile = ProcessingProfile(
            name=name,
            display_name=display_name,
            description=description,
            settings=settings,
            is_builtin=False,
            priority=100  # Custom profiles have lower priority
        )
        
        self.profiles[name] = profile
        self.save_custom_profiles()
        
        return profile
        
    def update_profile(
        self, 
        name: str, 
        settings: Optional[Dict[str, Any]] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> ProcessingProfile:
        """
        Update an existing custom profile.
        
        Args:
            name: Profile name
            settings: New settings (will be merged)
            display_name: New display name
            description: New description
            
        Returns:
            Updated profile
            
        Raises:
            ValueError: If profile doesn't exist or is built-in
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found")
            
        profile = self.profiles[name]
        
        if profile.is_builtin:
            raise ValueError(f"Cannot modify built-in profile '{name}'")
            
        # Update fields
        if display_name:
            profile.display_name = display_name
        if description:
            profile.description = description
        if settings:
            profile.settings = self._deep_merge(profile.settings, settings)
            
        self.save_custom_profiles()
        
        return profile
        
    def delete_profile(self, name: str):
        """
        Delete a custom profile.
        
        Args:
            name: Profile name
            
        Raises:
            ValueError: If profile doesn't exist or is built-in
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found")
            
        profile = self.profiles[name]
        
        if profile.is_builtin:
            raise ValueError(f"Cannot delete built-in profile '{name}'")
            
        del self.profiles[name]
        self.save_custom_profiles()
        
    def export_profile(self, name: str, output_path: Path):
        """
        Export a profile to a file.
        
        Args:
            name: Profile name
            output_path: Path to save the profile
            
        Raises:
            ValueError: If profile doesn't exist
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found")
            
        profile = self.profiles[name]
        
        with open(output_path, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
            
        logger.info(f"Exported profile '{name}' to {output_path}")
        
    def import_profile(self, input_path: Path, overwrite: bool = False):
        """
        Import a profile from a file.
        
        Args:
            input_path: Path to the profile file
            overwrite: Whether to overwrite existing profile
            
        Returns:
            Imported profile
            
        Raises:
            ValueError: If profile already exists and overwrite is False
        """
        with open(input_path, 'r') as f:
            profile_data = json.load(f)
            
        profile = ProcessingProfile.from_dict(profile_data)
        profile.is_builtin = False
        
        if profile.name in self.profiles and not overwrite:
            raise ValueError(f"Profile '{profile.name}' already exists")
            
        self.profiles[profile.name] = profile
        self.save_custom_profiles()
        
        logger.info(f"Imported profile '{profile.name}' from {input_path}")
        
        return profile
        
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def apply_profile(self, profile_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a profile's settings to a configuration dictionary.
        
        Args:
            profile_name: Name of the profile to apply
            config: Base configuration dictionary
            
        Returns:
            Updated configuration with profile settings applied
            
        Raises:
            ValueError: If profile not found
        """
        profile = self.get_profile(profile_name)
        if not profile:
            raise ValueError(f"Profile '{profile_name}' not found")
            
        # Deep merge profile settings into config
        return self._deep_merge(config, profile.settings)