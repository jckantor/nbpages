import pytest

from nbpages import Index

def test_index_import():
    pass

def test_index_constructor():
    """Test construction of an Index object"""
    assert type(Index()) == Index

def test_index_set_and_get():
    my_index = Index()
    my_index['key'] = 12
    assert my_index['key'] == 12

