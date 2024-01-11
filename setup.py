from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='LDZ',
    version='1.3',
    author='ElliottSF',
    scripts=[
        'src/source.py',
        'src/utils.py'
    ],
    include_package_data=True,
    package_data={'': ['src/images/*']},
    entry_points={
        # example: file some_module.py -> function main
        #'console_scripts': ['someprogram=some_module:main']
    }
)