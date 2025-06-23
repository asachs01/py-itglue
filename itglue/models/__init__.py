"""
ITGlue Models

Pydantic models for ITGlue API resources with data validation,
serialization, and JSON API specification compliance.
"""

from .base import (
    ITGlueResource,
    ITGlueResourceCollection,
    ITGlueRelationship,
    ITGlueLinks,
    ITGlueMeta,
    ResourceType,
)
from .common import (
    ITGlueDateTime,
    ITGlueDate,
    ITGlueURL,
    ITGlueEmail,
    ITGluePhone,
    ITGlueSlug,
)
from .organization import Organization, OrganizationCollection, OrganizationStatus, OrganizationTypeEnum
from .configuration import Configuration, ConfigurationCollection, ConfigurationStatus

__all__ = [
    # Base models
    "ITGlueResource",
    "ITGlueResourceCollection", 
    "ITGlueRelationship",
    "ITGlueLinks",
    "ITGlueMeta",
    "ResourceType",
    
    # Common types
    "ITGlueDateTime",
    "ITGlueDate", 
    "ITGlueURL",
    "ITGlueEmail",
    "ITGluePhone",
    "ITGlueSlug",
    
    # Resource models
    "Organization",
    "OrganizationCollection",
    "OrganizationStatus",
    "OrganizationTypeEnum",
    "Configuration",
    "ConfigurationCollection", 
    "ConfigurationStatus",
] 