"""Minimal setup.py shim for tools that do not support PEP 517/518.

All metadata and build configuration lives in pyproject.toml.
Install the package with:

    pip install .                   # runtime only
    pip install .[gui]              # with Flask GUI
    pip install .[dev]              # development tooling
    pip install -r requirements.txt # via requirements file
"""

from setuptools import setup

setup()
