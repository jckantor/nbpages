import os
import configparser
import datetime
import shutil

# DIRECTORY AND FILE LOCATIONS
TEMPLATE_DIR = "templates"
NOTEBOOK_SRC_DIR = "notebooks-dev"
NOTEBOOK_DST_DIR = "notebooks-public"
NOTEBOOK_DOWNLOAD_DIR = "docs"
HTML_DIR = "docs"

CONFIG_FILE = "nbpages.cfg"
README_MD = "README.md"

INDEX_MD = "index.md"
INDEX_NB = "index.ipynb"
INDEX_HTML = "index.html"

TOC_MD = os.path.join(HTML_DIR, "toc.md")
TOC_NB = os.path.join(HTML_DIR, "toc.ipynb")
TOC_HTML = os.path.join(HTML_DIR, "toc.html")

TAG_INDEX_MD = os.path.join(HTML_DIR, "tag_index.md")
TAG_INDEX_NB = os.path.join(HTML_DIR, "tag_index.ipynb")
TAG_INDEX_HTML = os.path.join(HTML_DIR, "tag_index.html")

# THERE SHOULD BE NO NEED TO EDIT ANYTHING BELOW THIS LINE

# read .git config to extract url, user, and page_title
assert os.path.exists('.git'), ".git subdirectory not found. "
git_config = configparser.ConfigParser(strict=False)
git_config.read(os.path.join(".git", "config"))

GITHUB_URL = git_config['remote "origin"']['url']
GITHUB_USER = GITHUB_URL.rsplit('/')[-2]
PAGE_TITLE = GITHUB_URL.rsplit('/')[-1].split('.')[0]
GITHUB_REPOSITORY = f"{GITHUB_USER}/{PAGE_TITLE}"
GITHUB_PAGE_URL = f"https://{GITHUB_USER}.github.io/{PAGE_TITLE}"

# CREATE STRING CONSTANTS

# tags
NOTEBOOK_HEADER_TAG = "<!--NOTEBOOK_HEADER-->"

# nbviewer/github url
NBVIEWER_URL = f"https://nbviewer.jupyter.org/github/{GITHUB_REPOSITORY}/blob/master/{NOTEBOOK_DST_DIR}/"

# TOC and INDEX page headers with link to page url
TOC_HEADER = f"# [{PAGE_TITLE}]({GITHUB_PAGE_URL})"
TAG_INDEX_HEADER = f"# [{PAGE_TITLE}]({GITHUB_PAGE_URL})"

# headers for TOC and index pages with links to nbviewer/github
INDEX_TOC = f"### [Table of Contents]({GITHUB_PAGE_URL}/toc.html?flush=true)"
INDEX_INDEX = f"### [Tag Index]({GITHUB_PAGE_URL}/tag_index.html?flush=true)"

# CREATE STRING TEMPLATES

# link template to open notebooks in Google colaboratory
COLAB_LINK = f'<p><a href="https://colab.research.google.com/github/{GITHUB_REPOSITORY}/blob/master/{NOTEBOOK_DST_DIR}' + \
             '/{notebook_filename}"> <img align="left" src="https://colab.research.google.com/assets/colab-badge.svg"' + \
             ' alt="Open in Colab" title="Open in Google Colaboratory"></a>'

# link template to download notebooks from github
DOWNLOAD_LINK = f'<p><a href="https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/master/{NOTEBOOK_DOWNLOAD_DIR}' +  \
             '/{notebook_filename}"> <img align="left" src="https://img.shields.io/badge/Github-Download-blue.svg"' + \
             ' alt="Download" title="Download Notebook"></a>'

# navigation bar templates for notebook pages
NAVBAR_TAG = "<!--NAVIGATION-->\n"
PREV_TEMPLATE = "< [{title}]({url}) "
CONTENTS = "| [Contents](toc.html) |"
INDEX = " [Tag Index](tag_index.html) |"
NEXT_TEMPLATE = " [{title}]({url}) >"
