#!/usr/bin/env python3
""" examples of searching Zenodo"""
import pyzenodo3

zen = pyzenodo3.Zenodo()

Recs = zen.search('scivision')
# %%
Rec = zen.find_record_by_github_repo('scivision/lowtran')

vers = Rec.get_versions_from_webpage()

print(vers)
