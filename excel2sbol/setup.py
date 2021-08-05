#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:41:00 2020

@author: isapoetzsch
"""

from setuptools import find_packages, setup

setup(name='excel2sbol',
      version='1.0.0-alpha-9',
      url='https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol',
      license='BSD 3-clause',
      maintainer='Tramy Nguyen',
      maintainer_email='tramy.nguy@gmail.com',
      description='convert excel resources into sbol',
      packages=find_packages(include=['utils']),
      long_description=open('README.md').read(),
      install_requires=['sbol2>=1.0b8',
                        'pandas>=1.0.1',
                        'numpy>=1.18.1',
                        'xlrd >= 1.0.0'],
      zip_safe=False)
