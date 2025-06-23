"""
Tests for ITGlue Configuration model.
"""

import pytest
from datetime import datetime

from itglue.models.configuration import (
    Configuration,
    ConfigurationCollection,
    ConfigurationStatus,
)
from itglue.models.base import ResourceType


class TestConfigurationStatus:
    """Test ConfigurationStatus enumeration."""
    
    def test_status_values(self):
        """Test configuration status values."""
        assert ConfigurationStatus.ACTIVE.value == "Active"
        assert ConfigurationStatus.INACTIVE.value == "Inactive"
        assert ConfigurationStatus.PLANNED.value == "Planned"
        assert ConfigurationStatus.RETIRED.value == "Retired"


class TestConfiguration:
    """Test Configuration model."""
    
    def test_configuration_creation_minimal(self):
        """Test minimal configuration creation."""
        config = Configuration(id="123")
        
        assert config.id == "123"
        assert config.type == ResourceType.CONFIGURATIONS
    
    def test_configuration_creation_with_attributes(self):
        """Test configuration creation with attributes."""
        config = Configuration(
            id="123",
            name="Test Server",
            hostname="test-server.example.com",
            **{"primary-ip": "192.168.1.100", "configuration-status-name": "Active"}
        )
        
        assert config.id == "123"
        assert config.name == "Test Server"
        assert config.hostname == "test-server.example.com"
        assert config.primary_ip == "192.168.1.100"
        assert config.configuration_status_name == "Active"
    
    def test_configuration_properties(self):
        """Test configuration properties work correctly."""
        config = Configuration(id="123")
        
        # Test name property
        config.name = "Test Configuration"
        assert config.name == "Test Configuration"
        
        # Test hostname property
        config.hostname = "test.example.com"
        assert config.hostname == "test.example.com"
        
        # Test status property
        config.configuration_status_name = "Active"
        assert config.configuration_status_name == "Active"
    
    def test_configuration_convenience_methods(self):
        """Test configuration convenience methods."""
        config = Configuration(id="123")
        
        # Test is_active
        config.configuration_status_name = ConfigurationStatus.ACTIVE.value
        assert config.is_active() is True
        
        config.configuration_status_name = ConfigurationStatus.INACTIVE.value
        assert config.is_active() is False
        
        # Test is_retired
        config.configuration_status_name = ConfigurationStatus.RETIRED.value
        assert config.is_retired() is True
        
        config.configuration_status_name = ConfigurationStatus.ACTIVE.value
        assert config.is_retired() is False
    
    def test_configuration_string_representation(self):
        """Test configuration string representations."""
        config = Configuration(
            id="123",
            name="Test Server",
            **{"configuration-status-name": "Active"}
        )
        
        str_repr = str(config)
        assert "123" in str_repr
        assert "Test Server" in str_repr
        
        repr_str = repr(config)
        assert "123" in repr_str
        assert "Test Server" in repr_str
        assert "Active" in repr_str
    
    def test_configuration_from_api_dict(self):
        """Test creating configuration from API response."""
        api_data = {
            "type": "configurations",
            "id": "123",
            "attributes": {
                "name": "Test Server",
                "hostname": "test-server.example.com",
                "primary-ip": "192.168.1.100",
                "configuration-status-name": "Active",
                "created-at": "2023-08-01T12:00:00.000Z"
            },
            "relationships": {
                "organization": {
                    "data": {
                        "type": "organizations",
                        "id": "1"
                    }
                }
            }
        }
        
        config = Configuration.from_api_dict(api_data)
        
        assert config.id == "123"
        assert config.name == "Test Server"
        assert config.hostname == "test-server.example.com"
        assert config.primary_ip == "192.168.1.100"
        assert config.configuration_status_name == "Active"
        assert config.created_at is not None
        assert config.organization_id == "1"
    
    def test_configuration_to_api_dict(self):
        """Test converting configuration to API format."""
        config = Configuration(
            id="123",
            name="Test Server",
            hostname="test-server.example.com",
            **{"configuration-status-name": "Active"}
        )
        
        api_dict = config.to_api_dict()
        
        assert api_dict["type"] == "configurations"
        assert api_dict["id"] == "123"
        assert api_dict["attributes"]["name"] == "Test Server"
        assert api_dict["attributes"]["hostname"] == "test-server.example.com"
        assert api_dict["attributes"]["configuration-status-name"] == "Active"


class TestConfigurationCollection:
    """Test ConfigurationCollection model."""
    
    def create_sample_configurations(self):
        """Create sample configurations for testing."""
        return [
            Configuration(
                id="1",
                name="Active Server",
                **{"configuration-status-name": "Active"}
            ),
            Configuration(
                id="2", 
                name="Planned Workstation",
                **{"configuration-status-name": "Planned"}
            ),
            Configuration(
                id="3",
                name="Retired Router",
                **{"configuration-status-name": "Retired"}
            ),
            Configuration(
                id="4",
                name="Another Active Server",
                **{"configuration-status-name": "Active"}
            )
        ]
    
    def test_collection_creation(self):
        """Test configuration collection creation."""
        configs = self.create_sample_configurations()
        collection = ConfigurationCollection(data=configs)
        
        assert len(collection) == 4
        assert collection.count == 4
        assert collection[0].name == "Active Server"
    
    def test_collection_get_by_name(self):
        """Test finding configuration by name."""
        configs = self.create_sample_configurations()
        collection = ConfigurationCollection(data=configs)
        
        # Case insensitive search
        config = collection.get_by_name("active server")
        assert config is not None
        assert config.id == "1"
        assert config.name == "Active Server"
        
        # Exact case
        config = collection.get_by_name("Planned Workstation")
        assert config is not None
        assert config.id == "2"
        
        # Non-existent
        config = collection.get_by_name("Non-existent")
        assert config is None
    
    def test_collection_get_active_configurations(self):
        """Test getting active configurations."""
        configs = self.create_sample_configurations()
        collection = ConfigurationCollection(data=configs)
        
        active_configs = collection.get_active_configurations()
        
        assert len(active_configs) == 2
        assert all(config.is_active() for config in active_configs)
        assert "3" not in [config.id for config in active_configs]  # Retired one excluded
    
    def test_collection_get_retired_configurations(self):
        """Test getting retired configurations."""
        configs = self.create_sample_configurations()
        collection = ConfigurationCollection(data=configs)
        
        retired_configs = collection.get_retired_configurations()
        
        assert len(retired_configs) == 1
        assert retired_configs[0].id == "3"
        assert retired_configs[0].is_retired()
    
    def test_collection_from_api_dict(self):
        """Test creating collection from API response."""
        api_data = {
            "data": [
                {
                    "type": "configurations",
                    "id": "1",
                    "attributes": {
                        "name": "Test Config 1",
                        "configuration-status-name": "Active"
                    }
                },
                {
                    "type": "configurations", 
                    "id": "2",
                    "attributes": {
                        "name": "Test Config 2",
                        "configuration-status-name": "Planned"
                    }
                }
            ],
            "meta": {
                "current-page": 1,
                "total-count": 2
            }
        }
        
        collection = ConfigurationCollection.from_api_dict(api_data)
        
        assert len(collection) == 2
        assert collection.total_count == 2
        assert collection.current_page == 1
        assert collection[0].name == "Test Config 1"
        assert collection[1].name == "Test Config 2" 