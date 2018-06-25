""" Zenodo uploads from Python"""
from pathlib import Path
import json
import requests
from configparser import ConfigParser
from typing import Dict, Union, List

SANDBOX_URL = "https://sandbox.zenodo.org/api"
BASE_URL = "https://zenodo.org/api"


def meta(inifn: Path) -> Path:
    """ creates metadata for Zenodo upload.
    1. create dict() with metadata
    2. convert dict() to json
    3. write JSON to disk
    """
    SECT = 'zenodo'
    inifn = Path(inifn).expanduser()

    Meta: Dict[str, dict] = {'metadata': {}}
    meta: Dict[str, Union[str, List[str], Dict[str, str]]] = {}

    C = ConfigParser(inline_comment_prefixes=('#', ';'))
    C.read(inifn)

    for k in C[SECT].keys():
        if k == 'license':
            meta['license'] = {'id': C.get(SECT, k)}
            continue

        m = C.get(SECT, k)

        if ',' in m:
            meta[k] = m.split(',')
        else:
            meta[k] = m

# %% assemble JSON output
    Meta['metadata'] = meta
    # indent is optional, for human readability
    json_meta = json.dumps(Meta, indent="\t")

    outfn = inifn.with_suffix('.json')

    print('writing JSON metadata to', outfn)
    outfn.write_text(json_meta)

    return outfn


def upload(metafn: Path, datafn: Path, token: str, live: bool):
    """takes metadata and file and uploads to Zenodo"""

    metafn = Path(metafn).expanduser()
    datafn = Path(datafn).expanduser()

    if not metafn.is_file():
        raise FileNotFoundError('meta JSON file is required')

    assert datafn.is_file(), "for now, upload a file only"

    meta = metafn.read_text()

    base_url = BASE_URL if live else SANDBOX_URL

    if not token or not isinstance(token, str):
        raise ValueError('API Token must be specified to upload to Zenodo')
# %% Create new paper submission
    url = f"{base_url}/deposit/depositions/?access_token={token}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=meta, headers=headers)

    if response.status_code != 200:
        raise requests.HTTPError(f"Error happened during submission, status code: {response.status_code}")
# %% Get the submission ID
    submission_id = json.loads(response.text)["id"]
# %% Upload
    url = f"{base_url}/api/deposit/depositions/{submission_id}/files?access_token={token}"

    upload_metadata = {'filename': str(metafn)}

    files = {'file': datafn.open('rb')}

    response = requests.post(url, data=upload_metadata, files=files)

    if response.status_code != 200:
        raise requests.HTTPError(f"Error happened during submission, status code: {response.status_code}")

    print(f"{datafn} submitted with submission ID = {submission_id} (DOI: 10.5281/zenodo.{submission_id})")
