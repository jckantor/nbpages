from nbcollection import *

notebooks = NbCollection()
notebooks.write_headers()
notebooks.write_navbars()
notebooks.write_toc()
notebooks.write_readme()
notebooks.keyword_index()

#notebooks.lint()


