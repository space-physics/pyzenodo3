#!/usr/bin/env python3
import pyzenodo3
import pytest


@pytest.fixture()
def zen():
    return pyzenodo3.Zenodo()


def test_search(zen):
    recs = zen.search('scivision')
    assert isinstance(recs, list)
    assert isinstance(recs[0], pyzenodo3.Record)
