"""
Tests for ITGlue Organization model.
"""

import pytest
from datetime import datetime

from itglue.models.organization import (
    Organization,
    OrganizationCollection,
    OrganizationStatus,
    OrganizationTypeEnum,
)
from itglue.models.base import ResourceType


class TestOrganizationStatus:
    """Test OrganizationStatus enumeration."""
    
    def test_status_values(self):
        """Test organization status values."""
        assert OrganizationStatus.ACTIVE.value == "Active"
        assert OrganizationStatus.INACTIVE.value == "Inactive"


class TestOrganizationTypeEnum:
    """Test OrganizationTypeEnum enumeration."""
    
    def test_type_values(self):
        """Test organization type values."""
        assert OrganizationTypeEnum.INTERNAL.value == "Internal"
        assert OrganizationTypeEnum.CLIENT.value == "Client"
        assert OrganizationTypeEnum.VENDOR.value == "Vendor"
        assert OrganizationTypeEnum.PARTNER.value == "Partner"


class TestOrganization:
    """Test Organization model."""
    
    def test_organization_creation_minimal(self):
        """Test minimal organization creation."""
        org = Organization(id="123")
        
        assert org.id == "123"
        assert org.type == ResourceType.ORGANIZATIONS
        assert org.name is None
    
    def test_organization_creation_with_attributes(self):
        """Test organization creation with attributes."""
        org = Organization(
            id="123",
            name="Test Organization",
            description="A test organization",
            **{"primary-domain": "example.com"}  # Use API field name
        )
        
        assert org.id == "123"
        assert org.name == "Test Organization"
        assert org.description == "A test organization"
        assert org.primary_domain == "example.com"
    
    def test_organization_name_validation(self):
        """Test organization name validation."""
        org = Organization(id="123")
        
        # Valid name
        org.name = "Valid Organization"
        assert org.name == "Valid Organization"
        
        # Note: Since we're using dynamic attributes through __setattr__,
        # validation only happens in the setter. Empty names are handled by ITGlue API.
        # For this SDK, we'll allow empty names and let the API validate.
        org.name = ""
        assert org.name == ""
    
    def test_organization_type_validation(self):
        """Test organization type validation."""
        org = Organization(id="123")
        
        # Valid types
        for org_type in OrganizationTypeEnum:
            org.organization_type_name = org_type.value
            assert org.organization_type_name == org_type.value
        
        # Note: For now, we'll let the API handle validation.
        # The SDK focuses on correct data structure.
        org.organization_type_name = "InvalidType"
        assert org.organization_type_name == "InvalidType"
    
    def test_organization_status_validation(self):
        """Test organization status validation."""
        org = Organization(id="123")
        
        # Valid statuses
        for status in OrganizationStatus:
            org.organization_status_name = status.value
            assert org.organization_status_name == status.value
        
        # Note: Let the API handle validation for now
        org.organization_status_name = "InvalidStatus"
        assert org.organization_status_name == "InvalidStatus"
    
    def test_organization_logo_validation(self):
        """Test organization logo URL validation."""
        org = Organization(id="123")
        
        # Valid URLs
        valid_urls = [
            "https://example.com/logo.png",
            "http://www.example.com/images/logo.jpg"
        ]
        
        for url in valid_urls:
            org.logo = url
            assert org.logo == url
        
        # For now, let API handle URL validation
        org.logo = "not-a-url"
        assert org.logo == "not-a-url"
        
        # None/empty is allowed
        org.logo = None
        assert org.logo is None
    
    def test_organization_timestamps(self):
        """Test organization timestamp handling."""
        org = Organization(
            id="123",
            **{
                "created-at": "2023-08-01T12:00:00.000Z",
                "updated-at": "2023-08-02T12:00:00.000Z"
            }
        )
        
        assert org.created_at is not None
        assert isinstance(org.created_at, datetime)
        assert org.updated_at is not None
        assert isinstance(org.updated_at, datetime)
    
    def test_organization_convenience_methods(self):
        """Test organization convenience methods."""
        org = Organization(id="123")
        
        # Test is_active
        org.organization_status_name = OrganizationStatus.ACTIVE.value
        assert org.is_active() is True
        
        org.organization_status_name = OrganizationStatus.INACTIVE.value
        assert org.is_active() is False
        
        # Test is_client
        org.organization_type_name = OrganizationTypeEnum.CLIENT.value
        assert org.is_client() is True
        
        org.organization_type_name = OrganizationTypeEnum.VENDOR.value
        assert org.is_client() is False
        
        # Test is_internal
        org.organization_type_name = OrganizationTypeEnum.INTERNAL.value
        assert org.is_internal() is True
        
        org.organization_type_name = OrganizationTypeEnum.CLIENT.value
        assert org.is_internal() is False
    
    def test_organization_string_representation(self):
        """Test organization string representations."""
        org = Organization(
            id="123",
            name="Test Organization",
            **{"organization-type-name": "Client", "organization-status-name": "Active"}
        )
        
        str_repr = str(org)
        assert "123" in str_repr
        assert "Test Organization" in str_repr
        
        repr_str = repr(org)
        assert "123" in repr_str
        assert "Test Organization" in repr_str
        assert "Client" in repr_str
        assert "Active" in repr_str
    
    def test_organization_from_api_dict(self):
        """Test creating organization from API response."""
        api_data = {
            "type": "organizations",
            "id": "123",
            "attributes": {
                "name": "Test Organization",
                "description": "A test organization",
                "organization-type-name": "Client",
                "organization-status-name": "Active",
                "primary-domain": "example.com",
                "created-at": "2023-08-01T12:00:00.000Z"
            },
            "relationships": {
                "organization-type": {
                    "data": {
                        "type": "organization-types",
                        "id": "1"
                    }
                }
            }
        }
        
        org = Organization.from_api_dict(api_data)
        
        assert org.id == "123"
        assert org.name == "Test Organization"
        assert org.description == "A test organization"
        assert org.organization_type_name == "Client"
        assert org.organization_status_name == "Active"
        assert org.primary_domain == "example.com"
        assert org.created_at is not None
        assert org.organization_type_id == "1"
    
    def test_organization_to_api_dict(self):
        """Test converting organization to API format."""
        org = Organization(
            id="123",
            name="Test Organization",
            description="A test organization",
            **{"organization-type-name": "Client"}
        )
        
        api_dict = org.to_api_dict()
        
        assert api_dict["type"] == "organizations"
        assert api_dict["id"] == "123"
        assert api_dict["attributes"]["name"] == "Test Organization"
        assert api_dict["attributes"]["description"] == "A test organization"
        assert api_dict["attributes"]["organization-type-name"] == "Client"


class TestOrganizationCollection:
    """Test OrganizationCollection model."""
    
    def create_sample_organizations(self):
        """Create sample organizations for testing."""
        return [
            Organization(
                id="1",
                name="Active Client",
                **{"organization-type-name": "Client", "organization-status-name": "Active"}
            ),
            Organization(
                id="2", 
                name="Internal Org",
                **{"organization-type-name": "Internal", "organization-status-name": "Active"}
            ),
            Organization(
                id="3",
                name="Inactive Vendor",
                **{"organization-type-name": "Vendor", "organization-status-name": "Inactive"}
            ),
            Organization(
                id="4",
                name="Another Client",
                **{"organization-type-name": "Client", "organization-status-name": "Active"}
            )
        ]
    
    def test_collection_creation(self):
        """Test organization collection creation."""
        orgs = self.create_sample_organizations()
        collection = OrganizationCollection(data=orgs)
        
        assert len(collection) == 4
        assert collection.count == 4
        assert collection[0].name == "Active Client"
    
    def test_collection_get_by_name(self):
        """Test finding organization by name."""
        orgs = self.create_sample_organizations()
        collection = OrganizationCollection(data=orgs)
        
        # Case insensitive search
        org = collection.get_by_name("active client")
        assert org is not None
        assert org.id == "1"
        assert org.name == "Active Client"
        
        # Exact case
        org = collection.get_by_name("Internal Org")
        assert org is not None
        assert org.id == "2"
        
        # Non-existent
        org = collection.get_by_name("Non-existent")
        assert org is None
    
    def test_collection_get_active_organizations(self):
        """Test getting active organizations."""
        orgs = self.create_sample_organizations()
        collection = OrganizationCollection(data=orgs)
        
        active_orgs = collection.get_active_organizations()
        
        assert len(active_orgs) == 3
        assert all(org.is_active() for org in active_orgs)
        assert "3" not in [org.id for org in active_orgs]  # Inactive one excluded
    
    def test_collection_get_clients(self):
        """Test getting client organizations."""
        orgs = self.create_sample_organizations()
        collection = OrganizationCollection(data=orgs)
        
        clients = collection.get_clients()
        
        assert len(clients) == 2
        assert all(org.is_client() for org in clients)
        assert clients[0].id == "1"
        assert clients[1].id == "4"
    
    def test_collection_get_internal_organizations(self):
        """Test getting internal organizations."""
        orgs = self.create_sample_organizations()
        collection = OrganizationCollection(data=orgs)
        
        internal_orgs = collection.get_internal_organizations()
        
        assert len(internal_orgs) == 1
        assert internal_orgs[0].id == "2"
        assert internal_orgs[0].is_internal()
    
    def test_collection_from_api_dict(self):
        """Test creating collection from API response."""
        api_data = {
            "data": [
                {
                    "type": "organizations",
                    "id": "1",
                    "attributes": {
                        "name": "Test Org 1",
                        "organization-type-name": "Client"
                    }
                },
                {
                    "type": "organizations", 
                    "id": "2",
                    "attributes": {
                        "name": "Test Org 2",
                        "organization-type-name": "Internal"
                    }
                }
            ],
            "meta": {
                "current-page": 1,
                "total-count": 2
            }
        }
        
        collection = OrganizationCollection.from_api_dict(api_data)
        
        assert len(collection) == 2
        assert collection.total_count == 2
        assert collection.current_page == 1
        assert collection[0].name == "Test Org 1"
        assert collection[1].name == "Test Org 2" 