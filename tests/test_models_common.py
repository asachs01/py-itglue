"""
Tests for ITGlue common field types and validators.
"""

import pytest
from datetime import datetime, date
from unittest.mock import patch

from itglue.models.common import (
    ITGlueDateTime,
    ITGlueDate,
    ITGlueURL,
    ITGlueEmail,
    ITGluePhone,
    ITGlueSlug,
    required_string,
    optional_string,
    itglue_id_field,
)


class TestITGlueDateTime:
    """Test ITGlue datetime field type."""
    
    def test_datetime_validation_valid_formats(self):
        """Test valid datetime formats."""
        # RFC3339 with Z suffix
        dt1 = ITGlueDateTime.validate("2023-08-01T12:00:00.000Z")
        assert isinstance(dt1, datetime)
        
        # RFC3339 with timezone offset
        dt2 = ITGlueDateTime.validate("2023-08-01T12:00:00.000+00:00")
        assert isinstance(dt2, datetime)
        
        # Already a datetime object
        now = datetime.now()
        dt3 = ITGlueDateTime.validate(now)
        assert dt3 == now
    
    def test_datetime_validation_invalid_formats(self):
        """Test invalid datetime formats."""
        with pytest.raises(ValueError, match="Invalid datetime format"):
            ITGlueDateTime.validate("invalid-date")
        
        with pytest.raises(ValueError, match="Invalid datetime type"):
            ITGlueDateTime.validate(123)


class TestITGlueDate:
    """Test ITGlue date field type."""
    
    def test_date_validation_valid_formats(self):
        """Test valid date formats."""
        # ISO date string
        d1 = ITGlueDate.validate("2023-08-01")
        assert isinstance(d1, date)
        assert d1.year == 2023
        assert d1.month == 8
        assert d1.day == 1
        
        # Already a date object
        today = date.today()
        d2 = ITGlueDate.validate(today)
        assert d2 == today
    
    def test_date_validation_invalid_formats(self):
        """Test invalid date formats."""
        with pytest.raises(ValueError, match="Invalid date format"):
            ITGlueDate.validate("invalid-date")
        
        with pytest.raises(ValueError, match="Invalid date type"):
            ITGlueDate.validate(123)


class TestITGlueURL:
    """Test ITGlue URL field type."""
    
    def test_url_validation_valid_urls(self):
        """Test valid URL formats."""
        valid_urls = [
            "https://www.example.com",
            "http://example.com",
            "https://api.itglue.com/organizations",
            "ftp://files.example.com/file.txt"
        ]
        
        for url in valid_urls:
            result = ITGlueURL.validate(url)
            assert result == url
    
    def test_url_validation_empty_url(self):
        """Test empty URL is allowed."""
        result = ITGlueURL.validate("")
        assert result == ""
    
    def test_url_validation_invalid_urls(self):
        """Test invalid URL formats."""
        invalid_urls = [
            "not-a-url",
            "missing-protocol.com",
            "http://",
            "https://"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid URL"):
                ITGlueURL.validate(url)
    
    def test_url_validation_non_string(self):
        """Test non-string input."""
        with pytest.raises(ValueError, match="URL must be a string"):
            ITGlueURL.validate(123)


class TestITGlueEmail:
    """Test ITGlue email field type."""
    
    def test_email_validation_valid_emails(self):
        """Test valid email formats."""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@test-domain.com",
            "admin@itglue.com"
        ]
        
        for email in valid_emails:
            result = ITGlueEmail.validate(email)
            assert result == email.lower()
    
    def test_email_validation_empty_email(self):
        """Test empty email is allowed."""
        result = ITGlueEmail.validate("")
        assert result == ""
    
    def test_email_validation_invalid_emails(self):
        """Test invalid email formats."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com",
            "user@domain",
            "user space@example.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                ITGlueEmail.validate(email)
    
    def test_email_validation_non_string(self):
        """Test non-string input."""
        with pytest.raises(ValueError, match="Email must be a string"):
            ITGlueEmail.validate(123)


class TestITGluePhone:
    """Test ITGlue phone field type."""
    
    def test_phone_validation_valid_phones(self):
        """Test valid phone formats."""
        valid_phones = [
            "+1-234-567-8900",
            "(555) 123-4567",
            "555.123.4567",
            "+44 20 7946 0958",
            "1234567890"
        ]
        
        for phone in valid_phones:
            result = ITGluePhone.validate(phone)
            assert result == phone
    
    def test_phone_validation_empty_phone(self):
        """Test empty phone is allowed."""
        result = ITGluePhone.validate("")
        assert result == ""
    
    def test_phone_validation_invalid_phones(self):
        """Test invalid phone formats."""
        invalid_phones = [
            "123",  # Too short
            "abc",  # No digits
            "+++",  # No actual numbers
        ]
        
        for phone in invalid_phones:
            with pytest.raises(ValueError, match="Invalid phone number"):
                ITGluePhone.validate(phone)
    
    def test_phone_validation_non_string(self):
        """Test non-string input."""
        with pytest.raises(ValueError, match="Phone number must be a string"):
            ITGluePhone.validate(123)


class TestITGlueSlug:
    """Test ITGlue slug field type."""
    
    def test_slug_validation_valid_slugs(self):
        """Test valid slug formats."""
        valid_slugs = [
            "my-organization",
            "test123",
            "server-01",
            "a-very-long-slug-name-123"
        ]
        
        for slug in valid_slugs:
            result = ITGlueSlug.validate(slug)
            assert result == slug
    
    def test_slug_validation_empty_slug(self):
        """Test empty slug is allowed."""
        result = ITGlueSlug.validate("")
        assert result == ""
    
    def test_slug_validation_invalid_slugs(self):
        """Test invalid slug formats."""
        invalid_slugs = [
            "My-Organization",  # Uppercase
            "test_123",  # Underscore
            "test 123",  # Space
            "test@123",  # Special character
        ]
        
        for slug in invalid_slugs:
            with pytest.raises(ValueError, match="Invalid slug format"):
                ITGlueSlug.validate(slug)
    
    def test_slug_validation_non_string(self):
        """Test non-string input."""
        with pytest.raises(ValueError, match="Slug must be a string"):
            ITGlueSlug.validate(123)


class TestFieldHelpers:
    """Test field helper functions."""
    
    def test_required_string_field(self):
        """Test required string field creation."""
        from pydantic._internal._fields import PydanticUndefined
        field = required_string(min_length=2, max_length=50)
        assert field.default == PydanticUndefined  # Required in Pydantic v2
        assert "Required string" in field.description
    
    def test_optional_string_field(self):
        """Test optional string field creation."""
        field = optional_string(max_length=100)
        assert field.default is None  # Optional
        assert "Optional string" in field.description
    
    def test_itglue_id_field(self):
        """Test ITGlue ID field creation."""
        from pydantic._internal._fields import PydanticUndefined
        field = itglue_id_field()
        assert field.default == PydanticUndefined  # Required in Pydantic v2
        assert "ITGlue resource ID" in field.description 