# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in procurement_customized/__init__.py
from procurement_customized import __version__ as version

setup(
	name='procurement_customized',
	version=version,
	description='Ledger customizations',
	author='Greycube',
	author_email='info@greycube.in',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
