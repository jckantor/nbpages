
[//]: # (The README.md is produced automatically by nbpages. Make changes by edittin templates/README.md.jinja.)
# nbpages

nbpages provides a Python toolset for managing a github repository of Jupyter notebooks. The project was
inspired by the tools included with the
[Python Data Science Handbook](https://github.com/jakevdp/PythonDataScienceHandbook) by
[Jake Vanderplas](https://github.com/jakevdp).

## Installation

    pip install nbpages

## Initial Setup

This package assumes you have created a github repository containing one or more Jupyter notebooks (*.ipynb) in a
subdirectory named `notebooks`. The initial setup is performed with the command

    python nbpages --setup

This creates a directory named `templates` if needed with configuration data found in the `.git` subdirectory. If not
already present, Jinja templates `README.md.jinja` and `notebook_header.jinja` are created. These templates should be
edited as required.

## Normal Usage

Notebooks filenames are prefixed with `nn.mm-` where`nn` refers to the chapter number or, if a letter, to an Appendix.
mm` refers to the section number. Section `00` the chapter title and any prefatory material.

To use, execute the command line

    python nbpages

from the top level directory of the notebook repository. The command will add or amend headers and navigation bars in
all notebooks, and create a table of contents and a keyword index accessible from README.md and the navigation bars.

## Utilities

To help achieve a consistent style over a collection of notebooks, use the command

    python nbpages --lint

to locate some forms of notebook 'lint'.  A current list of additional features can be found

    python nbpages --help



### [Table of Contents](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/toc.ipynb?flush=true)

### [Keyword Index](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/index.ipynb?flush=true)


### [Chapter 1.0 Getting Started with nbcollection](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.00-Getting-Started-with-nbcollection.ipynb)

- [1.1 Notebook Repository Layout](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.01-Notebook-Repository-Layout.ipynb)

- [1.2 Configuration](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.02-Configuration.ipynb)


### [Appendix A. Style Guide](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/A.00-Style-Guide.ipynb)
