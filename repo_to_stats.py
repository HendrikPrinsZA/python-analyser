#!/usr/bin/env python3

import os

from modules.GitStats import GitStats

PATH_TO_REPOS = os.path.realpath(f"{os.path.dirname(__file__)}/../")

gitStats = GitStats(PATH_TO_REPOS)
gitStats.repo_to_stats(f"{PATH_TO_REPOS}/repo-name")

"""
❯ git-quick-stats --detailed-git-stats
"""
