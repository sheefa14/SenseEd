#!/usr/bin/env python3
"""
Setup script for SenseEd - Multimodal AI Learning Assistant
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="senseed",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multimodal AI Learning Assistant for Accessible Education",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/senseed",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        "gui": [
            "PyQt5>=5.15.0",
            "kivy>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "senseed=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt", "*.md"],
    },
    keywords=[
        "ai", "assistant", "education", "accessibility", "multimodal",
        "speech", "vision", "nlp", "learning", "chatbot", "ocr",
        "gesture-recognition", "text-to-speech", "computer-vision"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/senseed/issues",
        "Source": "https://github.com/your-username/senseed",
        "Documentation": "https://github.com/your-username/senseed#readme",
    },
)



