# following https://stackoverflow.com/questions/13493288/python-cli-program-unit-testing

import pytest

import os

def test_entrypoint():
    assert 0 == os.system('nbpages --help')

def test_lint():
    assert 0 == os.system('nbpages --lint')

def test_metadata():
    assert 0 == os.system('nbpages --metadata')

def test_tags():
    assert 0 == os.system('nbpages --tags')

def test_get_cells():
    assert 0 != os.system('nbpages --get_cells')
    assert 0 == os.system('nbpages --get_cells exercises')

def test_search():
    assert 0 != os.system('nbpages --search')
    assert 0 == os.system('nbpages --search lint')

def test_publish():
    assert 0 == os.system('nbpages --publish')

def test_remove_cells():
    assert 0 != os.system('nbpages --remove_cells')
    assert 0 == os.system('nbpages --remove_cells exercises')

def test_remove_code():
    assert 0 == os.system('nbpages --remove_code')
