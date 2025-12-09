"""
Setup configuration for Tetris Ultimate Edition
"""

import os

from setuptools import find_packages, setup

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tetris-ultimate",
    version="1.0.0",
    author="GitHub Copilot",
    author_email="",
    description="A modern Tetris game with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tetris-ultimate",
    packages=find_packages(),
    py_modules=["tetris"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pygame>=2.6.0",
    ],
    entry_points={
        "console_scripts": [
            "tetris=tetris:main",
        ],
    },
    keywords="tetris game puzzle pygame",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/tetris-ultimate/issues",
        "Source": "https://github.com/yourusername/tetris-ultimate",
    },
)
