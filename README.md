# PyZenodo

[![DOI](https://zenodo.org/badge/138543765.svg)](https://zenodo.org/badge/latestdoi/138543765)
![Actions Status](https://github.com/space-physics/pyzenodo3/workflows/ci/badge.svg)
[![pypi versions](https://img.shields.io/pypi/pyversions/pyzenodo3.svg)](https://pypi.python.org/pypi/pyzenodo3)
[![PyPi Download stats](http://pepy.tech/badge/pyzenodo3)](http://pepy.tech/project/pyzenodo3)

Pure Python wrapper for [Zenodo REST API](http://developers.zenodo.org/).

Allows upload / download of data from Zenodo.

## Install

```sh
pip install pyzenodo3
```

Latest development

```sh
git clone https://github.com/scivision/pyzenodo3

pip install -e pyzenodo3
```

## Usage

Here are several examples of using Zenodo from Python 3.
All of them assume you have first:

```python
import pyzenodo3

zen = pyzenodo3.Zenodo()
```

### Upload file to Zenodo

0. Get a Zenodo `deposit:write` [API Token](https://zenodo.org/account/settings/applications/tokens/new/).
   This token must remain private, NOT uploaded to GitHub, etc.!
1. create a simple text file `mymeta.ini` containing title, author etc. (see the example `meta.ini` in this repo)
2. upload file to Zenodo  (myApiToken is the cut-n-pasted Zenodo API text token)

   ```sh
   ./upload_zenodo.py myApiToken mymeta.ini myfile.zip
   ```


### Find Zenodo record by Github repo

```python
Rec = zen.find_record__by_github_repo('scivision/lowtran')
```
This Zenodo Record contains the metadata that can be further manipulated in a simple class containing the data in dictionaries, with a few future helper methods.

### Find Zenodo records by Github username

```python
Recs = zen.search('scivision')
```
Recs is a `list` of Zenodo Records for the GitHub username queried, as in the example above.

## Notes

* We don't use `deposit:publish` API token to keep a human-in-the-loop in case of hacking of sensor nodes.
