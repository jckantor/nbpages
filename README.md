# nbcollection

nbcollection is a tool for managing a repository of Jupyter notebooks that comprise a book,
course, or other form of large project. It was inspired by the tools included with the
[Python Data Science Handbook](https://github.com/jakevdp/PythonDataScienceHandbook) by
[Jake Vanderplas](https://github.com/jakevdp).

## Dependencies

* [notedown](https://github.com/aaren/notedown)

## Notebook Repository Layout

    My-Amazing-Course/
    |
    |--- notebooks/
    |.   |--- figures/
    |    |--- 00.00-Preface.ipyb
    |    |--- 01.00-My-First-Chapter.ipynb
    |    |--- 01.01-My-First-Chapter-First-Section.ipynb
    |    |--- A.00-My-Appendix.ipynb
    |
    |--- _config.yml
    |--- .gitignore
    |--- LICENSE-code.txt
    |--- LICENSE-text.txt
    |--- README.md
    |--- templates/
         |--- nbviewer_url.txt          # nbviewer viewer base url
         |--- notebook_header.txt
         |--- page_title.txt
         |--- page_url.txt
         |--- README.md.jinja
         |--- repository.txt
         |--- repository_url.txt


### [Table of Contents](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/toc.ipynb?flush=true)

### [Keyword Index](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/index.ipynb?flush=true)


### [Appendix B. The Temperature Control Laboratory](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.00-TCLab.ipynb)

- [B.1 The TCLab Python Package](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.01-The-TCLab-Python-Package.ipynb)

- [B.2 Relay Control](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.02-Relay-Control.ipynb)

- [B.3 Step Testing](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.03-Step-Testing.ipynb)

- [B.4 Fitting Step Test Data to Empirical Models](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.04-Fitting-Step-Test-Data-to-Empirical-Models.ipynb)

- [B.5 First Order Model for a Single Heater](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.05-First-Order-Model-for-a-Single-Heater.ipynb)

- [B.6 Two-Input, Two-Output Model](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.06-Two-Input-Two-Output-Model.ipynb)

- [B.7 Two State Model for a Single Heater](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.07-Two-State-Model-for-a-Single-Heater.ipynb)

- [B.8 Four State Model](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.08-Four-State-Model.ipynb)

- [B.9 PID Control](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.09-PID_Control.ipynb)

- [B.10 Lab Assignment: PID Control](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.10-Lab-Assignment-PID-Control.ipynb)

- [B.11 Coding Controllers with Python Generators](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.11-Coding-Controllers-with-Python-Generators.ipynb)

- [B.12 Open and Closed Loop Estimation](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.12-Open-and-Closed-Loop-Estimation.ipynb)

- [B.13 Simulation, Control, and Estimation using Pyomo](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.13-Optimization-Control-and-Estimation-using-Pyomo.ipynb)

- [B.14 Simulation, Control, and Estimation using Pyomo](http://nbviewer.jupyter.org/github/jckantor/nbcollection/blob/master/notebooks/B.14-Optimization-Control-and-Estimation-using-Pyomo-With-Windows-ipopt.ipynb)
