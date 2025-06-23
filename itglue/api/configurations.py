"""Configurations API Resource

Provides specialized methods for managing ITGlue Configurations including
filtering by organization, configuration type, status, and asset management.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from .base import BaseAPI
from ..models.configuration import Configuration, ConfigurationStatus
from ..models.base import ResourceType, ITGlueResourceCollection
from ..http_client import ITGlueHTTPClient
from ..exceptions import ITGlueValidationError

logger = logging.getLogger(__name__)


class ConfigurationsAPI(BaseAPI[Configuration]):
    """API client for ITGlue Configurations.
    
    Provides CRUD operations and specialized methods for managing configurations
    including organization filtering, type-based queries, and asset management.
    """
    
    def __init__(self, client: ITGlueHTTPClient):
        super().__init__(
            client=client,
            resource_type=ResourceType.CONFIGURATIONS,
            model_class=Configuration,
            endpoint_path="configurations"
        )
    
    async def get_by_name(
        self,
        name: str,
        organization_id: Optional[str] = None,
        exact_match: bool = True,
        include: Optional[List[str]] = None
    ) -> Optional[Configuration]:
        """Get configuration by name, optionally within a specific organization.
        
        Args:
            name: Configuration name to search for
            organization_id: Optional organization ID to filter by
            exact_match: Whether to use exact name matching
            include: List of related resources to include
            
        Returns:
            Configuration if found, None otherwise
        """
        logger.info(f"Getting configuration by name: {name}")
        
        if exact_match:
            filter_params = {'name': name}
        else:
            # Use partial matching
            filter_params = {'name': f'*{name}*'}
        
        if organization_id:
            filter_params['organization-id'] = organization_id
        
        results = await self.list(
            filter_params=filter_params,
            include=include,
            per_page=1
        )
        
        return results.data[0] if results.data else None
    
    async def list_by_organization(
        self,
        organization_id: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include: Optional[List[str]] = None,
        **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """List configurations for a specific organization.
        
        Args:
            organization_id: Organization ID to filter by
            page: Page number for pagination
            per_page: Number of items per page
            include: List of related resources to include
            **kwargs: Additional query parameters
            
        Returns:
            Collection of configurations for the organization
        """
        logger.info(f"Listing configurations for organization: {organization_id}")
        
        filter_params = {'organization-id': organization_id}
        
        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            include=include,
            **kwargs
        )
    
    async def list_by_type(
        self,
        configuration_type_id: str,
        organization_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include: Optional[List[str]] = None,
        **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """List configurations filtered by type.
        
        Args:
            configuration_type_id: Configuration type ID to filter by
            organization_id: Optional organization ID to filter by
            page: Page number for pagination
            per_page: Number of items per page
            include: List of related resources to include
            **kwargs: Additional query parameters
            
        Returns:
            Collection of configurations with specified type
        """
        logger.info(f"Listing configurations with type: {configuration_type_id}")
        
        filter_params = {'configuration-type-id': configuration_type_id}
        
        if organization_id:
            filter_params['organization-id'] = organization_id
        
        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            include=include,
            **kwargs
        )
    
    async def list_by_status(
        self,
        status: Union[ConfigurationStatus, str],
        organization_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include: Optional[List[str]] = None,
        **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """List configurations filtered by status.
        
        Args:
            status: Configuration status to filter by
            organization_id: Optional organization ID to filter by
            page: Page number for pagination
            per_page: Number of items per page
            include: List of related resources to include
            **kwargs: Additional query parameters
            
        Returns:
            Collection of configurations with specified status
        """
        logger.info(f"Listing configurations with status: {status}")
        
        if isinstance(status, ConfigurationStatus):
            status_value = status.value
        else:
            status_value = status
        
        filter_params = {'configuration-status-name': status_value}
        
        if organization_id:
            filter_params['organization-id'] = organization_id
        
        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            include=include,
            **kwargs
        )
    
    async def get_active_configurations(
        self,
        organization_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """Get all active configurations.
        
        Args:
            organization_id: Optional organization ID to filter by
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters
            
        Returns:
            Collection of active configurations
        """
        return await self.list_by_status(
            status=ConfigurationStatus.ACTIVE,
            organization_id=organization_id,
            page=page,
            per_page=per_page,
            **kwargs
        )
    
    async def search_by_hostname(
        self,
        hostname: str,
        organization_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """Search configurations by hostname.
        
        Args:
            hostname: Hostname to search for
            organization_id: Optional organization ID to filter by
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters
            
        Returns:
            Collection of configurations matching hostname
        """
        logger.info(f"Searching configurations by hostname: {hostname}")
        
        filter_params = {'hostname': hostname}
        
        if organization_id:
            filter_params['organization-id'] = organization_id
        
        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            **kwargs
        )
    
    async def search_by_ip_address(
        self,
        ip_address: str,
        organization_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """Search configurations by IP address.
        
        Args:
            ip_address: IP address to search for
            organization_id: Optional organization ID to filter by
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters
            
        Returns:
            Collection of configurations matching IP address
        """
        logger.info(f"Searching configurations by IP address: {ip_address}")
        
        filter_params = {'primary-ip': ip_address}
        
        if organization_id:
            filter_params['organization-id'] = organization_id
        
        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            **kwargs
        )
    
    async def update_status(
        self,
        configuration_id: str,
        status: Union[ConfigurationStatus, str],
        **kwargs
    ) -> Configuration:
        """Update configuration status.
        
        Args:
            configuration_id: ID of configuration to update
            status: New status for the configuration
            **kwargs: Additional update data
            
        Returns:
            Updated configuration
            
        Raises:
            ITGlueValidationError: If status is invalid
        """
        logger.info(f"Updating configuration {configuration_id} status to: {status}")
        
        if isinstance(status, ConfigurationStatus):
            status_value = status.value
        else:
            status_value = status
            # Validate status
            try:
                ConfigurationStatus(status_value)
            except ValueError:
                raise ITGlueValidationError(f"Invalid configuration status: {status_value}")
        
        update_data = {'configuration_status_name': status_value}
        update_data.update(kwargs)
        
        return await self.update(configuration_id, update_data)
    
    async def create_configuration(
        self,
        name: str,
        organization_id: str,
        configuration_type_id: str,
        hostname: Optional[str] = None,
        primary_ip: Optional[str] = None,
        operating_system_id: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> Configuration:
        """Create a new configuration with required fields.
        
        Args:
            name: Configuration name
            organization_id: Organization ID this configuration belongs to
            configuration_type_id: Configuration type ID
            hostname: Optional hostname
            primary_ip: Optional primary IP address
            operating_system_id: Optional operating system ID
            notes: Optional notes
            **kwargs: Additional configuration attributes
            
        Returns:
            Created configuration
            
        Raises:
            ITGlueValidationError: If required data is missing or invalid
        """
        logger.info(f"Creating configuration: {name}")
        
        configuration_data = {
            'name': name,
            'organization_id': organization_id,
            'configuration_type_id': configuration_type_id,
            'configuration_status_name': ConfigurationStatus.ACTIVE.value,  # Default to active
        }
        
        if hostname:
            configuration_data['hostname'] = hostname
        if primary_ip:
            configuration_data['primary_ip'] = primary_ip
        if operating_system_id:
            configuration_data['operating_system_id'] = operating_system_id
        if notes:
            configuration_data['notes'] = notes
        
        # Add any additional attributes
        configuration_data.update(kwargs)
        
        return await self.create(configuration_data)
    
    async def bulk_update_status(
        self,
        configuration_ids: List[str],
        status: Union[ConfigurationStatus, str]
    ) -> List[Configuration]:
        """Update status for multiple configurations.
        
        Args:
            configuration_ids: List of configuration IDs to update
            status: New status for all configurations
            
        Returns:
            List of updated configurations
            
        Note:
            This performs individual updates. For true bulk operations,
            ITGlue may provide batch endpoints in the future.
        """
        logger.info(f"Bulk updating {len(configuration_ids)} configurations to status: {status}")
        
        updated_configurations = []
        for config_id in configuration_ids:
            try:
                updated_config = await self.update_status(config_id, status)
                updated_configurations.append(updated_config)
            except Exception as e:
                logger.error(f"Failed to update configuration {config_id}: {e}")
                continue
        
        logger.info(f"Successfully updated {len(updated_configurations)} of {len(configuration_ids)} configurations")
        return updated_configurations
    
    async def get_configuration_statistics(
        self,
        organization_id: Optional[str] = None,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Get statistics about configurations.
        
        Args:
            organization_id: Optional organization ID to filter by
            include_inactive: Whether to include inactive configurations in counts
            
        Returns:
            Dictionary with configuration statistics
        """
        logger.info("Generating configuration statistics")
        
        stats = {
            'total': 0,
            'by_status': {},
            'by_organization': {},
            'active': 0,
            'inactive': 0
        }
        
        # Get configurations
        filter_params = {}
        if organization_id:
            filter_params['organization-id'] = organization_id
        if not include_inactive:
            filter_params['configuration-status-name'] = ConfigurationStatus.ACTIVE.value
        
        if filter_params:
            configurations = await self.list(filter_params=filter_params)
        else:
            configurations = await self.list_all()
        
        stats['total'] = len(configurations.data)
        
        # Count by status and organization
        for config in configurations.data:
            # Count by status
            config_status = config.configuration_status_name or 'Unknown'
            stats['by_status'][config_status] = stats['by_status'].get(config_status, 0) + 1
            
            # Count by organization
            config_org = config.organization_id or 'Unknown'
            stats['by_organization'][config_org] = stats['by_organization'].get(config_org, 0) + 1
            
            if config.is_active():
                stats['active'] += 1
            else:
                stats['inactive'] += 1
        
        return stats
    
    async def get_configurations_by_contact(
        self,
        contact_id: str,
        contact_type: str = "Primary",
        organization_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """Get configurations associated with a specific contact.
        
        Args:
            contact_id: Contact ID to filter by
            contact_type: Type of contact relationship
            organization_id: Optional organization ID to filter by
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters
            
        Returns:
            Collection of configurations associated with the contact
        """
        logger.info(f"Getting configurations for contact: {contact_id}")
        
        contact_type_value = contact_type
        
        filter_params = {
            'contact-id': contact_id,
            'contact-type': contact_type_value
        }
        
        if organization_id:
            filter_params['organization-id'] = organization_id
        
        return await self.list(
            page=page,
            per_page=per_page,
            filter_params=filter_params,
            **kwargs
        ) 