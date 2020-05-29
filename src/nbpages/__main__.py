import os
import re
import sys
import argparse
import configparser

from .nbsetup import nbsetup, make_dir_if_needed

# parse command line arguments first
parser = argparse.ArgumentParser()
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
    src_dir = config["NBPAGES"]["src_dir"]
    dst_dir = config["NBPAGES"]["dst_dir"]

    # source and destination directories
    assert src_dir != dst_dir, "notebook source and destination directories must be different"
    assert os.path.exists(src_dir), f"notebook source directory '{src_dir}' not found"
    make_dir_if_needed(dst_dir)

    notebooks = NbCollection(config["NBPAGES"], src_dir, dst_dir)

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
        if args.remove_solution_code:
            notebooks.remove_solution_code()
        if args.publish:
            notebooks.insert_subsection_numbers()
            notebooks.insert_headers()
            notebooks.insert_navbars(dst_dir)
            notebooks.write_ipynb(dst_dir)
            notebooks.write_toc(dst_dir)
            notebooks.write_tag_index(dst_dir)
            notebooks.write_index_html(dst_dir)
            notebooks.write_html(dst_dir, os.path.join(templates_dir, 'nbpages.tpl'))
    return 0

if __name__ == "__main__":
    sys.exit(main())
