"""
Configuration management for MDTD Test Engine
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class Config:
    """Configuration class for the MDTD Test Engine"""

    # OpenAI Configuration
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    openai_model: str = field(default_factory=lambda: os.getenv('OPENAI_MODEL', 'gpt-4'))
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.3

    # Supported file extensions and languages
    supported_languages: Dict[str, List[str]] = field(default_factory=lambda: {
        'python': ['.py'],
        'java': ['.java'],
        'cpp': ['.cpp', '.cc', '.cxx', '.c++'],
        'c': ['.c'],
        'javascript': ['.js', '.ts'],
        'csharp': ['.cs'],
        'go': ['.go'],
        'rust': ['.rs'],
        'php': ['.php'],
        'ruby': ['.rb'],
        'kotlin': ['.kt'],
        'scala': ['.scala']
    })

    # MDTD Test Categories
    test_categories: List[str] = field(default_factory=lambda: [
        'equivalence_partitioning',
        'boundary_value_analysis',
        'error_condition_testing',
        'state_transition_testing',
        'decision_table_testing',
        'pairwise_testing'
    ])

    # Output Configuration
    output_formats: List[str] = field(default_factory=lambda: ['html', 'json', 'python', 'javascript'])
    max_tests_per_function: int = 20
    include_performance_tests: bool = True
    include_security_tests: bool = True

    # Web Interface Configuration
    web_port: int = 8080
    web_host: str = '127.0.0.1'
    enable_live_editing: bool = True

    # Logging Configuration
    log_level: str = 'INFO'
    log_file: Optional[str] = None

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file or environment"""
        config = cls()

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

        return config

    def save(self, config_path: str):
        """Save configuration to file"""
        config_dict = {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }

        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

    def get_language_for_extension(self, extension: str) -> Optional[str]:
        """Get language name for file extension"""
        for language, extensions in self.supported_languages.items():
            if extension.lower() in extensions:
                return language
        return None

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.openai_api_key:
            print("Warning: OpenAI API key not configured")
            return False

        return True
