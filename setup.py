from setuptools import setup

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    install_requires=install_requires,
    package_dir={'': 'src'},
    package_data={'ldz': ['images/*']}
)