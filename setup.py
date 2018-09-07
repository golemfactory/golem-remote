from setuptools import setup

setup(name='golem_remote',
    version='0.1',
    description='The MVP for wrapping functions to run on Golem',
    url='http://github.com/inexxt/golem_remote',
    author='inexxt',
    author_email='jacek@golem.network',
    license='MIT',
    packages=['golem_remote'],
    zip_safe=False,
    install_requires=[
        'redis',
        'cloudpickle'
    ],
    include_package_data=True
)
