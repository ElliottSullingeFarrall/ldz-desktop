from setuptools import setup

with open('requirements.txt') as requirements:
    install_requires = requirements.read().splitlines()

setup(
    package_dir={'': 'src'},
    package_data={'ldz': ['images/*']}
)