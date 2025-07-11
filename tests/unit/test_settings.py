"""
Unit tests for settings module.

This module tests the configuration and settings functionality.
"""

from sidekick.settings import APIConfig, LoggingConfig, Settings


class TestLoggingConfig:
    """Test cases for LoggingConfig."""

    def test_default_logging_config(self):
        """Test default logging configuration."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.format == "pretty"
        # In pytest mode, file is automatically set to logs/test-sidekick.log
        if config.pytest_mode:
            assert str(config.file) == "logs/test-sidekick.log"
        else:
            assert config.file is None

    def test_custom_logging_config(self):
        """Test custom logging configuration."""
        config = LoggingConfig(level="DEBUG", format="json", file="/tmp/test.log")
        assert config.level == "DEBUG"
        assert config.format == "json"
        assert str(config.file) == "/tmp/test.log"


class TestAPIConfig:
    """Test cases for APIConfig."""

    def test_default_api_config(self):
        """Test default API configuration."""
        config = APIConfig()
        assert config.host == "localhost"
        assert config.port == 8000
        assert config.timeout == 30

    def test_custom_api_config(self):
        """Test custom API configuration."""
        config = APIConfig(host="0.0.0.0", port=9000, timeout=60)
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.timeout == 60


class TestSettings:
    """Test cases for Settings."""

    def test_default_settings(self):
        """Test default settings."""
        settings = Settings()
        assert settings.app_name == "sidekick"
        assert settings.debug is False
        assert settings.environment == "development"
        assert settings.color_output is True
        assert settings.verbose is False

    def test_nested_configs(self):
        """Test nested configuration objects."""
        settings = Settings()
        assert isinstance(settings.logging, LoggingConfig)
        assert isinstance(settings.api, APIConfig)
        assert settings.logging.level == "INFO"
        assert settings.api.port == 8000

    def test_environment_variable_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("APP_NAME", "Test App")
        monkeypatch.setenv("LOGGING__LEVEL", "DEBUG")

        settings = Settings()
        assert settings.debug is True
        assert settings.app_name == "Test App"
        assert settings.logging.level == "DEBUG"
