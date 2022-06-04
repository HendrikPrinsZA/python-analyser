import hashlib
import shutil
from anybadge import Badge
import os
import pickle

from git import Repo
from progress.bar import Bar
from imgrender import render
import urllib

import requests

from modules.helpers import path_to_storage

class RepoAvatars:
    def __init__(self, path_to_base: str, repo_names: list) -> None:
        self.path_to_base = path_to_base

        # allowed extensions, order of preference
        self.allowed_extensions = [
            'svg', 'png', 'jpg', 'jpeg'
        ]

        # Set repository paths
        self.repo_names = repo_names
        self.repo_paths = []
        for repo_name in self.repo_names:
            # To-do: Exception handling if not git repo
            self.repo_paths.append(f"{self.path_to_base}/{repo_name}")

        # Storage directory
        self.path_to_storage = path_to_storage()
        self.path_to_avatars = f"{self.path_to_storage}/avatars"

        self.path_to = dict({
            'badges': f"{self.path_to_avatars}/1-badges",
            'gravatars': f"{self.path_to_avatars}/2-gravatars",
            'github': f"{self.path_to_avatars}/3-github-avatars",
            'custom': f"{self.path_to_avatars}/9-custom-selfies",
            'final': f"{self.path_to_avatars}/69-final"
        })

    def generate_avatars(self):
        aliases = self.get_aliases_from_repos()

        bar = Bar(f"Generating avatars as badges", max=len(aliases))
        for alias in aliases:
            self.create_alias_badge(alias)
            bar.next()
        bar.finish()

        bar = Bar(f"Generating avatars from gravatar", max=len(aliases))
        for alias in aliases:
            self.create_alias_gravatar(alias, aliases[alias])
            bar.next()
        bar.finish()

        bar = Bar(f"Generating avatars from github", max=len(aliases))
        for alias in aliases:
            self.create_alias_github_avatar(alias, aliases[alias])
            bar.next()
        bar.finish()

        self.create_alias_avatars_final()

    def create_alias_avatars_final(self) -> None:
        """
        Create the final aliases
        - display the avatars for each alias
        - create a lookup file, like avatars.json
        """

        # Note: this feels more confusing than moving it to __init__??? Nastia???
        # I want to have self.aliases
        aliases = self.get_aliases_from_repos()

        alias_avatars = dict({})

        bar = Bar("Generating avatars final", max=len(aliases))
        for alias in aliases:
            alias_avatars[alias] = self.create_alias_final(alias)
            bar.next()
        bar.finish()

        for alias in alias_avatars:
            _, avatar_extension, path_to_avatar = alias_avatars[alias]

            print(f"alias: {alias} -> {path_to_avatar}")

            if avatar_extension == 'svg':
                print(f"Cannot render SVG: {path_to_avatar}")
                continue

            render(path_to_avatar, (16, 16))

    def create_alias_final(self, fullname: str) -> str and str and str:
        """
        Walk through the avatar paths in reverse order
        - copy the first match to 69-final to be used as primary
        """
        path_to_final_dir = self.path_to.get('final')
        path_dir_reversed = self.path_to.copy().__reversed__()

        for path_to_dir in path_dir_reversed:
            if path_to_dir == 'final':
                continue

            path_to_avatar_dir = self.path_to[path_to_dir]

            for avatar_extension in self.allowed_extensions:
                path_to_avatar = f"{path_to_avatar_dir}/{fullname}.{avatar_extension}"
                path_to_final = f"{path_to_final_dir}/{fullname}.{avatar_extension}"

                if os.path.exists(path_to_avatar):
                    shutil.copyfile(path_to_avatar, path_to_final)
                    
                    return path_to_dir, avatar_extension, path_to_avatar
    
        print("Unhandled exception: We should never really reach here!")
        exit(1)

    def create_alias_badge(self, fullname: str) -> str:
        path_to_badge = f"{self.path_to.get('badges')}/{fullname}.svg"

        if os.path.isfile(path_to_badge):
            return None

        badge = Badge(
            'Alias',
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

    def create_alias_gravatar(self, fullname: str, usernames: list) -> str:
        path_to_gravatar = None
        for username in usernames:
            url = self.get_gravatar_url(username)
            response = requests.get(url, stream=True)

            if not response.ok:
                continue

            if not response.content:
                continue

            path_to_gravatar = f"{self.path_to.get('gravatars')}/{fullname}.png"
            if os.path.isfile(path_to_gravatar):
                return None

            with open(path_to_gravatar, 'wb') as file_handler:
                file_handler.write(response.content)
                file_handler.close()

        return path_to_gravatar

    def create_alias_github_avatar(self, fullname: str, usernames: list) -> str:
        return None

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


    def get_aliases_from_repos(self) -> dict:
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


    
