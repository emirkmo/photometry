from setuptools import setup, find_packages

setup(
    name = 'WCSINTERACTIVE',
    author = 'Simon Holmbo',
    packages = find_packages(),
    entry_points = {
        'console_scripts' : ['wcsinteractive = wcsinteractive.wcsinteractive:main'],
    },
    include_package_data = True,
)
