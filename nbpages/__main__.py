import argparse

from nbsetup import nbsetup
from nbcollection import NbCollection

parser = argparse.ArgumentParser()
parser.add_argument("--setup", help="create templates directory", action="store_true")
parser.add_argument("--lint",  help="report any notebook lint", action="store_true")
parser.add_argument("--metadata", help="display notebook metadata", action="store_true")

args = parser.parse_args()

def main():
    if args.setup:
        nbsetup()
        return
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

