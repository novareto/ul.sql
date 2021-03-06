# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(
        os.path.join(
            os.path.join(os.path.dirname(__file__), 'docs'),
            *rnames)).read()

version = '0.2.2.dev0'
long_description = read('README.txt') + '\n' + read('HISTORY.txt')

install_requires = [
     "cromlech.sqlalchemy",
     "dolmen.sqlcontainer",
     "setuptools",
     "sqlalchemy-imageattach",
     "transaction",
     "ul.browser",
    ]

tests_require = [
    ]

setup(
    name='ul.sql',
    version=version,
    author='Novareto GmbH',
    author_email='',
    url='http://www.novareto.de',
    download_url='http://pypi.python.org/pypi/ul.sql',
    description='SQL components for uvclight',
    long_description=long_description,
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['ul'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require
        },
    )
