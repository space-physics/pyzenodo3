from pathlib import Path
import pytest

import pyzenodo3
import pyzenodo3.upload as zup

R = Path(__file__).parent
metain = R / "meta.ini"


@pytest.fixture
def zen():
    return pyzenodo3.Zenodo()


def test_search(zen):
    recs = zen.search("scivision")
    assert isinstance(recs, list)
    assert isinstance(recs[0], pyzenodo3.Record)


def test_meta():
    zup.meta(metain)

    assert metain.with_suffix(".json").is_file()


def test_download(zen):
    rec = zen.get_record("888276") # this is record related to scivision query search.

    rec.download("./")

    file_downloaded =  Path("./Geomagnetic%20Model%20of%20Brazil.ipynb")

    assert file_downloaded.is_file()

    file_downloaded.unlink()
