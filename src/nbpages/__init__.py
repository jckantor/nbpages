"""Manage a Collection of Jupyter Notebooks
"""
from .index import Index
from .nbcollection import Nb, NbCollection
from .nbsetup import nbsetup, make_dir_if_needed, write_template_if_needed
