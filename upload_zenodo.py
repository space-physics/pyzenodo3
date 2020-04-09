#!/usr/bin/env python
"""
inspired by https://github.com/darvasd/upload-to-zenodo/
"""
from argparse import ArgumentParser, Namespace
import pyzenodo3.upload as zup
from pyzenodo3.base import BASE_URL


def cmdparse() -> Namespace:
    p = ArgumentParser(description="Upload data to Zenodo staging")
    p.add_argument("apikey", help="Zenodo API key", nargs="?")
    p.add_argument("inifn", help="mymeta.ini file with author, title, etc.")
    p.add_argument("path", help="directory or file to upload to Zenodo", nargs="?")
    p.add_argument("--use-sandbox", help="Use sandbox.zenodo.org instead of the real site.", action='store_true')
    return p.parse_args()


def main():
    p = cmdparse()

    metafn = zup.meta(p.inifn)

    if p.use_sandbox:
        base_url = "https://sandbox.zenodo.org/api"
    else:
        base_url = BASE_URL

    zup.upload(metafn, p.path, p.apikey, base_url=base_url)


if __name__ == "__main__":
    main()
