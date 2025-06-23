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
            endpoint_path="configurations",
        )

    def get_by_name(
        self, name: str, exact_match: bool = False, **kwargs
    ) -> Optional[Configuration]:
        """Get configuration by name.
        
        Args:
            name: Configuration name to search for
            exact_match: If True, performs exact match; otherwise fuzzy search
            **kwargs: Additional query parameters
            
        Returns:
            Configuration if found, None otherwise
        """
        logger.info(f"Getting configuration by name: {name}")
        
        if exact_match:
            # Use exact filter for exact match
            kwargs["filter_params"] = {"name": name}
            kwargs["per_page"] = 1
            
            result = self.list(**kwargs)
            return result.data[0] if result.data else None
        else:
            # Use search for fuzzy matching
            return self.search(name, **kwargs)

    def list_by_organization(self, organization_id: str, **kwargs) -> ITGlueResourceCollection[Configuration]:
        """List configurations for a specific organization.
        
        Args:
            organization_id: ID of the organization
            **kwargs: Additional query parameters
            
        Returns:
            ConfigurationCollection containing matching configurations
        """
        logger.info(f"Listing configurations for organization: {organization_id}")
        
        filter_params = kwargs.get("filter_params", {})
        filter_params["organization-id"] = organization_id
        kwargs["filter_params"] = filter_params
        
        return self.list(**kwargs)

    def list_by_type(self, configuration_type_id: str, **kwargs) -> ITGlueResourceCollection[Configuration]:
        """List configurations by type.
        
        Args:
            configuration_type_id: ID of the configuration type
            **kwargs: Additional query parameters
            
        Returns:
            ConfigurationCollection containing matching configurations
        """
        logger.info(f"Listing configurations by type: {configuration_type_id}")
        
        filter_params = kwargs.get("filter_params", {})
        filter_params["configuration-type-id"] = configuration_type_id
        kwargs["filter_params"] = filter_params
        
        return self.list(**kwargs)

    def list_by_status(
        self, status: Union[ConfigurationStatus, str], **kwargs
    ) -> ITGlueResourceCollection[Configuration]:
        """List configurations by status.
        
        Args:
            status: Configuration status (enum or string)
            **kwargs: Additional query parameters
            
        Returns:
            ConfigurationCollection containing matching configurations
        """
        if isinstance(status, ConfigurationStatus):
            status_name = status.value
        else:
            status_name = status
            
        logger.info(f"Listing configurations by status: {status_name}")
        
        filter_params = kwargs.get("filter_params", {})
        filter_params["configuration-status-name"] = status_name
        kwargs["filter_params"] = filter_params
        
        return self.list(**kwargs)

    def get_active_configurations(self, **kwargs) -> ITGlueResourceCollection[Configuration]:
        """Get all active configurations.
        
        Args:
            **kwargs: Additional query parameters
            
        Returns:
            ConfigurationCollection containing active configurations
        """
        return self.list_by_status(ConfigurationStatus.ACTIVE, **kwargs)

    def search_by_hostname(self, hostname: str, **kwargs) -> ITGlueResourceCollection[Configuration]:
        """Search configurations by hostname.
        
        Args:
            hostname: Hostname to search for
            **kwargs: Additional query parameters
            
        Returns:
            ConfigurationCollection containing matching configurations
        """
        logger.info(f"Searching configurations by hostname: {hostname}")
        
        filter_params = kwargs.get("filter_params", {})
        filter_params["hostname"] = hostname
        kwargs["filter_params"] = filter_params
        
        return self.list(**kwargs)

    def search_by_ip_address(self, ip_address: str, **kwargs) -> ITGlueResourceCollection[Configuration]:
        """Search configurations by IP address.
        
        Args:
            ip_address: IP address to search for
            **kwargs: Additional query parameters
            
        Returns:
            ConfigurationCollection containing matching configurations
        """
        logger.info(f"Searching configurations by IP: {ip_address}")
        
        filter_params = kwargs.get("filter_params", {})
        filter_params["primary-ip"] = ip_address
        kwargs["filter_params"] = filter_params
        
        return self.list(**kwargs)

    def update_status(
        self, configuration_id: str, status: Union[ConfigurationStatus, str], **kwargs
    ) -> Configuration:
        """Update configuration status.
        
        Args:
            configuration_id: ID of the configuration to update
            status: New status (enum or string)
            **kwargs: Additional query parameters
            
        Returns:
            Updated Configuration
            
        Raises:
            ITGlueValidationError: If status is invalid
        """
        if isinstance(status, ConfigurationStatus):
            status_name = status.value
        elif isinstance(status, str) and status in [s.value for s in ConfigurationStatus]:
            status_name = status
        else:
            raise ITGlueValidationError(f"Invalid configuration status: {status}")
            
        logger.info(f"Updating configuration {configuration_id} status to: {status_name}")
        
        data = {"configuration-status-name": status_name}
        return self.update(configuration_id, data, **kwargs)

    def create_configuration(
        self,
        organization_id: str,
        name: str,
        configuration_type_id: str,
        hostname: Optional[str] = None,
        primary_ip: Optional[str] = None,
        operating_system_notes: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs,
    ) -> Configuration:
        """Create a new configuration.
        
        Args:
            organization_id: ID of the organization
            name: Configuration name
            configuration_type_id: ID of the configuration type
            hostname: Optional hostname
            primary_ip: Optional primary IP address
            operating_system_notes: Optional OS notes
            notes: Optional general notes
            **kwargs: Additional configuration attributes
            
        Returns:
            Created Configuration
        """
        logger.info(f"Creating configuration: {name} for organization {organization_id}")
        
        data = {
            "organization-id": organization_id,
            "name": name,
            "configuration-type-id": configuration_type_id,
        }
        
        # Add optional fields
        if hostname:
            data["hostname"] = hostname
        if primary_ip:
            data["primary-ip"] = primary_ip
        if operating_system_notes:
            data["operating-system-notes"] = operating_system_notes
        if notes:
            data["notes"] = notes
            
        # Add any additional kwargs
        data.update(kwargs)
        
        return self.create(data)

    def bulk_update_status(
        self, configuration_ids: List[str], status: Union[ConfigurationStatus, str]
    ) -> List[Configuration]:
        """Bulk update status for multiple configurations.
        
        Args:
            configuration_ids: List of configuration IDs to update
            status: New status for all configurations
            
        Returns:
            List of updated Configuration objects
        """
        if isinstance(status, ConfigurationStatus):
            status_name = status.value
        elif isinstance(status, str) and status in [s.value for s in ConfigurationStatus]:
            status_name = status
        else:
            raise ITGlueValidationError(f"Invalid configuration status: {status}")
            
        logger.info(f"Bulk updating {len(configuration_ids)} configurations to status: {status_name}")
        
        updated_configs = []
        for config_id in configuration_ids:
            try:
                updated_config = self.update_status(config_id, status_name)
                updated_configs.append(updated_config)
            except Exception as e:
                logger.error(f"Failed to update configuration {config_id}: {e}")
                
        return updated_configs

    def get_configuration_statistics(self) -> Dict[str, Any]:
        """Get statistics about configurations.
        
        Returns:
            Dictionary containing configuration statistics
        """
        logger.info("Getting configuration statistics")
        
        # Get all configurations for analysis
        all_configs = self.list_all()
        
        stats = {
            "total_count": len(all_configs.data),
            "by_status": {},
            "by_type": {},
            "by_organization": {},
        }
        
        for config in all_configs.data:
            # Count by status
            status = config.configuration_status_name or "Unknown"
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by type
            config_type = config.configuration_type_name or "Unknown"
            stats["by_type"][config_type] = stats["by_type"].get(config_type, 0) + 1
            
            # Count by organization
            org_id = config.organization_id or "Unknown"
            stats["by_organization"][org_id] = stats["by_organization"].get(org_id, 0) + 1
            
        return stats

    def get_organization_configuration_report(self, organization_id: str) -> Dict[str, Any]:
        """Get detailed configuration report for an organization.
        
        Args:
            organization_id: ID of the organization
            
        Returns:
            Dictionary containing organization configuration report
        """
        logger.info(f"Getting configuration report for organization: {organization_id}")
        
        configs = self.list_by_organization(organization_id)
        
        report = {
            "organization_id": organization_id,
            "total_configurations": len(configs.data),
            "active_configurations": len([c for c in configs.data if c.is_active()]),
            "retired_configurations": len([c for c in configs.data if c.is_retired()]),
            "configurations_by_type": {},
        }
        
        for config in configs.data:
            config_type = config.configuration_type_name or "Unknown"
            if config_type not in report["configurations_by_type"]:
                report["configurations_by_type"][config_type] = {
                    "total": 0,
                    "active": 0,
                    "retired": 0,
                }
            
            report["configurations_by_type"][config_type]["total"] += 1
            if config.is_active():
                report["configurations_by_type"][config_type]["active"] += 1
            elif config.is_retired():
                report["configurations_by_type"][config_type]["retired"] += 1
                
        return report
