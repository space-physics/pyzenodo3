""" Zenodo uploads from Python"""
from pathlib import Path
import json
import requests
from configparser import ConfigParser
from typing import Dict, Union, List

from .base import BASE_URL

HDR = {"Content-Type": "application/json"}


def meta(inifn: Path) -> Path:
    """ creates metadata for Zenodo upload.
    1. create dict() with metadata
    2. convert dict() to json
    3. write JSON to disk
    """
    SECT = "zenodo"
    inifn = Path(inifn).expanduser()

    Meta: Dict[str, dict] = {"metadata": {}}
    meta: Dict[str, Union[str, List[str], Dict[str, str]]] = {}

    C = ConfigParser(inline_comment_prefixes=("#", ";"))
    C.read(inifn)

    for k in C[SECT].keys():
        if k == "license":
            meta["license"] = {"id": C.get(SECT, k)}
            continue

        m = C.get(SECT, k)

        if "," in m:
            meta[k] = m.split(",")
        else:
            meta[k] = m

    # %% assemble JSON output
    Meta["metadata"] = meta
    # indent is optional, for human readability
    json_meta = json.dumps(Meta, indent="\t")

    outfn = inifn.with_suffix(".json")

    print("writing JSON metadata to", outfn)
    outfn.write_text(json_meta)

    return outfn


def check_token(token: str, base_url: str):
    if not isinstance(token, str) or not token:
        raise TypeError("Token need to be a string")

    r = requests.get(f"{base_url}/deposit/depositions", params={"access_token": token})

    if r.status_code != 200:
        raise requests.HTTPError(f"Token accept error, status code: {r.status_code}  {r.json()['message']}")


def get_token(token: Union[str, Path]) -> str:
    if Path(token).expanduser().is_file():
        token = Path(token).expanduser().read_text().strip()  # in case \n or spaces sneak in
    elif isinstance(token, str) and 100 > len(token) > 10:
        pass
    else:
        raise ValueError("API Token must be specified to upload to Zenodo")

    return token


def upload_meta(token: str, metafn: Path, depid: str):
    """upload metadata to zenodo"""

    if not metafn:
        raise ValueError("must specify API token or file containing the token")

    metafn = Path(metafn).expanduser()

    if not metafn.is_file():
        raise FileNotFoundError("meta JSON file is required")

    meta = metafn.read_text()

    r = requests.put(
        f"{BASE_URL}/deposit/depositions/{depid}", params={"access_token": token}, data=meta, headers=HDR  # json.dumps(meta),
    )

    if r.status_code != 200:
        raise requests.HTTPError(f"Error in metadata upload, status code: {r.status_code}   {r.json()['message']}")


def upload_data(token: str, datafn: Path, depid: str, base_url: str):

    r = requests.post(
        f"{base_url}/deposit/depositions/{depid}/files",
        params={"access_token": token},
        data={"filename": str(datafn)},
        files={"file": datafn.open("rb")},
    )

    if r.status_code != 201:
        raise requests.HTTPError(f"Error in data upload, status code: {r.status_code}   {r.json()['message']}")

    print(f"{datafn} ID = {depid} (DOI: 10.5281/zenodo.{depid})")


def create(token: str, base_url: str) -> str:

    r = requests.post(f"{base_url}/deposit/depositions", params={"access_token": token}, json={}, headers=HDR)

    if r.status_code != 201:
        raise requests.HTTPError(f"Error in creation, status code: {r.status_code}   {r.json()['message']}")
    # %% Get the deposition ID
    return r.json()["id"]


def upload(metafn: Path, datafn: Path, token: Union[str, Path], base_url=BASE_URL):
    """takes metadata and file and uploads to Zenodo"""

    datafn = Path(datafn).expanduser()
    assert datafn.is_file(), "for now, upload a file only"

    # %% token check
    token = get_token(token)

    check_token(token, base_url)
    # %% Create new submission
    depid = create(token, base_url)
    # %% Upload data
    upload_data(token, datafn, depid, base_url)

    # %% add metadata
    # upload_meta(token, metafn, depid)
