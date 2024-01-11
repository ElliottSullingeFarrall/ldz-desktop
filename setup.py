from setuptools import setup

with open('requirements.txt') as requirements:
    install_requires = requirements.read().splitlines()

setup(
    name='LDZ',
    version='1.3',
    author='ElliottSF',
    package_dir={'': 'src'},
    package_data={'ldz': ['images/*']},
)