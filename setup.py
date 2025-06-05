"""SEC EDGAR client package setup."""
from setuptools import setup, find_packages

setup(
    name="sec-edgar-via-mcp",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.23.0"
    ]
)