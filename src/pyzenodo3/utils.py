import requests
from tqdm import tqdm
import hashlib
import urllib
from pathlib import Path
#FILE_PATH_TYPE = Union(str, pathlib.Path )
USER_AGENT = "pyzenodo3"

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
    file_loc = root/file_name

    if (file_loc.is_file() and check_md5(file_loc, checksum)):
        print(f"File {file_name} already downloaded at location {file_loc}")
        return 

    _urlretrieve(url, file_loc)

    if (not check_md5(file_loc, checksum)):
        file_loc.unlink()
        print(f"MD5 checksum did not match for {url}. Deleting the {file_loc}. If you trust the file, please manually download.")
        return 
    print(f"file {file_loc} downloaded successfully")
    
def _save_response_content(
    content,
    destination,
    length= None,
) :
    with open(destination, "wb") as fh, tqdm(total=length) as pbar:
        for chunk in content:
            # filter out keep-alive new chunks
            if not chunk:
                continue

            fh.write(chunk)
            pbar.update(len(chunk))


def _urlretrieve(url, file_loc, chunk_size = 1024 * 32):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT})) as response:
        _save_response_content(iter(lambda: response.read(chunk_size), b""), file_loc, length=response.length)
