from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='LDZ',
    version='1.3',
    author='ElliottSF',
    install_requires=[
        'tkcalendar==1.6.1',
        'pandas==2.1.4',
        'openpyxl==3.1.2',
        'appdirs==1.4.4'
    ],
    python_requires='==3.10.12',
    scripts=[
        'src/source.py',
        'src/utils.py'
    ],
    entry_points={
        # example: file some_module.py -> function main
        #'console_scripts': ['someprogram=some_module:main']
    }
)