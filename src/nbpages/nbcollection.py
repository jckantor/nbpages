import re
import collections, itertools
import json
import configparser
import glob, os, shutil
import nbformat
from nbformat.v4.nbbase import new_markdown_cell, new_notebook
from nbconvert import HTMLExporter
from jinja2 import Environment, FileSystemLoader

# configuration file
config_file = "nbpages.cfg"

# read configuration file
if not os.path.exists(config_file):
    print(f"configuration file not founds. Run nbpages --setup to create a config file.")
    sys.exit(1)

config = configparser.ConfigParser()
config.read(config_file)
config =  config["nbpages"]

# extract configuration information
github_user_name = config['github_user_name']
github_repo_name = config['github_repo_name']
github_repo_url = config['github_repo_url']
github_pages_url = config['github_pages_url']
templates_dir = config['templates_dir']
src_dir = config["src_dir"]
dst_dir = config["dst_dir"]
figures_subdir = config['figures_subdir']
data_subdir = config['data_subdir']

# source and destination directories
assert src_dir != dst_dir, "notebook source and destination directories must be different"
assert os.path.exists(src_dir), f"notebook source directory '{src_dir}' not found"
assert os.path.exists(dst_dir), f"notebook destination directory '{dst_dir}' not found"

# tags
NOTEBOOK_HEADER_TAG = "<!--NOTEBOOK_HEADER-->"
NAVBAR_TAG = "<!--NAVIGATION-->\n"

# regular expressions
NB_FILENAME = re.compile(r'(\d\d|[A-Z])\.(\d\d)-(.*)\.ipynb')
HTML_ANCHOR = re.compile(r'<a [^>]*>')
HTML_IMG = re.compile(r'<img[^>]*>')
MARKDOWN_FIG = re.compile(r'(?:!\[(?P<txt>.*?)\]\((?P<url>.*?)\))')
MARKDOWN_HEADER = re.compile(r'(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)')
MARKDOWN_LINK = re.compile(r'(?:[^!]\[(?P<txt>.*?)\]\((?P<url>.*?)\))')
SOLUTION_CODE = re.compile("### BEGIN SOLUTION(.*)### END SOLUTION", re.DOTALL)
HIDDEN_TESTS = re.compile("### BEGIN HIDDEN TESTS(.*)### END HIDDEN TESTS", re.DOTALL)


class Nb:

    def __init__(self, filename, chapter, section):
        self.filename = filename
        self.chapter = str(int(chapter)) if chapter.isdigit() else chapter
        self.section = str(int(section))
        self.content = nbformat.read(os.path.join(src_dir, filename), as_version=4)

        #self.path_download = os.path.join("docs", filename)   # need to download from github pages
        #self.path_html = os.path.join("docs", filename)

        self.html_filename = os.path.splitext(self.filename)[0] + ".html"
        self.html_url = f"{github_pages_url}/{self.html_filename}"
        #self.colab_link = COLAB_LINK.format(notebook_filename=os.path.basename(self.filename))
        #self.download_link = DOWNLOAD_LINK.format(notebook_filename=os.path.basename(self.filename))

    def __gt__(self, nb):
        return self.filename > nb.filename

    def __str__(self):
        return self.filename

    @property
    def title(self):
        """Return notebook title by extracting the first level one header."""
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                m = MARKDOWN_HEADER.match(cell.source)
                if m and len(m.group('level')) == 1:
                    return m.group('header').strip()
        return None

    @property
    def markdown_figs(self):
        """Return a list of markdown figures in the markdown cells of this notebook."""
        figs = []
        for cell in self.content.cells[2:-1]:
            if cell.cell_type == "markdown":
                figs.extend(MARKDOWN_FIG.findall(cell.source))
        return figs

    @property
    def markdown_links(self):
        """Return a list of markdown links in the markdown cells of this notebook."""
        links = []
        for cell in self.content.cells[2:-1]:
            if cell.cell_type == "markdown":
                links.extend(MARKDOWN_LINK.findall(cell.source))
        return links

    @property
    def html_anchor_tags(self):
        """Return a list of html anchor tags appearing in this notebook."""
        tags = []
        for cell in self.content.cells[2:-1]:
            tags.extend(HTML_ANCHOR.findall(cell.source))
        return tags

    @property
    def html_img_tags(self):
        """Return a list of html img tags appearing in this notebook."""
        tags = []
        for cell in self.content.cells[2:-1]:
            tags.extend(HTML_IMG.findall(cell.source))
        return tags

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
        tags = collections.defaultdict(list)
        for cell in self.content.cells:
            if 'tags' in cell.metadata.keys():
                for tag in cell.metadata['tags']:
                    tags[tag].append(cell.metadata["nbpages"]["link"])
        return tags

    @property
    def orphan_headers(self):
        """"Return a list of headers not in the first line of a cell) in a notebook."""
        orphans = []
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                orphans.extend([line for line in cell.source.splitlines()[1:] if MARKDOWN_HEADER.match(line)])
        return orphans

    @property
    def output_errors(self):
        output_errors = []
        for cell in self.content.cells:
            if cell.cell_type == "code":
                for output in cell.outputs:
                    if output["output_type"] == "error":
                        output_errors.append(f"{output['ename']}: {output['evalue']}")
                    if "name" in output.keys():
                        if output["name"] == "stderr":
                            output_errors.append(f"{output['name']}: {output['text'].splitlines()[0]}")
        return output_errors


    def insert_subsection_numbers(self):
        subsection_number_root = f"{self.chapter}.{self.section}"
        subsection_level = 0
        header_numbers = [0] * 6
        subsection_header = ""
        subsection_url = self.html_url
        for cell in self.content.cells:
            if cell.cell_type == "markdown":
                m = MARKDOWN_HEADER.match(cell.source)
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

    def get_cells(self, tag):
        """return a list of cells with a specified tag"""
        cells = []
        for cell in self.content.cells:
            if 'tags' in cell.metadata.keys() and tag in cell.metadata['tags']:
                cells.append(cell)
        return [cell for cell in self.content.cells if 'tags' in cell.metadata.keys() and tag in cell.metadata['tags']]

    def lint(self):
        lint_list = (
            (self.html_anchor_tags, "Remove or replace HTML anchor tags with markdown links."),
            (self.html_img_tags, "Replace HTML img tags with markdown image links."),
            (self.orphan_headers, "Move orphan headers to the first line in a markdown cell."),
            (self.output_errors, "Fix errors found in the output of codes cells."))
        if any([lint for lint, msg in lint_list]):
            print(self.filename)
            for lint, msg in lint_list:
                if lint:
                    print(f"    {msg}")
                    for s in lint:
                        print(f"        {s}")

    def remove_cells(self, tag):
        for cell in self.content.cells:
            if 'tags' in cell.metadata.keys() and tag in cell.metadata['tags']:
                print("- remove cell tagged", tag, "from", self.filename)
        self.content.cells = [c for c in self.content.cells if 'tags' not in c.metadata.keys() or tag not in c.metadata['tags']]

    def remove_solution_code(self):
        for cell in self.content.cells:
            if cell.cell_type=='code':
                if SOLUTION_CODE.findall(cell.source):
                    cell.source = SOLUTION_CODE.sub("# YOUR SOLUTION HERE", cell.source)
                    print("- remove solution code from", self.filename)
                if HIDDEN_TESTS.findall(cell.source):
                    cell.source = HIDDEN_TESTS.sub("", cell.source)
                    print("- remove hidden tests code from", self.filename)


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
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('notebook_header.tpl')
        self.content = template.render(page_title=github_repo_name, page_url=github_pages_url, github_url=github_repo_url)
        self.source = NOTEBOOK_HEADER_TAG + self.content

    def insert(self, nb):
        """
        Insert header to notebook contents.
        """
        if nb.content.cells[0].source.startswith(NOTEBOOK_HEADER_TAG):
            print('- amending header for {0}'.format(nb.filename))
            nb.content.cells[0].source = self.source
        else:
            print('- inserting header for {0}'.format(nb.filename))
            # print('- inserting header for {0}'.format(nb.filenapatth_srme))
            nb.content.cells.insert(0, new_markdown_cell(self.source))


class NbCollection:

    def __init__(self):

        self.notebooks = []
        for filename in sorted(os.listdir(src_dir)):
            if NB_FILENAME.match(filename):
                chapter, section, _ = NB_FILENAME.match(filename).groups()
                if section not in "00":
                    self.notebooks.append(Section(filename, chapter, section))
                elif chapter in "00":
                    self.notebooks.append(FrontMatter(filename, chapter, section))
                elif chapter.isdigit():
                    self.notebooks.append(Chapter(filename, chapter, section))
                else:
                    self.notebooks.append(Appendix(filename, chapter, section))
        self.nbheader = NbHeader()

        # property caches
        self._data = []
        self._data_index = {}
        self._figures = []
        self._figure_index = {}
        self._keyword_index = {}
        self._tag_index = collections.defaultdict(list)

    @property
    def data(self):
        """Return list of .txt and .csv data files in data directory."""
        path = os.path.join(src_dir, data_subdir)
        assert os.path.exists(path), f"- data subdirectory {path} was not found"
        if not self._data:
            self._data = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) \
                          and not f.startswith('.') and (f.endswith('.csv') or f.endswith('.txt'))]
        return self._data

    @property
    def data_index(self):
        """Return dictionary of data files and link appearing in a collection of notebooks."""
        if not self._data_index:
            for data in self.data:
                regex = re.compile(data)
                self._data_index[data] = [cell.metadata["nbpages"]["link"] \
                                     for nb in self.notebooks for cell in nb.content.cells if regex.search(cell.source)]
        return self._data_index

    @property
    def figures(self):
        """Return list of figure files in the figures directory."""
        dir = os.path.join(src_dir, figures_subdir)
        assert os.path.exists(dir), f"- figures subdirectory {dir} was not found"
        if not self._figures:
            self._figures = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) \
                             and not f.startswith('.') and not f.endswith('.tex') and not f.endswith('.pdf')]
        return self._figures

    @property
    def figure_index(self):
        """Return dictionary of figures and links appearing in a collection of notebooks."""
        if not self._figure_index:
            for figure in self.figures:
                regex = re.compile(figure)
                self._figure_index[figure] = [cell.metadata["nbpages"]["link"] \
                                     for nb in self.notebooks for cell in nb.content.cells if regex.search(cell.source)]
        return self._figure_index

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
            for nb in self.notebooks:
                for tag, links in nb.tags.items():
                    self._tag_index[tag].extend(links)
            for tag in self._tag_index.keys():
                self._tag_index[tag] = list(sorted(set(self._tag_index[tag]), key=str.casefold))
        return self._tag_index

    def get_cells(self, tag):
        """Return a new notebook created from cells with a specified tag."""
        cells = []
        for nb in self.notebooks:
            cells.extend(nb.get_cells(tag))
        print(cells)
        nb.format.write(new_notebook(cells=cells).content, 'ma.ipynb')
        return

    def insert_headers(self):
        """Insert a common header into a collection of notebooks."""
        for nb in self.notebooks:
            self.nbheader.insert(nb)

    def insert_navbars(self):
        """Insert navigation bars into a collection of notebooks."""

        # navigation bar templates for notebook pages
        PREV_TEMPLATE = "< [{title}]({url}) "
        CONTENTS = "| [Contents](toc.html) |"
        INDEX = " [Tag Index](tag_index.html) |"
        NEXT_TEMPLATE = " [{title}]({url}) >"

        # colab opens from github repository
        COLAB_LINK = f'<p><a href="https://colab.research.google.com/github/{github_user_name}/{github_repo_name}' + \
            '/blob/master/{dst}/{notebook_filename}"> ' + \
            '<img align="left" src="https://colab.research.google.com/assets/colab-badge.svg"' + \
            ' alt="Open in Colab" title="Open in Google Colaboratory"></a>'

        # download from github pages
        DOWNLOAD_LINK = f'<p><a href="{github_pages_url}' + \
                        '/{notebook_filename}"> <img align="left" src="https://img.shields.io/badge/Github-Download-blue.svg"' + \
                        ' alt="Download" title="Download Notebook"></a>'

        a, b, c = itertools.tee(self.notebooks, 3)
        try:
            next(c)
        except StopIteration:
            return
        for prev_nb, nb, next_nb in zip(itertools.chain([None], a), b, itertools.chain(c, [None])):
            navbar = NAVBAR_TAG
            navbar += f"< [{prev_nb.title}]({prev_nb.html_url}) " if prev_nb else ""
            navbar += f"| [Contents](toc.html) |"
            navbar += f" [Tag Index](tag_index.html) |" if self.tag_index or self.keyword_index else ""
            navbar += f" [{next_nb.title}]({next_nb.html_url})" if next_nb else ""
            navbar += COLAB_LINK.format(dst=dst_dir, notebook_filename=nb.filename)
            navbar += DOWNLOAD_LINK.format(notebook_filename=nb.filename)
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

    def insert_subsection_numbers(self):
        for nb in self.notebooks:
            nb.insert_subsection_numbers()

    def lint(self):
        """Report style issues interfering with nbpages in a collection of notebooks."""
        for nb in self.notebooks:
            nb.lint()
        for data in sorted(self.data, key=str.casefold):
            regex = re.compile(data)
            found = False
            for nb in self.notebooks:
                for cell in nb.content.cells:
                    found = regex.search(cell.source)
                    if found:
                        break
                if found:
                    break
            if not found:
                print(f"    Data file not used in any notebook: {data}")
        for figure in sorted(self.figures, key=str.casefold):
            regex = re.compile(figure)
            found = False
            for nb in self.notebooks:
                for cell in nb.content.cells:
                    found = regex.search(cell.source)
                    if found:
                        break
                if found:
                    break
            if not found:
                print(f"    Figure not used in any notebook: {figure}")

    def metadata(self):
        """Print selected metadata for a collection of notebooks."""
        for nb in self.notebooks:
            print(f"\n{nb.filename}")
            print(json.dumps(nb.content['metadata'], sort_keys=True, indent=4))

    def remove_cells(self, tag):
        for nb in self.notebooks:
            nb.remove_cells(tag)

    def remove_solution_code(self):
        for nb in self.notebooks:
            nb.remove_solution_code()

    def search(self, pattern):
        regex = re.compile(pattern)
        for nb in self.notebooks:
            for cell in nb.content.cells:
                if regex.search(cell.source):
                    print(nb.filename)
                    break

    def remove(self, pattern):
        assert dst_dir != src_dir, "destination directory must be different than the source directory"
        html_files = glob.glob(os.path.join(dst_dir, pattern))
        for file in html_files:
            print(f"- removing {file}")
            os.remove(file)

    def write_data_index(self):
        content = ""
        self.remove(os.path.join(data_subdir, "*"))
        if self.data_index:
            print("- writing data index")
            content += f"# [{github_repo_name}]({github_pages_url})\n"
            content += "\n## Index of Data files in this Repository\n"
            for data, links in sorted(self.data_index.items(), key=lambda x: str.casefold(x[0])):
                if links:
                    content += f"\n### {data}\n"
                    content += f"![{data}]({data_subdir}/{data})\n"
                    for link in links:
                        content += f"* {link}\n"
                    data_src = os.path.join(src_dir, data_subdir, data)
                    data_dst = os.path.join(dst_dir, data_subdir, data)
                    print(f"- copying {data_src} to {data_dst}")
                    shutil.copy(data_src, data_dst)
        self.write_md2html("data_index", content)

    def write_figure_index(self):
        content = ""
        self.remove(os.path.join(figures_subdir, "*"))
        if self.figure_index:
            print("- writing figure index")
            content += f"# [{github_repo_name}]({github_pages_url})\n"
            content += "\n## Index of Figures in this Repository\n"
            for figure, links in sorted(self.figure_index.items(), key=lambda x: str.casefold(x[0])):
                if links:
                    content += f"\n### {figure}\n"
                    content += f"![{figure}]({figures_subdir}/{figure})\n"
                    for link in links:
                        content += f"* {link}\n"
                    figure_src = os.path.join(src_dir, figures_subdir, figure)
                    figure_dst = os.path.join(dst_dir, figures_subdir, figure)
                    print(f"- copying {figure_src} to {figure_dst}")
                    shutil.copy(figure_src, figure_dst)
        self.write_md2html("figure_index", content)

    def write_html(self):
        """Write html files for a collection of notebooks to a specified directory."""
        html_exporter = HTMLExporter()
        html_exporter.template_file = os.path.join(templates_dir, 'notebook.tpl')
        for nb in self.notebooks:
            (body, resources) = html_exporter.from_notebook_node(nb.content)
            html_path = os.path.join(dst_dir,  os.path.splitext(nb.filename)[0] + ".html")
            print(f"- writing {html_path}")
            with open(html_path, 'w') as f:
                f.write(body)

    def write_ipynb(self):
        """Write notebooks to a specified directory."""
        for nb in self.notebooks:
            nbformat.write(nb.content, os.path.join(dst_dir, nb.filename))

    def write_index_html(self):
        """Write index.md using the index.md.tpl template."""
        print("- writing index.md")
        index_toc = [f"### [Table of Contents]({github_pages_url}/toc.html)"] if self.notebooks else []
        if os.path.isfile(os.path.join(dst_dir, "data_index.html")):
            index_toc += [f"### [Data Index]({github_pages_url}/data_index.html)"]
        if os.path.isfile(os.path.join(dst_dir, "figure_index.html")):
            index_toc += [f"### [Figure Index]({github_pages_url}/figure_index.html)"]
        if os.path.isfile(os.path.join(dst_dir, "python_index.html")):
            index_toc += [f"### [Python Module Index]({github_pages_url}/python_index.html)"]
        if os.path.isfile(os.path.join(dst_dir, "tag_index.html")):
            index_toc += [f"### [Tag Index]({github_pages_url}/tag_index.html)"]
        index_toc += [nb.readme for nb in self.notebooks]
        env = Environment(loader=FileSystemLoader("templates"))
        with open(os.path.join(dst_dir, "index.md"), 'w') as file:
            file.write(env.get_template('index.md.tpl').render(
                readme_toc=index_toc, page_title=github_repo_name, github_url=github_repo_url))

    def write_python_index(self):
        python_index = collections.defaultdict(list)
        IMPORT = re.compile(r"^\s*import\s*(?P<txt>\S+)")
        FROM = re.compile(r"^\s*from\s*(?P<txt>\w[\w|.]*)\s*import\s*(?P<fcn>[*|\w+][,\s*\w+]*)")
        for nb in self.notebooks:
            for cell  in nb.content.cells:
                if cell.cell_type == "code":
                    for line in cell.source.strip().splitlines():
                        m = IMPORT.match(line)
                        if m:
                            python_index[m.group("txt")].append(cell.metadata["nbpages"]["link"])
                        m = FROM.match(line)
                        if m:
                            for fcn in list(filter(None, re.split('[,|\s+]', m.group("fcn")))):
                                if fcn=='as':
                                    break
                                key = m.group("txt") + "." + fcn
                                python_index[key].append(cell.metadata["nbpages"]["link"])

        content = ""
        if python_index:
            print("- writing python index")
            python_index_file = os.path.join(dst_dir, "python_index")

            content += f"# [{github_repo_name}]({github_pages_url})\n"
            content += "\n## Index of Python Libraries used in this Repository\n"
            for key in sorted(python_index.keys(), key=str.casefold):
                if python_index[key]:
                    content += f"\n### {key}\n"
                    for link in python_index[key]:
                        content += f"* {link}\n"
        self.write_md2html("python_index", content)

    def write_tag_index(self):
        """Write tag index file for a collection of notebooks."""
        content = ""
        if self.tag_index:
            print("- writing tag index file")
            content += f"# [{github_repo_name}]({github_pages_url})\n"
            content += "\n## Tag Index\n"
            for tag in sorted(self.tag_index.keys(), key=str.casefold):
                content += f"* <a name={tag}></a>{tag}\n"
                for link in self.tag_index[tag]:
                    content += f"    - {link}\n"
        self.write_md2html("tag_index", content)

    def write_toc(self):
        """Write table of contents file for a collection of notebooks."""
        content = ""
        if self.notebooks:
            print("- writing table of contents file")
            content = f"# [{github_repo_name}]({github_pages_url})\n"
            for nb in self.notebooks:
                content += '\n' + '\n'.join(nb.toc) + '\n'
                if nb.markdown_figs:
                    content += "* Markdown Figures\n"
                    for txt, url in nb.markdown_figs:
                        content += "    - [{0}]({1})\n".format(txt if txt else url, url)
                if nb.markdown_links:
                    content += "* Markdown Links\n"
                    for txt, url in nb.markdown_links:
                        content += f"    - [{txt}]({url})\n"
                if nb.tags:
                    content += "* Tags: " + ", ".join([tag for tag in nb.tags]) + "\n"
        self.write_md2html("toc", content)

    def write_md2html(self, stem, content):
        STEM = os.path.join(dst_dir, stem)
        if content:
            with open(f"{STEM}.md", 'w') as f:
                f.write(content)
            os.system(f"notedown {STEM}.md > {STEM}.ipynb")
            os.system(f"jupyter nbconvert {STEM}.ipynb")
            os.remove(f"{STEM}.md")
            os.remove(f"{STEM}.ipynb")
        else:
            if os.path.isfile(f"{STEM}.html"):
                os.remove(f"{STEM}.html")
