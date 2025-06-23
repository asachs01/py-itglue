"""
Tests for Flexible Asset models.

Tests the FlexibleAsset, FlexibleAssetType, and FlexibleAssetField models
along with their collection classes.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from itglue.models.flexible_asset import (
    FlexibleAsset,
    FlexibleAssetCollection,
    FlexibleAssetType,
    FlexibleAssetTypeCollection,
    FlexibleAssetField,
    FlexibleAssetFieldCollection,
    FlexibleAssetStatus,
)
from itglue.models.base import ResourceType


class TestFlexibleAssetStatus:
    """Test FlexibleAssetStatus enumeration."""

    def test_status_values(self):
        """Test status enumeration values."""
        assert FlexibleAssetStatus.ACTIVE.value == "Active"
        assert FlexibleAssetStatus.INACTIVE.value == "Inactive"
        assert FlexibleAssetStatus.ARCHIVED.value == "Archived"


class TestFlexibleAsset:
    """Test FlexibleAsset model."""

    def test_initialization_minimal(self):
        """Test minimal flexible asset initialization."""
        asset = FlexibleAsset(id="1", name="Test Asset")

        assert asset.id == "1"
        assert asset.type == ResourceType.FLEXIBLE_ASSETS
        assert asset.name == "Test Asset"

    def test_initialization_full(self):
        """Test full flexible asset initialization."""
        traits = {
            "server_name": "WEB01",
            "ip_address": "192.168.1.100",
            "status": "Production",
        }
        tags = ["production", "web-server", "critical"]

        asset = FlexibleAsset(
            id="123",
            name="Web Server",
            description="Production web server",
            flexible_asset_type_name="Servers",
            status="Active",
            traits=traits,
            tag_list=tags,
            organization_id="456",
        )

        assert asset.id == "123"
        assert asset.name == "Web Server"
        assert asset.description == "Production web server"
        assert asset.flexible_asset_type_name == "Servers"
        assert asset.status == "Active"
        assert asset.traits == traits
        assert asset.tag_list == tags
        assert asset.organization_id == "456"

    def test_property_setters(self):
        """Test property setters."""
        asset = FlexibleAsset(id="1")

        asset.name = "Updated Asset"
        asset.description = "Updated description"
        asset.flexible_asset_type_name = "Workstations"
        asset.status = "Inactive"

        assert asset.name == "Updated Asset"
        assert asset.description == "Updated description"
        assert asset.flexible_asset_type_name == "Workstations"
        assert asset.status == "Inactive"

    def test_traits_management(self):
        """Test trait management methods."""
        asset = FlexibleAsset(id="1", name="Test")

        # Test setting traits
        asset.set_trait("cpu", "Intel i7")
        asset.set_trait("ram", "16GB")

        assert asset.get_trait("cpu") == "Intel i7"
        assert asset.get_trait("ram") == "16GB"
        assert asset.get_trait("nonexistent", "default") == "default"

        # Test has_trait
        assert asset.has_trait("cpu")
        assert asset.has_trait("ram")
        assert not asset.has_trait("storage")

        # Test list_trait_names
        trait_names = asset.list_trait_names()
        assert "cpu" in trait_names
        assert "ram" in trait_names
        assert len(trait_names) == 2

    def test_tag_management(self):
        """Test tag management methods."""
        asset = FlexibleAsset(id="1", name="Test")

        # Test adding tags
        asset.add_tag("production")
        asset.add_tag("critical")

        assert asset.has_tag("production")
        assert asset.has_tag("critical")
        assert not asset.has_tag("development")

        # Test adding duplicate tag
        asset.add_tag("production")  # Should not duplicate
        assert asset.tag_list.count("production") == 1

        # Test removing tags
        asset.remove_tag("critical")
        assert not asset.has_tag("critical")
        assert asset.has_tag("production")

    def test_convenience_methods(self):
        """Test convenience methods."""
        asset = FlexibleAsset(id="1", name="Test")

        # Test status checks
        asset.status = "Active"
        assert asset.is_active()
        assert not asset.is_archived()

        asset.status = "Archived"
        assert not asset.is_active()
        assert asset.is_archived()

    def test_relationship_helpers(self):
        """Test relationship helper properties."""
        asset = FlexibleAsset(id="1", name="Test")

        # Mock relationships using proper ITGlueRelationship objects
        from itglue.models.base import ITGlueRelationship, ITGlueRelationshipData

        asset.relationships = {
            "organization": ITGlueRelationship(
                data=ITGlueRelationshipData(type="organizations", id="456")
            ),
            "flexible-asset-type": ITGlueRelationship(
                data=ITGlueRelationshipData(type="flexible_asset_types", id="789")
            ),
            "attachments": ITGlueRelationship(
                data=[
                    ITGlueRelationshipData(type="attachments", id="100"),
                    ITGlueRelationshipData(type="attachments", id="101"),
                ]
            ),
        }

        assert asset.organization_id == "456"
        assert asset.flexible_asset_type_id == "789"
        assert asset.attachments_ids == ["100", "101"]

    def test_string_representations(self):
        """Test string representations."""
        asset = FlexibleAsset(
            id="123",
            name="Test Asset",
            flexible_asset_type_name="Servers",
            status="Active",
        )

        str_repr = str(asset)
        assert "FlexibleAsset" in str_repr
        assert "id=123" in str_repr
        assert "Test Asset" in str_repr
        assert "Servers" in str_repr

        repr_str = repr(asset)
        assert "FlexibleAsset" in repr_str
        assert "id=123" in repr_str
        assert "Test Asset" in repr_str
        assert "status=Active" in repr_str

    def test_from_api_dict(self):
        """Test creating asset from API response."""
        api_data = {
            "id": "123",
            "type": "flexible_assets",
            "attributes": {
                "name": "Web Server",
                "description": "Production web server",
                "flexible-asset-type-name": "Servers",
                "status": "Active",
                "traits": {"hostname": "web01", "ip_address": "192.168.1.100"},
                "tag-list": ["production", "web"],
                "created-at": "2023-01-01T00:00:00Z",
                "updated-at": "2023-01-02T00:00:00Z",
            },
            "relationships": {
                "organization": {"data": {"type": "organizations", "id": "456"}}
            },
        }

        asset = FlexibleAsset.from_api_dict(api_data)

        assert asset.id == "123"
        assert asset.name == "Web Server"
        assert asset.description == "Production web server"
        assert asset.flexible_asset_type_name == "Servers"
        assert asset.status == "Active"
        assert asset.traits["hostname"] == "web01"
        assert asset.traits["ip_address"] == "192.168.1.100"
        assert asset.tag_list == ["production", "web"]
        assert asset.organization_id == "456"


class TestFlexibleAssetType:
    """Test FlexibleAssetType model."""

    def test_initialization(self):
        """Test flexible asset type initialization."""
        asset_type = FlexibleAssetType(
            id="1",
            name="Servers",
            description="Server assets",
            icon="server",
            enabled=True,
            builtin=False,
        )

        assert asset_type.id == "1"
        assert asset_type.type == ResourceType.FLEXIBLE_ASSET_TYPES
        assert asset_type.name == "Servers"
        assert asset_type.description == "Server assets"
        assert asset_type.icon == "server"
        assert asset_type.enabled is True
        assert asset_type.builtin is False

    def test_string_representation(self):
        """Test string representation."""
        asset_type = FlexibleAssetType(id="1", name="Servers")

        str_repr = str(asset_type)
        assert "FlexibleAssetType" in str_repr
        assert "id=1" in str_repr
        assert "Servers" in str_repr


class TestFlexibleAssetField:
    """Test FlexibleAssetField model."""

    def test_initialization(self):
        """Test flexible asset field initialization."""
        field = FlexibleAssetField(
            id="1",
            name="Hostname",
            kind="Text",
            hint="Server hostname",
            tag_type="hostname",
            required=True,
            show_in_list=True,
            sort_order=1,
        )

        assert field.id == "1"
        assert field.type == ResourceType.FLEXIBLE_ASSET_FIELDS
        assert field.name == "Hostname"
        assert field.kind == "Text"
        assert field.hint == "Server hostname"
        assert field.tag_type == "hostname"
        assert field.required is True
        assert field.show_in_list is True
        assert field.sort_order == 1

    def test_string_representation(self):
        """Test string representation."""
        field = FlexibleAssetField(id="1", name="Hostname", kind="Text")

        str_repr = str(field)
        assert "FlexibleAssetField" in str_repr
        assert "id=1" in str_repr
        assert "Hostname" in str_repr
        assert "Text" in str_repr


class TestFlexibleAssetCollection:
    """Test FlexibleAssetCollection model."""

    def create_test_assets(self) -> list:
        """Create test assets for collection tests."""
        return [
            FlexibleAsset(
                id="1",
                name="Web Server 1",
                flexible_asset_type_name="Servers",
                status="Active",
                tag_list=["production", "web"],
            ),
            FlexibleAsset(
                id="2",
                name="Web Server 2",
                flexible_asset_type_name="Servers",
                status="Active",
                tag_list=["production", "web"],
            ),
            FlexibleAsset(
                id="3",
                name="Workstation 1",
                flexible_asset_type_name="Workstations",
                status="Inactive",
                tag_list=["office"],
            ),
        ]

    def test_collection_basic_operations(self):
        """Test basic collection operations."""
        assets = self.create_test_assets()
        collection = FlexibleAssetCollection(data=assets)

        assert len(collection) == 3
        assert collection.count == 3

        # Test iteration
        asset_names = [asset.name for asset in collection]
        assert "Web Server 1" in asset_names
        assert "Web Server 2" in asset_names
        assert "Workstation 1" in asset_names

        # Test indexing
        assert collection[0].id == "1"
        assert collection[1].id == "2"
        assert collection[2].id == "3"

    def test_get_by_name(self):
        """Test finding assets by name."""
        assets = self.create_test_assets()
        collection = FlexibleAssetCollection(data=assets)

        asset = collection.get_by_name("Web Server 1")
        assert asset is not None
        assert asset.id == "1"
        assert asset.name == "Web Server 1"

        # Test case insensitive
        asset = collection.get_by_name("web server 1")
        assert asset is not None
        assert asset.id == "1"

        # Test not found
        asset = collection.get_by_name("Nonexistent")
        assert asset is None

    def test_get_by_type(self):
        """Test finding assets by type."""
        assets = self.create_test_assets()
        collection = FlexibleAssetCollection(data=assets)

        servers = collection.get_by_type("Servers")
        assert len(servers) == 2
        assert all(asset.flexible_asset_type_name == "Servers" for asset in servers)

        workstations = collection.get_by_type("Workstations")
        assert len(workstations) == 1
        assert workstations[0].flexible_asset_type_name == "Workstations"

        # Test case insensitive
        servers = collection.get_by_type("servers")
        assert len(servers) == 2

    def test_get_active_assets(self):
        """Test getting active assets."""
        assets = self.create_test_assets()
        collection = FlexibleAssetCollection(data=assets)

        active_assets = collection.get_active_assets()
        assert len(active_assets) == 2
        assert all(asset.is_active() for asset in active_assets)

    def test_get_by_tag(self):
        """Test finding assets by tag."""
        assets = self.create_test_assets()
        collection = FlexibleAssetCollection(data=assets)

        production_assets = collection.get_by_tag("production")
        assert len(production_assets) == 2
        assert all(asset.has_tag("production") for asset in production_assets)

        office_assets = collection.get_by_tag("office")
        assert len(office_assets) == 1
        assert office_assets[0].has_tag("office")

    def test_get_by_trait(self):
        """Test finding assets by trait."""
        assets = self.create_test_assets()
        # Add traits to test assets
        assets[0].set_trait("environment", "production")
        assets[1].set_trait("environment", "production")
        assets[2].set_trait("environment", "development")
        assets[0].set_trait("cpu_cores", "8")

        collection = FlexibleAssetCollection(data=assets)

        # Test trait existence
        env_assets = collection.get_by_trait("environment")
        assert len(env_assets) == 3

        # Test trait value match
        prod_assets = collection.get_by_trait("environment", "production")
        assert len(prod_assets) == 2

        cpu_assets = collection.get_by_trait("cpu_cores", "8")
        assert len(cpu_assets) == 1
        assert cpu_assets[0].id == "1"

    def test_from_api_dict(self):
        """Test creating collection from API response."""
        api_data = {
            "data": [
                {
                    "id": "1",
                    "type": "flexible_assets",
                    "attributes": {
                        "name": "Test Asset 1",
                        "flexible-asset-type-name": "Servers",
                    },
                },
                {
                    "id": "2",
                    "type": "flexible_assets",
                    "attributes": {
                        "name": "Test Asset 2",
                        "flexible-asset-type-name": "Workstations",
                    },
                },
            ],
            "meta": {"total-count": 2, "current-page": 1},
        }

        collection = FlexibleAssetCollection.from_api_dict(api_data)

        assert len(collection) == 2
        assert collection.total_count == 2
        assert collection.current_page == 1
        assert collection[0].name == "Test Asset 1"
        assert collection[1].name == "Test Asset 2"


class TestFlexibleAssetTypeCollection:
    """Test FlexibleAssetTypeCollection model."""

    def test_get_by_name(self):
        """Test finding asset types by name."""
        types = [
            FlexibleAssetType(id="1", name="Servers", enabled=True),
            FlexibleAssetType(id="2", name="Workstations", enabled=True),
            FlexibleAssetType(id="3", name="Printers", enabled=False),
        ]
        collection = FlexibleAssetTypeCollection(data=types)

        servers_type = collection.get_by_name("Servers")
        assert servers_type is not None
        assert servers_type.id == "1"

        # Test case insensitive
        servers_type = collection.get_by_name("servers")
        assert servers_type is not None
        assert servers_type.id == "1"

    def test_get_enabled_types(self):
        """Test getting enabled asset types."""
        types = [
            FlexibleAssetType(id="1", name="Servers", enabled=True),
            FlexibleAssetType(id="2", name="Workstations", enabled=True),
            FlexibleAssetType(id="3", name="Printers", enabled=False),
        ]
        collection = FlexibleAssetTypeCollection(data=types)

        enabled_types = collection.get_enabled_types()
        assert len(enabled_types) == 2
        assert all(t.enabled for t in enabled_types)


class TestFlexibleAssetFieldCollection:
    """Test FlexibleAssetFieldCollection model."""

    def test_get_by_name(self):
        """Test finding fields by name."""
        fields = [
            FlexibleAssetField(id="1", name="Hostname", kind="Text"),
            FlexibleAssetField(id="2", name="IP Address", kind="Text"),
            FlexibleAssetField(id="3", name="CPU Cores", kind="Number"),
        ]
        collection = FlexibleAssetFieldCollection(data=fields)

        hostname_field = collection.get_by_name("Hostname")
        assert hostname_field is not None
        assert hostname_field.id == "1"

    def test_get_required_fields(self):
        """Test getting required fields."""
        fields = [
            FlexibleAssetField(id="1", name="Hostname", required=True),
            FlexibleAssetField(id="2", name="IP Address", required=False),
            FlexibleAssetField(id="3", name="Description", required=True),
        ]
        collection = FlexibleAssetFieldCollection(data=fields)

        required_fields = collection.get_required_fields()
        assert len(required_fields) == 2
        assert all(f.required for f in required_fields)

    def test_get_by_kind(self):
        """Test getting fields by kind."""
        fields = [
            FlexibleAssetField(id="1", name="Hostname", kind="Text"),
            FlexibleAssetField(id="2", name="IP Address", kind="Text"),
            FlexibleAssetField(id="3", name="CPU Cores", kind="Number"),
        ]
        collection = FlexibleAssetFieldCollection(data=fields)

        text_fields = collection.get_by_kind("Text")
        assert len(text_fields) == 2
        assert all(f.kind == "Text" for f in text_fields)

        number_fields = collection.get_by_kind("Number")
        assert len(number_fields) == 1
        assert number_fields[0].kind == "Number"
