import os
import configparser
import datetime
import shutil

### LOCAL DIRECTORY AND FILE LOCATIONS

# directory locations
TEMPLATE_DIR = os.path.join(os.getcwd(), 'templates/')
NOTEBOOK_SRC_DIR = 'notebooks_dev'
NOTEBOOK_DST_DIR = 'notebooks_public'

NOTEBOOK_SRC = os.path.join(os.getcwd(), NOTEBOOK_SRC_DIR)
NOTEBOOK_DST = os.path.join(os.getcwd(), NOTEBOOK_DST_DIR)

# file locations
CONFIG_FILE = os.path.join(os.getcwd(), "nbpages.cfg")
README_MD = os.path.join(os.getcwd(), 'README.md')

# table of contents and index files
TOC_MD = os.path.join(NOTEBOOK_DST, 'toc.md')
TOC_NB = os.path.join(NOTEBOOK_DST, 'toc.ipynb')
INDEX_MD = os.path.join(NOTEBOOK_DST, 'index.md')
INDEX_NB= os.path.join(NOTEBOOK_DST, 'index.ipynb')

### THERE SHOULD BE NO NEED TO EDIT ANYTHING BELOW THIS LINE

# read .git config to extract url, user, and page_title

assert os.path.exists('.git'), ".git subdirectory not found. "
git_config = configparser.ConfigParser(strict=False)
git_config.read(os.path.join(".git", "config"))

GITHUB_URL = git_config['remote "origin"']['url']
GITHUB_USER = GITHUB_URL.rsplit('/')[-2]
PAGE_TITLE = GITHUB_URL.rsplit('/')[-1].split('.')[0]
GITHUB_REPOSITORY = f"{GITHUB_USER}/{PAGE_TITLE}"
GITHUB_PAGE_URL = f"https://{GITHUB_USER}.github.io/{PAGE_TITLE}"

### CREATE STRING CONSTANTS

# tags
NOTEBOOK_HEADER_TAG = "<!--NOTEBOOK_HEADER-->"

# nbviewer/github url
NBVIEWER_URL = f"https://nbviewer.jupyter.org/github/{GITHUB_REPOSITORY}/blob/master/{NOTEBOOK_DST_DIR}/"

# TOC and INDEX page headers with link to page url
TOC_HEADER = f"# [{PAGE_TITLE}]({GITHUB_PAGE_URL})"
INDEX_HEADER = f"# [{PAGE_TITLE}]({GITHUB_PAGE_URL})"

# headers for TOC and index pages with links to nbviewer/github
README_TOC = f"### [Table of Contents]({NBVIEWER_URL}toc.ipynb?flush=true)"
README_INDEX = f"### [Keyword Index]({NBVIEWER_URL}index.ipynb?flush=true)"

### CREATE STRING TEMPLATES

# link template to open notebooks in Google colaboratory
COLAB_LINK = f'<p><a href="https://colab.research.google.com/github/{GITHUB_REPOSITORY}/blob/master/{NOTEBOOK_DST_DIR}' + \
             '/{notebook_filename}"> <img align="left" src="https://colab.research.google.com/assets/colab-badge.svg"' + \
             ' alt="Open in Colab" title="Open in Google Colaboratory"></a>'

# link template to download notebooks from github
DOWNLOAD_LINK = f'<p><a href="https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/master/{NOTEBOOK_DST_DIR}' +  \
             '/{notebook_filename}"> <img align="left" src="https://img.shields.io/badge/Github-Download-blue.svg"' + \
             ' alt="Download" title="Download Notebook"></a>'

# navigation bar templates for notebook pages
NAVBAR_TAG = "<!--NAVIGATION-->\n"
PREV_TEMPLATE = "< [{title}]({url}) "
CONTENTS = "| [Contents](toc.ipynb) |"
INDEX = " [Index](index.ipynb) |"
NEXT_TEMPLATE = " [{title}]({url}) >"
