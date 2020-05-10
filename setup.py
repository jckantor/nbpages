from setuptools import setup
"""
    python setup.py check
    python setup.py sdist
    twine upload dist/*
    then update version number in the development branch
    
    packaged following recommendations in https://github.com/yngvem/python-project-structure
"""

setup(
    entry_points = {
        'console_scripts': [
            'nbpages = nbpages.__main__:main'
        ]
    },
)