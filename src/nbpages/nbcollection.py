import re
import collections
import itertools
import json
import configparser
import glob
import os
import shutil
import nbformat
from nbformat.v4.nbbase import new_markdown_cell, new_notebook, new_code_cell
from nbconvert import HTMLExporter
from jinja2 import Environment, FileSystemLoader

def read_config():

    global config

    # configuration file
    config_file = "nbpages.cfg"
    assert os.path.exists(config_file), f"configuration file {config_file} not found. Run nbpages --setup"

    config = configparser.ConfigParser()
    config.read(config_file)
    config = config["nbpages"]

    # source and destination directories
    assert config["src_dir"] != config["dst_dir"], "notebook source and destination directories must be different"
    assert os.path.exists(config["src_dir"]), f"notebook source directory '{config['src_dir']}' not found"
    assert os.path.exists(config["dst_dir"]), f"notebook destination directory '{config['dst_dir']}' not found"


# tags
NOTEBOOK_HEADER_TAG = "<!--NOTEBOOK_HEADER-->"
NAVBAR_TAG = "<!--NAVIGATION-->\n"
DATA_IMPORT_TAG = "# IMPORT DATA FILES USED BY THIS NOTEBOOK"
SOLUTION_CODE = "### BEGIN SOLUTION(.*)### END SOLUTION"
HIDDEN_TESTS = "### BEGIN HIDDEN TESTS(.*)### END HIDDEN TESTS"

# regular expressions and patterns
NB_FILENAME = re.compile(r'(\d\d|[A-Z])\.(\d\d)-(.*)\.ipynb')
MARKDOWN_FIG = re.compile(r'(?:!\[(?P<txt>.*?)\]\((?P<url>.*?)\))')
MARKDOWN_HEADER = re.compile(r'(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)')
MARKDOWN_LINK = re.compile(r'(?:[^!]\[(?P<txt>.*?)\]\((?P<url>.*?)\))')


# function to sort numbered section headings in natural order
def natsort(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


class Nb:

    def __init__(self, filename, chapter, section):
        self.filename = filename
        self.chapter = str(int(chapter)) if chapter.isdigit() else chapter
        self.section = str(int(section))
        self.content = nbformat.read(os.path.join(config["src_dir"], filename), as_version=4)
        self.html_filename = os.path.splitext(self.filename)[0] + ".html"
        self.html_url = f"{config['github_pages_url']}/{self.html_filename}"

    def __gt__(self, nb):
        return self.filename > nb.filename

    def __str__(self):
        return self.filename

    @property
    def data_import_links(self):
        """Return list of (datapath, url) pairs."""
        dirpath = os.path.join(config["src_dir"], config["data_subdir"])
        assert os.path.exists(dirpath), f"- data subdirectory {dirpath} was not found"
        data = [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))
                and not f.startswith('.') and f.endswith('.csv') or f.endswith('.txt')]
        data = filter(lambda f: any([re.search(f, cell.source) for cell in self.content.cells]), data)
        return [(os.path.join(config["data_subdir"], f), f"{config['github_pages_url']}/data/{f}") for f in data]

    @property
    def figure_links(self):
        """Return list of (fig, url) pairs."""
        dirpath = os.path.join(config["src_dir"], config["figures_subdir"])
        assert os.path.exists(dirpath), f"- figures subdirectory {dirpath} was not found"
        figures = [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))
                and not f.startswith('.') and not f.endswith('.tex') and not f.endswith('.pdf')]
        figures = filter(lambda f: any([re.search(f, cell.source) for cell in self.content.cells]), figures)
        return [(os.path.join(config["figures_subdir"], figure), f"{config['github_pages_url']}/figures/{figure}") for figure in figures]

    @property
    def html_anchor_tags(self):
        """Return a list of html anchor tags."""
        return self.findall_markdown_cells(r'<a [^>]*>')

    @property
    def html_img_tags(self):
        """Return a list of html img tags."""
        return self.findall_markdown_cells(r'<img[^>]*>')

    @property
    def link(self):
        """Return a markdown link to the html view."""
        return f"[{self.numbered_title}]({self.html_url})"

    @property
    def markdown_figs(self):
        """Return a list of markdown figures in the markdown cells."""
        return self.findall_markdown_cells(MARKDOWN_FIG)

    @property
    def markdown_links(self):
        """Return a list of markdown links in the markdown cells."""
        return self.findall_markdown_cells(MARKDOWN_LINK)

    @property
    def orphan_headers(self):
        """"Return a list of headers not in the first line of a cell."""
        orphans = []
        for cell in self.markdown_cells():
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
    def title(self):
        """Return notebook title by extracting the first level one header."""
        for cell in self.markdown_cells():
            m = MARKDOWN_HEADER.match(cell.source)
            if m and len(m.group('level')) == 1:
                return m.group('header').strip()
        return None

    @property
    def toc(self):
        """Return formatted list of markdown links to cells starting with a markdown header."""
        toc = []
        header_cells = (cell for cell in self.markdown_cells() if cell.source.startswith("##"))
        for header_cell in header_cells:
            header = header_cell.source.splitlines()[0].strip().split()
            txt = ' '.join(header[1:])
            url = '#'.join([self.html_url, '-'.join(header[1:])])
            toc.append("    " * (len(header[0]) - 2) + f"- [{txt}]({url})")
        return toc

    def findall_markdown_cells(self, regex):
        return [s for cell in self.markdown_cells() for s in re.findall(regex, cell.source)]

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
        """Return a list of all cells with a specified tag."""
        return [cell for cell in self.content.cells if 'tags' in cell.metadata.keys() and tag in cell.metadata['tags']]

    def lint(self):
        """Print list of lint items."""
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

    def markdown_cells(self):
        """Iterator for all markdown cells excluding navbars and header"""
        for cell in self.content.cells:
            if cell.cell_type == "markdown" and not cell.source.startswith(NOTEBOOK_HEADER_TAG) \
                    and not cell.source.startswith(NAVBAR_TAG):
                yield cell

    def remove_cells(self, tag):
        """Remove cells with a specified tag."""
        tagged_cells = self.get_cells(tag)
        if tagged_cells:
            print(f"- removing cells tagged {tag} from {self.filename}")
            self.content.cells = filter(lambda cell: cell not in tagged_cells, self.content.cells)

    def replace_code(self, pattern, repl):
        """Find and replace a regular expression from code cells."""
        regex = re.compile(pattern, re.DOTALL)
        for cell in self.content.cells:
            if cell.cell_type == "code" and regex.findall(cell.source):
                cell.source = regex.sub(repl, cell.source)
                print(f"- code removed from {self.filename}")


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
    def numbered_title(self):
        """Return formatted title with numbering for a notebook."""
        return f"{self.title}"

    @property
    def toc(self):
        """Return table of contents entry for a notebook."""
        toc = Nb.toc.fget(self)
        toc.insert(0, "### " + self.link)
        return toc


class NbCollection:

    def __init__(self, src_dir=None, dst_dir=None):
        read_config()
        for k in config.keys():
            print(k, config[k])
        self.notebooks = []
        self.src_dir = src_dir if src_dir else config["src_dir"]
        self.dst_dir = dst_dir if dst_dir else config["dst_dir"]
        for filename in sorted(os.listdir(self.src_dir)):
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

        # property caches
        self._data = []
        self._data_index = {}
        self._figures = []
        self._figure_index = {}
        self._tag_index = collections.defaultdict(list)

    def get_files(self, sub_dir, suffixes):
        """Return an iterator over the file names in a notebooks subdirectory which have any of the given suffixes"""
        path = os.path.join(self.src_dir, sub_dir)
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and not f.startswith('.') and any(list(map(f.endswith, suffixes))):
                yield f

    def index_terms(self, terms):
        """Return a dictionary of deduplicated links to cells indexed by the entries in terms."""
        index = dict()
        for term in terms:
            links = [cell.metadata["nbpages"]["link"] for nb in self.notebooks
                     for cell in nb.content.cells if re.search(term, cell.source) if "nbpages" in cell.metadata.keys()]
            index[term] = list(dict.fromkeys(links))
        return index

    @property
    def data_index(self):
        """Return deduplicated dictionary of links indexed by data file names."""
        if not self._data_index:
            self._data_index = self.index_terms(self.get_files(config["data_subdir"], ['.csv', '.txt']))
        return self._data_index

    @property
    def figure_index(self):
        """Return deduplicated dictionary of links indexed by figure file names."""
        if not self._figure_index:
            self._figure_index  = self.index_terms(self.get_files(config["figures_subdir"], ['.png', '.jpg']))
        return self._figure_index

    @property
    def python_index(self):
        python_index = collections.defaultdict(list)
        IMPORT_AS = re.compile(r"^\s*import\s+((?P<module>\w[\w|\.]*)\s+as\s+(?P<name>\w+))")
        IMPORT = re.compile(r"^\s*import\s+(?P<txt>[*|\w+][,\s*\w+]*)")
        FROM = re.compile(r"^\s*from\+(?P<txt>\w[\w|.]*)\s*import\s*(?P<fcn>[*|\w+][,\s*\w+]*)")
        for nb in self.notebooks:
            for cell in nb.content.cells:
                if cell.cell_type == "code":
                    if "nbpages" in cell.metadata.keys():
                        for line in cell.source.strip().splitlines():
                            m = IMPORT.match(line)
                            if m:
                                for lib in list(filter(None, re.split(r'[,|\s+]', m.group("txt")))):
                                    if lib == 'as':
                                        break
                                    python_index[lib].append(cell.metadata["nbpages"]["link"])
                            m = FROM.match(line)
                            if m:
                                for fcn in list(filter(None, re.split(r'[,|\s+]', m.group("fcn")))):
                                    if fcn == 'as':
                                        break
                                    key = m.group("txt") + "." + fcn
                                    python_index[key].append(cell.metadata["nbpages"]["link"])
        return python_index

    @property
    def tag_index(self):
        """Return dictionary of sorted list of links to cells indexed by tags."""
        if not self._tag_index:
            for nb in self.notebooks:
                for tag, links in nb.tags.items():
                    self._tag_index[tag].extend(links)
            for tag in self._tag_index.keys():
                self._tag_index[tag] = list(sorted(set(self._tag_index[tag]), key=natsort))
        return self._tag_index

    def get_cells(self, tag):
        """Return a new notebook created from cells with a specified tag."""
        cells = []
        for nb in self.notebooks:
            cells.extend(nb.get_cells(tag))
        nb = new_notebook(cells=cells)
        nb["metadata"]["kernelspec"] = {"name": "python3"}
        return nbformat.writes(nb)

    def insert_data_imports(self):
        """Insert code cell to import data files required by notebooks."""
        for nb in self.notebooks:
            if nb.data_import_links:
                import_cell = None
                for cell in nb.content.cells:
                    if cell.cell_type == "code" and cell.source.startswith(DATA_IMPORT_TAG):
                        print(f"- amending data import for {nb.filename}")
                        import_cell = cell
                        break
                if import_cell is None:
                    print(f"- inserting data import for {nb.filename}")
                    nb.content.cells.insert(2, new_code_cell())
                    import_cell = nb.content.cells[2]
                content = f"{DATA_IMPORT_TAG}" "\n"
                content += "import os,  requests\n\n"
                content += f"file_links = [" + ",\n    ".join([f"(\"{path}\", \"{url}\")" for (path, url) in nb.data_import_links]) + "]\n"
                content += """
# This cell has been added by nbpages. Run this cell to download data files required for this notebook.

for filepath, fileurl in file_links:
    stem, filename = os.path.split(filepath)
    if stem:
        if not os.path.exists(stem):
            os.mkdir(stem)
    if not os.path.isfile(filepath):
        with open(filepath, 'wb') as f:
            response = requests.get(fileurl)
            f.write(response.content)
"""
                import_cell.source = content

    def insert_headers(self):
        env = Environment(loader=FileSystemLoader(config["templates_dir"]))
        template = env.get_template('notebook_header.tpl')
        source = NOTEBOOK_HEADER_TAG + template.render(page_title=config["github_repo_name"],
                                                       page_url=config["github_pages_url"],
                                                       github_url=config["github_repo_url"])
        for nb in self.notebooks:
            """Insert header to notebook contents."""
            if nb.content.cells[0].source.startswith(NOTEBOOK_HEADER_TAG):
                print('- amending header for {0}'.format(nb.filename))
                nb.content.cells[0].source = source
            else:
                print('- inserting header for {0}'.format(nb.filename))
                nb.content.cells.insert(0, new_markdown_cell(source))

    def insert_navbars(self):
        """Insert navigation bars."""

        # colab opens from github repository
        COLAB_LINK = f'<p><a href="https://colab.research.google.com/github/{config["github_user_name"]}/{config["github_repo_name"]}' + \
            '/blob/master/{dst}/{notebook_filename}"> ' + \
            '<img align="left" src="https://colab.research.google.com/assets/colab-badge.svg"' + \
            ' alt="Open in Colab" title="Open in Google Colaboratory"></a>'

        # download from github pages
        DOWNLOAD_LINK = f'<p><a href="{config["github_pages_url"]}' + \
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
            navbar += f" [Tag Index](tag_index.html) |" if self.tag_index else ""
            navbar += f" [{next_nb.title}]({next_nb.html_url}) >" if next_nb else ""
            navbar += COLAB_LINK.format(dst=self.dst_dir, notebook_filename=nb.filename)
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
        """Report style issues."""
        for nb in self.notebooks:
            nb.lint()
        for data in sorted(list(self.get_files(config["data_subdir"], ['.csv', '.txt'])), key=str.casefold):
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
        for figure in sorted(list(self.get_files(config["figures_subdir"], ['.png', '.jpg'])), key=str.casefold):
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
        """Print metadata."""
        for nb in self.notebooks:
            print(f"\n{nb.filename}")
            print(json.dumps(nb.content['metadata'], sort_keys=True, indent=4))

    def remove_cells(self, tag):
        for nb in self.notebooks:
            nb.remove_cells(tag)

    def remove_code(self):
        for nb in self.notebooks:
            nb.replace_code(SOLUTION_CODE, "# YOUR SOLUTION HERE")
            nb.replace_code(HIDDEN_TESTS, "")

    def search(self, pattern):
        regex = re.compile(pattern)
        for nb in self.notebooks:
            for cell in nb.content.cells:
                if regex.search(cell.source):
                    print(nb.filename)
                    break

    def remove(self, pattern):
        assert self.dst_dir != self.src_dir, "destination directory must be different than source"
        html_files = glob.glob(os.path.join(self.dst_dir, pattern))
        for f in html_files:
            print(f"- removing {f}")
            os.remove(f)

    def write_data_index(self):
        """Write data_index.html and copy data files to destination directory."""
        content = ""
        self.remove(os.path.join(config["data_subdir"], "*"))
        if self.data_index:
            print("- writing data index")
            content += f"# [{config['github_repo_name']}]({config['github_pages_url']})\n"
            content += "\n## Index of Data files in this Repository\n"
            for data, links in sorted(self.data_index.items(), key=lambda x: natsort(x[0])):
                if links:
                    content += f"\n### {data}\n"
                    content += f"![{data}]({config['data_subdir']}/{data})\n"
                    for link in links:
                        content += f"* {link}\n"
                    data_src = os.path.join(self.src_dir, config["data_subdir"], data)
                    data_dst = os.path.join(self.dst_dir, config["data_subdir"], data)
                    print(f"- copying {data_src} to {data_dst}")
                    shutil.copy(data_src, data_dst)
        self.write_md2html("data_index", content)

    def write_figure_index(self):
        content = ""
        self.remove(os.path.join(config["figures_subdir"], "*"))
        if self.figure_index:
            print("- writing figure index")
            content += f"# [{config['github_repo_name']}]({config['github_pages_url']})\n"
            content += "\n## Index of Figures in this Repository\n"
            for figure, links in sorted(self.figure_index.items(), key=lambda x: natsort(x[0])):
                if links:
                    content += f"\n### {figure}\n"
                    content += f"![{figure}]({config['figures_subdir']}/{figure})\n"
                    for link in links:
                        content += f"* {link}\n"
                    figure_src = os.path.join(self.src_dir, config["figures_subdir"], figure)
                    figure_dst = os.path.join(self.dst_dir, config["figures_subdir"], figure)
                    print(f"- copying {figure_src} to {figure_dst}")
                    shutil.copy(figure_src, figure_dst)
        self.write_md2html("figure_index", content)

    def write_html(self):
        """Create and write html files to the destination directory."""
        html_exporter = HTMLExporter()
        html_exporter.template_file = os.path.join(config["templates_dir"], "notebook.tpl")
        for nb in self.notebooks:
            (body, resources) = html_exporter.from_notebook_node(nb.content)
            body = re.sub('{github_user_name}', config["github_user_name"], body)
            body = re.sub('{github_repo_name}', config["github_repo_name"], body)
            html_path = os.path.join(self.dst_dir,  os.path.splitext(nb.filename)[0] + ".html")
            print(f"- writing {html_path}")
            with open(html_path, 'w') as f:
                f.write(body)

    def write_ipynb(self):
        """Write notebooks to the destination directory."""
        for nb in self.notebooks:
            nbformat.write(nb.content, os.path.join(self.dst_dir, nb.filename))

    def write_index_html(self):
        """Write index.md using the index.md.tpl template."""
        print("- writing index.md")
        index_toc = [f"### [Table of Contents]({config['github_pages_url']}/toc.html)"] if self.notebooks else []
        if os.path.isfile(os.path.join(self.dst_dir, "data_index.html")):
            index_toc += [f"### [Data Index]({config['github_pages_url']}/data_index.html)"]
        if os.path.isfile(os.path.join(self.dst_dir, "figure_index.html")):
            index_toc += [f"### [Figure Index]({config['github_pages_url']}/figure_index.html)"]
        if os.path.isfile(os.path.join(self.dst_dir, "python_index.html")):
            index_toc += [f"### [Python Module Index]({config['github_pages_url']}/python_index.html)"]
        if os.path.isfile(os.path.join(self.dst_dir, "tag_index.html")):
            index_toc += [f"### [Tag Index]({config['github_pages_url']}/tag_index.html)"]
        index_toc += [f"- {nb.link}" if type(nb) == Section else f"\n### {nb.link}" for nb in self.notebooks]
        env = Environment(loader=FileSystemLoader("templates"))
        with open(os.path.join(self.dst_dir, "index.md"), 'w') as f:
            f.write(env.get_template('index.md.tpl').render(
                readme_toc=index_toc, page_title=config['github_repo_name'], github_url=config['github_repo_url']))

    def write_python_index(self):
        content = ""
        if self.python_index:
            print("- writing python index")
            content += f"# [{config['github_repo_name']}]({config['github_pages_url']})\n"
            content += "\n## Index of Python Libraries used in this Repository\n"
            for key in sorted(self.python_index.keys(), key=str.casefold):
                if self.python_index[key]:
                    content += f"\n### {key}\n"
                    for link in self.python_index[key]:
                        content += f"* {link}\n"
        self.write_md2html("python_index", content)

    def write_tag_index(self):
        """Write tag index."""
        content = ""
        if self.tag_index:
            print("- writing tag index file")
            content += f"# [{config['github_repo_name']}]({config['github_pages_url']})\n"
            content += "\n## Tag Index\n"
            for tag in sorted(self.tag_index.keys(), key=str.casefold):
                content += f"* <a name={tag}></a>{tag}\n"
                for link in self.tag_index[tag]:
                    content += f"    - {link}\n"
        self.write_md2html("tag_index", content)

    def write_toc(self):
        """Write table of contents."""
        content = ""
        if self.notebooks:
            print("- writing table of contents file")
            content = f"# [{config['github_repo_name']}]({config['github_pages_url']})\n"
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
                if nb.figure_links:
                    content += "* Figure files used\n"
                    for txt, url in nb.figure_links:
                        content += f"    - [{txt}]({url})\n"

        self.write_md2html("toc", content)

    def write_md2html(self, stem, content):
        dir_stem = os.path.join(self.dst_dir, stem)
        if content:
            with open(f"{dir_stem}.md", 'w') as f:
                f.write(content)
            os.system(f"notedown {dir_stem}.md > {dir_stem}.ipynb")
            os.system(f"jupyter nbconvert {dir_stem}.ipynb")
            os.remove(f"{dir_stem}.md")
            os.remove(f"{dir_stem}.ipynb")
        else:
            # if no content, remove old file
            if os.path.isfile(f"{dir_stem}.html"):
                os.remove(f"{dir_stem}.html")
