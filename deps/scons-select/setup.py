# -*- coding: utf-8 -*-

from setuptools import setup

setup(
        name='scons-select',
        version='1.0',
        install_requires=[
            'scons>=3.0.1; python_version>="3"',
            'scons>=3.0.1,<3.1; python_version<"3"'
        ],
        description='Selects appropriate SCons version for python2/python3',
)

# vim: set expandtab tabstop=4 shiftwidth=4:
