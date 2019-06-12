
[//]: # (The README.md is produced automatically by nbpages. Make changes by edittin templates/README.md.jinja.)
# nbpages

nbpages provides a Python toolset for managing a github repository of Jupyter notebooks. The project was
inspired by the tools included with the
[Python Data Science Handbook](https://github.com/jakevdp/PythonDataScienceHandbook) by
[Jake Vanderplas](https://github.com/jakevdp).

## Installation

    pip install nbpages

## Usage

This package assumes you have already created one or more Jupyter notebooks in a `notebooks` subdirectory. The notebook
file names must be prefaced by an 'dd.dd-' prefix indicating chapter and section numbering.  The direcortory should
published as a github repository.

To use, execute the command line

    python nbpages

from the top level directory of the notebook repository. The will create a directory containing configuration data and
templates for a README.md file and notebook headers.


### [Table of Contents](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/toc.ipynb?flush=true)

### [Keyword Index](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/index.ipynb?flush=true)


### [Chapter 1.0 Getting Started with nbcollection](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.00-Getting-Started-with-nbcollection.ipynb)

- [1.1 Notebook Repository Layout](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.01-Notebook-Repository-Layout.ipynb)

- [1.2 Configuration](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.02-Configuration.ipynb)


### [Appendix A. Style Guide](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/A.00-Style-Guide.ipynb)
