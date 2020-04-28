# -*- coding: utf-8 -*-
import requests
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urlencode

BASE_URL = "https://zenodo.org/api/"


class Record:
    def __init__(self, data, zenodo, base_url: str = BASE_URL) -> None:
        self.base_url = base_url
        self.data = data
        self._zenodo = zenodo

    def _row_to_version(self, row: Tag) -> Dict[str, str]:
        link = row.select("a")[0]
        linkrec = row.select("a")[0].attrs["href"]
        if not linkrec:
            raise KeyError("record not found in parsed HTML")

        texts = row.select("small")
        recmatch = re.match(r"/record/(\d*)", linkrec)
        if not recmatch:
            raise LookupError("record match not found in parsed HTML")

        recid = recmatch.group(1)

        return {
            "recid": recid,
            "name": link.text,
            "doi": texts[0].text,
            "date": texts[1].text,
            "original_version": self._zenodo.get_record(recid).original_version(),
        }

    def get_versions(self) -> list:
        url = f"{self.base_url}srecords?all_versions=1&size=100&q=conceptrecid:{self.data['conceptrecid']}"

        print(url)

        data = requests.get(url).json()

        return [Record(hit, self._zenodo) for hit in data["hits"]["hits"]]

    def get_versions_from_webpage(self) -> list:
        """Get version details from Zenodo webpage (it is not available in the REST api)"""
        res = requests.get("https://zenodo.org/record/" + self.data["conceptrecid"])
        soup = BeautifulSoup(res.text, "html.parser")
        version_rows = soup.select(".well.metadata > table.table tr")
        if len(version_rows) == 0:  # when only 1 version
            return [
                {
                    "recid": self.data["id"],
                    "name": "1",
                    "doi": self.data["doi"],
                    "date": self.data["created"],
                    "original_version": self.original_version(),
                }
            ]
        return [self._row_to_version(row) for row in version_rows if len(row.select("td")) > 1]

    def original_version(self):
        for identifier in self.data["metadata"]["related_identifiers"]:
            if identifier["relation"] == "isSupplementTo":
                return re.match(r".*/tree/(.*$)", identifier["identifier"]).group(1)
        return None

    def __str__(self):
        return str(self.data)


class Zenodo:
    def __init__(self, api_key: str = "", base_url: str = BASE_URL) -> None:
        self.base_url = base_url
        self._api_key = api_key
        self.re_github_repo = re.compile(r".*github.com/(.*?/.*?)[/$]")

    def search(self, search: str) -> List[Record]:
        """search Zenodo record for string `search`

        :param search: string to search
        :return: Record[] results
        """
        search = search.replace("/", " ")  # zenodo can't handle '/' in search query
        params = {"q": search}

        recs = self._get_records(params)

        if not recs:
            raise LookupError(f"No records found for search {search}")

        return recs

    def _extract_github_repo(self, identifier):
        matches = self.re_github_repo.match(identifier)

        if matches:
            return matches.group(1)

        raise LookupError(f"No records found with {identifier}")

    def find_record_by_github_repo(self, search: str):
        records = self.search(search)
        for record in records:
            if "metadata" not in record.data or "related_identifiers" not in record.data["metadata"]:
                continue

            for identifier in [identifier["identifier"] for identifier in record.data["metadata"]["related_identifiers"]]:
                repo = self._extract_github_repo(identifier)

                if repo and repo.upper() == search.upper():
                    return record

        raise LookupError(f"No records found in {search}")

    def find_record_by_doi(self, doi: str):
        params = {"q": f"conceptdoi:{doi.replace('/', '*')}"}
        records = self._get_records(params)

        if len(records) > 0:
            return records[0]
        else:
            params = {"q": "doi:%s" % doi.replace("/", "*")}
            return self._get_records(params)[0]

    def get_record(self, recid: str) -> Record:

        url = self.base_url + "records/" + recid

        return Record(requests.get(url).json(), self)

    def _get_records(self, params: Dict[str, str]) -> List[Record]:
        url = self.base_url + "records?" + urlencode(params)

        return [Record(hit, self) for hit in requests.get(url).json()["hits"]["hits"]]
