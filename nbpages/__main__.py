from nbcollection import *
from setup import *

setup()

notebooks = NbCollection()
#notebooks.lint()
notebooks.write_headers()
notebooks.write_navbars()
notebooks.write_toc()
notebooks.keyword_index()
notebooks.write_readme()




