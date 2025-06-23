"""ITGlue API Resource Classes

This module provides high-level API resource classes for interacting with
ITGlue endpoints. Each resource class encapsulates CRUD operations and
follows consistent patterns for authentication, error handling, and data
validation.
"""

from .organizations import OrganizationsAPI
from .configurations import ConfigurationsAPI
from .flexible_assets import FlexibleAssetsAPI, FlexibleAssetTypesAPI, FlexibleAssetFieldsAPI
from .users import UsersAPI
from .passwords import PasswordsAPI

__all__ = [
    'OrganizationsAPI',
    'ConfigurationsAPI',
    'FlexibleAssetsAPI',
    'FlexibleAssetTypesAPI',
    'FlexibleAssetFieldsAPI',
    'UsersAPI',
    'PasswordsAPI',
] 