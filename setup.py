from setuptools import setup, find_packages
import os

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get version from version file
with open(os.path.join(here, "itglue", "version.py"), encoding="utf-8") as f:
    exec(f.read())

setup(
    name="py-itglue",
    version=__version__,
    description="Comprehensive Python SDK for ITGlue API with AI agent capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/py-itglue",
    author="Your Organization",
    author_email="contact@yourorg.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="itglue api sdk documentation management",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.2",
        "urllib3>=2.0.0",
        "aiohttp>=3.8.0",
        "asyncio-throttle>=1.0.0",
        "redis>=4.5.0",
        "cachetools>=5.3.0",
        "tenacity>=8.2.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "structlog>=23.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.1.0",
        ],
        "testing": [
            "responses>=0.23.0",
            "factory-boy>=3.3.0",
            "faker>=19.3.0",
        ],
        "performance": [
            "uvloop>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "itglue-cli=itglue.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-org/py-itglue/issues",
        "Source": "https://github.com/your-org/py-itglue",
        "Documentation": "https://py-itglue.readthedocs.io/",
    },
)
