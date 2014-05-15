#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from plume import __version__
from setuptools import find_packages, setup


cmdclass = {}

# Check for Babel availability
try:
    from babel.messages.frontend import compile_catalog, extract_messages, init_catalog, update_catalog

    cmdclass.update({
        'compile_catalog': compile_catalog,
        'extract_messages': extract_messages,
        'init_catalog': init_catalog,
        'update_catalog': update_catalog,
    })
except ImportError:
    pass


# Get data files list
data_files = []

for root, dirs, files in os.walk('share'):
    data_files.append((os.path.join('share/plume', root[6:]), [os.path.join(root, x) for x in files]))


setup(
    name='plume',
    version=__version__,
    author='Vincent Batoufflet',
    author_email='vincent@batoufflet.info',
    license='BSD',
    url='https://github.com/vbatoufflet/plume/',
    description='A minimalist wiki solution',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    packages=find_packages(),
    data_files=data_files,
    scripts=[
        'scripts/plumectl',
    ],
    cmdclass=cmdclass,
    zip_safe=False,
    install_requires=[
        'argparse >= 1.1',
        'Flask >= 0.7',
        'Flask-Babel >= 0.7',
        'gunicorn >= 0.10',
        'misaka >= 1.0.0',
        'Pygments >= 1.3.1',
        'SQLAlchemy > 0.7.2',
        'Whoosh >= 2.4.1',
        'pyyaml >= 3.10',
    ],
)
