
[//]: # (DO NOT EDIT. README.md is generated by nbpages. Make changes to templates/README.md.jinja.)

# nbpages

nbpages is a command line tool for managing a collection of Jupyter notebooks published on
[Github Pages](https://pages.github.com/). This project was inspired by the tools included with the
[Python Data Science Handbook](https://github.com/jakevdp/PythonDataScienceHandbook) by
[Jake Vanderplas](https://github.com/jakevdp).

## Installation

    pip install nbpages

To upgrade a previously installed version to the latest version

    pip install nbpages --upgrade

## Setting up the notebook repository

The first step in publishing a collection of notebooks on Github Pages is to
[create a repository on Github.com](https://help.github.com/en/articles/creating-a-new-repository).
Github Pages are enabled under the settings tab for the repository. Scroll down to the Github Pages heading and select
`master branch` for the source. This is also a good time to select a theme for the published collection.

`nbpages` requires a local copy of the repository that can be created by cloning the remote repository.
Then from the command line, navigate to the top level directory of the local repository and issue the command

    nbpages --setup

Directories named `notebooks` and `templates` will be created if they do not already exist.  A configuration file
`config` will be created inside the directory using data read from the `.git`. Jinja templates `README.md.jinja` and
`notebook_header.jinja` willed created if they don't already exist. These templates can be edited as required
using data fields defined in `config`.

## Notebook organization

Notebooks are maintained within the `notebooks` directory. Thare are organized into a chapter/section heirarchy
using a filename prefix. Filenames have an `nn.mm-` prefix where`nn` refers to the chapter number or, if a letter, to
an Appendix. The digits `mm` refers to the section number. Section `00` is reserved to hold the chapter title and
any introductory material. The notebooks must also have the usual `.ipynb` suffix.

## Normal usage

Following setup, the normal use of `nbpages` is to execute the command line

    nbpages

from the top level directory of the notebook repository. Normally this command would be between completing edits or
additions to the notebooks and prior to a github commit. The command will

* add or amend headers and navigation bars in all notebooks,
* write a table of contents file
* write a keyword index
* write README.md using the template file

## Utilities

To help achieve a consistent style over a collection of notebooks, use the command

    nbpages --lint

to locate some forms of notebook 'lint'.  A current list of additional features can be found

    nbpages --help

[//]: # (The following template code is used to insert a list of notebook links.)


### [Table of Contents](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master//Users/jeff/Google Drive/GitHub/nbpages/notebooks-public//toc.ipynb?flush=true)

### [Keyword Index](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master//Users/jeff/Google Drive/GitHub/nbpages/notebooks-public//index.ipynb?flush=true)


### [Chapter 1.0 Style Guide](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master//Users/jeff/Google Drive/GitHub/nbpages/notebooks-public//01.00-Style-Guide.ipynb)


### [Chapter 2.0 Examples](http://nbviewer.jupyter.org/github/jckantor/nbpages/blob/master//Users/jeff/Google Drive/GitHub/nbpages/notebooks-public//02.00-Examples.ipynb)
