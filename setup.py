#!/usr/bin/env python

import pathlib

from setuptools import setup, find_packages

from svelte_web_components.setup_node import setup_node

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

readme = pathlib.Path('README.md').read_text()

setup(
    author="Panos Stavrianos",
    author_email='panos@orbitsystems.gr',
    python_requires='>=3.6',
    description="Svelte web components for python",
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    setup_requires=[
        'requests',
    ],
    license="MIT license",
    include_package_data=True,
    keywords=['svelte', 'web components', 'python', 'fastapi', 'flask'],
    name='svelte_web_components',
    packages=find_packages(include=['svelte_web_components', 'svelte_web_components.*']),
    url='https://github.com/panos-stavrianos/svelte_web_components',
    version='{{VERSION_PLACEHOLDER}}',
    zip_safe=False,
    extras_require={
        'fastapi': ['fastapi', 'uvicorn', 'jinja2', 'starlette'],
    }
)
print("Setting up node...")
setup_node()
