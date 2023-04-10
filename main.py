from pyzenodo3 import Zenodo


zen = Zenodo()

recs = zen.search("scivision")


for i in recs:
    print(i.data)
    print("\n"*10)
