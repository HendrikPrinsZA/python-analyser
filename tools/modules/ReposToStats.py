import re
import subprocess
from typing import Any
from modules.helpers import *

class ReposToStats:
    def __init__(self) -> None:
        self.repo_paths = get_repo_paths()

        self._stats = dict({
            'insertions': 0,
            'deletions': 0,
            'files': 0,
            'commits': 0,
        })

        self._stats_alias = dict({
            'insertions': 0,
            'deletions': 0,
            'files': 0,
            'commits': 0,
            'lines changed': 0,
            'first commit': None,
            'last commit': None,
        })

        self.path_to_stats = f"{get_path_to_storage()}/instances/{get_instance_id()}/stats"

        if not os.path.isdir(self.path_to_stats):
            os.makedirs(self.path_to_stats, exist_ok=True)

    def generate(self):
        stats = self.generate_stats()
        path_to_stats = f"{self.path_to_stats}/general.json"
        path_to_stats = save_object_as_json(stats, path_to_stats)
        print(f"Saved as '{path_to_stats}'")

    def print_stats(self, stats:dict) -> None:
        for repo_name in stats['repo_names']:
            repo_stats = stats['repo_names'][repo_name]

            print(f"Repo name: {repo_name}")
            print(f"- insertions: {repo_stats['insertions']}")
            print(f"- deletions: {repo_stats['deletions']}")
            print(f"- files: {repo_stats['files']}")
            print(f"- commits: {repo_stats['commits']}")

            print(f"- aliases: ")
            for alias in repo_stats['aliases']:
                alias_stats = repo_stats['aliases'][alias]
                print(f"  - {alias}:")
                print(f"    - insertions: {alias_stats['insertions']}")
                print(f"    - deletions: {alias_stats['deletions']}")
                print(f"    - files: {alias_stats['files']}")
                print(f"    - commits: {alias_stats['commits']}")
                print(f"    - lines changed: {alias_stats['lines changed']}")
                print(f"    - first commit: {alias_stats['first commit']}")
                print(f"    - last commit: {alias_stats['last commit']}")

    def generate_stats(self) -> dict:
        """
        Generate stats per branch
        """
        stats = dict({
            'total': self._stats.copy(),
            'aliases': dict({}),
            'repo_names': dict({})
        })

        for repo_path in get_repo_paths():
            repo_name = os.path.basename(repo_path)
            stats['repo_names'][repo_name] = self.get_repo_stats(repo_path)

            # sum totals
            for key in stats['total'].keys():
                stats['total'][key] += stats['repo_names'][repo_name][key]
            
            # sum aliases
            for alias in stats['repo_names'][repo_name]['aliases'].keys():
                alias_stats = stats['repo_names'][repo_name]['aliases'][alias]

                # copy template dict
                if not alias in stats['aliases']:
                    stats['aliases'][alias] = self._stats_alias.copy()

                # sum alias totals
                for key in alias_stats.keys():
                    value = alias_stats[key]

                    # increment int
                    if isinstance(value, int):
                        stats['aliases'][alias][key] += value
                        continue 
                    
                    # set value of key if none
                    current_value = stats['aliases'][alias][key]
                    if current_value is None:
                        stats['aliases'][alias][key] = value
                        continue 
                    
                    # use latest date
                    if isinstance(value, datetime) and value > current_value:
                        stats['aliases'][alias][key] = value
                        continue

        return stats

    def get_repo_stats(self, path_to_repo:str) -> dict:
        command = f"cd '{path_to_repo}' && git-quick-stats --detailed-git-stats"
        response = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)

        stats = self._stats.copy()
        stats['aliases'] = dict({})

        current_alias = None
        lines = response.decode('utf8').splitlines()
        for line in lines:
            line = line.strip()
            
            if line == 'total:':
                current_alias = 'TOTAL'
                continue

            alias, username = self.line_to_alias_and_username(line)
            if alias is not None and username is not None:
                current_alias = alias
                continue
            
            if current_alias is None: 
                continue

            key, value = self.line_to_key_value(line)
            if key is None or value is None:
                continue

            if current_alias == 'TOTAL':
                if isinstance(value, int):
                    stats[key] += value
                else:
                    stats[key] = value
            else:
                if current_alias not in stats['aliases'].keys():
                    stats['aliases'][current_alias] = self._stats_alias.copy()

                if isinstance(value, int):
                    stats['aliases'][current_alias][key] += value
                else:
                    stats['aliases'][current_alias][key] = value
        
        return stats

    def line_to_alias_and_username(self, line:str) -> str and str:
        """
        In 'John Doe <johndoe@company.com>'
        Out 'John Doe' 'johndoe@company.com>'
        """
        alias = None
        username = None
        parts = line.split('<')
        
        if len(parts) != 2:
            return None, None
        
        alias = parts[0].strip()
        username = re.sub('(<|\:|>)', '', parts[1].strip(), flags=re.IGNORECASE)
        
        return alias, username

    def line_to_key_value(self, line:str) -> str and Any:
        """
        In: 'insertions:    44459	(100%)'
        Out 'insertions' '44459'
        """
        key = None
        value = None
        parts = line.split(':')
        
        if len(parts) < 2:
            return None, None
        
        key = parts[0].strip()
        value = ':'.join(parts[1:]).split('(')[0].strip()
        
        if key in ['first commit', 'last commit']:
            date_format = "%a %b %d %H:%M:%S %Y %z"
            value = datetime.strptime(value, date_format)
        else:
            value = int(value)
        
        return key, value
