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
parser.add_argument("--remove_solution_code", help="remove solution code from code cells", action="store_true")
parser
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
        return

    if args.metadata:
        notebooks.metadata()
        return

    if args.tags:
        for tag in list(sorted(notebooks.tag_index.keys(), key=str.casefold)):
            print(tag)
        return

    if args.remove_cells:
        for tag in args.remove_cells:
            notebooks.remove_cells(tag)

    if args.remove_solution_code:
        notebooks.remove_solution_code()

    notebooks.write_headers()
    notebooks.write_navbars()
    notebooks.write_toc()
    notebooks.write_tag_index()
    notebooks.write_index_html()
    notebooks.write_html()

    return 0


if __name__ == "__main__":
    sys.exit(main())
