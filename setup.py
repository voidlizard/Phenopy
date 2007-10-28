#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import phenopy

setup(
    name = 'phenopy',
    version = phenopy.__version__,
    url = '',
    download_url = '',
    license = phenopy.__license__,
    author = 'Dmitry Zuikov',
    author_email = 'dmz@phenopy.net',
    description = 'Misc stuffs',
    long_description = phenopy.__doc__,
    keywords = 'wsgi web sql postgres aop',
    packages = ['phenopy',
                'phenopy.aop', 
                'phenopy.decorators',
                'phenopy.misc',
                'phenopy.sql',
                'phenopy.webutils',
                'phenopy.webutils.xslt',
                'phenopy.webutils.xml',
                'phenopy.xml_tools'],
    platforms = 'any',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: %s' % phenopy.__license__,
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
