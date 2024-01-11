from setuptools import setup

with open('requirements.txt') as requirements:
    install_requires = requirements.read().splitlines()

setup(
    install_requires=install_requires,
    packages=[
        'ldz'
    ],
    package_dir={
        'ldz': 'src'
    },
    package_data={
        'ldz': ['images/*']
    },
    entry_points = {
        'console_scripts': ['ldz = src.__init__:main']
    }
)