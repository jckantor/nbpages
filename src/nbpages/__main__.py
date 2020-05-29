import os
import re
import sys
import argparse
import configparser

from .nbsetup import nbsetup, make_dir_if_needed

# parse command line arguments first
parser = argparse.ArgumentParser()
parser.add_argument("--src", help="notebook source directory", nargs=1, metavar="SRC")
parser.add_argument("--dst", help="notebook destination directory", nargs=1, metavar="DST")
parser.add_argument("--config", help="specify config file", default="nbpages.cfg", metavar="CONFIG_FILE")

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
parser.add_argument("--remove_solution_code", help="remove solution code from code cells", action="store_true")

# print help if no arguments
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

# parse command line arguments
args = parser.parse_args()
config_file = args.config


# verify nbpages is being run in the top level of a github repository
if not os.path.exists('.git'):
    print("nbpages must be run in the top level directory of a github notebook respository")
    sys.exit(1)

# setup
if args.setup:
    nbsetup(config_file)
    sys.exit(0)

if not os.path.exists(config_file):
    print(f"configuration file {config_file} not founds. Run nbpages --setup to create a config file.")
    sys.exit(1)

from .nbcollection import NbCollection

def main():

    config = configparser.ConfigParser()
    config.read(config_file)
    templates_dir = config['NBPAGES']['templates_dir']

    # source and destination directories
    NOTEBOOK_SRC_DIR = args.src[0] if args.src else config["NBPAGES"]["src_dir"]
    NOTEBOOK_DST_DIR = args.dst[0] if args.dst else config["NBPAGES"]["dst_dir"]
    assert NOTEBOOK_SRC_DIR != NOTEBOOK_DST_DIR, "notebook source and destination directories must be different"
    assert os.path.exists(NOTEBOOK_SRC_DIR), f"notebook source directory '{NOTEBOOK_SRC_DIR}' not found"
    make_dir_if_needed(NOTEBOOK_DST_DIR)

    notebooks = NbCollection(config["NBPAGES"], NOTEBOOK_SRC_DIR, NOTEBOOK_DST_DIR)

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

    if args.publish:

        notebooks.insert_subsection_numbers()
        notebooks.insert_headers()
        notebooks.insert_navbars(NOTEBOOK_DST_DIR)
        notebooks.write_ipynb(NOTEBOOK_DST_DIR)
        notebooks.write_toc(NOTEBOOK_DST_DIR)
        notebooks.write_tag_index(NOTEBOOK_DST_DIR)
        notebooks.write_index_html(NOTEBOOK_DST_DIR)
        notebooks.write_html(NOTEBOOK_DST_DIR, os.path.join(templates_dir, 'nbpages.tpl'))

    return 0

if __name__ == "__main__":
    sys.exit(main())
