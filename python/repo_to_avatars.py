#!/usr/bin/env python3

import os

from modules.RepoAvatars import RepoAvatars

REPO_NAMES = [
  'vesper-forge'
]

PATH_TO_BASE = os.path.realpath(f"{os.path.dirname(__file__)}/../../")

repoAvatars = RepoAvatars(PATH_TO_BASE, REPO_NAMES)
# repoAvatars.print_aliases()
repoAvatars.generate_avatars()
