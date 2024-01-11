from setuptools import setup

with open('requirements.txt') as requirements:
    install_requires = requirements.read().splitlines()

setup(
    install_requires = install_requires,
    package_dir = {'': 'src'},
    package_data = {'ldz': ['images/*']},
    scripts = ['src/ldz/utils.py'],
    entry_points = {'console_scripts': ['ldz = ldz:main']}
)