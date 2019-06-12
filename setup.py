from setuptools import setup
"""
    python setup.py check
    python setup.py sdist
    twine upload dist/*
"""

setup(
    name = "nbpages",
    version = "0.0.1.dev0",
    description = "Tools to maintain a respository of Jupyter notebooks",
    author = "jckantor",
    author_email = "Kantor.1@nd.edu",
    url = "https://github.com/jckantor/nbpages",
    packages = ["nbpages", ],
    license = "MIT",
    long_description = open("README.md").read(),
    long_description_content_type = "text/markdown",
)