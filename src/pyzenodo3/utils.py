import requests
import hashlib
import urllib
from pathlib import Path
#FILE_PATH_TYPE = Union(str, pathlib.Path )

def calculate_md5(file_path, chunk_size =1024):
    """
    A function to calculate the md5 hash of a file.

    """


    m = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda : f.read(chunk_size), b""):
            m.update(chunk)
    return m.hexdigest();



def check_md5(file_loc, checksum:str)->bool:

    if (calculate_md5(file_loc)!=checksum):
        return False
    return True

# check if the given root exist, if not make the root, then create the 

def download_file(url, checksum, root = "./"):

    root = Path(root)

    if (not root.is_dir()):
        root.mkdir()

    file_name = url.split("/")[-1]
    file_loc = root + '/' + file_name

    urllib.request.urlretrieve(url, file_loc)

    if (not check_md5(file_loc, checksum)):
        file_loc.unlink()
        print(f"MD5 checksum did not match for {url}. Deleting the {file_loc}. If you trust the file, please manually download.")
        return 
    print(f"file {file_loc} downloaded successfully")
    

