"""
Tests for User model and UserCollection.

This module tests the User model functionality including profile management,
role checking, authentication tracking, reputation scoring, and collection operations.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from itglue.models.user import User, UserCollection, UserRole, UserStatus


class TestUserModel:
    """Test cases for the User model."""

    def test_user_initialization_empty(self):
        """Test User creation with no data."""
        user = User()
        assert user.id is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.email is None
        assert user.role_name is None
        assert user.full_name == ""

    def test_user_initialization_with_data(self):
        """Test User creation with data."""
        data = {
            "id": "123",
            "type": "users",
            "attributes": {
                "first-name": "John",
                "last-name": "Doe",
                "email": "john.doe@example.com",
                "role-name": "Admin",
                "reputation": 5000,
            },
        }

        user = User.from_api_dict(data)
        assert user.id == "123"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"
        assert user.role_name == "Admin"
        assert user.reputation == 5000

    def test_user_full_name_property(self):
        """Test full name generation."""
        # Both names
        user = User()
        user.first_name = "John"
        user.last_name = "Doe"
        assert user.full_name == "John Doe"

        # First name only
        user = User()
        user.first_name = "John"
        assert user.full_name == "John"

        # Last name only
        user = User()
        user.last_name = "Doe"
        assert user.full_name == "Doe"

        # No names
        user = User()
        assert user.full_name == ""

    def test_user_role_checks(self):
        """Test role checking methods."""
        user = User()

        # Test admin role
        user.role_name = UserRole.ADMIN.value
        assert user.is_admin() is True
        assert user.is_creator() is False
        assert user.is_editor() is False
        assert user.is_lite() is False
        assert user.is_viewer() is False

        # Test creator role
        user.role_name = UserRole.CREATOR.value
        assert user.is_admin() is False
        assert user.is_creator() is True
        assert user.is_editor() is False
        assert user.is_lite() is False
        assert user.is_viewer() is False

        # Test editor role
        user.role_name = UserRole.EDITOR.value
        assert user.is_admin() is False
        assert user.is_creator() is False
        assert user.is_editor() is True
        assert user.is_lite() is False
        assert user.is_viewer() is False

        # Test lite role
        user.role_name = UserRole.LITE.value
        assert user.is_admin() is False
        assert user.is_creator() is False
        assert user.is_editor() is False
        assert user.is_lite() is True
        assert user.is_viewer() is False

        # Test viewer role
        user.role_name = UserRole.VIEWER.value
        assert user.is_admin() is False
        assert user.is_creator() is False
        assert user.is_editor() is False
        assert user.is_lite() is False
        assert user.is_viewer() is True

    def test_user_my_glue_access(self):
        """Test MyGlue access checking."""
        user = User()

        # No MyGlue access
        assert user.has_my_glue_access() is False

        # With MyGlue access
        user.set_attribute("my-glue", True)
        assert user.has_my_glue_access() is True

        # Explicitly disabled
        user.set_attribute("my-glue", False)
        assert user.has_my_glue_access() is False

    def test_user_invitation_status(self):
        """Test invitation status checking."""
        user = User()

        # No invitation
        assert user.is_invited() is False
        assert user.is_active() is False

        # Invited but not accepted
        user.set_attribute("invitation-sent-at", datetime.now(timezone.utc))
        assert user.is_invited() is True
        assert user.is_active() is False

        # Invited and accepted
        user.set_attribute("invitation-accepted-at", datetime.now(timezone.utc))
        assert user.is_invited() is False
        assert user.is_active() is True

        # Accepted without sent (edge case)
        user = User()
        user.set_attribute("invitation-accepted-at", datetime.now(timezone.utc))
        assert user.is_invited() is False
        assert user.is_active() is True

    def test_user_reputation_levels(self):
        """Test reputation level categorization."""
        user = User()

        # No reputation
        assert user.get_reputation_level() == "No Activity"

        # Novice level (1-99)
        user.set_attribute("reputation", 50)
        assert user.get_reputation_level() == "Novice"

        # Beginner level (100-999)
        user.set_attribute("reputation", 500)
        assert user.get_reputation_level() == "Beginner"

        # Intermediate level (1000-4999)
        user.set_attribute("reputation", 2500)
        assert user.get_reputation_level() == "Intermediate"

        # Advanced level (5000-9999)
        user.set_attribute("reputation", 7500)
        assert user.get_reputation_level() == "Advanced"

        # Expert level (10000+)
        user.set_attribute("reputation", 15000)
        assert user.get_reputation_level() == "Expert"

    def test_user_activity_days_calculation(self):
        """Test activity days calculation."""
        user = User()

        # No last sign-in
        assert user.calculate_activity_days() is None

        # Recent activity (1 day ago)
        user.set_attribute(
            "last-sign-in-at", datetime.now(timezone.utc) - timedelta(days=1)
        )
        days = user.calculate_activity_days()
        assert days == 1

        # Older activity (30 days ago)
        user.set_attribute(
            "last-sign-in-at", datetime.now(timezone.utc) - timedelta(days=30)
        )
        days = user.calculate_activity_days()
        assert days == 30

        # Handle timezone-naive datetime
        user.set_attribute("last-sign-in-at", datetime.now() - timedelta(days=5))
        days = user.calculate_activity_days()
        assert days == 5

    def test_user_string_representation(self):
        """Test string representation of user."""
        user = User()

        # With name and email
        user.first_name = "John"
        user.last_name = "Doe"
        user.email = "john.doe@example.com"
        assert str(user) == "User: John Doe (john.doe@example.com)"

        # With email only
        user = User()
        user.email = "jane@example.com"
        assert str(user) == "User: jane@example.com"

        # With ID only
        user = User()
        user.id = "123"
        assert str(user) == "User: 123"

        # No identifying information
        user = User()
        assert str(user) == "User: None"

    def test_user_property_setters(self):
        """Test property setter methods."""
        user = User()

        # Test first name setter
        user.first_name = "Jane"
        assert user.first_name == "Jane"

        # Test last name setter
        user.last_name = "Smith"
        assert user.last_name == "Smith"

        # Test email setter
        user.email = "jane.smith@example.com"
        assert user.email == "jane.smith@example.com"

        # Test role setter
        user.role_name = "Editor"
        assert user.role_name == "Editor"

        # Test avatar setter
        user.avatar = "https://example.com/avatar.jpg"
        assert user.avatar == "https://example.com/avatar.jpg"


class TestUserCollection:
    """Test cases for the UserCollection."""

    def create_sample_users(self):
        """Create sample users for testing."""
        users_data = {
            "data": [
                {
                    "id": "1",
                    "type": "users",
                    "attributes": {
                        "first-name": "John",
                        "last-name": "Doe",
                        "email": "john@example.com",
                        "role-name": "Admin",
                        "reputation": 5000,
                        "my-glue": True,
                        "invitation-accepted-at": "2023-01-01T00:00:00Z",
                    },
                },
                {
                    "id": "2",
                    "type": "users",
                    "attributes": {
                        "first-name": "Jane",
                        "last-name": "Smith",
                        "email": "jane@example.com",
                        "role-name": "Editor",
                        "reputation": 2500,
                        "my-glue": False,
                        "invitation-sent-at": "2023-06-01T00:00:00Z",
                    },
                },
                {
                    "id": "3",
                    "type": "users",
                    "attributes": {
                        "first-name": "Bob",
                        "last-name": "Wilson",
                        "email": "bob@example.com",
                        "role-name": "Viewer",
                        "reputation": 1000,
                        "my-glue": True,
                        "invitation-accepted-at": "2023-03-01T00:00:00Z",
                    },
                },
            ]
        }
        return UserCollection.from_api_dict(users_data)

    def test_collection_initialization_empty(self):
        """Test UserCollection creation with no data."""
        collection = UserCollection()
        assert len(collection) == 0
        assert list(collection) == []

    def test_collection_initialization_with_data(self):
        """Test UserCollection creation with data."""
        collection = self.create_sample_users()
        assert len(collection) == 3
        assert collection[0].first_name == "John"
        assert collection[1].first_name == "Jane"
        assert collection[2].first_name == "Bob"

    def test_collection_iteration(self):
        """Test iterating over collection."""
        collection = self.create_sample_users()
        names = [user.first_name for user in collection]
        assert names == ["John", "Jane", "Bob"]

    def test_collection_indexing(self):
        """Test indexing into collection."""
        collection = self.create_sample_users()
        assert collection[0].first_name == "John"
        assert collection[1].first_name == "Jane"
        assert collection[2].first_name == "Bob"

    def test_collection_add_remove(self):
        """Test adding and removing users from collection."""
        collection = UserCollection()
        user = User.from_api_dict(
            {"id": "999", "type": "users", "attributes": {"first-name": "Test"}}
        )

        # Add user (modify data list directly since ITGlueResourceCollection doesn't have add/remove)
        collection.data.append(user)
        assert len(collection) == 1
        assert collection[0].first_name == "Test"

        # Remove user
        collection.data.remove(user)
        assert len(collection) == 0

    def test_find_by_email(self):
        """Test finding user by email."""
        collection = self.create_sample_users()

        # Found user
        user = collection.find_by_email("john@example.com")
        assert user is not None
        assert user.first_name == "John"

        # Case insensitive
        user = collection.find_by_email("JANE@EXAMPLE.COM")
        assert user is not None
        assert user.first_name == "Jane"

        # Not found
        user = collection.find_by_email("notfound@example.com")
        assert user is None

    def test_find_by_name(self):
        """Test finding users by name."""
        collection = self.create_sample_users()

        # Find by first name
        users = collection.find_by_name("John")
        assert len(users) == 1
        assert users[0].first_name == "John"

        # Find by last name
        users = collection.find_by_name("Smith")
        assert len(users) == 1
        assert users[0].last_name == "Smith"

        # Partial match (case insensitive)
        users = collection.find_by_name("jo")
        assert len(users) == 1
        assert users[0].first_name == "John"

        # No matches
        users = collection.find_by_name("xyz")
        assert len(users) == 0

    def test_filter_by_role(self):
        """Test filtering users by role."""
        collection = self.create_sample_users()

        # Filter by string role
        admins = collection.filter_by_role("Admin")
        assert len(admins) == 1
        assert admins[0].first_name == "John"

        # Filter by enum role
        editors = collection.filter_by_role(UserRole.EDITOR)
        assert len(editors) == 1
        assert editors[0].first_name == "Jane"

        # No matches
        creators = collection.filter_by_role("Creator")
        assert len(creators) == 0

    def test_filter_by_my_glue_access(self):
        """Test filtering users by MyGlue access."""
        collection = self.create_sample_users()

        # Users with MyGlue access
        with_access = collection.filter_by_my_glue_access(True)
        assert len(with_access) == 2
        names = [user.first_name for user in with_access]
        assert "John" in names
        assert "Bob" in names

        # Users without MyGlue access
        without_access = collection.filter_by_my_glue_access(False)
        assert len(without_access) == 1
        assert without_access[0].first_name == "Jane"

    def test_filter_active_and_invited_users(self):
        """Test filtering active and invited users."""
        collection = self.create_sample_users()

        # Active users (accepted invitation)
        active = collection.filter_active_users()
        assert len(active) == 2
        names = [user.first_name for user in active]
        assert "John" in names
        assert "Bob" in names

        # Invited users (sent but not accepted)
        invited = collection.filter_invited_users()
        assert len(invited) == 1
        assert invited[0].first_name == "Jane"

    def test_get_top_reputation_users(self):
        """Test getting top reputation users."""
        collection = self.create_sample_users()

        # Top 2 users
        top_users = collection.get_top_reputation_users(2)
        assert len(top_users) == 2
        assert top_users[0].first_name == "John"  # 5000 reputation
        assert top_users[1].first_name == "Jane"  # 2500 reputation

        # Limit more than available
        all_users = collection.get_top_reputation_users(10)
        assert len(all_users) == 3

    def test_get_recently_active_users(self):
        """Test getting recently active users."""
        collection = UserCollection()

        # Add user with recent activity
        recent_user_data = {
            "id": "1",
            "type": "users",
            "attributes": {
                "first-name": "Recent",
                "last-sign-in-at": (
                    datetime.now(timezone.utc) - timedelta(days=5)
                ).isoformat(),
            },
        }

        # Add user with old activity
        old_user_data = {
            "id": "2",
            "type": "users",
            "attributes": {
                "first-name": "Old",
                "last-sign-in-at": (
                    datetime.now(timezone.utc) - timedelta(days=60)
                ).isoformat(),
            },
        }

        collection.data.append(User.from_api_dict(recent_user_data))
        collection.data.append(User.from_api_dict(old_user_data))

        # Get users active in last 30 days
        recent = collection.get_recently_active_users(30)
        assert len(recent) == 1
        assert recent[0].first_name == "Recent"

    def test_get_role_distribution(self):
        """Test getting role distribution statistics."""
        collection = self.create_sample_users()

        distribution = collection.get_role_distribution()
        assert distribution["Admin"] == 1
        assert distribution["Editor"] == 1
        assert distribution["Viewer"] == 1

    def test_get_my_glue_statistics(self):
        """Test getting MyGlue access statistics."""
        collection = self.create_sample_users()

        stats = collection.get_my_glue_statistics()
        assert stats["total_users"] == 3
        assert stats["with_my_glue_access"] == 2
        assert stats["without_my_glue_access"] == 1
        assert stats["my_glue_adoption_percentage"] == 66.67

    def test_to_list(self):
        """Test converting collection to list."""
        collection = self.create_sample_users()
        user_list = collection.to_list()

        assert isinstance(user_list, list)
        assert len(user_list) == 3
        assert user_list[0].first_name == "John"

        # Ensure it's a copy
        user_list.pop()
        assert len(collection) == 3  # Original unchanged


class TestUserEnums:
    """Test cases for User enums."""

    def test_user_role_enum(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN.value == "Admin"
        assert UserRole.CREATOR.value == "Creator"
        assert UserRole.EDITOR.value == "Editor"
        assert UserRole.LITE.value == "Lite"
        assert UserRole.VIEWER.value == "Viewer"

    def test_user_status_enum(self):
        """Test UserStatus enum values."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INVITED.value == "invited"
        assert UserStatus.SUSPENDED.value == "suspended"
        assert UserStatus.DISABLED.value == "disabled"
