"""
Application settings and configuration management.

This module provides centralized configuration management with support for
environment variables, configuration files, and hierarchical settings.
"""

import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseModel):
    """Logging configuration with support for standard environment variables."""

    level: str = Field(default="INFO", description="Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    format: str = Field(default="pretty", description="Log format: pretty or json")
    file: Path | None = Field(
        default=None, description="Path to log file, defaults to logs/sidekick.log in pytest mode"
    )

    # Internal fields for enhanced functionality
    trace_enabled: bool = Field(default=False, description="Enable TRACE level logging")
    pytest_mode: bool = Field(default=False, description="Running under pytest")

    @model_validator(mode="after")
    def configure_logging(self):
        """Post-validation configuration."""
        # Detect pytest execution
        self.pytest_mode = self._detect_pytest()

        # Enable trace if level is TRACE
        if self.level.upper() == "TRACE":
            self.trace_enabled = True

        # Auto-configure file logging for pytest
        if self.pytest_mode and self.file is None:
            self.file = Path("logs/test-sidekick.log")
        elif not self.pytest_mode and self.file is None:
            # Default file location for non-pytest runs if desired
            pass

        return self

    @staticmethod
    def _detect_pytest() -> bool:
        """Detect if running under pytest."""
        return "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ


class APIConfig(BaseModel):
    """API configuration."""

    host: str = "localhost"
    port: int = 8000
    timeout: int = 30


class Settings(BaseSettings):
    """Main application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    # Application settings
    app_name: str = "sidekick"
    debug: bool = False
    environment: str = "development"

    # Logging configuration with standard environment variables
    log_level: str = Field(default="INFO", description="Log level (standard env: LOG_LEVEL, legacy: LOGGING__LEVEL)")
    log_format: str = Field(
        default="pretty", description="Log format (standard env: LOG_FORMAT, legacy: LOGGING__FORMAT)"
    )
    log_file: Path | None = Field(
        default=None, description="Log file path (standard env: LOG_FILE, legacy: LOGGING__FILE)"
    )

    # Component configs
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    api: APIConfig = Field(default_factory=APIConfig)

    # CLI settings
    color_output: bool = True
    verbose: bool = False

    def __init__(self, **data):
        """Initialize settings with environment variable priority."""
        # Check for standard environment variables first, then legacy
        log_level = os.getenv("LOG_LEVEL") or os.getenv("LOGGING__LEVEL") or "INFO"
        log_format = os.getenv("LOG_FORMAT") or os.getenv("LOGGING__FORMAT") or "pretty"
        log_file = os.getenv("LOG_FILE") or os.getenv("LOGGING__FILE")

        # Override with provided values
        data.setdefault("log_level", log_level)
        data.setdefault("log_format", log_format)
        if log_file:
            data.setdefault("log_file", Path(log_file))

        super().__init__(**data)

    @model_validator(mode="after")
    def sync_logging_config(self):
        """Synchronize top-level logging settings with LoggingConfig."""
        # Update logging config with top-level settings
        self.logging.level = self.log_level
        self.logging.format = self.log_format
        if self.log_file:
            self.logging.file = self.log_file

        # Trigger LoggingConfig post-validation
        self.logging = LoggingConfig.model_validate(self.logging.model_dump())
        return self


# Global settings instance
settings = Settings()
