# Python Analyser
Random analysis of git repositories an/or random related stuff. Another no scope project.

## Getting started
Install all required dependencies, follow the guides below.

## Requirements
System requirements.

### Third party software
- For streaming/recording see https://obsproject.com/welcome
### MacOS via Brew
- Gource: `brew install gource`
- ffmpeg: `brew install ffmpeg`
- arzzen/git-quick-stats: `brew install git-quick-stats`

### Python
- Install [Python3](https://www.python.org/downloads/)
- Install all dependencies: `python3 -m pip install -r requirements.txt`

# Tools
The current tools are supported:
- WhatsApp group stats
- Git repositories to stats
## WhatsApp group stats
Generate stats from WhatsApp group chat exports

### Steps 
1. Export a group chat 
2. Save as `storage/sources/whatsapp/export-2022-07-12.txt` (today's date)
3. Get the stats
```
npm run tools:whatsapp_to_stats
```

## Git repositories
Get stats from GitHub repositories.

### Steps
1. Create avatars from repos: `npm run tools:repos_to_avatars`
2. Create videos from repos: `npm run tools:repos_to_videos`
3. Create stats from repos: `npm run tools:repos_to_stats`

### Known issues
Was unable to install some of the required Python packages (like scipy), had to 
install the following libs through brew. This also failed via a venv?!
```
brew install numpy scipy ipython jupyter
```
