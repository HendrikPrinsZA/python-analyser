from anybadge import Badge
import os
import pickle

from git import Repo
from progress.bar import Bar

from imgrender import render

class GitStats:
    def __init__(self, path_to_repos: str) -> None:
        self.path_to_repos = path_to_repos
        self.path_to_base = os.path.realpath(f"{os.path.dirname(__file__)}/../")
        self.path_to_avatars = f"{self.path_to_base}/avatars"
        self.repo_names = [
            'repo-name',
        ]
        self.aliases = self.get_aliases()

    def get_avatars(self):
        path_to_badges = f"{self.path_to_avatars}/badges"

        # For testing only
        if not os.path.isdir(path_to_badges):
            os.makedirs(path_to_badges, exist_ok=True)

        for fullname in self.aliases.keys():
            self.create_avatar_badge(fullname)
            
            # The idea was to fetch the avatars from github/slack, but too much effort!
            # decided to just do this part manually

            # print(f"Getting avatars for '{fullname}'")
            # for username in self.aliases[fullname]:
            #     print(f"Look for {username}")

    def create_avatar_badge(self, fullname: str):
        path_to_badges = f"{self.path_to_avatars}/badges"
        path_to_badge = f"{path_to_badges}/{fullname}.svg"

        if os.path.isfile(path_to_badge):
            return

        badge = Badge(
            'alias',
            fullname,
            font_size=11,
            num_padding_chars=0.5,
        )

        badge.write_badge(path_to_badge)

    def print_aliases(self):
        path_to_avatars = "avatars/selfies"
        path_to_default_avatar = f"{path_to_avatars}/_default.png"

        facelesst = []
        for fullname in self.aliases.keys():
            print(f"{fullname}: {','.join(self.aliases.get(fullname))}")
            
            found = False
            for ext in ['jpeg', 'png', 'svg']:
                path_to_avatar = os.path.realpath(f"{path_to_avatars}/{fullname}.{ext}")

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
        for repo_name in self.repo_names:
            repo_path = f"{self.path_to_repos}/{repo_name}"
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


    
