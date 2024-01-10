from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='LDZ',
    version='1.3',
    author='ElliottSF',
    install_requires=[
        'pandas',
        'openpyxl'
        'appdirs'
    ],
    scripts=[
        'src/source.py',
        'src/utils.py'
    ],
    entry_points={
        # example: file some_module.py -> function main
        #'console_scripts': ['someprogram=some_module:main']
    }
)