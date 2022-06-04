import json
import os
import numpy as np
from numpyencoder import NumpyEncoder

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
