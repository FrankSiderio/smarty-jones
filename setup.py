"""Setup for Smarty Jones - Minimal Version"""

from setuptools import setup, find_packages

setup(
    name="smarty-jones",
    version="0.1.0",
    description="Minimal debugging assistant with AI-powered error analysis",
    author="Smarty Jones Team", 
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[],  # No dependencies!
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)