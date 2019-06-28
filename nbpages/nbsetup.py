import os
import configparser

readme_template = """
[//]: # (DO NOT EDIT. README.md is generated by nbpages. Make changes templates/README.md.jinja.)
# {{ page_title }}

{% for line in readme_toc %}
{{ line }}
{% endfor %}
"""

notebook_header_template = """
*This notebook contains material from [{{ page_title }}]({{ page_url }});
content is available [on Github]({{ github_url }}).*
"""


def make_dir_if_needed(dir_name):
    """Create new directory if not present, and verify that it exists."""
    if not os.path.exists(dir_name):
        print(f"- creating {dir_name} directory")
        os.mkdir(dir_name)
    else:
        print(f"- {dir_name} directory already exists")
    assert os.path.exists(dir_name), f"{dir_name} directory not found in current working directory"


def write_template_if_needed(template_content, template_filename):
    """Create template file if needed, and verify that it exists."""
    fname = f"templates/{template_filename}"
    if not os.path.isfile(fname):
        with open(fname, 'w') as f:
            print(f"- writing {fname}")
            f.write(template_content)
    else:
        print(f"- {fname} already exists")


def nbsetup():
    """Setup directory if needed with default configuration and templates."""
    if os.path.isfile("README.md"):
        print("- moving README.md to README.md.bak")
        os.rename("README.md", "README.md.bak")
    make_dir_if_needed("notebooks")
    make_dir_if_needed("templates")
    write_template_if_needed(notebook_header_template, 'notebook_header.jinja')
    write_template_if_needed(readme_template, 'README.md.jinja')

    # create default templates/config if needed
    if not os.path.isfile("templates/config"):
        print(f"- creating default templates/config from .git/config")
        assert os.path.exists('.git'), ".git not found. Create a github repository."

        git_config = configparser.ConfigParser(strict=False)
        git_config.read('.git/config')

        github_url = git_config['remote "origin"']['url']
        github_user = github_url.rsplit('/')[-2]
        page_title = github_url.rsplit('/')[-1].split('.')[0]

        config = configparser.ConfigParser()
        config['NBPAGES'] = {'github_url': github_url,
                             'repository': '/'.join([github_user, page_title]),
                             'page_title': page_title,
                             'page_url': f"https://{github_user}.github.io/{page_title}"
                             }
        with open('templates/config', 'w') as f:
            print("- writing templates/config")
            config.write(f)
    else:
        print(f"- templates/config already exists")


if __name__ == "__main__":
    nbsetup()