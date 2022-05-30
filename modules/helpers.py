import json
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