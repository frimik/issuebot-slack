# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

version_file = open(os.path.join(os.path.dirname(__file__), 'src/jiraslacker', 'VERSION'))
version = version_file.read().strip()

setup(
    name='jiraslacker',
    version='0.1',
    include_package_data=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        '': ['*.yaml'],
    },
    install_requires=[
        'Click',
        'Flask',
        'jira',
        'gevent',
        'PyStaticConfiguration',
        'PyYAML',
        'requests-cache',
        'slacker',
        'Flask-SQLAlchemy',

    ],
    entry_points='''
    [console_scripts]
    jiraslacker=jiraslacker.app:run
    '''
)
