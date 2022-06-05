#!/usr/bin/env python3

import os

from modules.RepoAvatars import RepoAvatars

REPO_NAMES = [
  'repo-name'
]

PATH_TO_BASE = os.path.realpath(f"{os.path.dirname(__file__)}/../../")

repoAvatars = RepoAvatars(PATH_TO_BASE, REPO_NAMES)
repoAvatars.generate_avatars()
