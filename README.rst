nbpages
=======

``nbpages`` is a command line tool for managing a collection of Jupyter notebooks published on
`Github Pages <https://pages.github.com>`_ . This project was inspired by the tools included with the
`Python Data Science Handbook <https://github.com/jakevdp/PythonDataScienceHandbook>`_ by
`Jake Vanderplas <https://github.com/jakevdp>`_.

Installation
------------

    pip install nbpages

To upgrade a previously installed version to the latest version

    pip install nbpages --upgrade

(Advanced Users) For an editable installation from a local clone of the git repo, use:

    pip install --editable .

An editable installation will allow you keep your installation of nbpages in sync with github using `git pull` commands.

Setting up the notebook repository
----------------------------------

Step 1. [Create a repository on Github.com](https://help.github.com/en/articles/creating-a-new-repository). A minimal
repository will include README.md, .gitignore (typically the python option), and a license. Clone the
repository to a local directory using either the command line or the "Code > Open with Github Desktop" menu option.

Step 2. Open a terminal/command window on your laptop, and navigate to the top level directory of the local repository
created in Step 1. Issue the command

    nbpages --setup

This will setup a `docs`, `notebooks`, and `templates` directory, load several templates into the templates directory,
and create an `nbpages.cfg` configuration file. The templates and configuration file can be edited to change from
default settings. When complete, push these changes to the remote git repository.

Step 3. Github Pages are enabled in the settings tab of the remote repository. Scroll down to the Github Pages
heading. For source select `master branch /docs folder` and choose an appropriate theme. Selecting a theme will insert
a file named `_config.yml` in the `docs` folder. If you wish to include a logo for the theme, add a line
`logo: image_url` to `_config.yml` where `image_url` is a url for the desired logo image. Finally, on the main
repository page you may wish to click `edit` to add a brief description and the github pages url as the website for the
repository. When finished, sync these changes to the local repository.

Step 4. In the top level directory of the local repository, run the command

    nbpages --publish

This will create additional table of contents and tag_index files in the `docs` directory. Commit and push these changes
to the remote directory. At this stage you have a published an empty collection of notebooks to github pages.

Notebook organization
---------------------

Notebooks are maintained within the `notebooks` directory. Thare are organized into a chapter/section heirarchy
using a filename prefix. Filenames have an `nn.mm-` prefix where`nn` refers to the chapter number or, if a letter, to
an Appendix. The digits `mm` refers to the section number. Section `00` is reserved to hold the chapter title and
any introductory material. The notebooks must also have the usual `.ipynb` suffix.

Normal usage
------------

Following setup, the normal use of `nbpages` is to execute the command line

    nbpages --publish

from the top level directory of the notebook repository. Normally this command would be between completing edits or
additions to the notebooks and prior to a github commit. The command will

* add or amend headers and navigation bars in all notebooks,
* write a table of contents file
* write a keyword index
* write index.md using the template file

Removing solution and hidden code
---------------------------------

`nbpages` can be used to manage a collection of notebooks that serve as course notes that incorporate exercises
and homework assignments. For that purpose, the command line

    nbpages --remove_code --publish

will selectively remove code segments from code cells. Code segments beginning and ending with

    ### BEGIN SOLUTION
    ... python code ...
    ### END SOLUTION

are replaced with

    # YOUR SOLUTION HERE

Code segments beginning and ending with

    ### BEGIN HIDDEN TESTS
    ... python code ...
    ### END HIDDEN TESTS

are removed with no replacement text.

Utilities
---------

To help achieve a consistent style over a collection of notebooks, use the command

    nbpages --lint

to locate some forms of notebook 'lint'.  A current list of additional features can be found

    nbpages --help

A summary of notebook metadata, such as python version last used to run the notebooks, is printed to stdout with

    nbpages  --metadata





Documentation
-------------

Documentation is available on the `nbpages` website
`https://jckantor.github.io/nbpages/ <https://jckantor.github.io/nbpages/>?`_.
