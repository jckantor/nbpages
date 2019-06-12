import os
import re
import nbformat
from nbformat.v4.nbbase import new_markdown_cell
import itertools
import copy
import json
import configparser

from nbconvert import HTMLExporter
import shutil

config = configparser.ConfigParser()
config.read('templates/config')
REPOSITORY = config['NBPAGES']['repository']
PAGE_TITLE = config['NBPAGES']['page_title']
PAGE_URL = config['NBPAGES']['page_url']
GITHUB_URL = config['NBPAGES']['github_url']

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


NBVIEWER_URL = f"http://nbviewer.jupyter.org/github/{REPOSITORY}/blob/master/notebooks/"

# Header on TOC page ... link to page url
TOC_HEADER = f"# [{PAGE_TITLE}]({PAGE_URL})"

# Header point to Table of Contents page viewed on nbviewer
README_TOC = f"### [Table of Contents]({NBVIEWER_URL}toc.ipynb?flush=true)"
README_INDEX = f"### [Keyword Index]({NBVIEWER_URL}index.ipynb?flush=true)"

# template for link to open notebooks in Google colaboratory
COLAB_LINK = f'<p><a href="https://colab.research.google.com/github/{REPOSITORY}' \
             '/blob/master/notebooks/{notebook_filename}">' + \
             '<img align="left" src="https://colab.research.google.com/assets/colab-badge.svg"' + \
             ' alt="Open in Colab" title="Open in Google Colaboratory"></a>'

# location of notebook directory
NOTEBOOK_DIR = os.path.join(os.getcwd(), 'notebooks/')

# location of files in local repository
README_FILE = os.path.join(os.getcwd(), 'README.md')
TOC_FILE = os.path.join(NOTEBOOK_DIR, 'toc.md')
TOC_NB = os.path.join(NOTEBOOK_DIR, 'toc.ipynb')
INDEX_FILE = os.path.join(NOTEBOOK_DIR, 'index.md')
INDEX_NB= os.path.join(NOTEBOOK_DIR, 'index.ipynb')

# location of notebook directory in the local repository
#HTML_DIR = os.path.join(os.path.dirname(__file__), '..', 'html')
#CUSTOM_CSS = os.path.join(os.path.dirname(__file__), 'custom.css')
#if not os.path.exists(HTML_DIR):
#    os.mkdir(HTML_DIR)
#shutil.copy(CUSTOM_CSS, os.path.join(HTML_DIR, 'custom.css'))

# regular expression that matches notebook filenames to be included in the TOC
REG = re.compile(r'(\d\d|[A-Z])\.(\d\d)-(.*)\.ipynb')

# nav bar templates_old
NAVBAR_TAG = "<!--NAVIGATION-->\n"
PREV_TEMPLATE = "< [{title}]({url}) "
CONTENTS = "| [Contents](toc.ipynb) | [Index](index.ipynb) |"
NEXT_TEMPLATE = " [{title}]({url}) >"


class Nb:

    # match markdown link returning txt and url groups
    MD_LINK = re.compile(r'(?:[^!]\[(?P<txt>.*?)\]\((?P<url>.*?)\))')

    # match markdown figure returning txt and url groups
    MD_FIG = re.compile(r'(?:!\[(?P<txt>.*?)\]\((?P<url>.*?)\))')

    # match html image tag
    HTML_IMG = re.compile(r'<img[^>]*>')

    # match markdown header
    MD_HEADER = re.compile(r'(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)')

    def __init__(self, filename):
        self.filename = filename
        self.path = os.path.join(NOTEBOOK_DIR, filename)
        #self.html = os.path.join(HTML_DIR, filename.replace('.ipynb', '.html'))
        self.chapter, self.section, _ = REG.match(filename).groups()
        self.url = os.path.join(NBVIEWER_URL, filename)
        self.colab_link = COLAB_LINK.format(notebook_filename=os.path.basename(self.filename))
        self.content = nbformat.read(self.path, as_version=4)
        self.navbar = None

    @property
    def title(self):
        """
        notebook title obtained from the first level one header
        """
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                m = self.__class__.MD_HEADER.match(cell.source)
                if m and len(m.group('level')) == 1:
                    return m.group('header').strip()
        return None

    @property
    def figs(self):
        """
        list of markdown figures
        """
        figs = []
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                figs.extend(self.__class__.MD_FIG.findall(cell.source))
        return figs

    @property
    def links(self):
        """
        list of markdown links
        """
        links = []
        for cell in self.content.cells[2:-1]:
            if cell.cell_type == "markdown":
                links.extend(self.__class__.MD_LINK.findall(cell.source))
        return links

    @property
    def imgs(self):
        """
        list of html img tags
        """
        imgs = []
        for cell in self.content.cells[2:-1]:
            if cell.cell_type == "markdown":
                imgs.extend(self.__class__.HTML_IMG.findall(cell.source))
        return imgs

    @property
    def link(self):
        """
        markdown link to html view
        """
        return f"[{self.numbered_title}]({self.url})"

    @property
    def readme(self):
        """
        formatted entry for this notebook in the repository readme file
        """
        return "\n### " + self.link

    @property
    def toc(self):
        """
        formmatted list of markdown links to cells starting with a markdown header
        """
        toc = []
        header_cells = (cell for cell in self.content.cells if cell.cell_type == "markdown" and cell.source.startswith("##"))
        for header_cell in header_cells:
            header = header_cell.source.splitlines()[0].strip().split()
            txt = ' '.join(header[1:])
            url = '#'.join([self.url, '-'.join(header[1:])])
            toc.append("    "*(len(header[0])-2) + f"- [{txt}]({url})")
        return toc

    @property
    def keyword_index(self):
        index = dict()
        headercells = (cell for cell in self.content.cells if cell.cell_type == "markdown" and cell.source.startswith("#"))
        for headercell in headercells:
            lines = headercell.source.splitlines()
            header = lines[0].strip().split()
            txt = ' '.join(header[1:])
            url = '#'.join([self.url, '-'.join(header[1:])])
            for keywordline in [line.strip() for line in lines[1:] if line.lower().startswith("keywords: ")]:
                for word in keywordline.split(':')[1].split(','):
                    index.setdefault(word.strip(), []).append(f"[{txt}]({url})")
        return index

    @property
    def orphan_headers(self):
        orphans = []
        for cell in self.content.cells[2:-1]:
            if cell.cell_type == "markdown":
                 for line in cell.source.splitlines()[1:]:
                     if self.__class__.MD_HEADER.match(line):
                         orphans.append(line)
        return orphans

    def write_navbar(self):
        if self.content.cells[1].source.startswith(NAVBAR_TAG):
            print(f"- amending navbar for {self.filename}")
            self.content.cells[1].source = self.navbar
        else:
            print(f"- inserting navbar for {self.filename}")
            self.content.cells.insert(1, new_markdown_cell(source=self.navbar))
        if self.content.cells[-1].source.startswith(NAVBAR_TAG):
            print(f"- amending navbar for {self.filename}")
            self.content.cells[-1].source = self.navbar
        else:
            print(f"- inserting navbar for {self.filename}")
            self.content.cells.append(new_markdown_cell(source=self.navbar))
        nbformat.write(self.content, self.path)

    def write_html(self):
        print("writing", self.html)
        html_exporter = HTMLExporter()
        html_exporter.template_file = 'full'
        # do a deeo copy to any chance of overwriting the original notebooks
        content = copy.deepcopy(self.content)
        content.cells = content.cells[2:-1]
        content.cells[0].source = "# " + self.numbered_title
        (body, resources) = html_exporter.from_notebook_node(content)
        with open(self.html, 'w') as f:
            f.write(body)

    def __gt__(self, nb):
        return self.filename > nb.filename

    def __str__(self):
        return self.filename


class FrontMatter(Nb):
    def __init__(self, filename):
        super().__init__(filename)

    @property
    def numbered_title(self):
        """
        formatted title with numbering
        """
        return f"{self.title}"

    @property
    def toc(self):
        toc = Nb.toc.fget(self)
        toc.insert(0, "\n## " + self.link)
        return toc


class Chapter(Nb):
    def __init__(self, filename):
        super().__init__(filename)

    @property
    def numbered_title(self):
        """
        formatted title with numbering
        """
        return f"Chapter {int(self.chapter)}.{int(self.section)} {self.title}"

    @property
    def toc(self):
        toc = Nb.toc.fget(self)
        toc.insert(0, "\n## " + self.link)
        return toc


class Appendix(Nb):
    def __init__(self, filename):
        super().__init__(filename)

    @property
    def numbered_title(self):
        """
        formatted title with numbering
        """
        return f"Appendix {self.chapter}. {self.title}"

    @property
    def toc(self):
        toc =  Nb.toc.fget(self)
        toc.insert(0, "\n## " + self.link)
        return toc


class Section(Nb):
    def __init__(self, filename):
        super().__init__(filename)

    @property
    def readme(self):
        """
        formatted entry for this notebook in the repository readme file
        """
        return "- " + self.link

    @property
    def numbered_title(self):
        """
        formatted title with numbering
        """
        try:
            return f"{int(self.chapter)}.{int(self.section)} {self.title}"
        except:
            return f"{self.chapter}.{int(self.section)} {self.title}"

    @property
    def toc(self):
        toc =  Nb.toc.fget(self)
        toc.insert(0, "### " + self.link)
        return toc


class NbHeader:

    NOTEBOOK_HEADER_TAG = "<!--NOTEBOOK_HEADER-->"

    def __init__(self):
        template = env.get_template('notebook_header.jinja')
        self.content = template.render(page_title=PAGE_TITLE, page_url=PAGE_URL, github_url=GITHUB_URL)
        self.source = self.__class__.NOTEBOOK_HEADER_TAG + self.content

    def write(self, nb):
        """
        write header to a notebook file
        :param nb: notebook object
        :return: None
        """
        if nb.content.cells[0].source.startswith(self.__class__.NOTEBOOK_HEADER_TAG):
            print('- amending header for {0}'.format(nb.filename))
            nb.content.cells[0].source = self.source
        else:
            print('- inserting header for {0}'.format(nb.filename))
            nb.content.cells.insert(0, new_markdown_cell(self.source))

        nbformat.write(nb.content, nb.path)


class NbCollection:

    def __init__(self, dir=NOTEBOOK_DIR):
        #self.notebooks = sorted([Nb(filename) for filename in os.listdir(dir) if REG.match(filename)])
        self.notebooks = []
        for filename in sorted(os.listdir(dir)):
            if REG.match(filename):
                chapter, section, _ = REG.match(filename).groups()
                if section not in "00":
                    self.notebooks.append(Section(filename))
                elif chapter in "00":
                    self.notebooks.append(Fronmatter(filename))
                elif chapter.isdigit():
                    self.notebooks.append(Chapter(filename))
                else:
                    self.notebooks.append(Appendix(filename))
        self.nbheader = NbHeader()

    def write_headers(self):
        for nb in self.notebooks:
            self.nbheader.write(nb)

    def write_navbars(self):
        a, b, c = itertools.tee(self.notebooks, 3)
        next (c)
        for prev_nb, nb, next_nb in zip(itertools.chain([None], a), b, itertools.chain(c, [None])):
            nb.navbar = NAVBAR_TAG
            nb.navbar += PREV_TEMPLATE.format(title=prev_nb.title, url=prev_nb.url) if prev_nb else ''
            nb.navbar += CONTENTS
            nb.navbar += NEXT_TEMPLATE.format(title=next_nb.title, url=next_nb.url) if next_nb else ''
            nb.navbar += nb.colab_link
            nb.write_navbar()

    def write_toc(self):
        with open(TOC_FILE, 'w') as f:
            print(TOC_HEADER, file=f)
            for nb in self.notebooks:
                f.write('\n')
                f.write('\n'.join(nb.toc) + '\n')
                if nb.figs:
                    print("* Figures", file=f)
                    for txt, url in nb.figs:
                        print("    - [{0}]({1})".format(txt if txt else url, url), file=f)
                if nb.links:
                    print("* Links", file=f)
                    for txt, url in nb.links:
                        print(f"    - [{txt}]({url})", file=f)
        os.system(' '.join(['notedown', f'"{TOC_FILE}"', '>', f'"{TOC_NB}"']))

    def write_readme(self):
        readme_toc = [README_TOC] + [README_INDEX] + [nb.readme for nb in self.notebooks]
        with open(README_FILE, 'w') as f:
            f.write(env.get_template('README.md.jinja').render(page_title=PAGE_TITLE, readme_toc=readme_toc))

    def write_html(self):
        for nb in self.notebooks:
            nb.write_html()

    def keyword_index(self):
        index = {}
        for nb in self.notebooks:
            for word, links in nb.keyword_index.items():
                for link in links:
                    index.setdefault(word, []).append(link)
        keywords = sorted(index.keys(), key=str.lower)
        if keywords:
            with open(INDEX_FILE, 'w') as f:
                print(TOC_HEADER + "\n## Keyword Index", file=f)
                f.write("\n")
                for keyword in keywords:
                    f.write("* " + keyword + "\n")
                    for link in index[keyword]:
                        f.write("    - " + link + "\n" )
            os.system(' '.join(['notedown', f'"{INDEX_FILE}"', ">", f'"{INDEX_NB}"']))

    def lint(self):
        for nb in self.notebooks:
            if nb.imgs:
                print("\n", nb.filename)
                for img in nb.imgs:
                    print(img)
            if nb.orphan_headers:
                print("\nOrphan headers in ", nb.filename)
                for orphan in nb.orphan_headers:
                    print(orphan)

    def metadata(self):
        """print metadata for all notebooks"""
        for nb in self.notebooks:
            print(json.dumps(nb.content['metadata'], sort_keys=True, indent=4))

