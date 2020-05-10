import os
import sys
import argparse

# parse command line arguments first
parser = argparse.ArgumentParser()
parser.add_argument("--setup", help="create templates directory", action="store_true")
parser.add_argument("--lint", help="report any notebook lint", action="store_true")
parser.add_argument("--metadata", help="display notebook metadata", action="store_true")
parser.add_argument("--html", help="write static html", action="store_true")
parser.add_argument("--tags", help="display notebook tags", action="store_true")
args = parser.parse_args()

from .config import *

# asserts
assert os.path.exists(TEMPLATE_DIR), "template directorynot found. Run 'nbpages --setup' to create config directory."
assert os.path.exists(NOTEBOOK_SRC), "notebooks directory not found. Run 'nbpages --setup' to create notebooks directory."

# optional initial setup. setup required before nbcollection can be imported

if args.setup:
    nbsetup()
    sys.exit(0)

from .nbcollection import NbCollection

def main():

    notebooks = NbCollection()

    if args.lint:
        notebooks.lint()

    elif args.metadata:
        notebooks.metadata()

    elif args.tags:
        notebooks.write_tag_index()

    elif args.html:
        notebooks.write_html()

    else:
        notebooks.write_headers()
        notebooks.write_navbars()
        notebooks.write_toc()
        notebooks.write_keyword_index()
        notebooks.write_readme()

    return 0

if __name__ == "__main__":
    sys.exit(main())
