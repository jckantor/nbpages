import configparser
import os
from jinja2 import Environment, FileSystemLoader

### LOCAL DIRECTORY AND FILE LOCATIONS

# directory locations
CONFIG_DIR = os.path.join(os.getcwd(), 'config')
NOTEBOOK_DIR = os.path.join(os.getcwd(), 'notebooks/')
HTML_DIR = os.path.join(os.getcwd(), 'html'

# file locations
CONFIG_FILE = os.path.join(CONFIG_DIR, "config")
README_MD = os.path.join(os.getcwd(), 'README.md')
TOC_MD = os.path.join(NOTEBOOK_DIR, 'toc.md')
TOC_NB = os.path.join(NOTEBOOK_DIR, 'toc.ipynb')
INDEX_MD = os.path.join(NOTEBOOK_DIR, 'index.md')
INDEX_NB= os.path.join(NOTEBOOK_DIR, 'index.ipynb')

### READ CONFIGURATION FILE

# read configuration file
assert os.path.exists(CONFIG_FILE), CONFIG_FILE + " not found. "
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# extract configuration information
REPOSITORY = config['NBPAGES']['repository']
PAGE_TITLE = config['NBPAGES']['page_title']
PAGE_URL = config['NBPAGES']['page_url']
GITHUB_URL = config['NBPAGES']['github_url']

### CREATE STRING CONSTANTS

# tags
NOTEBOOK_HEADER_TAG = "<!--NOTEBOOK_HEADER-->"

# nbviewer/github url
NBVIEWER_URL = f"http://nbviewer.jupyter.org/github/{REPOSITORY}/blob/master/notebooks/"

# TOC and INDEX page headers with link to page url
TOC_HEADER = f"# [{PAGE_TITLE}]({PAGE_URL})"
INDEX_HEADER = f"# [{PAGE_TITLE}]({PAGE_URL})"

# headers for TOC and index pages with links to nbviewer/github
README_TOC = f"### [Table of Contents]({NBVIEWER_URL}toc.ipynb?flush=true)"
README_INDEX = f"### [Keyword Index]({NBVIEWER_URL}index.ipynb?flush=true)"

### CREATE STRING TEMPLATES

# link template to open notebooks in Google colaboratory
COLAB_LINK = f'<p><a href="https://colab.research.google.com/github/{REPOSITORY}' + \
             '/blob/master/notebooks/{notebook_filename}">' + \
             '<img align="left" src="https://colab.research.google.com/assets/colab-badge.svg"' + \
             ' alt="Open in Colab" title="Open in Google Colaboratory"></a>'

# link template to download notebooks from github
DOWNLOAD_LINK = f'<p><a href="https://raw.githubusercontent.com/{REPOSITORY}' + \
             '/master/notebooks/{notebook_filename}">' + \
             '<img align="left" src="https://img.shields.io/badge/Github-Download-blue.svg"' + \
             ' alt="Download" title="Download Notebook"></a>'

# navigation bar templates for notebook pages
NAVBAR_TAG = "<!--NAVIGATION-->\n"
PREV_TEMPLATE = "< [{title}]({url}) "
CONTENTS = "| [Contents](toc.ipynb) |"
INDEX = " [Index](index.ipynb) |"
NEXT_TEMPLATE = " [{title}]({url}) >"
