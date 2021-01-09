from setuptools import setup, find_packages

setup(
    name = 'FINDINGCHART',
    author = 'Simon Holmbo',
    packages = find_packages(),
    entry_points = {
        'console_scripts' : ['findingchart = findingchart.findingchart:main'],
    },
    include_package_data = True,
)
