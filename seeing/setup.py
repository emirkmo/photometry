from setuptools import setup, find_packages

setup(
    name = 'SEEING',
    author = 'Simon Holmbo',
    packages = find_packages(),
    entry_points = {
        'console_scripts' : ['seeing = seeing.seeing:main'],
    },
    include_package_data = True,
)
