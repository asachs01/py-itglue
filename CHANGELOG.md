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