"""Configuration management for dbt-ai"""

import os
from typing import Optional


class Config:
    """Configuration class for dbt-ai settings"""

    # Model configurations
    DEFAULT_MODEL = "gpt-4o-mini"  # Cost-effective, high-quality model
    ADVANCED_MODEL = "gpt-4o"  # More powerful model for complex tasks
    FALLBACK_MODEL = "gpt-3.5-turbo"  # Fallback for compatibility

    # API settings
    MAX_TOKENS = 4000
    TEMPERATURE = 0.1

    # Image generation
    DEFAULT_IMAGE_SIZE = "1024x1024"

    @classmethod
    def get_basic_model(cls) -> str:
        """Get model for basic suggestions"""
        return os.getenv("DBT_AI_BASIC_MODEL", cls.DEFAULT_MODEL)

    @classmethod
    def get_advanced_model(cls) -> str:
        """Get model for advanced suggestions"""
        return os.getenv("DBT_AI_ADVANCED_MODEL", cls.ADVANCED_MODEL)

    @classmethod
    def get_fallback_model(cls) -> str:
        """Get fallback model for compatibility"""
        return os.getenv("DBT_AI_FALLBACK_MODEL", cls.FALLBACK_MODEL)

    @classmethod
    def get_max_tokens(cls) -> int:
        """Get maximum tokens for API calls"""
        return int(os.getenv("DBT_AI_MAX_TOKENS", str(cls.MAX_TOKENS)))

    @classmethod
    def get_temperature(cls) -> float:
        """Get temperature for API calls"""
        return float(os.getenv("DBT_AI_TEMPERATURE", str(cls.TEMPERATURE)))

    @classmethod
    def get_openai_api_key(cls) -> Optional[str]:
        """Get OpenAI API key"""
        return os.getenv("OPENAI_API_KEY")

    @classmethod
    def is_api_available(cls) -> bool:
        """Check if OpenAI API key is available"""
        return bool(cls.get_openai_api_key())
