import os
import sys
import argparse

# parse command line arguments first
parser = argparse.ArgumentParser()
parser.add_argument("--setup", help="create templates directory", action="store_true")
parser.add_argument("--lint", help="report any notebook lint", action="store_true")
parser.add_argument("--metadata", help="display notebook metadata", action="store_true")
parser.add_argument("--tags", help="display notebook tags", action="store_true")
parser.add_argument("--remove_cells", help="remove tagged cells", nargs="+")
args = parser.parse_args()

from .config import *

# asserts
assert os.path.exists(TEMPLATE_DIR), "template directory not found. Run 'nbpages --setup'."
assert os.path.exists(NOTEBOOK_SRC_DIR), "notebook source directory not found. Run 'nbpages --setup'."
assert os.path.exists(NOTEBOOK_DST_DIR), "notebook destination directory not found. Run 'nbpages --setup'."

# optional initial setup. setup required before nbcollection can be imported

if args.setup:
    nbsetup()
    sys.exit(0)

from .nbcollection import NbCollection


def main():

    notebooks = NbCollection()

    if args.lint:
        notebooks.lint()

    if args.metadata:
        notebooks.metadata()

    if args.tags:
        notebooks.write_tag_index()

    if args.remove_cells:
        for value in args.remove_cells:
            print("remove", value)

    notebooks.write_headers()
    notebooks.write_navbars()
    notebooks.write_toc()
    notebooks.write_tag_index()
    notebooks.write_index()
    notebooks.write_html()

    return 0


if __name__ == "__main__":
    sys.exit(main())