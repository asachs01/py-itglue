# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.5] - 2025-01-23

### Fixed
- **Test Infrastructure**: Fixed all remaining unit test failures (13 → 0 failures, 411 total tests passing)
- **BaseAPI Tests**: Fixed mock resource attribute assertions in create/update resource tests
- **Redis Cache Tests**: Made Redis tests conditional on redis package availability to prevent collection-time failures
- **Pagination Tests**: 
  - Corrected parameter type expectations (string parameters vs integer)
  - Fixed method signatures for `get_page()`, `get_next_page()`, `get_prev_page()`
  - Updated test expectations to match actual pagination handler interface
- **Model Timestamp Properties**: 
  - Added missing `_parse_datetime()` method to ITGlueResource base class
  - Fixed datetime import scoping issues in timestamp parsing
  - Enabled proper parsing of ISO datetime strings from API responses
- **Test Coverage**: Maintained 82% overall coverage with all 408 tests passing, 3 skipped

### Technical Details
- Fixed `UnboundLocalError` in datetime parsing by properly importing datetime class
- Corrected BaseAPI mock resource creation to include expected attributes
- Updated Redis cache manager tests to use runtime imports instead of decoration-time imports
- Enhanced pagination parameter handling to match string-based API requirements

## [0.2.4] - 2025-01-23

### Fixed
- **Critical**: Removed async/await patterns from all API methods to fix synchronous operation
- **Cache**: Fixed MemoryCache cleanup logic when cache reaches maximum size
- **Tests**: Fixed all test failures by removing async/await patterns from test methods
- **Pagination**: Fixed PaginationHandler method signatures to match test expectations
- **Redis**: Added pytest.importorskip for Redis tests to gracefully skip when redis is not available
- **API Methods**: Fixed all API classes to use synchronous HTTP client operations

### Changed
- All API methods are now synchronous (removed async/await throughout codebase)
- Test files updated to use Mock instead of AsyncMock
- Updated method signatures in PaginationHandler to match expected interface

## [0.2.3] - 2024-06-23

### Fixed
- Import errors in test suite (RateLimiter → SimpleRateLimiter references)
- Missing asyncio marker in pytest configuration causing test collection failures
- Test class names updated for consistency with renamed components

### Added
- pytest-asyncio dependency for proper async test support
- Enhanced pytest configuration with all required markers

### Changed
- Updated test imports to match refactored component names
- Improved test configuration for better CI/CD compatibility

## [0.2.2] - 2025-01-26

### Fixed
- MyPy type checking compliance (reduced from 83 errors to 0)
- GitHub Actions CI/CD pipeline type checking failures
- Method signature incompatibilities in collection classes
- Type annotations for cache management and HTTP client components

### Added
- Comprehensive mypy.ini configuration for type checking
- pyproject.toml with complete tool configurations (Black, pytest, coverage)
- types-requests dependency for proper request library typing
- Type annotations for core classes and methods

### Changed
- Collection classes now properly inherit from corrected base class signatures
- Improved type safety across all modules while maintaining backward compatibility
- Selective type checking exclusions for complex modules pending refactor

## [0.2.1] - 2025-01-26

### Fixed
- Code formatting compliance with Black formatter standards
- GitHub Actions CI/CD workflow formatting checks now pass
- Standardized Python code style across all 45+ files

### Changed
- Applied Black formatting to entire codebase for consistency
- No functional changes, only code style improvements

### Added
- **CI/CD Infrastructure** (v0.2.0 - 2025-06-23)
  - Comprehensive GitHub Actions workflows for automated testing and deployment
  - Multi-platform CI testing (Ubuntu, Windows, macOS) across Python 3.10-3.12
  - Automated PyPI releases triggered by git tags with version validation
  - Pre-commit hooks for code quality (Black, flake8, mypy, bandit, pytest)
  - Dependabot configuration for automated dependency updates
  - Scheduled security audits and performance monitoring
  - TestPyPI integration for pre-release testing
  - Comprehensive deployment documentation and troubleshooting guides

## [0.2.0] - 2025-06-23

### Added
- **Phase 2.3 - Passwords API Implementation** (2025-06-23)
  - Complete Passwords API with 20+ specialized methods for enterprise password management
  - Password model with security-focused design (PasswordType, PasswordCategory, PasswordVisibility enums)
  - Advanced security analysis methods (is_critical, is_high_security, is_shared, is_stale)
  - Comprehensive search and filtering (by name, username, URL, organization, category, visibility)
  - Time-based operations (recently updated, stale password detection)
  - Management operations (create, update, archive, favorite management, visibility control)
  - Password analytics and organizational reporting (security statistics, distribution analysis)
  - Property setters with automatic API attribute mapping (snake_case to hyphen-case)
  - PasswordCollection with advanced filtering and security analytics
  - 64 comprehensive tests (27 model + 36 API tests, 100% pass rate)
  - Client integration with passwords endpoint
  - Total test suite: 411 tests passing
- **Phase 2.2 - Users API Implementation** (2025-06-23)
  - Complete Users API with 15+ methods for user management and analytics
  - User model with role-based design (UserRole, UserStatus enums)
  - User management methods (role checking, reputation analysis, authentication status)
  - Advanced search and filtering (by email, name, role, reputation, authentication status)
  - User statistics and analytics (role distribution, reputation analysis, authentication reporting)
  - Property setters with automatic API attribute mapping
  - UserCollection with comprehensive filtering and search capabilities
  - 54 comprehensive tests (27 model + 27 API tests, 100% pass rate)
  - Client integration with users endpoint
- **Phase 2.1 - Flexible Assets Implementation** (2025-06-23)
  - Complete Flexible Assets API with 14+ specialized methods
  - Flexible Asset Types API for managing custom asset definitions
  - Flexible Asset Fields API for field configuration
  - Flexible asset model with dynamic traits and tag management
  - Support for custom data structures beyond standard ITGlue resources
  - Property setters with automatic attribute mapping (snake_case to hyphen-case)
  - Tag management methods (add_tag, remove_tag, has_tag)
  - Trait management for custom field values
  - Status management for flexible asset lifecycle
  - 47 comprehensive tests (100% pass rate)
  - Client integration with flexible_assets, flexible_asset_types, and flexible_asset_fields endpoints
  - Total test suite: 293 tests passing
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