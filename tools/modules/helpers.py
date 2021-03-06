import json
from math import ceil
import os
import re
from datetime import datetime, timezone
from typing import Any
from progress.bar import Bar
from time import sleep
import numpy as np
from numpyencoder import NumpyEncoder

_SCRIPT_DATETIME = datetime.now()
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

def get_instance_id() -> str:
    """
    Returns a unique id to be used for the instance

    Currently, this is the date and time the script started executing
    """
    return _SCRIPT_DATETIME.__format__("%Y%m%d_%H%M%S")

def save_list_as_json(list: list, path_to_file: str) -> str:
    """
    Saves the list as JSON by safely converting with numpy
    """
    numpy_data = np.array(list)
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
        file_handler.close()
    
    return path_to_file

def save_object_as_json(object: Any, path_to_file: str) -> str:
    """
    Saves the object as JSON by safely converting with numpy
    """
    with open(path_to_file, 'w') as file_handler:
        json.dump(
            object,
            file_handler,
            indent=4,
            sort_keys=True,
            separators=(', ', ': '), 
            ensure_ascii=False,
            cls=NumpyEncoder,
            default=str
        )
        file_handler.close()

    return path_to_file

def get_repo_names() -> list:
    """
    Returns a list of repo names (see configs/core.json)
    """
    path_to_config = os.path.realpath(f"{os.path.dirname(__file__)}/../../configs/core.json")
    with open(path_to_config, 'rb') as file_handler:
        config = json.load(file_handler)
        file_handler.close()

        return config['repo_names']

def get_repo_paths() -> list:
    """
    Returns a list of repo absolute paths (see configs/core.json)
    """
    path_to_base = os.path.realpath(f"{os.path.dirname(__file__)}/../../../")
    repo_names = get_repo_names()
    repo_paths = []
    for repo_name in repo_names:
        repo_path = f"{path_to_base}/{repo_name}"
        if not os.path.isdir(repo_path):
            print(f"Error: Invalid path to repo '{repo_path}'")
            exit(1)

        if not os.path.isdir(f"{repo_path}/.git"):
            print(f"Error: Invalid path to repo, expected to find '{repo_path}/.git'")
            exit(1)

        repo_paths.append(repo_path)
    
    return repo_paths

def get_path_to_storage() -> str:
    """
    Get the absolute path to storage from anywhere
    """
    path_to_storage = os.path.realpath(f"{os.path.dirname(__file__)}/../../storage")
    return asb_to_relative_path(path_to_storage)

def asb_to_relative_path(abs_path:str) -> str:
    """
    Convert an absolute path to relative
    """
    path_to_storage = os.path.realpath(f"{os.path.dirname(__file__)}/../../")
    relative_path = abs_path.replace(path_to_storage, '')
    relative_path = f".{relative_path}"

    return relative_path

def is_email_address(string:str) -> bool:
    """
    Checks if the string is a valid email address
    """
    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    if re.match(pat,string):
        return True
    return False

def wait_until(expiration:datetime) -> bool:
    """
    Forces the user to wait

    Used when exceeding rate limit from services
    """
    now = datetime.now(tz=LOCAL_TIMEZONE)
    expiration_human = expiration.__format__("%Y-%m-%d %H:%M:%S")
    
    seconds = ceil((expiration - now).total_seconds())
    bar = Bar(f"Waiting for {seconds}s", max=seconds)
    for i in range(seconds):
        bar.next()
        time_left = seconds - i
        bar.message = f"Waiting for {time_left}s"
        sleep(1)
    bar.finish()

    return True
