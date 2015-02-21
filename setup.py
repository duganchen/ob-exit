#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "ob-exit",
    version = "1.0",
    packages = find_packages(),
    entry_points={
        'console_scripts': 'ob-exit = ob_exit.ob_exit'
    }
)
