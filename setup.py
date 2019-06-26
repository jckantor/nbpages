from setuptools import setup
"""
    python setup.py check
    python setup.py sdist
    twine upload dist/*
"""

setup(
    name = "nbpages",
    version = "0.0.1.dev7",
    packages=["nbpages", ],
    entry_points = {
        'console_scripts': [
            'nbpages = nbpages.__main__:main'
        ]
    },
    description = "Tools to maintain a respository of Jupyter notebooks",
    author = "jckantor",
    author_email = "Kantor.1@nd.edu",
    url = "https://github.com/jckantor/nbpages",

    license = "MIT",
    long_description = open("README.md").read(),
    long_description_content_type = "text/markdown",
)