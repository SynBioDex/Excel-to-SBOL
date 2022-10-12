#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:41:00 2020

@author: isapoetzsch
"""

from setuptools import find_packages, setup

setup(name='excel2sbol',
      version='1.0.0-alpha-9',
      url='https://github.com/SynBioDex/Excel-to-SBOL/',
      license='BSD 3-clause',
      maintainer='Jet Mante',
      maintainer_email='jet.mante@colorado.edu',
      include_package_data=True,
      description='convert excel resources into sbol',
      packages=find_packages(include=['excel2sbol']),
      long_description=open('README.md').read(),
      install_requires=['sbol2>=1.4.1',
                        'pandas>=1.0.1',
                        'numpy>=1.18.1',
                        'validators>=0.18.2',
                        'openpyxl>=3.0.7',
                        'tyto>=1.2',
                        'sbol3>=1.0.1',
                        'xlrd >= 1.0.0',
                        'excel_sbol_utils >= 1.0.42'],
      zip_safe=False)
