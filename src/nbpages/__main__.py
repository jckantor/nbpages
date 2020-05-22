import os
import re
import sys
import argparse
import configparser

from .nbsetup import nbsetup

# parse command line arguments first
parser = argparse.ArgumentParser()
parser.add_argument("--src", help="notebook source directory (default 'notebooks')", default="notebooks", metavar="SRC")
parser.add_argument("--dst", help="notebook destination directory (default 'docs')", default="docs", metavar="DST")
parser.add_argument("--templates", help="specify templates directory (default 'templates')", default="templates", metavar="TEMPLATES")

# commands that don't write to the destination directory
parser.add_argument("--setup", help="create templates directory", action="store_true")
parser.add_argument("--lint", help="report notebook lint", action="store_true")
parser.add_argument("--metadata", help="display notebook metadata", action="store_true")
parser.add_argument("--tags", help="display notebook tags", action="store_true")
parser.add_argument("--get_cells", help="extract cells with specified tags", nargs="+")
parser.add_argument("--search", help="show notebooks containing a regular expression", nargs=1)

# commands that do write to the destination directory
parser.add_argument("--publish", help="prepare notebooks for github pages", action="store_true")
parser.add_argument("--remove_cells", help="remove tagged cells", nargs="+")
parser.add_argument("--remove_solution_code", help="remove solution code from code cells", action="store_true")
args = parser.parse_args()

config_file = "nbpages.cfg"

if args.setup:
    nbsetup()
    sys.exit(0)

from .nbcollection import NbCollection

def main():

    # read configuration file
    assert os.path.exists(config_file), f"{config_file} not found"
    config = configparser.ConfigParser()
    config.read(config_file)
    github_user_name = config['NBPAGES']['github_user_name']
    github_repo_name = config['NBPAGES']['github_repo_name']
    github_repo_url = config['NBPAGES']['github_repo_url']
    github_pages_url = config['NBPAGES']['github_pages_url']

    # source and destination directories
    NOTEBOOK_SRC_DIR = args.src
    NOTEBOOK_DST_DIR = args.dst
    assert os.path.exists(NOTEBOOK_SRC_DIR), f"notebook source directory '{NOTEBOOK_SRC_DIR}' not found"
    assert os.path.exists(NOTEBOOK_DST_DIR), f"notebook destination directory '{NOTEBOOK_DST_DIR}' not found"
    assert NOTEBOOK_SRC_DIR != NOTEBOOK_DST_DIR, "notebook source and destination directories must be different"

    TEMPLATES_DIR = args.templates
    assert os.path.exists(TEMPLATES_DIR), f"templates directory '{TEMPLATES_DIR}' not found"

    CONFIG_FILE = "nbpages.cfg"
    assert os.path.exists(CONFIG_FILE), f"configuration file '{CONFIG_FILE}' not found"

    notebooks = NbCollection(NOTEBOOK_SRC_DIR, NOTEBOOK_DST_DIR)

    if args.lint:
        notebooks.lint()
        return 0

    if args.metadata:
        notebooks.metadata()
        return 0

    if args.search:
        notebooks.search(args.search[0])
        return 0

    if args.tags:
        for tag in list(sorted(notebooks.tag_index.keys(), key=str.casefold)):
            print(tag)
        return 0

    if args.get_cells:
        notebooks.get_cells(args.get_cells[0])
        return 0

    if args.remove_cells:
        for tag in args.remove_cells:
            notebooks.remove_cells(tag)

    if args.remove_solution_code:
        notebooks.remove_solution_code()

    notebooks.insert_subsection_numbers()
    notebooks.insert_headers()
    notebooks.insert_navbars(NOTEBOOK_DST_DIR)
    notebooks.write_ipynb(NOTEBOOK_DST_DIR)
    notebooks.write_toc(NOTEBOOK_DST_DIR)
    notebooks.write_tag_index(NOTEBOOK_DST_DIR)
    notebooks.write_index_html(NOTEBOOK_DST_DIR)
    notebooks.write_html(NOTEBOOK_DST_DIR, os.path.join("templates", 'nbpages.tpl'))

    return 0

if __name__ == "__main__":
    sys.exit(main())
