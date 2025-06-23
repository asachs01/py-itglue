"""Organizations API Resource

Provides specialized methods for managing ITGlue Organizations including
status transitions, filtering by organization type, and relationship management.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from .base import BaseAPI
from ..models.organization import Organization, OrganizationStatus, OrganizationTypeEnum
from ..models.base import ResourceType, ITGlueResourceCollection
from ..http_client import ITGlueHTTPClient
from ..exceptions import ITGlueValidationError

logger = logging.getLogger(__name__)


class OrganizationsAPI(BaseAPI[Organization]):
    """API client for ITGlue Organizations.

    Provides CRUD operations and specialized methods for managing organizations
    including status filtering, type-based queries, and bulk operations.
    """

    def __init__(self, client: ITGlueHTTPClient):
        super().__init__(
            client=client,
            resource_type=ResourceType.ORGANIZATIONS,
            model_class=Organization,
            endpoint_path="organizations",
        )

    async def get_by_name(
        self, name: str, exact_match: bool = True, include: Optional[List[str]] = None
    ) -> Optional[Organization]:
        """Get organization by name.

        Args:
            name: Organization name to search for
            exact_match: Whether to use exact name matching
            include: List of related resources to include

        Returns:
            Organization if found, None otherwise
        """
        logger.info(f"Getting organization by name: {name}")

        if exact_match:
            filter_params = {"name": name}
        else:
            # Use partial matching
            filter_params = {"name": f"*{name}*"}

        results = await self.list(
            filter_params=filter_params, include=include, per_page=1
        )

        return results.data[0] if results.data else None

    async def list_by_status(
        self,
        status: Union[OrganizationStatus, str],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include: Optional[List[str]] = None,
        **kwargs,
    ) -> ITGlueResourceCollection[Organization]:
        """List organizations filtered by status.

        Args:
            status: Organization status to filter by
            page: Page number for pagination
            per_page: Number of items per page
            include: List of related resources to include
            **kwargs: Additional query parameters

        Returns:
            Collection of organizations with specified status
        """
        logger.info(f"Listing organizations with status: {status}")

        if isinstance(status, OrganizationStatus):
            status_value = status.value
        else:
            status_value = status

        filter_params = {"organization-status-name": status_value}

        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            include=include,
            **kwargs,
        )

    async def list_by_type(
        self,
        org_type: Union[OrganizationTypeEnum, str],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include: Optional[List[str]] = None,
        **kwargs,
    ) -> ITGlueResourceCollection[Organization]:
        """List organizations filtered by type.

        Args:
            org_type: Organization type to filter by
            page: Page number for pagination
            per_page: Number of items per page
            include: List of related resources to include
            **kwargs: Additional query parameters

        Returns:
            Collection of organizations with specified type
        """
        logger.info(f"Listing organizations with type: {org_type}")

        if isinstance(org_type, OrganizationTypeEnum):
            type_value = org_type.value
        else:
            type_value = org_type

        filter_params = {"organization-type-name": type_value}

        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            include=include,
            **kwargs,
        )

    async def get_active_organizations(
        self, page: Optional[int] = None, per_page: Optional[int] = None, **kwargs
    ) -> ITGlueResourceCollection[Organization]:
        """Get all active organizations.

        Args:
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters

        Returns:
            Collection of active organizations
        """
        return await self.list_by_status(
            status=OrganizationStatus.ACTIVE, page=page, per_page=per_page, **kwargs
        )

    async def get_client_organizations(
        self,
        active_only: bool = True,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> ITGlueResourceCollection[Organization]:
        """Get client organizations.

        Args:
            active_only: Whether to only return active clients
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters

        Returns:
            Collection of client organizations
        """
        logger.info(f"Getting client organizations (active_only={active_only})")

        filter_params = {"organization-type-name": OrganizationTypeEnum.CLIENT.value}

        if active_only:
            filter_params["organization-status-name"] = OrganizationStatus.ACTIVE.value

        return await self.list(
            page=page, per_page=per_page, filter_params=filter_params, **kwargs
        )

    async def get_internal_organizations(
        self, page: Optional[int] = None, per_page: Optional[int] = None, **kwargs
    ) -> ITGlueResourceCollection[Organization]:
        """Get internal organizations.

        Args:
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters

        Returns:
            Collection of internal organizations
        """
        return await self.list_by_type(
            org_type=OrganizationTypeEnum.INTERNAL,
            page=page,
            per_page=per_page,
            **kwargs,
        )

    async def search_by_domain(
        self,
        domain: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> ITGlueResourceCollection[Organization]:
        """Search organizations by primary domain.

        Args:
            domain: Domain to search for
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters

        Returns:
            Collection of organizations matching domain
        """
        logger.info(f"Searching organizations by domain: {domain}")

        filter_params = {"primary-domain": domain}

        return await self.list(
            page=page, per_page=per_page, filter_params=filter_params, **kwargs
        )

    async def update_status(
        self, organization_id: str, status: Union[OrganizationStatus, str], **kwargs
    ) -> Organization:
        """Update organization status.

        Args:
            organization_id: ID of organization to update
            status: New status for the organization
            **kwargs: Additional update data

        Returns:
            Updated organization

        Raises:
            ITGlueValidationError: If status is invalid
        """
        logger.info(f"Updating organization {organization_id} status to: {status}")

        if isinstance(status, OrganizationStatus):
            status_value = status.value
        else:
            status_value = status
            # Validate status
            try:
                OrganizationStatus(status_value)
            except ValueError:
                raise ITGlueValidationError(
                    f"Invalid organization status: {status_value}"
                )

        update_data = {"organization_status_name": status_value}
        update_data.update(kwargs)

        return await self.update(organization_id, update_data)

    async def create_organization(
        self,
        name: str,
        organization_type: Union[OrganizationTypeEnum, str],
        description: Optional[str] = None,
        primary_domain: Optional[str] = None,
        quick_notes: Optional[str] = None,
        **kwargs,
    ) -> Organization:
        """Create a new organization with required fields.

        Args:
            name: Organization name
            organization_type: Type of organization
            description: Optional description
            primary_domain: Optional primary domain
            quick_notes: Optional quick notes
            **kwargs: Additional organization attributes

        Returns:
            Created organization

        Raises:
            ITGlueValidationError: If required data is missing or invalid
        """
        logger.info(f"Creating organization: {name}")

        if isinstance(organization_type, OrganizationTypeEnum):
            type_value = organization_type.value
        else:
            type_value = organization_type
            # Validate type
            try:
                OrganizationTypeEnum(type_value)
            except ValueError:
                raise ITGlueValidationError(f"Invalid organization type: {type_value}")

        organization_data = {
            "name": name,
            "organization_type_name": type_value,
            "organization_status_name": OrganizationStatus.ACTIVE.value,  # Default to active
        }

        if description:
            organization_data["description"] = description
        if primary_domain:
            organization_data["primary_domain"] = primary_domain
        if quick_notes:
            organization_data["quick_notes"] = quick_notes

        # Add any additional attributes
        organization_data.update(kwargs)

        return await self.create(organization_data)

    async def bulk_update_status(
        self, organization_ids: List[str], status: Union[OrganizationStatus, str]
    ) -> List[Organization]:
        """Update status for multiple organizations.

        Args:
            organization_ids: List of organization IDs to update
            status: New status for all organizations

        Returns:
            List of updated organizations

        Note:
            This performs individual updates. For true bulk operations,
            ITGlue may provide batch endpoints in the future.
        """
        logger.info(
            f"Bulk updating {len(organization_ids)} organizations to status: {status}"
        )

        updated_organizations = []
        for org_id in organization_ids:
            try:
                updated_org = await self.update_status(org_id, status)
                updated_organizations.append(updated_org)
            except Exception as e:
                logger.error(f"Failed to update organization {org_id}: {e}")
                continue

        logger.info(
            f"Successfully updated {len(updated_organizations)} of {len(organization_ids)} organizations"
        )
        return updated_organizations

    async def get_organization_statistics(
        self, include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Get statistics about organizations.

        Args:
            include_inactive: Whether to include inactive organizations in counts

        Returns:
            Dictionary with organization statistics
        """
        logger.info("Generating organization statistics")

        stats = {"total": 0, "by_type": {}, "by_status": {}, "active": 0, "inactive": 0}

        # Get all organizations (or just active ones)
        if include_inactive:
            organizations = await self.list_all()
        else:
            organizations = await self.get_active_organizations()

        stats["total"] = len(organizations.data)

        # Count by type and status
        for org in organizations.data:
            # Count by type
            org_type = org.organization_type_name or "Unknown"
            stats["by_type"][org_type] = stats["by_type"].get(org_type, 0) + 1

            # Count by status
            org_status = org.organization_status_name or "Unknown"
            stats["by_status"][org_status] = stats["by_status"].get(org_status, 0) + 1

            if org.is_active():
                stats["active"] += 1
            else:
                stats["inactive"] += 1

        return stats
