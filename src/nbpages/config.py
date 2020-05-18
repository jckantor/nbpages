import os
import datetime
from pathlib import Path
import shutil
import configparser

# DIRECTORY AND FILE NAMES
TEMPLATE_DIR = "templates"
NOTEBOOK_SRC_DIR = "notebooks"
CONFIG = "nbpages.cfg"

# THERE SHOULD BE NO NEED TO EDIT BELOW THIS LINE
DOCS_DIR= "docs"
NOTEBOOK_DST_DIR = DOCS_DIR

README_MD = "readme.md"

INDEX_HTML = os.path.join(DOCS_DIR, "index.html")
INDEX_MD = os.path.join(DOCS_DIR, "index.md")
INDEX_NB = os.path.join(DOCS_DIR, "index.nb")

TOC_HTML = os.path.join(DOCS_DIR, "toc.html")
TOC_MD = os.path.join(DOCS_DIR, "toc.md")
TOC_NB = os.path.join(DOCS_DIR, "toc.ipynb")

TAG_INDEX_HTML = os.path.join(DOCS_DIR, "tag_index.html")
TAG_INDEX_MD = os.path.join(DOCS_DIR, "tag_index.md")
TAG_INDEX_NB = os.path.join(DOCS_DIR, "tag_index.ipynb")

# read .git config from the local directory to extract url, user, and page_title
assert os.path.exists('.git'), "local .git subdirectory not found. "
git_config = configparser.ConfigParser(strict=False)
git_config.read(os.path.join(".git", "config"))

GITHUB_URL = git_config['remote "origin"']['url']
GITHUB_USER = GITHUB_URL.rsplit('/')[-2]
PAGE_TITLE = GITHUB_URL.rsplit('/')[-1].split('.')[0]
GITHUB_REPOSITORY = f"{GITHUB_USER}/{PAGE_TITLE}"
GITHUB_PAGE_URL = f"https://{GITHUB_USER}.github.io/{PAGE_TITLE}"


# TOC and INDEX page headers with link to page url
TOC_HEADER = f"# [{PAGE_TITLE}]({GITHUB_PAGE_URL})"
TAG_INDEX_HEADER = f"# [{PAGE_TITLE}]({GITHUB_PAGE_URL})"

# headers for TOC and index pages with links to nbviewer/github
INDEX_TOC = f"### [Table of Contents]({GITHUB_PAGE_URL}/toc.html?flush=true)"
INDEX_INDEX = f"### [Tag Index]({GITHUB_PAGE_URL}/tag_index.html?flush=true)"

# CREATE STRING TEMPLATES

#

# navigation bar templates for notebook pages
PREV_TEMPLATE = "< [{title}]({url}) "
CONTENTS = "| [Contents](toc.html) |"
INDEX = " [Tag Index](tag_index.html) |"
NEXT_TEMPLATE = " [{title}]({url}) >"
