"""
ITGlue Client

Main client class for interacting with the ITGlue API.
"""

from typing import Optional

from .config import ITGlueConfig


class ITGlueClient:
    """Main client for ITGlue API interactions."""
    
    def __init__(self, config: Optional[ITGlueConfig] = None):
        """Initialize the ITGlue client."""
        self.config = config or ITGlueConfig.from_environment()
        self.config.validate()
    
    @classmethod
    def from_environment(cls) -> "ITGlueClient":
        """Create client from environment variables."""
        return cls(ITGlueConfig.from_environment())
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ITGlueClient(base_url='{self.config.base_url}')" 