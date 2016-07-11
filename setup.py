import os
from setuptools import setup, find_packages

version_file = open(os.path.join('jiraslacker', 'VERSION'))
version = version_file.read().strip()

setup(
    name='jiraslacker',
    version='0.1',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'Click',
        'Flask',
        'jira',
        'gevent',
        'PyStaticConfiguration',
        'PyYAML',
        'dataset',
        'requests-cache',
    ],
    entry_points='''
    [console_scripts]
    jiraslacker=jiraslacker.app:run
    '''
)
