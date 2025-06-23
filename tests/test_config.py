"""
Test script for ITGlue SDK configuration module.

This tests basic functionality to ensure the foundation works before expanding.
"""

import os
import pytest
from unittest.mock import patch

from itglue.config import ITGlueConfig, ITGlueRegion


class TestITGlueConfig:
    """Test cases for ITGlueConfig class."""

    def test_config_creation_with_required_params(self):
        """Test creating config with minimum required parameters."""
        config = ITGlueConfig(api_key="test-key")

        assert config.api_key == "test-key"
        assert config.base_url == ITGlueRegion.US.value
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_config_headers(self):
        """Test that headers are properly generated."""
        config = ITGlueConfig(api_key="test-key")
        headers = config.get_headers()

        assert headers["x-api-key"] == "test-key"
        assert headers["Content-Type"] == "application/vnd.api+json"
        assert "User-Agent" in headers

    def test_config_full_url(self):
        """Test URL construction."""
        config = ITGlueConfig(api_key="test-key")

        url = config.get_full_url("organizations")
        assert url == "https://api.itglue.com/organizations"

        url = config.get_full_url("/organizations")
        assert url == "https://api.itglue.com/organizations"

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = ITGlueConfig(api_key="test-key")
        config.validate()  # Should not raise

    def test_config_validation_failure_no_api_key(self):
        """Test validation failure when no API key."""
        config = ITGlueConfig(api_key="")

        with pytest.raises(ValueError, match="API key is required"):
            config.validate()

    def test_config_validation_failure_invalid_timeout(self):
        """Test validation failure with invalid timeout."""
        config = ITGlueConfig(api_key="test-key", timeout=0)

        with pytest.raises(ValueError, match="Timeout must be positive"):
            config.validate()

    def test_config_validation_failure_invalid_page_size(self):
        """Test validation failure with invalid page size."""
        config = ITGlueConfig(api_key="test-key", default_page_size=0)

        with pytest.raises(ValueError, match="Page size must be between"):
            config.validate()

    @patch.dict(
        os.environ,
        {
            "ITGLUE_API_KEY": "env-test-key",
            "ITGLUE_REGION": "EU",
            "ITGLUE_TIMEOUT": "60",
        },
    )
    def test_config_from_environment(self):
        """Test creating config from environment variables."""
        config = ITGlueConfig.from_environment()

        assert config.api_key == "env-test-key"
        assert config.base_url == ITGlueRegion.EU.value
        assert config.timeout == 60

    def test_config_from_environment_missing_api_key(self):
        """Test error when API key is missing from environment."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="ITGLUE_API_KEY environment variable is required"
            ):
                ITGlueConfig.from_environment()

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = ITGlueConfig(api_key="test-key", timeout=45)
        config_dict = config.to_dict()

        assert config_dict["api_key"] == "test-key"
        assert config_dict["timeout"] == 45
        assert "base_url" in config_dict

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {"api_key": "dict-test-key", "timeout": 45, "max_retries": 5}

        config = ITGlueConfig.from_dict(config_dict)

        assert config.api_key == "dict-test-key"
        assert config.timeout == 45
        assert config.max_retries == 5

    def test_region_enum(self):
        """Test ITGlue region enum values."""
        assert ITGlueRegion.US.value == "https://api.itglue.com"
        assert ITGlueRegion.EU.value == "https://api.eu.itglue.com"
        assert ITGlueRegion.AU.value == "https://api.au.itglue.com"


if __name__ == "__main__":
    # Run basic tests if executed directly
    print("Running basic ITGlue SDK configuration tests...")

    # Test 1: Basic config creation
    try:
        config = ITGlueConfig(api_key="test-key")
        config.validate()
        print("✓ Basic config creation works")
    except Exception as e:
        print(f"✗ Basic config creation failed: {e}")

    # Test 2: Headers generation
    try:
        config = ITGlueConfig(api_key="test-key")
        headers = config.get_headers()
        assert "x-api-key" in headers
        assert "Content-Type" in headers
        print("✓ Headers generation works")
    except Exception as e:
        print(f"✗ Headers generation failed: {e}")

    # Test 3: URL construction
    try:
        config = ITGlueConfig(api_key="test-key")
        url = config.get_full_url("organizations")
        assert url == "https://api.itglue.com/organizations"
        print("✓ URL construction works")
    except Exception as e:
        print(f"✗ URL construction failed: {e}")

    print(
        "\nBasic tests completed. Run 'pytest tests/test_config.py' for full test suite."
    )
