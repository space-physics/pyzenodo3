#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path
import pyzenodo3 as zen


def main():
    p = ArgumentParser(description='Upload data to Zenodo staging')
    p.add_argument('path', help='directory or file to upload to Zenodo')
    p.add_argument('-y', '--yes', help='upload to Zenodo, not just the sandbox',
                   action='store_true')
    P = p.parse_args()

    path = Path(P.path).expanduser()

    if path.is_file() or path.is_dir():
        pass
    else:
        raise FileNotFoundError(
            f'{path} does not seem to be a file or directory')

    zen


if __name__ == '__main__':
    main()
