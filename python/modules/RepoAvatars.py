import hashlib
from anybadge import Badge
import os
import pickle

from git import Repo
from progress.bar import Bar
from imgrender import render
from bs4 import BeautifulSoup
import urllib

import requests

from modules.helpers import path_to_storage

class RepoAvatars:
    def __init__(self, path_to_base: str, repo_names: list) -> None:
        self.path_to_base = path_to_base

        # Set repository paths
        self.repo_names = repo_names
        self.repo_paths = []
        for repo_name in self.repo_names:
            # To-do: Exception handling if not git repo
            self.repo_paths.append(f"{self.path_to_base}/{repo_name}")

        # Storage directory
        self.path_to_avatars = f"{path_to_storage()}/avatars"
        self.path_to_badges = f"{self.path_to_avatars}/1-badges"
        self.path_to_gravatars = f"{self.path_to_avatars}/2-gravatars"
        self.path_to_github = f"{self.path_to_avatars}/3-github"
        self.path_to_custom = f"{self.path_to_avatars}/9-custom"
        self.path_to_final = f"{self.path_to_avatars}/69-final"

        dir_paths = [
            self.path_to_badges,
            self.path_to_gravatars,
            self.path_to_github,
            self.path_to_custom,
            self.path_to_final
        ]

        for path_to_dir in dir_paths:
            if not os.path.isdir(path_to_dir):
                os.makedirs(path_to_dir, exist_ok=True)

    def generate_avatars(self):
        aliases = self.get_aliases()

        # badges
        for alias in aliases:
            path = self.create_badge(alias)
            if path is not None:
                print(f"Created badge for: {alias} at {path}")

        # gravatars
        for alias in aliases:
            alias_usernames = aliases[alias]
            path_to_gravatar = self.create_gravatar(alias, alias_usernames)

            if path_to_gravatar is not None:
                print(f"Created gravatar for: {alias} at {path_to_gravatar}")

        # github
        for alias in aliases:
            alias_usernames = aliases[alias]
            path_to_gravatar = self.create_github(alias, alias_usernames)

            if path_to_gravatar is not None:
                print(f"Created gravatar for: {alias} at {path_to_gravatar}")

    def create_badge(self, fullname: str) -> str:
        path_to_badge = f"{self.path_to_badges}/{fullname}.svg"

        if os.path.isfile(path_to_badge):
            return None

        badge = Badge(
            'alias',
            fullname,
            font_size=11,
            num_padding_chars=0.5,
        )

        badge.write_badge(path_to_badge)
        return path_to_badge

    def get_gravatar_url(self, username:str, size:int=100):
        default = '404'

        # construct the url
        gravatar_url = "https://secure.gravatar.com/avatar/" + hashlib.md5(username.lower().encode('utf-8')).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({
            'd': default,
            's': str(size)
        })

        return gravatar_url

    def create_gravatar(self, fullname: str, usernames: list) -> str:
        path_to_gravatar = None
        for username in usernames:
            url = self.get_gravatar_url(username)
            response = requests.get(url, stream=True)

            if not response.ok:
                continue

            if not response.content:
                continue

            path_to_gravatar = f"{self.path_to_gravatars}/{fullname}.png"
            if os.path.isfile(path_to_gravatar):
                return None

            with open(path_to_gravatar, 'wb') as file_handler:
                file_handler.write(response.content)
                file_handler.close()

        return path_to_gravatar

    def create_github(self, fullname: str, usernames: list) -> str:
        return None

    def get_avatars(self):
        path_to_badges = f"{self.path_to_avatars}/badges"

        # For testing only
        if not os.path.isdir(path_to_badges):
            os.makedirs(path_to_badges, exist_ok=True)

        for fullname in self.aliases.keys():
            self.create_badge(fullname)

    def print_aliases(self):
        path_to_default_avatar = f"{self.path_to_avatars}/_default.png"

        facelesst = []
        for fullname in self.aliases.keys():
            print(f"{fullname}: {','.join(self.aliases.get(fullname))}")
            
            found = False
            for ext in ['jpeg', 'png', 'svg']:
                path_to_avatar = os.path.realpath(f"{self.path_to_avatars}/{fullname}.{ext}")

                if os.path.isfile(path_to_avatar):
                    render(path_to_avatar, (32, 32))
                    found = True
                    break

            if not found:
                facelesst.append(fullname)
                render(path_to_default_avatar, (32, 32))
        
        if len(facelesst) > 0:
            facelesst_list = '\n- '.join(facelesst)
            print(f"The following aliases don't have avatars: \n- {facelesst_list}")


    def get_aliases(self) -> dict:
        aliases = dict()
        for repo_path in self.repo_paths:
            repo_name = os.path.basename(repo_path)
            repo_cache_path = f"{self.path_to_avatars}/{repo_name}-aliases.pkl"

            # Debugging: clear cache
            # if os.path.isfile(repo_cache_path):
            #     os.remove(repo_cache_path)

            if os.path.isfile(repo_cache_path):
                with open(repo_cache_path, 'rb') as file_handler:
                    repo_aliases = pickle.load(file_handler)
                    file_handler.close()
            else:
                repo_aliases = self.repo_to_aliases_slow(repo_path)
            
                with open(repo_cache_path, 'wb') as file_handler:
                    pickle.dump(repo_aliases, file_handler)
                    file_handler.close()

            aliases = self.merge_aliases(aliases, repo_aliases)
        
        return aliases

    def append_alias(self, aliases: dict, fullname: str, username: str) -> dict:
        if fullname not in aliases.keys():
            aliases[fullname] = list()

        if username not in aliases[fullname]:
            aliases[fullname].append(username)
        
        return aliases

    def repo_to_aliases_slow(self, repo_path: str) -> dict:
        aliases = dict()
        repo = Repo(repo_path)

        commits = list(repo.iter_commits())
        commits_count = len(commits)

        bar = Bar(f"Finding aliases in {repo_path}", max=commits_count)
        for commit in commits:
            alias_parts = repo.git.show("-s", "--format=%an|%ae", commit.hexsha)
            alias_parts = alias_parts.split('|')

            alias_fullname = alias_parts[0]
            alias_username = alias_parts[1]

            aliases = self.append_alias(aliases, alias_fullname, alias_username)
            bar.next()
        
        bar.finish()
        return aliases

    def repo_to_stats(self, repo_path: str) -> dict:
        stats = dict()
        repo = Repo(repo_path)

        commits = list(repo.iter_commits())
        commits_count = len(commits)

        bar = Bar(f"Finding stats for {repo_path}", max=commits_count)
        for commit in commits:
            alias_parts = repo.git.show("-s", "--format=%an|%ae", commit.hexsha)
            alias_parts = alias_parts.split('|')

            alias_fullname = alias_parts[0]
            alias_username = alias_parts[1]
            
            bar.next()
        
        bar.finish()
        return stats
    
    def merge_aliases(self, aliasesA: dict, aliasesB: dict) -> dict:
        aliases = dict()
        for fullname in aliasesA.keys():
            for username in aliasesA[fullname]:
                aliases = self.append_alias(aliases, fullname, username)

        for fullname in aliasesB.keys():
            for username in aliasesB[fullname]:
                aliases = self.append_alias(aliases, fullname, username)
        
        return aliases


    
