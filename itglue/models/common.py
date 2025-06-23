"""
Common field types and validators for ITGlue models.

Provides custom field types that handle ITGlue-specific data formats,
validation rules, and transformations.
"""

import re
from datetime import datetime, date
from typing import Any, Union, Optional
from urllib.parse import urlparse

from pydantic import Field, field_validator, ConfigDict
from pydantic.types import AwareDatetime


class ITGlueDateTime(AwareDatetime):
    """
    ITGlue datetime field that handles RFC3339 UTC format.
    
    ITGlue API returns dates in RFC3339 format with UTC timezone.
    This field type ensures proper parsing and validation.
    """
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> datetime:
        """Validate and parse ITGlue datetime strings."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Handle ITGlue's RFC3339 format: 2023-08-01T12:00:00.000Z
            try:
                # Remove microseconds if present and add UTC timezone if missing
                if v.endswith('Z'):
                    v = v[:-1] + '+00:00'
                elif not v.endswith(('+00:00', 'Z')) and 'T' in v:
                    v = v + '+00:00'
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {v}")
        raise ValueError(f"Invalid datetime type: {type(v)}")


class ITGlueDate(date):
    """
    ITGlue date field for date-only values.
    
    Handles date strings in YYYY-MM-DD format.
    """
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> date:
        """Validate and parse ITGlue date strings."""
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v).date()
            except ValueError:
                raise ValueError(f"Invalid date format: {v}")
        raise ValueError(f"Invalid date type: {type(v)}")


class ITGlueURL(str):
    """
    ITGlue URL field with validation.
    
    Validates that the value is a properly formatted URL.
    """
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        """Validate URL format."""
        if not isinstance(v, str):
            raise ValueError("URL must be a string")
        
        if not v:
            return v
        
        try:
            result = urlparse(v)
            if not result.scheme or not result.netloc:
                raise ValueError("Invalid URL format")
            return v
        except Exception:
            raise ValueError(f"Invalid URL: {v}")


class ITGlueEmail(str):
    """
    ITGlue email field with validation.
    
    Validates email format using regex pattern.
    """
    
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        """Validate email format."""
        if not isinstance(v, str):
            raise ValueError("Email must be a string")
        
        if not v:
            return v
        
        if not cls.EMAIL_REGEX.match(v):
            raise ValueError(f"Invalid email format: {v}")
        
        return v.lower()


class ITGluePhone(str):
    """
    ITGlue phone number field with basic validation.
    
    Allows various phone number formats and normalizes them.
    """
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        """Validate and normalize phone number."""
        if not isinstance(v, str):
            raise ValueError("Phone number must be a string")
        
        if not v:
            return v
        
        # Remove common separators for validation
        cleaned = re.sub(r'[^\d+]', '', v)
        
        # Basic validation - must have at least 7 digits
        if len(re.sub(r'[^\d]', '', cleaned)) < 7:
            raise ValueError(f"Invalid phone number: {v}")
        
        return v


class ITGlueSlug(str):
    """
    ITGlue slug field for URL-safe identifiers.
    
    Validates that the value contains only lowercase letters,
    numbers, and hyphens.
    """
    
    SLUG_REGEX = re.compile(r'^[a-z0-9-]+$')
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        """Validate slug format."""
        if not isinstance(v, str):
            raise ValueError("Slug must be a string")
        
        if not v:
            return v
        
        if not cls.SLUG_REGEX.match(v):
            raise ValueError(
                f"Invalid slug format: {v}. "
                "Must contain only lowercase letters, numbers, and hyphens."
            )
        
        return v


# Common field definitions with validation
def required_string(min_length: int = 1, max_length: Optional[int] = None) -> Field:
    """Create a required string field with length validation."""
    return Field(
        ...,
        min_length=min_length,
        max_length=max_length,
        description=f"Required string with {min_length}-{max_length or 'unlimited'} characters"
    )


def optional_string(max_length: Optional[int] = None) -> Field:
    """Create an optional string field with optional length validation."""
    return Field(
        None,
        max_length=max_length,
        description=f"Optional string with max {max_length or 'unlimited'} characters"
    )


def required_int(ge: Optional[int] = None, le: Optional[int] = None) -> Field:
    """Create a required integer field with range validation."""
    return Field(
        ...,
        ge=ge,
        le=le,
        description=f"Required integer {f'between {ge}' if ge else ''}{f' and {le}' if le else ''}"
    )


def optional_int(ge: Optional[int] = None, le: Optional[int] = None) -> Field:
    """Create an optional integer field with range validation."""
    return Field(
        None,
        ge=ge,
        le=le,
        description=f"Optional integer {f'between {ge}' if ge else ''}{f' and {le}' if le else ''}"
    )


def itglue_id_field() -> Field:
    """Create an ITGlue ID field (positive integer as string)."""
    return Field(
        ...,
        pattern=r'^\d+$',
        description="ITGlue resource ID (positive integer as string)"
    )


def optional_itglue_id_field() -> Field:
    """Create an optional ITGlue ID field."""
    return Field(
        None,
        pattern=r'^\d+$',
        description="Optional ITGlue resource ID (positive integer as string)"
    ) 