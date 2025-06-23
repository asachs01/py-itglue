"""
Tests for Password model and PasswordCollection.

This module tests the Password model functionality including security management,
visibility controls, password categorization, and collection operations.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from itglue.models.password import (
    Password,
    PasswordCollection,
    PasswordType,
    PasswordCategory,
    PasswordVisibility,
)


class TestPasswordModel:
    """Test cases for the Password model."""

    def test_password_initialization_empty(self):
        """Test Password creation with no data."""
        password = Password()
        assert password.id is None
        assert password.name is None
        assert password.username is None
        assert password.password is None
        assert password.url is None
        assert password.notes is None

    def test_password_initialization_with_data(self):
        """Test Password creation from API data."""
        data = {
            "id": "123",
            "type": "passwords",
            "attributes": {
                "name": "Gmail Account",
                "username": "user@example.com",
                "password": "secure123",
                "url": "https://gmail.com",
                "notes": "Primary email account",
                "password-type": "embedded",
                "password-category-name": "high",
                "visibility": "private",
                "favorite": True,
                "archived": False,
            },
        }

        password = Password.from_api_dict(data)
        assert password.id == "123"
        assert password.name == "Gmail Account"
        assert password.username == "user@example.com"
        assert password.password == "secure123"
        assert password.url == "https://gmail.com"
        assert password.notes == "Primary email account"
        assert password.password_type == PasswordType.EMBEDDED
        assert password.password_category == PasswordCategory.HIGH
        assert password.visibility == PasswordVisibility.PRIVATE
        assert password.favorite is True
        assert password.archived is False

    def test_password_property_setters(self):
        """Test property setter methods."""
        password = Password()

        # Test basic properties
        password.name = "Test Password"
        assert password.name == "Test Password"

        password.username = "testuser"
        assert password.username == "testuser"

        password.password = "newpassword"
        assert password.password == "newpassword"

        password.url = "https://example.com"
        assert password.url == "https://example.com"

        password.notes = "Test notes"
        assert password.notes == "Test notes"

        # Test enum properties
        password.password_type = PasswordType.LINKED
        assert password.password_type == PasswordType.LINKED

        password.password_category = PasswordCategory.CRITICAL
        assert password.password_category == PasswordCategory.CRITICAL

        password.visibility = PasswordVisibility.EVERYONE
        assert password.visibility == PasswordVisibility.EVERYONE

        # Test boolean properties
        password.favorite = True
        assert password.favorite is True

        password.archived = True
        assert password.archived is True

    def test_password_string_representation(self):
        """Test string representation of password."""
        password = Password()

        # With name and username
        password.name = "Gmail"
        password.username = "user@example.com"
        assert str(password) == "Password: Gmail (user@example.com)"

        # With name only
        password = Password()
        password.name = "Gmail"
        assert str(password) == "Password: Gmail"

        # With username only
        password = Password()
        password.username = "user@example.com"
        assert str(password) == "Password: user@example.com"

        # With ID only
        password = Password()
        password.id = "123"
        assert str(password) == "Password: 123"

        # No identifying information
        password = Password()
        assert str(password) == "Password: None"

    def test_password_type_enum(self):
        """Test PasswordType enum functionality."""
        password = Password()

        # Test string assignment
        password.password_type = "embedded"
        assert password.password_type == PasswordType.EMBEDDED

        password.password_type = "linked"
        assert password.password_type == PasswordType.LINKED

        # Test enum assignment
        password.password_type = PasswordType.EMBEDDED
        assert password.password_type == PasswordType.EMBEDDED

    def test_password_category_enum(self):
        """Test PasswordCategory enum functionality."""
        password = Password()

        # Test string assignment (case insensitive)
        password.password_category = "low"
        assert password.password_category == PasswordCategory.LOW

        password.password_category = "HIGH"
        assert password.password_category == PasswordCategory.HIGH

        # Test enum assignment
        password.password_category = PasswordCategory.CRITICAL
        assert password.password_category == PasswordCategory.CRITICAL

    def test_password_visibility_enum(self):
        """Test PasswordVisibility enum functionality."""
        password = Password()

        # Test string assignment
        password.visibility = "private"
        assert password.visibility == PasswordVisibility.PRIVATE

        password.visibility = "everyone"
        assert password.visibility == PasswordVisibility.EVERYONE

        # Test enum assignment
        password.visibility = PasswordVisibility.ORGANIZATION
        assert password.visibility == PasswordVisibility.ORGANIZATION

    def test_security_helper_methods(self):
        """Test security-related helper methods."""
        password = Password()

        # Test critical password detection
        password.password_category = PasswordCategory.CRITICAL
        assert password.is_critical() is True
        assert password.is_high_security() is True

        password.password_category = PasswordCategory.HIGH
        assert password.is_critical() is False
        assert password.is_high_security() is True

        password.password_category = PasswordCategory.MEDIUM
        assert password.is_critical() is False
        assert password.is_high_security() is False

    def test_sharing_helper_methods(self):
        """Test sharing-related helper methods."""
        password = Password()

        # Test private password
        password.visibility = PasswordVisibility.PRIVATE
        assert password.is_shared() is False
        assert password.is_organization_visible() is False

        # Test shared password
        password.visibility = PasswordVisibility.SHARED
        assert password.is_shared() is True
        assert password.is_organization_visible() is False

        # Test organization visible password
        password.visibility = PasswordVisibility.ORGANIZATION
        assert password.is_shared() is True
        assert password.is_organization_visible() is True

        # Test everyone visible password
        password.visibility = PasswordVisibility.EVERYONE
        assert password.is_shared() is True
        assert password.is_organization_visible() is True

    def test_type_helper_methods(self):
        """Test type-related helper methods."""
        password = Password()

        # Test embedded password
        password.password_type = PasswordType.EMBEDDED
        assert password.is_embedded() is True
        assert password.is_linked() is False

        # Test linked password
        password.password_type = PasswordType.LINKED
        assert password.is_embedded() is False
        assert password.is_linked() is True

    def test_timestamp_properties(self):
        """Test timestamp property parsing."""
        data = {
            "id": "123",
            "type": "passwords",
            "attributes": {
                "created-at": "2023-01-01T00:00:00Z",
                "updated-at": "2023-01-02T00:00:00Z",
                "password-updated-at": "2023-01-03T00:00:00Z",
            },
        }

        password = Password.from_api_dict(data)

        assert password.created_at is not None
        assert password.updated_at is not None
        assert password.password_updated_at is not None

        # Check that they're properly parsed datetime objects
        assert isinstance(password.created_at, datetime)
        assert isinstance(password.updated_at, datetime)
        assert isinstance(password.password_updated_at, datetime)

    def test_relationship_properties(self):
        """Test relationship property access."""
        data = {
            "id": "123",
            "type": "passwords",
            "attributes": {
                "organization-name": "Test Org",
                "resource-type": "configurations",
                "resource-name": "Test Configuration",
            },
            "relationships": {
                "organization": {"data": {"type": "organizations", "id": "456"}},
                "resource": {"data": {"type": "configurations", "id": "789"}},
            },
        }

        password = Password.from_api_dict(data)

        assert password.organization_id == "456"
        assert password.organization_name == "Test Org"
        assert password.resource_id == "789"
        assert password.resource_type_name == "configurations"
        assert password.resource_name == "Test Configuration"

    def test_age_calculation_methods(self):
        """Test password age calculation methods."""
        password = Password()

        # Test with recent update
        recent_time = datetime.now(timezone.utc) - timedelta(days=15)
        password.set_attribute("password-updated-at", recent_time.isoformat())

        assert password.is_recently_updated(30) is True
        assert password.is_recently_updated(10) is False
        assert password.is_stale(90) is False
        assert password.is_stale(10) is True

        age_days = password.get_age_days()
        assert age_days is not None
        assert 14 <= age_days <= 16  # Allow for some time variance

        # Test with no password update time
        password.set_attribute("password-updated-at", None)
        assert password.is_recently_updated(30) is False
        assert password.is_stale(90) is True
        assert password.get_age_days() is None


class TestPasswordCollection:
    """Test cases for the PasswordCollection."""

    def create_sample_passwords(self):
        """Create sample passwords for testing."""
        passwords_data = {
            "data": [
                {
                    "id": "1",
                    "type": "passwords",
                    "attributes": {
                        "name": "Gmail",
                        "username": "user1@example.com",
                        "password": "pass123",
                        "url": "https://gmail.com",
                        "password-type": "embedded",
                        "password-category-name": "high",
                        "visibility": "private",
                        "favorite": True,
                        "archived": False,
                        "password-updated-at": (
                            datetime.now(timezone.utc) - timedelta(days=15)
                        ).isoformat(),
                    },
                },
                {
                    "id": "2",
                    "type": "passwords",
                    "attributes": {
                        "name": "Office 365",
                        "username": "user2@company.com",
                        "password": "pass456",
                        "url": "https://office.com",
                        "password-type": "linked",
                        "password-category-name": "critical",
                        "visibility": "organization",
                        "favorite": False,
                        "archived": False,
                        "password-updated-at": (
                            datetime.now(timezone.utc) - timedelta(days=100)
                        ).isoformat(),
                    },
                },
                {
                    "id": "3",
                    "type": "passwords",
                    "attributes": {
                        "name": "Old System",
                        "username": "admin",
                        "password": "oldpass",
                        "password-type": "embedded",
                        "password-category-name": "low",
                        "visibility": "private",
                        "favorite": False,
                        "archived": True,
                        "password-updated-at": (
                            datetime.now(timezone.utc) - timedelta(days=200)
                        ).isoformat(),
                    },
                },
            ]
        }

        return PasswordCollection.from_api_dict(passwords_data)

    def test_collection_initialization_empty(self):
        """Test empty collection initialization."""
        collection = PasswordCollection()
        assert len(collection) == 0
        assert collection.count == 0

    def test_collection_initialization_with_data(self):
        """Test collection initialization with data."""
        collection = self.create_sample_passwords()
        assert len(collection) == 3
        assert collection.count == 3

    def test_find_by_name(self):
        """Test finding password by exact name."""
        collection = self.create_sample_passwords()

        password = collection.find_by_name("Gmail")
        assert password is not None
        assert password.name == "Gmail"

        password = collection.find_by_name("gmail")  # Case insensitive
        assert password is not None
        assert password.name == "Gmail"

        password = collection.find_by_name("NonExistent")
        assert password is None

    def test_search_by_name(self):
        """Test searching passwords by name."""
        collection = self.create_sample_passwords()

        results = collection.search_by_name("Office")
        assert len(results) == 1
        assert results[0].name == "Office 365"

        results = collection.search_by_name("System")
        assert len(results) == 1
        assert results[0].name == "Old System"

        results = collection.search_by_name("NonExistent")
        assert len(results) == 0

    def test_find_by_username(self):
        """Test finding passwords by username."""
        collection = self.create_sample_passwords()

        results = collection.find_by_username("admin")
        assert len(results) == 1
        assert results[0].username == "admin"

        results = collection.find_by_username("user1@example.com")
        assert len(results) == 1
        assert results[0].username == "user1@example.com"

    def test_search_by_url(self):
        """Test searching passwords by URL."""
        collection = self.create_sample_passwords()

        results = collection.search_by_url("gmail")
        assert len(results) == 1
        assert "gmail" in results[0].url.lower()

        results = collection.search_by_url("office")
        assert len(results) == 1
        assert "office" in results[0].url.lower()

    def test_filter_by_category(self):
        """Test filtering passwords by security category."""
        collection = self.create_sample_passwords()

        critical = collection.filter_by_category(PasswordCategory.CRITICAL)
        assert len(critical) == 1
        assert critical[0].password_category == PasswordCategory.CRITICAL

        high = collection.filter_by_category("high")
        assert len(high) == 1
        assert high[0].password_category == PasswordCategory.HIGH

        low = collection.filter_by_category(PasswordCategory.LOW)
        assert len(low) == 1
        assert low[0].password_category == PasswordCategory.LOW

    def test_filter_by_visibility(self):
        """Test filtering passwords by visibility."""
        collection = self.create_sample_passwords()

        private = collection.filter_by_visibility(PasswordVisibility.PRIVATE)
        assert len(private) == 2

        org = collection.filter_by_visibility("organization")
        assert len(org) == 1
        assert org[0].visibility == PasswordVisibility.ORGANIZATION

    def test_filter_by_type(self):
        """Test filtering passwords by type."""
        collection = self.create_sample_passwords()

        embedded = collection.filter_by_type(PasswordType.EMBEDDED)
        assert len(embedded) == 2

        linked = collection.filter_by_type("linked")
        assert len(linked) == 1
        assert linked[0].password_type == PasswordType.LINKED

    def test_special_getters(self):
        """Test special getter methods."""
        collection = self.create_sample_passwords()

        # Test favorites
        favorites = collection.get_favorites()
        assert len(favorites) == 1
        assert favorites[0].favorite is True

        # Test archived
        archived = collection.get_archived()
        assert len(archived) == 1
        assert archived[0].archived is True

        # Test active
        active = collection.get_active()
        assert len(active) == 2
        assert all(not p.archived for p in active)

        # Test critical passwords
        critical = collection.get_critical_passwords()
        assert len(critical) == 1
        assert critical[0].password_category == PasswordCategory.CRITICAL

        # Test high security passwords
        high_security = collection.get_high_security_passwords()
        assert len(high_security) == 2  # high + critical

        # Test shared passwords
        shared = collection.get_shared_passwords()
        assert len(shared) == 1  # organization visibility

        # Test private passwords
        private = collection.get_private_passwords()
        assert len(private) == 2

    def test_time_based_filtering(self):
        """Test time-based filtering methods."""
        collection = self.create_sample_passwords()

        # Test stale passwords (older than 90 days)
        stale = collection.get_stale_passwords(90)
        assert len(stale) == 2  # Office 365 (100 days) and Old System (200 days)

        # Test recently updated passwords (within 30 days)
        recent = collection.get_recently_updated_passwords(30)
        assert len(recent) == 1  # Gmail (15 days)

        # Test with different thresholds
        stale_strict = collection.get_stale_passwords(50)
        assert len(stale_strict) == 2

        recent_strict = collection.get_recently_updated_passwords(10)
        assert len(recent_strict) == 0  # Gmail is 15 days old

    def test_type_specific_getters(self):
        """Test type-specific getter methods."""
        collection = self.create_sample_passwords()

        linked = collection.get_linked_passwords()
        assert len(linked) == 1
        assert linked[0].password_type == PasswordType.LINKED

        embedded = collection.get_embedded_passwords()
        assert len(embedded) == 2
        assert all(p.password_type == PasswordType.EMBEDDED for p in embedded)

    def test_distribution_methods(self):
        """Test distribution analysis methods."""
        collection = self.create_sample_passwords()

        # Test security distribution
        security_dist = collection.get_security_distribution()
        assert security_dist["critical"] == 1
        assert security_dist["high"] == 1
        assert security_dist["low"] == 1
        assert security_dist["medium"] == 0

        # Test visibility distribution
        visibility_dist = collection.get_visibility_distribution()
        assert visibility_dist["private"] == 2
        assert visibility_dist["organization"] == 1
        assert visibility_dist["shared"] == 0
        assert visibility_dist["everyone"] == 0

        # Test type distribution
        type_dist = collection.get_type_distribution()
        assert type_dist["embedded"] == 2
        assert type_dist["linked"] == 1

    def test_security_statistics(self):
        """Test comprehensive security statistics."""
        collection = self.create_sample_passwords()

        stats = collection.get_security_statistics()

        assert stats["total_passwords"] == 3
        assert stats["active_passwords"] == 2
        assert stats["archived_passwords"] == 1
        assert stats["favorite_passwords"] == 1
        assert stats["critical_passwords"] == 1
        assert stats["high_security_passwords"] == 2
        assert stats["shared_passwords"] == 1
        assert stats["private_passwords"] == 2
        assert stats["linked_passwords"] == 1
        assert stats["embedded_passwords"] == 2

        # Check distributions are included
        assert "security_distribution" in stats
        assert "visibility_distribution" in stats
        assert "type_distribution" in stats

    def test_to_list(self):
        """Test converting collection to list."""
        collection = self.create_sample_passwords()
        password_list = collection.to_list()

        assert isinstance(password_list, list)
        assert len(password_list) == 3
        assert all(isinstance(p, Password) for p in password_list)
