# GitHub Workflows Documentation

This directory contains GitHub Actions workflows for continuous integration, deployment, and maintenance of the ITGlue Python SDK.

## Workflows Overview

### 🔄 CI Workflow (`ci.yml`)
**Trigger**: Push/PR to main or develop branches

**Purpose**: Comprehensive testing and quality assurance
- **Multi-platform testing**: Ubuntu, Windows, macOS
- **Multi-version support**: Python 3.10, 3.11, 3.12
- **Code quality**: Black formatting, flake8 linting, mypy type checking
- **Security**: Safety dependency checks, bandit security scanning
- **Coverage**: Test coverage reporting with Codecov integration

### 🚀 Release Workflow (`release.yml`) 
**Trigger**: Git tags (v*), GitHub releases, manual dispatch

**Purpose**: Automated PyPI package publishing
- **Build verification**: Package building and validation with twine
- **Version consistency**: Ensures git tag matches package version
- **Dual deployment**: 
  - TestPyPI for pre-releases (tags with `-` like `v1.0.0-beta1`)
  - PyPI for stable releases (tags without `-` like `v1.0.0`)
- **GitHub releases**: Automatic release creation with changelog extraction
- **Artifact management**: Build artifacts attached to releases

### ⏰ Scheduled Tests (`scheduled-tests.yml`)
**Trigger**: Weekly (Mondays 9:00 AM UTC), manual dispatch

**Purpose**: Proactive quality monitoring
- **Comprehensive testing**: Full test suite across all supported platforms
- **Performance benchmarks**: Client initialization and model creation timing
- **Memory monitoring**: Import memory usage tracking  
- **Security audits**: Regular safety, bandit, and semgrep scans
- **Integration testing**: Package installation and import verification

## Required Secrets

Configure these secrets in your GitHub repository settings:

### PyPI Publishing
- `PYPI_API_TOKEN`: PyPI API token for production releases
- `TEST_PYPI_API_TOKEN`: TestPyPI API token for pre-releases

### Optional Integrations
- `CODECOV_TOKEN`: For enhanced coverage reporting (optional)

## Release Process

### 1. Automatic Releases (Recommended)
```bash
# Create and push a release tag
git tag v1.0.0
git push origin v1.0.0
```

The release workflow will automatically:
- Build and test the package
- Publish to PyPI 
- Create a GitHub release with changelog
- Attach distribution files

### 2. Pre-release Testing
```bash
# Create a pre-release tag (includes dash)
git tag v1.0.0-beta1  
git push origin v1.0.0-beta1
```

This will publish to TestPyPI for testing before production release.

### 3. Manual Deployment
Use the "Actions" tab → "Release to PyPI" → "Run workflow" to manually trigger deployment to either TestPyPI or PyPI.

## Workflow Configuration

### Environment Protection
The workflows use GitHub environments for additional security:
- Production PyPI deployments require manual approval
- Environment-specific secrets and variables
- Deployment history and rollback capabilities

### Dependency Management
- **Dependabot**: Automated dependency updates (`.github/dependabot.yml`)
- **Security scanning**: Multiple tools for vulnerability detection
- **Version pinning**: Specific action versions for reproducibility

### Pre-commit Hooks
The repository includes pre-commit configuration (`.pre-commit-config.yaml`) that runs:
- Code formatting (Black, isort)
- Linting (flake8)
- Security checks (bandit)
- Type checking (mypy)
- Tests (pytest)

Install with:
```bash
pip install pre-commit
pre-commit install
```

## Monitoring and Notifications

### Success Indicators
- ✅ All CI checks pass
- ✅ Package successfully published to PyPI
- ✅ GitHub release created with artifacts
- ✅ Scheduled tests maintain green status

### Failure Handling
- 🔍 **CI failures**: Check logs for test failures, linting issues, or security problems
- 🚫 **Release failures**: Verify version consistency, secrets configuration, and package validity
- ⚠️ **Scheduled test failures**: Indicates potential regressions or environment issues

## Best Practices

1. **Version Management**: Always update version in `itglue/version.py` before tagging
2. **Changelog**: Update `CHANGELOG.md` following Keep a Changelog format
3. **Testing**: Ensure all tests pass locally before pushing
4. **Security**: Regular dependency updates via Dependabot
5. **Documentation**: Update docs for any API changes

## Troubleshooting

### Common Issues

**"Version mismatch" error**
- Ensure `itglue/version.py` version matches git tag
- Example: Tag `v1.0.0` should have version `"1.0.0"` in version.py

**PyPI upload failures**
- Check API token validity and permissions
- Verify package name availability on PyPI
- Ensure distribution files are valid (twine check)

**Test failures in CI but not locally**
- Check for platform-specific issues (Windows/macOS)
- Verify all dependencies are properly specified
- Review environment differences (Python version, dependencies)

For additional support, check the GitHub Actions logs and repository issues. 