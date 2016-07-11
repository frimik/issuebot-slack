from setuptools import setup, find_packages


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
    jiraslacker=jiraslacker:run
    '''
)
