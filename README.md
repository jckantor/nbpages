
[//]: # (The README.md is produced automatically by nbpages. Make changes by edittin templates/README.md.jinja.)
# nbpages

nbpages provides a Python toolset for managing a github repository of Jupyter notebooks. The project was
inspired by the tools included with the
[Python Data Science Handbook](https://github.com/jakevdp/PythonDataScienceHandbook) by
[Jake Vanderplas](https://github.com/jakevdp).

## Installation

    pip install nbpages

## Usage

This package assumes you have already created a github repository containing one or more Jupyter notebooks in a
subdirectory named `notebooks`. The notebook files end with a `.ipynb` suffix, and begin with a `nn.mm-` prefix.
`nn` refers to the chapter number or, if a letter, to an Appendix.  `mm` refers to section number. Section `00`
includes the chapter title and any prefatory material.

To use, execute the command line

    python nbpages

from the top level directory of the notebook repository. The initial use of this command will:

1. Create a directory named `templates` with configuration data found in the `.git` subdirectory, and jinja
templates for a README.md file and notebook headers. The templates may be edited and include any variable from
the configuration file.
2. Create `README.md` using the template `README.md.jinja`. The default template includes a formatted list of all
notebooks in the respository.
3. Add headers and navigation bars in all notebooks. The headers can be modified by the editing
`notebook_header.jinja` template.
4. Create a table of contents and a keyword index accessible from README.md and the navigation bars.


### [Table of Contents](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/toc.ipynb?flush=true)

### [Keyword Index](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/index.ipynb?flush=true)


### [Chapter 1.0 Getting Started with nbcollection](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.00-Getting-Started-with-nbcollection.ipynb)

- [1.1 Notebook Repository Layout](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.01-Notebook-Repository-Layout.ipynb)

- [1.2 Configuration](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/01.02-Configuration.ipynb)


### [Appendix A. Style Guide](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master/notebooks/A.00-Style-Guide.ipynb)
