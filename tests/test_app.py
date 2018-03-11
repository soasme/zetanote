import pytest
from zetanote.app import truncate

def test_truncate():
    assert truncate('a' * 50) == 'a' * 20 + '...'

