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
from .organization import (
    Organization,
    OrganizationCollection,
    OrganizationStatus,
    OrganizationTypeEnum,
)
from .configuration import Configuration, ConfigurationCollection, ConfigurationStatus
from .flexible_asset import (
    FlexibleAsset,
    FlexibleAssetCollection,
    FlexibleAssetType,
    FlexibleAssetTypeCollection,
    FlexibleAssetField,
    FlexibleAssetFieldCollection,
    FlexibleAssetStatus,
)
from .user import User, UserCollection, UserRole, UserStatus
from .password import (
    Password,
    PasswordCollection,
    PasswordType,
    PasswordCategory,
    PasswordVisibility,
)

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
    "FlexibleAsset",
    "FlexibleAssetCollection",
    "FlexibleAssetType",
    "FlexibleAssetTypeCollection",
    "FlexibleAssetField",
    "FlexibleAssetFieldCollection",
    "FlexibleAssetStatus",
    "User",
    "UserCollection",
    "UserRole",
    "UserStatus",
    "Password",
    "PasswordCollection",
    "PasswordType",
    "PasswordCategory",
    "PasswordVisibility",
]
