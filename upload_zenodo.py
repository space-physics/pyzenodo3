#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path
import json
import requests

SANDBOX_URL = "https://sandbox.zenodo.org/api"
BASE_URL = "https://zenodo.org/api"


def upload(metadata, path: Path, token: str, live: bool):
    assert path.is_file(), "for now, a file only"

    base_url = BASE_URL if live else SANDBOX_URL

    if not token or not isinstance(token, str):
        raise ValueError('API Token must be specified to upload to Zenodo')
# %% Create new paper submission
    url = f"{base_url}/deposit/depositions/?access_token={token}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=metadata, headers=headers)

    if response.status_code != 200:
        raise requests.HTTPError(f"Error happened during submission, status code: {response.status_code}")
# %% Get the submission ID
    submission_id = json.loads(response.text)["id"]
# %% Upload
    url = f"{base_url}/api/deposit/depositions/{submission_id}/files?access_token={token}"
    upload_metadata = {'filename': str(path)}
    files = {'file': path.open('rb')}

    response = requests.post(url, data=upload_metadata, files=files)

    if response.status_code != 200:
        raise requests.HTTPError(f"Error happened during submission, status code: {response.status_code}")

    print(f"{path} submitted with submission ID = {submission_id} (DOI: 10.5281/zenodo.{submission_id})")


def main():
    p = ArgumentParser(description='Upload data to Zenodo staging')
    p.add_argument('path', help='directory or file to upload to Zenodo')
    p.add_argument('apikey', help='Zenodo API key')
    p.add_argument('-y', '--yes', help='upload to Zenodo, not just the sandbox',
                   action='store_true')
    P = p.parse_args()

    path = Path(P.path).expanduser()

    if path.is_file() or path.is_dir():
        pass
    else:
        raise FileNotFoundError(
            f'{path} does not seem to be a file or directory')

    upload(path, P.apikey, P.yes)


if __name__ == '__main__':
    main()
