import re
import nbformat
from nbformat.v4.nbbase import new_markdown_cell
import itertools
import json
import os
from jinja2 import Environment, FileSystemLoader

from .config import *

# specify html exporter, replace standard 'full' with custom template
from nbconvert import HTMLExporter
html_exporter = HTMLExporter()
html_exporter.template_file = os.path.join(TEMPLATE_DIR, 'nbpages.tpl')


class Nb:
    # regular expressions for the notebook class
    HTML_IMG = re.compile(r'<img[^>]*>')
    MARKDOWN_FIG = re.compile(r'(?:!\[(?P<txt>.*?)\]\((?P<url>.*?)\))')
    MARKDOWN_HEADER = re.compile(r'(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)')
    MARKDOWN_LINK = re.compile(r'(?:[^!]\[(?P<txt>.*?)\]\((?P<url>.*?)\))')

    def __init__(self, filename, chapter, section):
        self.filename = filename
        self.path_src = os.path.join(NOTEBOOK_SRC_DIR, filename)
        self.path_dst = os.path.join(NOTEBOOK_DST_DIR, filename)
        self.path_download = os.path.join(DOCS_DIR, filename)   # need to download from github pages
        self.path_html = os.path.join(DOCS_DIR, filename)
        self.chapter = str(int(chapter)) if chapter.isdigit() else chapter
        self.section = str(int(section))
        self.html_filename = os.path.splitext(self.filename)[0] + ".html"
        self.html_url = GITHUB_PAGE_URL + "/" + self.html_filename
        self.colab_link = COLAB_LINK.format(notebook_filename=os.path.basename(self.filename))
        self.download_link = DOWNLOAD_LINK.format(notebook_filename=os.path.basename(self.filename))
        self.content = nbformat.read(self.path_src, as_version=4)
        self.insert_subsection_numbering()

    def __gt__(self, nb):
        return self.filename > nb.filename

    def __str__(self):
        return self.filename

    @property
    def title(self):
        """Return notebook title by extracting the first level one header."""
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                m = self.__class__.MARKDOWN_HEADER.match(cell.source)
                if m and len(m.group('level')) == 1:
                    return m.group('header').strip()
        return None

    @property
    def markdown_figs(self):
        """Return a list of markdown figures appearing in the markdown cells of this notebook."""
        figs = []
        for cell in self.content.cells[2:-1]:
            if cell.cell_type == "markdown":
                figs.extend(self.__class__.MARKDOWN_FIG.findall(cell.source))
        return figs

    @property
    def markdown_links(self):
        """Return a list of markdown links appearing in the markdown cells of this notebook."""
        links = []
        for cell in self.content.cells[2:-1]:
            if cell.cell_type == "markdown":
                links.extend(self.__class__.MARKDOWN_LINK.findall(cell.source))
        return links

    @property
    def img_tags(self):
        """Return a list of html img tags appearing in all cells of this notebook."""
        img_tags = []
        for cell in self.content.cells[2:-1]:
            img_tags.extend(self.__class__.HTML_IMG.findall(cell.source))
        return img_tags

    @property
    def link(self):
        """Return a markdown link to the html view of this notebook."""
        return f"[{self.numbered_title}]({self.html_url})"

    @property
    def html_link(self):
        """Return a markdown link to the  html view of this notebook."""
        return f"[{self.numbered_title}]({self.html})"

    @property
    def readme(self):
        """Return formatted entry for this notebook in the repository readme file."""
        return "\n### " + self.link

    @property
    def toc(self):
        """Return formatted list of markdown links to cells starting with a markdown header."""
        toc = []
        header_cells = (cell for cell in self.content.cells if cell.cell_type == "markdown" and cell.source.startswith("##"))
        for header_cell in header_cells:
            header = header_cell.source.splitlines()[0].strip().split()
            txt = ' '.join(header[1:])
            url = '#'.join([self.html_url, '-'.join(header[1:])])
            toc.append("    "*(len(header[0])-2) + f"- [{txt}]({url})")
        return toc

    @property
    def keyword_index(self):
        """Return keyword index and links for a notebook."""
        index = dict()
        headercells = (cell for cell in self.content.cells if cell.cell_type == "markdown" and cell.source.startswith("#"))
        for headercell in headercells:
            lines = headercell.source.splitlines()
            header = lines[0].strip().split()
            txt = ' '.join(header[1:])
            url = '#'.join([self.html_url, '-'.join(header[1:])])
            for keywordline in [line.strip() for line in lines[1:] if line.lower().startswith("keywords: ")]:
                for word in keywordline.split(':')[1].split(','):
                    index.setdefault(word.strip(), []).append(f"[{txt}]({url})")
        return index

    @property
    def tags(self):
        """Return a dictionary with tags as keys and a list of cell links as values."""
        tags = dict()
        for cell in self.content.cells:
            if 'tags' in cell.metadata.keys():
                for tag in cell.metadata['tags']:
                    tags.setdefault(tag, []).append(cell.metadata["nbpages"]["link"])
        return tags

    @property
    def orphan_headers(self):
        """"Return a list of orphan headers (i.e., headers not in the first line of a cell) in a notebook."""
        orphans = []
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                for line in cell.source.splitlines()[1:]:
                    if self.__class__.MARKDOWN_HEADER.match(line):
                        orphans.append(line)
        return orphans

    def insert_subsection_numbering(self):
        subsection_number_root = f"{self.chapter}.{self.section}"
        subsection_level = 0
        header_numbers = [0] * 6
        subsection_header = ""
        subsection_url = self.html_url
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                m = self.__class__.MARKDOWN_HEADER.match(cell.source)
                if m:
                    subsection_level = len(m.group('level'))
                    header_numbers[subsection_level - 1] += 1
                    header_numbers[subsection_level:] = [0] * (6 - subsection_level)
                    subsection_header = subsection_number_root \
                                    + "".join(f".{int(n)}" for n in header_numbers[1:] if n > 0) \
                                    + m.group("header")
                    subsection_url = '#'.join([self.html_url, '-'.join(subsection_header.strip().split())])
                    cell.source = cell.source[:m.start("header")] + " " + subsection_header + cell.source[m.end("header"):]
            cell.metadata["nbpages"] = {
                "level": subsection_level,
                "section": subsection_header,
                "link": f"[{subsection_header}]({subsection_url})"
            }

    def remove_cells(self, tag):
        for cell in self.content.cells:
            if 'tags' in cell.metadata.keys() and tag in cell.metadata['tags']:
                print("- remove cell tagged", tag, "from", self.filename)
        self.content.cells = [c for c in self.content.cells if 'tags' not in c.metadata.keys() or tag not in c.metadata['tags']]

    def remove_solution_code(self):
        SOLUTION_CODE = re.compile("### BEGIN SOLUTION(.*)### END SOLUTION", re.DOTALL)
        for cell in self.content.cells:
            if cell.cell_type=='code':
                if SOLUTION_CODE.findall(cell.source):
                    cell.source = SOLUTION_CODE.sub("# YOUR SOLUTION HERE", cell.source)
                    print("- remove solution code from", self.filename)

class FrontMatter(Nb):
    def __init__(self, filename, chapter, section):
        super().__init__(filename, chapter, section)

    @property
    def numbered_title(self):
        """Return formatted title with numbering for a notebook."""
        return f"{self.title}"

    @property
    def toc(self):
        """Return table of contents entry for a notebook."""
        toc = Nb.toc.fget(self)
        toc.insert(0, "\n## " + self.link)
        return toc


class Chapter(Nb):
    def __init__(self, filename, chapter, section):
        super().__init__(filename, chapter, section)

    @property
    def numbered_title(self):
        """Return formatted title with numbering for a notebook."""
        return f"Chapter {self.title}"

    @property
    def toc(self):
        """Return table of contents entry for a notebook."""
        toc = Nb.toc.fget(self)
        toc.insert(0, "\n## " + self.link)
        return toc


class Appendix(Nb):
    def __init__(self, filename, chapter, section):
        super().__init__(filename, chapter, section)

    @property
    def numbered_title(self):
        """Return formatted title with numbering for a notebook."""
        return f"Appendix {self.chapter}. {self.title}"

    @property
    def toc(self):
        """Return table of contents entry for a notebook."""
        toc = Nb.toc.fget(self)
        toc.insert(0, "\n## " + self.link)
        return toc


class Section(Nb):
    def __init__(self, filename, chapter, section):
        super().__init__(filename, chapter, section)

    @property
    def readme(self):
        """Return formatted entry for this notebook in the repository readme file."""
        return "- " + self.link

    @property
    def numbered_title(self):
        """Return formatted title with numbering for a notebook."""
        return f"{self.title}"

    @property
    def toc(self):
        """Return table of contents entry for a notebook."""
        toc = Nb.toc.fget(self)
        toc.insert(0, "### " + self.link)
        return toc


class NbHeader:

    def __init__(self):
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template('notebook_header.jinja')
        self.content = template.render(page_title=PAGE_TITLE, page_url=GITHUB_PAGE_URL, github_url=GITHUB_URL)
        self.source = NOTEBOOK_HEADER_TAG + self.content

    def write(self, nb):
        """
        Write header to a local notebook file.
        """
        if nb.content.cells[0].source.startswith(NOTEBOOK_HEADER_TAG):
            print('- amending header for {0}'.format(nb.filename))
            nb.content.cells[0].source = self.source
        else:
            print('- inserting header for {0}'.format(nb.filename))
            nb.content.cells.insert(0, new_markdown_cell(self.source))
        nbformat.write(nb.content, nb.path_dst)
        nbformat.write(nb.content, nb.path_download)


class NbCollection:
    # regular expression that matches notebook filenames to be included in the TOC
    REG = re.compile(r'(\d\d|[A-Z])\.(\d\d)-(.*)\.ipynb')

    def __init__(self, dir=NOTEBOOK_SRC_DIR):
        self.notebooks = []
        for filename in sorted(os.listdir(dir)):
            if self.__class__.REG.match(filename):
                chapter, section, _ = self.__class__.REG.match(filename).groups()
                if section not in "00":
                    self.notebooks.append(Section(filename, chapter, section))
                elif chapter in "00":
                    self.notebooks.append(FrontMatter(filename, chapter, section))
                elif chapter.isdigit():
                    self.notebooks.append(Chapter(filename, chapter, section))
                else:
                    self.notebooks.append(Appendix(filename, chapter, section))
        self.nbheader = NbHeader()
        self._keyword_index = {}
        self._tag_index = {}

    @property
    def keyword_index(self):
        """Return keyword dictionary with list of links for a collection of notebooks."""
        # use self._keyword_index to cache results
        if not self._keyword_index:
            for nb in self.notebooks:
                for word, links in nb.keyword_index.items():
                    for link in links:
                        self._keyword_index.setdefault(word, []).append(link)
        return self._keyword_index

    @property
    def tag_index(self):
        """Return of dictionary sorted links to tags indexed by tags."""
        if not self._tag_index:
            self._tag_index = dict()
            for nb in self.notebooks:
                for tag, links in nb.tags.items():
                    self._tag_index.setdefault(tag, []).extend(links)
            for tag in self._tag_index.keys():
                self._tag_index[tag] = list(sorted(set(self._tag_index[tag]), key=str.casefold))
        return self._tag_index

    def lint(self):
        """Report style issues in a collection of notebooks."""
        for nb in self.notebooks:
            if nb.img_tags:
                print("\n", nb.filename)
                print(*nb.img_tags, sep="\n")
            if nb.orphan_headers:
                print("\nOrphan headers in ", nb.filename)
                print(*nb.orphan_headers, sep="\n")

    def metadata(self):
        """Print metadata for a collection of notebooks."""
        for nb in self.notebooks:
            print(json.dumps(nb.content['metadata'], sort_keys=True, indent=4))

    def remove_cells(self, tag):
        for nb in self.notebooks:
            nb.remove_cells(tag)

    def remove_solution_code(self):
        for nb in self.notebooks:
            nb.remove_solution_code()

    def write_headers(self):
        """Insert a common header into a collection of notebooks."""
        for nb in self.notebooks:
            self.nbheader.write(nb)

    def write_html(self):
        """Write html files for a collection of notebooks."""
        for nb in self.notebooks:
            (body, resources) = html_exporter.from_notebook_node(nb.content)
            html_filename = os.path.splitext(nb.filename)[0] + ".html"
            html_path = os.path.join(DOCS_DIR, html_filename)
            print(f"- writing {html_path}")
            with open(html_path, 'w') as f:
                f.write(body)

    def write_navbars(self):
        """Insert navigation bars into a collection of notebooks."""
        a, b, c = itertools.tee(self.notebooks, 3)
        try:
            next(c)
        except StopIteration:
            return
        for prev_nb, nb, next_nb in zip(itertools.chain([None], a), b, itertools.chain(c, [None])):
            navbar = NAVBAR_TAG
            navbar += PREV_TEMPLATE.format(title=prev_nb.title, url=prev_nb.html_url) if prev_nb else ''
            navbar += CONTENTS + INDEX if self.keyword_index else CONTENTS
            navbar += NEXT_TEMPLATE.format(title=next_nb.title, url=next_nb.html_url) if next_nb else ''
            navbar += nb.colab_link
            navbar += nb.download_link
            if nb.content.cells[1].source.startswith(NAVBAR_TAG):
                print(f"- amending navbar for {nb.filename}")
                nb.content.cells[1].source = navbar
            else:
                print(f"- inserting navbar for {nb.filename}")
                nb.content.cells.insert(1, new_markdown_cell(source=navbar))
            if nb.content.cells[-1].source.startswith(NAVBAR_TAG):
                print(f"- amending navbar for {nb.filename}")
                nb.content.cells[-1].source = navbar
            else:
                print(f"- inserting navbar for {nb.filename}")
                nb.content.cells.append(new_markdown_cell(source=navbar))
            nbformat.write(nb.content, nb.path_dst)
            nbformat.write(nb.content, nb.path_download)


    def write_toc(self):
        """Write table of contents file for a collection of notebooks."""
        print("- writing table of contents file")
        with open(TOC_MD, 'w') as f:
            f.write(TOC_HEADER + "\n")
            for nb in self.notebooks:
                f.write('\n')
                f.write('\n'.join(nb.toc) + '\n')
                if nb.markdown_figs:
                    f.write("* Markdown Figures" + "\n")
                    for txt, url in nb.markdown_figs:
                        f.write("    - [{0}]({1})\n".format(txt if txt else url, url))
                if nb.markdown_links:
                    f.write("* Markdown Links" + "\n")
                    for txt, url in nb.markdown_links:
                        f.write(f"    - [{txt}]({url})\n")
                if nb.tags:
                    f.write("* Tags: ")
                    f.write(", ".join([tag for tag in nb.tags]) + "\n")

        #with open(TOC_HTML, 'w') as output_file:
        #    output_file.write(Markdown().convert(open(TOC_MD).read()))

        os.system(' '.join(['notedown', f'"{TOC_MD}"', '>', f'"{TOC_NB}"']))
        os.system(' '.join(['jupyter', 'nbconvert', TOC_NB]))
        os.remove(TOC_MD)
        os.remove(TOC_NB)

    def write_tag_index(self):
        """Write tag index file for a collection of notebooks."""
        keywords = sorted(self.keyword_index.keys(), key=str.lower)
        print("- writing tag index file")
        with open(TAG_INDEX_MD, 'w') as f:
            f.write(TAG_INDEX_HEADER + "\n")
            if keywords:
                print("\n## Keyword Index\n", file=f)
                for keyword in keywords:
                    f.write(f"* {keyword}\n")
                    for link in self.keyword_index[keyword]:
                        f.write("    - " + link + "\n")

            if self.tag_index:
                print("\n## Tag Index\n", file=f)
                for tag in sorted(self.tag_index.keys(), key=str.casefold):
                    f.write(f"* {tag}\n")
                    for val in self.tag_index[tag]:
                        f.write("    - " + val + "\n")

        os.system(' '.join(['notedown', f'"{TAG_INDEX_MD}"', ">", f'"{TAG_INDEX_NB}"']))
        os.system(' '.join(['jupyter', 'nbconvert', TAG_INDEX_NB]))
        os.remove(TAG_INDEX_MD)
        os.remove(TAG_INDEX_NB)

    def write_index_html(self):
        """Write index.md using the index.md.jinja template."""
        print("- writing README.md")
        index_toc = [INDEX_TOC] if self.notebooks else []
        index_toc += [INDEX_INDEX] if self.keyword_index.keys() else []
        index_toc += [nb.readme for nb in self.notebooks]
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        with open(INDEX_MD, 'w') as f:
            f.write(env.get_template('index.md.jinja').render(
                readme_toc=index_toc, page_title=PAGE_TITLE, github_url=GITHUB_URL))

