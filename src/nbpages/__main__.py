import os
import re
import sys
import argparse
import configparser

from .nbsetup import nbsetup, make_dir_if_needed

# parse command line arguments first
parser = argparse.ArgumentParser()

# commands that don't write to the destination directory
parser.add_argument("--setup", help="create templates directory", action="store_true")
parser.add_argument("--lint", help="report notebook lint", action="store_true")
parser.add_argument("--metadata", help="display notebook metadata", action="store_true")
parser.add_argument("--tags", help="display notebook tags", action="store_true")
parser.add_argument("--get_cells", help="extract cells with specified tags", nargs="+")
parser.add_argument("--search", help="show notebooks containing a regular expression", nargs=1)

# commands that do write to the destination directory
parser.add_argument("--publish", help="publish notebooks to the distination directory for github pages", action="store_true")
parser.add_argument("--remove_cells", help="remove tagged cells", nargs="+")
parser.add_argument("--remove_code", help="remove hidden and solution code from code cells", action="store_true")

# parse command line arguments
args = parser.parse_args()

# print help if no arguments
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

# verify nbpages is run in the top level of a github repository
if not os.path.exists('.git'):
    print("nbpages must be run in the top level directory of a github notebook respository")
    sys.exit(1)

# setup must be run to create configuration file before importing NbCollection
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
    elif args.search:
        notebooks.search(args.search[0])
    elif args.tags:
        for tag in list(sorted(notebooks.tag_index.keys(), key=str.casefold)):
            print(tag)
    elif args.get_cells:
        notebooks.get_cells(args.get_cells[0])
    else:
        if args.remove_cells:
            for tag in args.remove_cells:
                notebooks.remove_cells(tag)
        if args.remove_code:
            notebooks.remove_code()
        if args.publish:
            notebooks.insert_subsection_numbers()
            notebooks.insert_headers()
            notebooks.insert_navbars()
            notebooks.insert_data_imports()
            notebooks.remove("*.html")
            notebooks.remove("*.ipynb")
            notebooks.write_ipynb()
            notebooks.write_toc()
            notebooks.write_data_index()
            notebooks.write_figure_index()
            notebooks.write_tag_index()
            notebooks.write_python_index()
            notebooks.write_html()
            notebooks.write_index_html()
    return 0

if __name__ == "__main__":
    sys.exit(main())
