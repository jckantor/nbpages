
from nbsetup import nbsetup
from nbcollection import Nb, NbCollection


def main():
    nbsetup()
    notebooks = NbCollection()
    #notebooks.lint()
    notebooks.write_headers()
    notebooks.write_navbars()
    notebooks.write_toc()
    notebooks.write_keyword_index()
    notebooks.write_readme()

if __name__ == '__main__':
    main()




