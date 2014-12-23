#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    "requests",
    "lxml",
    "appindicator"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='zdsindicator',
    version='0.0.1',
    description='Un applet ubuntu pour le site Zeste de Savoir',
    long_description=readme + '\n\n' + history,
    author='poulp',
    author_email='mathieu.nerv@gmail.com',
    url='https://github.com/poulp/zdsindicator',
    packages=[
        'zdsindicator',
    ],
    package_dir={'zdsindicator':
                 'zdsindicator'},
    package_data= {'zdsindicator': ['icons/*.*']},
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='zdsindicator',
    scripts = ["bin/zdsindicator"],
)