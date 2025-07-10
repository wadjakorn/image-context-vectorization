#!/usr/bin/env python3
"""
Setup script for Image Context Extractor
"""
from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from package
def get_version():
    version_file = os.path.join("src", "image_context_extractor", "__init__.py")
    with open(version_file, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="image-context-extractor",
    version=get_version(),
    author="Image Context Extractor Team",
    author_email="contact@example.com",
    description="A tool for extracting contextual information from images and storing them in a vector database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/image-context-extractor",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    # CLI entry point removed - CLI functionality deprecated
    # entry_points={
    #     "console_scripts": [
    #         "image-context-extractor=image_context_extractor.cli:main",
    #     ],
    # },
    include_package_data=True,
    zip_safe=False,
)