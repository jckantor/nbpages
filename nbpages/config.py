import configparser
import os
from jinja2 import Environment, FileSystemLoader

# read configuration file
config = configparser.ConfigParser()
config.read('templates/config')

REPOSITORY = config['NBPAGES']['repository']
PAGE_TITLE = config['NBPAGES']['page_title']
PAGE_URL = config['NBPAGES']['page_url']
GITHUB_URL = config['NBPAGES']['github_url']

NBVIEWER_URL = f"http://nbviewer.jupyter.org/github/{REPOSITORY}/blob/master/notebooks/"

# Header on TOC page ... link to page url
TOC_HEADER = f"# [{PAGE_TITLE}]({PAGE_URL})"
INDEX_HEADER = f"# [{PAGE_TITLE}]({PAGE_URL})"

# Header point to Table of Contents page viewed on nbviewer
README_TOC = f"### [Table of Contents]({NBVIEWER_URL}toc.ipynb?flush=true)"
README_INDEX = f"### [Keyword Index]({NBVIEWER_URL}index.ipynb?flush=true)"

# template for link to open notebooks in Google colaboratory
COLAB_LINK = f'<p><a href="https://colab.research.google.com/github/{REPOSITORY}' \
             '/blob/master/notebooks/{notebook_filename}">' + \
             '<img align="left" src="https://colab.research.google.com/assets/colab-badge.svg"' + \
             ' alt="Open in Colab" title="Open in Google Colaboratory"></a>'

# location of notebook directory
NOTEBOOK_DIR = os.path.join(os.getcwd(), 'notebooks/')

# location of files in local repository
README_FILE = os.path.join(os.getcwd(), 'README.md')
TOC_FILE = os.path.join(NOTEBOOK_DIR, 'toc.md')
TOC_NB = os.path.join(NOTEBOOK_DIR, 'toc.ipynb')
INDEX_FILE = os.path.join(NOTEBOOK_DIR, 'index.md')
INDEX_NB= os.path.join(NOTEBOOK_DIR, 'index.ipynb')

# nav bar templates
NAVBAR_TAG = "<!--NAVIGATION-->\n"
PREV_TEMPLATE = "< [{title}]({url}) "
CONTENTS = "| [Contents](toc.ipynb) |"
INDEX = " [Index](index.ipynb) |"
NEXT_TEMPLATE = " [{title}]({url}) >"
