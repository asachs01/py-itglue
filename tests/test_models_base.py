"""
Tests for ITGlue base models and JSON API compliance.
"""

import pytest
from typing import Dict, Any

from itglue.models.base import (
    ResourceType,
    ITGlueLinks,
    ITGlueMeta,
    ITGlueRelationshipData,
    ITGlueRelationship,
    ITGlueResource,
    ITGlueResourceCollection,
)


class TestResourceType:
    """Test ResourceType enumeration."""

    def test_resource_type_values(self):
        """Test that resource types have correct string values."""
        assert ResourceType.ORGANIZATIONS.value == "organizations"
        assert ResourceType.CONFIGURATIONS.value == "configurations"
        assert ResourceType.PASSWORDS.value == "passwords"
        assert ResourceType.FLEXIBLE_ASSETS.value == "flexible_assets"

    def test_resource_type_membership(self):
        """Test resource type membership."""
        assert "organizations" in [t.value for t in ResourceType]
        assert "configurations" in [t.value for t in ResourceType]
        assert "invalid_type" not in [t.value for t in ResourceType]


class TestITGlueLinks:
    """Test ITGlue links model."""

    def test_links_creation(self):
        """Test links creation with various fields."""
        links = ITGlueLinks(
            self="https://api.itglue.com/organizations/123",
            related="https://api.itglue.com/organizations/123/configurations",
            first="https://api.itglue.com/organizations?page[number]=1",
            last="https://api.itglue.com/organizations?page[number]=10",
            next="https://api.itglue.com/organizations?page[number]=3",
            prev="https://api.itglue.com/organizations?page[number]=1",
        )

        assert links.self == "https://api.itglue.com/organizations/123"
        assert (
            links.related == "https://api.itglue.com/organizations/123/configurations"
        )
        assert links.first == "https://api.itglue.com/organizations?page[number]=1"
        assert links.last == "https://api.itglue.com/organizations?page[number]=10"
        assert links.next == "https://api.itglue.com/organizations?page[number]=3"
        assert links.prev == "https://api.itglue.com/organizations?page[number]=1"

    def test_links_empty(self):
        """Test empty links creation."""
        links = ITGlueLinks()
        assert links.self is None
        assert links.related is None
        assert links.first is None
        assert links.last is None
        assert links.next is None
        assert links.prev is None

    def test_links_extra_fields(self):
        """Test that extra fields are allowed."""
        links = ITGlueLinks(custom_link="https://example.com")
        assert hasattr(links, "custom_link")


class TestITGlueMeta:
    """Test ITGlue meta model."""

    def test_meta_pagination(self):
        """Test meta with pagination data."""
        meta_data = {
            "current-page": 2,
            "next-page": 3,
            "prev-page": 1,
            "total-pages": 10,
            "total-count": 100,
        }

        meta = ITGlueMeta.model_validate(meta_data)

        assert meta.current_page == 2
        assert meta.next_page == 3
        assert meta.prev_page == 1
        assert meta.total_pages == 10
        assert meta.total_count == 100

    def test_meta_with_timestamps(self):
        """Test meta with timestamp data."""
        meta_data = {
            "created-at": "2023-08-01T12:00:00.000Z",
            "updated-at": "2023-08-02T12:00:00.000Z",
        }

        meta = ITGlueMeta.model_validate(meta_data)

        assert meta.created_at is not None
        assert meta.updated_at is not None

    def test_meta_empty(self):
        """Test empty meta creation."""
        meta = ITGlueMeta()
        assert meta.current_page is None
        assert meta.total_count is None


class TestITGlueRelationshipData:
    """Test relationship data model."""

    def test_relationship_data_creation(self):
        """Test relationship data creation."""
        rel_data = ITGlueRelationshipData(type=ResourceType.ORGANIZATIONS, id="123")

        assert rel_data.type == ResourceType.ORGANIZATIONS
        assert rel_data.id == "123"

    def test_relationship_data_validation(self):
        """Test relationship data validation."""
        # Valid ID (numeric string)
        rel_data = ITGlueRelationshipData(type=ResourceType.CONFIGURATIONS, id="456")
        assert rel_data.id == "456"


class TestITGlueRelationship:
    """Test relationship model."""

    def test_relationship_single_data(self):
        """Test relationship with single data reference."""
        rel_data = ITGlueRelationshipData(type=ResourceType.ORGANIZATIONS, id="123")

        relationship = ITGlueRelationship(data=rel_data)

        assert relationship.data == rel_data
        assert relationship.links is None
        assert relationship.meta is None

    def test_relationship_multiple_data(self):
        """Test relationship with multiple data references."""
        rel_data_list = [
            ITGlueRelationshipData(type=ResourceType.CONFIGURATIONS, id="1"),
            ITGlueRelationshipData(type=ResourceType.CONFIGURATIONS, id="2"),
        ]

        relationship = ITGlueRelationship(data=rel_data_list)

        assert isinstance(relationship.data, list)
        assert len(relationship.data) == 2
        assert relationship.data[0].id == "1"
        assert relationship.data[1].id == "2"

    def test_relationship_with_links_and_meta(self):
        """Test relationship with links and meta."""
        rel_data = ITGlueRelationshipData(type=ResourceType.ORGANIZATIONS, id="123")
        links = ITGlueLinks(related="https://api.itglue.com/organizations/123")
        meta = ITGlueMeta(total_count=5)

        relationship = ITGlueRelationship(data=rel_data, links=links, meta=meta)

        assert relationship.data == rel_data
        assert relationship.links == links
        assert relationship.meta == meta


class TestITGlueResource:
    """Test base resource model."""

    def test_resource_creation_minimal(self):
        """Test minimal resource creation."""
        resource = ITGlueResource(type=ResourceType.ORGANIZATIONS, id="123")

        assert resource.id == "123"
        assert resource.type == ResourceType.ORGANIZATIONS
        assert resource.attributes == {}

    def test_resource_creation_with_attributes(self):
        """Test resource creation with attributes."""
        resource = ITGlueResource(
            type=ResourceType.ORGANIZATIONS,
            id="123",
            name="Test Organization",
            description="A test organization",
        )

        assert resource.id == "123"
        assert resource.type == ResourceType.ORGANIZATIONS
        assert resource.attributes["name"] == "Test Organization"
        assert resource.attributes["description"] == "A test organization"

    def test_resource_attribute_access(self):
        """Test accessing attributes as properties."""
        resource = ITGlueResource(
            type=ResourceType.ORGANIZATIONS, id="123", name="Test Organization"
        )

        # Direct access through attributes dict
        assert resource.attributes["name"] == "Test Organization"

        # Access through __getattr__
        assert resource.name == "Test Organization"

    def test_resource_attribute_setting(self):
        """Test setting attributes as properties."""
        resource = ITGlueResource(type=ResourceType.ORGANIZATIONS, id="123")

        # Set through property
        resource.name = "New Name"
        assert resource.attributes["name"] == "New Name"
        assert resource.name == "New Name"

        # Set through method
        resource.set_attribute("description", "New Description")
        assert resource.get_attribute("description") == "New Description"

    def test_resource_relationships(self):
        """Test resource relationships."""
        rel_data = ITGlueRelationshipData(type=ResourceType.ORGANIZATIONS, id="456")
        relationship = ITGlueRelationship(data=rel_data)

        resource = ITGlueResource(
            type=ResourceType.CONFIGURATIONS,
            id="123",
            relationships={"organization": relationship},
        )

        assert resource.get_relationship("organization") == relationship
        assert resource.get_related_id("organization") == "456"

    def test_resource_relationship_helpers(self):
        """Test relationship helper methods."""
        # Single relationship
        rel_data = ITGlueRelationshipData(type=ResourceType.ORGANIZATIONS, id="456")
        relationship = ITGlueRelationship(data=rel_data)

        resource = ITGlueResource(type=ResourceType.CONFIGURATIONS, id="123")
        resource.set_relationship("organization", relationship)

        assert resource.get_related_id("organization") == "456"
        assert resource.get_related_ids("organization") == ["456"]

        # Multiple relationships
        rel_data_list = [
            ITGlueRelationshipData(type=ResourceType.CONFIGURATIONS, id="1"),
            ITGlueRelationshipData(type=ResourceType.CONFIGURATIONS, id="2"),
        ]
        multi_relationship = ITGlueRelationship(data=rel_data_list)
        resource.set_relationship("configurations", multi_relationship)

        assert resource.get_related_ids("configurations") == ["1", "2"]

    def test_resource_to_api_dict(self):
        """Test converting resource to API dictionary."""
        rel_data = ITGlueRelationshipData(type=ResourceType.ORGANIZATIONS, id="456")
        relationship = ITGlueRelationship(data=rel_data)

        resource = ITGlueResource(
            type=ResourceType.CONFIGURATIONS,
            id="123",
            name="Test Config",
            relationships={"organization": relationship},
        )

        api_dict = resource.to_api_dict()

        assert api_dict["type"] == "configurations"
        assert api_dict["id"] == "123"
        assert api_dict["attributes"]["name"] == "Test Config"
        assert "organization" in api_dict["relationships"]

    def test_resource_from_api_dict(self):
        """Test creating resource from API dictionary."""
        api_data = {
            "type": "organizations",
            "id": "123",
            "attributes": {
                "name": "Test Organization",
                "description": "A test organization",
            },
            "relationships": {
                "organization-type": {"data": {"type": "organization-types", "id": "1"}}
            },
        }

        resource = ITGlueResource.from_api_dict(api_data)

        assert resource.id == "123"
        assert resource.type == ResourceType.ORGANIZATIONS
        assert resource.name == "Test Organization"
        assert resource.description == "A test organization"
        assert resource.get_related_id("organization-type") == "1"


class TestITGlueResourceCollection:
    """Test resource collection model."""

    def test_collection_creation(self):
        """Test collection creation."""
        resources = [
            ITGlueResource(type=ResourceType.ORGANIZATIONS, id="1", name="Org 1"),
            ITGlueResource(type=ResourceType.ORGANIZATIONS, id="2", name="Org 2"),
        ]

        collection = ITGlueResourceCollection(data=resources)

        assert len(collection) == 2
        assert collection.count == 2
        assert collection[0].name == "Org 1"
        assert collection[1].name == "Org 2"

    def test_collection_iteration(self):
        """Test collection iteration."""
        resources = [
            ITGlueResource(type=ResourceType.ORGANIZATIONS, id="1", name="Org 1"),
            ITGlueResource(type=ResourceType.ORGANIZATIONS, id="2", name="Org 2"),
        ]

        collection = ITGlueResourceCollection(data=resources)

        names = [resource.name for resource in collection]
        assert names == ["Org 1", "Org 2"]

    def test_collection_with_meta(self):
        """Test collection with metadata."""
        # Use alias field names for API data format
        meta_data = {"current-page": 2, "total-pages": 5, "total-count": 100}
        meta = ITGlueMeta.model_validate(meta_data)

        collection = ITGlueResourceCollection(data=[], meta=meta)

        assert collection.current_page == 2
        assert collection.total_pages == 5
        assert collection.total_count == 100

    def test_collection_pagination_helpers(self):
        """Test pagination helper methods."""
        # Use alias field names for API data format
        meta_data = {
            "current-page": 2,
            "next-page": 3,
            "prev-page": 1,
            "total-pages": 5,
        }
        meta = ITGlueMeta.model_validate(meta_data)

        collection = ITGlueResourceCollection(data=[], meta=meta)

        assert collection.has_next_page is True
        assert collection.has_prev_page is True

        # Test without next page
        meta_last_data = {"current-page": 5, "prev-page": 4, "total-pages": 5}
        meta_last = ITGlueMeta.model_validate(meta_last_data)

        collection_last = ITGlueResourceCollection(data=[], meta=meta_last)

        assert collection_last.has_next_page is False
        assert collection_last.has_prev_page is True

    def test_collection_included_resources(self):
        """Test included resources functionality."""
        included = [
            ITGlueResource(type=ResourceType.ORGANIZATIONS, id="1", name="Org 1"),
            ITGlueResource(type=ResourceType.CONFIGURATIONS, id="2", name="Config 1"),
        ]

        collection = ITGlueResourceCollection(data=[], included=included)

        org = collection.get_included(ResourceType.ORGANIZATIONS, "1")
        assert org is not None
        assert org.name == "Org 1"

        config = collection.get_included(ResourceType.CONFIGURATIONS, "2")
        assert config is not None
        assert config.name == "Config 1"

        # Test non-existent
        missing = collection.get_included(ResourceType.PASSWORDS, "999")
        assert missing is None
