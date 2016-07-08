from setuptools import setup, find_packages


setup(
    name='eajiraslacker',
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
    ],
    entry_points='''
    [console_scripts]
    eajiraslacker=eajiraslacker:serve
    '''
)
