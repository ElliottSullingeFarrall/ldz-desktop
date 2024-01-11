from setuptools import setup, find_packages

with open('requirements.txt') as requirements:
    install_requires = requirements.read().splitlines()

setup(
    install_requires=install_requires,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={'ldz': ['images/*']},
    entry_points = {'console_scripts': ['ldz = ldz:main']}
)