#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = '0.1'

import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-gazetteer',
    version = VERSION,
    description='Gazetteer builder for geo data environments with Linked Data support',
    packages=['gazetteer'],
    include_package_data=True,
    author='Rob Atkinson',
    author_email='rob@metalinkage.com.au',
    license='BSD',
    long_description=read('README.md'),
    download_url='git://github.com/rob-metalinkage/django-gazetteer.git',
    install_requires = ['django-skosxl>=0.1.0'
                        ],
    dependency_links = [
        'git://github.com/rob-metalinkage/django-skosxl.git#egg=skosxl',
    ],
    zip_safe=False

)

