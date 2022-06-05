from datetime import datetime, timezone
import hashlib
import json
import shutil
from anybadge import Badge
import os
import pickle
from git import Repo
from progress.bar import Bar
from imgrender import render
import urllib
import requests

from modules.helpers import *

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

class ReposToAvatars:
    def __init__(self) -> None:
        self.repo_paths = get_repo_paths()
        self.path_to_storage = get_path_to_storage()
        self.path_to_avatars = f"{self.path_to_storage}/avatars"
        
        # allowed extensions, order of preference
        self.allowed_extensions = [
            'svg', 'png', 'jpg', 'jpeg'
        ]

        self.path_to = dict({
            'badges': f"{self.path_to_avatars}/01-badges",
            'gravatars': f"{self.path_to_avatars}/02-gravatars",
            'github': f"{self.path_to_avatars}/03-github-avatars",
            'custom': f"{self.path_to_avatars}/09-custom-selfies",
            'final': f"{self.path_to_avatars}/69-final"
        })

    def generate(self):
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
            path_to_dir, avatar_extension, path_to_avatar = alias_avatars[alias]

            print(f"alias: {alias} from {path_to_dir}")

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
        for username in usernames:
            path_to_gravatar = f"{self.path_to.get('gravatars')}/{fullname}.png"
            if os.path.isfile(path_to_gravatar):
                continue
            
            url = self.get_gravatar_url(username)
            return self.download_image(url, path_to_gravatar)

        return None

    def download_image(self, url:str, target_path:str) -> str:
        response = requests.get(url, stream=True)

        if not response.ok:
            return None

        if not response.content:
            return None
        
        with open(target_path, 'wb') as file_handler:
            file_handler.write(response.content)
            file_handler.close()
        
        return target_path

    def get_github_avatar_url(self, username: str) -> str:
        if not is_email_address(username):
            None

        response = requests.get(f"https://api.github.com/search/users?q={username}", stream=True)

        if response.status_code != 200:
            wait = float(response.headers.get('x-ratelimit-reset'))

            if wait > 0:
                dt_wait = datetime.fromtimestamp(wait, tz=LOCAL_TIMEZONE)
                wait_until(dt_wait)
                return self.get_github_avatar_url(username)

            print(f"Uncaught exception, status_code = {response.status_code}")
            exit(1)

        username = None
        try: 
            data = json.loads(response.content)
            return data['items'][0]['avatar_url']
        except: 
            return None

    def create_alias_github_avatar(self, fullname: str, usernames: list) -> str:
        for username in usernames:
            path_to_image = f"{self.path_to.get('github')}/{fullname}.png"
            if os.path.isfile(path_to_image):
                continue

            github_avatar_url = self.get_github_avatar_url(username)

            if github_avatar_url is not None:
                dl_path = self.download_image(github_avatar_url, path_to_image)

                if dl_path is not None:
                    return dl_path
                
                # To-do: Copy default image (to prevent loading again) 
                # - alternatively catch from parent and cache
                    
        return None

    def get_aliases_from_repos(self) -> dict:
        aliases = dict()
        for repo_path in self.repo_paths:
            repo_name = os.path.basename(repo_path)
            repo_cache_path = f"{self.path_to_avatars}/{repo_name}-aliases.pkl"

            if os.path.isfile(repo_cache_path):
                with open(repo_cache_path, 'rb') as file_handler:
                    repo_aliases = pickle.load(file_handler)
                    file_handler.close()
            else:
                repo_aliases = self.repo_to_aliases_slow(repo_path)
            
                with open(repo_cache_path, 'wb') as file_handler:
                    pickle.dump(repo_aliases, file_handler)
                    file_handler.close()

            aliases = self.merge_dicts(aliases, repo_aliases)
        
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

    def append_alias(self, aliases: dict, fullname: str, username: str) -> dict:
        if fullname not in aliases.keys():
            aliases[fullname] = list()

        if username not in aliases[fullname]:
            aliases[fullname].append(username)
        
        return aliases
    
    def merge_dicts(self, aliases_1: dict, aliases_2: dict) -> dict:
        """
        Merge two alias dicts

        Future idea:
        - Intercept here to build global cache
        - Rename to merge_dicks
        """
        aliases = dict()
        for fullname in aliases_1.keys():
            for username in aliases_1[fullname]:
                aliases = self.append_alias(aliases, fullname, username)

        for fullname in aliases_2.keys():
            for username in aliases_2[fullname]:
                aliases = self.append_alias(aliases, fullname, username)
        
        return aliases


    
