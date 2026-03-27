#!/usr/bin/env python3
"""CIEL/Ω Quantum Consciousness Suite — Package setup."""

from setuptools import find_packages, setup

setup(
    name="ciel-omega",
    version="2.0.0",
    packages=find_packages(exclude=["ext", "ext.*"]),
    install_requires=["numpy", "scipy", "matplotlib", "networkx", "sympy"],
    entry_points={
        "console_scripts": [
            "ciel-engine=ciel.cli:run_engine",
            "ciel-smoke=ciel.cli:smoke_test",
        ]
    },
    description="CIEL/Ω — Consciousness-Integrated Emergent Logic (full pipeline)",
    author="Adrian Lipa / Intention Lab",
    license="CIEL-Research-NonCommercial-1.1",
    python_requires=">=3.10",
)
