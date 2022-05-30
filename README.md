# Python Analyser
Random project

## Getting started (rough)
1. Clone this repo into the same path as the repos you want to analyse
```
cd /path/to/projects
git clone git@github.com:HendrikPrinsZA/python-analyser.git
```
2. Search and replace "repo-name" to the repo you want to analyse
```
- repo_to_stats.py
- repo_to_video.py
- modules/GitStats.py
```
3. Install the dependencies
```
make init
```
4. (optional) Export a group chat and save it as storage/sources/whatsapp/export-YYYY-MM-DD.txt
```
touch storage/sources/whatsapp/export-2022-05-30.txt
```
5. Run some stuff
```
# Repo to video (in progress)
python3 repo_to_video.py

# Whatsapp to stats (in progress)
python3 whatsapp_to_stats.py

# Repo to avatars (not working)
python3 repo_to_avatars.py

# Repo to stats (not working)
python3 repo_to_stats.py
```

## Software to look into
- https://obsproject.com/welcome

## Requirements (Brew)
- Gource
```
brew install gource
```
- ffmpeg
```
brew install ffmpeg
```
- https://github.com/arzzen/git-quick-stats#macos-homebrew
```
brew install git-quick-stats
```

## Requirements (NPM)
- See https://github.com/IonicaBizau/git-stats
```
npm i --save-dev git-stats
```

## Getting started
```
direnv allow .envrc
python3 -m venv .
```

### Section A (GitHub)

### Section B (WhatsApp)
Was unable to install some of the required Python packages (like scipy), had to 
install the following libs through brew. This also failed via a venv?!
```
brew install numpy scipy ipython jupyter
```
