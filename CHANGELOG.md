# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Phase 1.2 - Core SDK Architecture** (2025-06-20)
  - HTTP client with authentication, rate limiting, and retry logic
  - Comprehensive error handling with custom exception hierarchy
  - Pagination system supporting JSON API specification
  - Caching system with memory and Redis backends
  - Rate limiter with configurable requests per minute/5-minutes
  - Response parsing and validation
  - Integration of all components in main client class
  - 120 comprehensive tests with 100% pass rate
  - Support for GET, POST, PATCH, DELETE operations
  - Context manager support for proper resource cleanup
  - Cache statistics and management utilities

#### Phase 1.3 - Data Models & Validation (2025-01-20)

**Core Model Framework**
- Base Pydantic models for JSON API resources with full specification compliance
- ITGlueResource base class with attributes, relationships, links, and meta support
- ITGlueResourceCollection for handling paginated responses with metadata
- Generic type support for strongly-typed collections

**Field Types & Validation**
- Custom field types: ITGlueDateTime, ITGlueDate, ITGlueURL, ITGlueEmail, ITGluePhone, ITGlueSlug
- Field helpers: required_string(), optional_string(), itglue_id_field()
- Automatic validation and type conversion for ITGlue-specific data formats
- Support for both API field names (kebab-case) and Python properties (snake_case)

**Resource Models**
- Complete Organization model with 15+ properties and convenience methods
- Complete Configuration model with 20+ properties for IT asset management
- Property-based access with automatic API field name translation
- Relationship helpers for accessing linked resource IDs
- Convenience methods (is_active(), is_retired(), etc.)

**JSON API Compliance**
- ResourceType enumeration covering all 24+ ITGlue resource types
- ITGlueLinks for navigation and related resource URLs
- ITGlueMeta for pagination and timestamps with field aliasing
- ITGlueRelationship for resource relationships (to-one and to-many)
- Proper serialization/deserialization with from_api_dict() and to_api_dict()

**Collection Features**
- Type-safe collections with generic support
- Pagination helpers (has_next_page, current_page, total_count)
- Search and filtering methods (get_by_name, get_active_*, etc.)
- Included resource handling for JSON API side-loading

**Testing & Quality**
- 81 comprehensive model tests (100% pass rate)
- Property setter/getter validation
- API data format compatibility testing
- Collection manipulation and filtering tests
- Total test suite: 201 tests passing

### Technical Details
- `ITGlueHTTPClient`: Core HTTP client with tenacity-based retry logic
- `RateLimiter`: Simple rate limiting for API compliance
- `PaginationHandler`: JSON API pagination with automatic page iteration
- `CacheManager`: Pluggable caching with memory/Redis backends
- `ITGlueClient`: High-level client integrating all components
- Full test coverage across all components and error scenarios

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2025-06-20

### Added
- **Phase 1.1 - Foundation** 
  - Project structure and configuration management
  - ITGlue region support (US, EU, AU)
  - Environment variable configuration
  - Exception hierarchy for comprehensive error handling
  - Package infrastructure with proper imports
  - Initial test framework with pytest
  - Documentation structure (README, ERD, project plan)
  - Git repository initialization
  - Virtual environment setup

---

**Note**: This project follows [Semantic Versioning](https://semver.org/). Version numbers are assigned as follows:
- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner  
- **PATCH** version when you make backwards compatible bug fixes 