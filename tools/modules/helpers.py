import json
from math import ceil
import os
import re
from datetime import datetime, timezone
from progress.bar import Bar
from time import sleep
import numpy as np
from pytime import pytime
from numpyencoder import NumpyEncoder

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

def save_data_as_json(data: list, path_to_file: str) -> None:
    numpy_data = np.array(data)
    with open(path_to_file, 'w') as file_handler:
        json.dump(
            numpy_data, 
            file_handler, 
            indent=4, 
            sort_keys=True,
            separators=(', ', ': '), 
            ensure_ascii=False,
            cls=NumpyEncoder
        )

# Get the path to storage from anywhere
def path_to_storage() -> str:
    path_to_storage = os.path.realpath(f"{os.path.dirname(__file__)}/../../storage")
    return asb_to_relative_path(path_to_storage)

def asb_to_relative_path(abs_path:str) -> str:
    path_to_storage = os.path.realpath(f"{os.path.dirname(__file__)}/../../")
    relative_path = abs_path.replace(path_to_storage, '')
    relative_path = f".{relative_path}"

    return relative_path

def is_email_address(string:str) -> bool:
   pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,string):
      return True
   return False

def wait_until(expiration:datetime) -> bool:
    now = datetime.now(tz=LOCAL_TIMEZONE)
    expiration_human = expiration.__format__("%Y-%m-%d %H:%M:%S")
    
    seconds = ceil((expiration - now).total_seconds())
    bar = Bar(f"Waiting for {seconds}s ({expiration_human})", max=seconds)
    for _ in range(seconds):
        bar.next()
        sleep(1)
    bar.finish()

    return True
