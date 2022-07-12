# Python Analyser
Random project

## Getting started (redo-this)
...
## Software to look into
- https://obsproject.com/welcome

## Requirements (Brew)
- Gource: `brew install gource`
- ffmpeg: `brew install ffmpeg`
- arzzen/git-quick-stats: `brew install git-quick-stats`

## Requirements (Python)
- Dependencies: `python3 -m pip install -r requirements.txt`

### WhatsApp
Generate stats from whatsapp exports

#### Steps 
1. Export a group chat 
2. Save as `storage/sources/whatsapp/export-2022-07-12.txt` (today's date)
3. Get the stats
```
npm run tools:whatsapp_to_stats
```

### GitHub
Get stats from GitHub repositories

#### Steps
Add steps...

### Known issues
Was unable to install some of the required Python packages (like scipy), had to 
install the following libs through brew. This also failed via a venv?!
```
brew install numpy scipy ipython jupyter
```
