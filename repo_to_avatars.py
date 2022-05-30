#!/usr/bin/env python3

import os
from git import Repo
from progress.bar import Bar

from modules.GitStats import GitStats

PATH_TO_REPOS = os.path.realpath(f"{os.path.dirname(__file__)}/../")

gitStats = GitStats(PATH_TO_REPOS)
gitStats.print_aliases()
