# ITGlue Python SDK

A comprehensive Python SDK for the ITGlue API with AI agent capabilities.

## Overview

The ITGlue Python SDK provides a complete interface to the ITGlue API, enabling developers to:

- Manage organizations, configurations, passwords, and flexible assets
- Perform bulk operations with built-in error handling
- Implement real-time integrations with automatic rate limiting
- Cache responses for improved performance
- Build AI agents that can interact with ITGlue data

## Features

- **Complete API Coverage**: All ITGlue API endpoints supported
- **Built-in Pagination**: Automatic handling of paginated responses
- **Rate Limiting**: Intelligent throttling to respect API limits
- **Caching**: Redis and memory-based caching for performance
- **Data Validation**: Pydantic models for type safety
- **Bulk Operations**: Efficient batch processing with progress tracking
- **Multi-Region Support**: US, EU, and AU data centers
- **AI Agent Ready**: High-level semantic operations for AI integration

## Installation

```bash
# Install from PyPI (when available)
pip install py-itglue

# Install from source
git clone https://github.com/your-org/py-itglue.git
cd py-itglue
pip install -e .
```

## Quick Start

```python
import os
from itglue import ITGlueClient

# Set your API key
os.environ['ITGLUE_API_KEY'] = 'your-api-key-here'

# Create client
client = ITGlueClient.from_environment()

# List organizations
orgs = client.organizations.list()
print(f"Found {len(orgs)} organizations")

# Get specific organization
org = client.organizations.get(org_id=123)
print(f"Organization: {org.name}")

# Create a new configuration
config_data = {
    "name": "Web Server",
    "organization_id": 123,
    "configuration_type_id": 1,
    "configuration_status_id": 1
}
new_config = client.configurations.create(config_data)
```

## Configuration

### Environment Variables

- `ITGLUE_API_KEY`: Your ITGlue API key (required)
- `ITGLUE_REGION`: API region (`US`, `EU`, `AU`) - default: `US`
- `ITGLUE_BASE_URL`: Custom base URL (overrides region)
- `ITGLUE_TIMEOUT`: Request timeout in seconds - default: `30`
- `ITGLUE_MAX_RETRIES`: Maximum retry attempts - default: `3`
- `ITGLUE_ENABLE_CACHING`: Enable response caching - default: `true`
- `ITGLUE_CACHE_TTL`: Cache TTL in seconds - default: `300`
- `ITGLUE_LOG_LEVEL`: Logging level - default: `INFO`

### Programmatic Configuration

```python
from itglue import ITGlueClient
from itglue.config import ITGlueConfig

config = ITGlueConfig(
    api_key="your-api-key",
    base_url="https://api.itglue.com",
    timeout=60,
    enable_caching=True,
    cache_ttl=600
)

client = ITGlueClient(config)
```

## API Resources

### Organizations
- List, get, create, update, delete organizations
- Bulk operations support

### Configurations
- Manage IT infrastructure configurations
- Support for all configuration types and statuses

### Passwords
- Secure password management
- Category-based organization

### Flexible Assets
- Custom data structures
- Dynamic field support

### Contacts
- People and contact management
- Integration with organizations

### And More...
- Locations, Documents, Attachments
- Users, Groups, Logs
- Manufacturers, Models, Platforms
- Complete API coverage

## Advanced Features

### Bulk Operations

```python
# Bulk create configurations
configs_data = [
    {"name": "Server 1", "organization_id": 123},
    {"name": "Server 2", "organization_id": 123},
    {"name": "Server 3", "organization_id": 123},
]

results = client.configurations.bulk_create(configs_data)
print(f"Created {results.successful_count} configurations")
```

### Caching

```python
# Enable Redis caching
config = ITGlueConfig(
    api_key="your-key",
    cache_type="redis",
    redis_url="redis://localhost:6379/0"
)

client = ITGlueClient(config)
```

### AI Agent Integration

```python
# High-level semantic operations
agent = client.get_ai_agent()

# Natural language queries
results = agent.find("all web servers in production")
summary = agent.summarize_infrastructure(org_id=123)
recommendations = agent.suggest_improvements(org_id=123)
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/py-itglue.git
cd py-itglue

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=itglue --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run basic functionality test
python tests/test_config.py
```

### Code Quality

```bash
# Format code
black itglue tests

# Lint code
flake8 itglue tests

# Type checking
mypy itglue
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://py-itglue.readthedocs.io/](https://py-itglue.readthedocs.io/)
- Issues: [https://github.com/your-org/py-itglue/issues](https://github.com/your-org/py-itglue/issues)
- ITGlue API Documentation: [https://api.itglue.com/developer/](https://api.itglue.com/developer/)

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Note**: This SDK is not officially affiliated with ITGlue. It is a community-driven project to provide Python developers with a comprehensive interface to the ITGlue API. 