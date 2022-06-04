#!/usr/bin/env python3

import os

from modules.GitStats import GitStats

PATH_TO_BASE = os.path.realpath(f"{os.path.dirname(__file__)}/../../")

gitStats = GitStats(PATH_TO_BASE)
gitStats.repo_to_stats(f"{PATH_TO_BASE}/repo-name")

"""
❯ git-quick-stats --detailed-git-stats
"""
