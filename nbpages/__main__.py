
import os
import argparse

from .nbsetup import nbsetup

parser = argparse.ArgumentParser()
parser.add_argument("--setup", help="create templates directory", action="store_true")
parser.add_argument("--lint", help="report any notebook lint", action="store_true")
parser.add_argument("--metadata", help="display notebook metadata", action="store_true")

args = parser.parse_args()

def main():

    if not os.path.exists('.git'):
        print(".git directory wasn't found. Create repository first and then run 'nbpages --setup'")
        return

    if args.setup:
        nbsetup()
        return

    if not os.path.exists('templates'):
        print("templates directory wasn't found. Run 'nbpages --setup' to create templates directory.")
        return

    if not os.path.exists('notebooks'):
        print("notebooks directory wasn't found. Run 'nbpages --setup' to create notebooks directory.")
        return

    from .nbcollection import NbCollection

    notebooks = NbCollection()
    if args.lint:
        notebooks.lint()
        return
    if args.metadata:
        notebooks.metadata()
        return

    notebooks.write_headers()
    notebooks.write_navbars()
    notebooks.write_toc()
    notebooks.write_keyword_index()
    notebooks.write_readme()

if __name__ == "__main__":
    main()