# Roadmap
## General
- Restrict tools based on time period
- Config driven
- Simple file based database to prevent config passing everywhere
- All reports should be saved under the date generated
- Dockerise

## Generate avatars from repos (done)
- Use repo names from config
- Sources - in order of preference
  1. Badges
  2. Gravatars
  3. GitHub
  4. Custom - manual override
- Refactor storage
  - `storage/avatars/`
- Refactor entry command
  - `npm run tools:repos-to-avatars`

## Generate videos from repos (done)
- Use repo names from config
- Refactor storage
  - `storage/instances/{instance_id}/vidoes/{repo-name}.mp4`
- Refactor entry command
  - `npm run tools:repos-to-videos`

## Generate stats from repos
- Use repo names from config
- Refactor storage
  - `storage/instances/{instance_id}/stats/general.json`
  - `storage/instances/{instance_id}/stats/commits.json`
  - `storage/instances/{instance_id}/stats/general-{repo-name}.json`
  - `storage/instances/{instance_id}/stats/commits-{repo-name}.json`
- Refactor entry command
  - `npm run tools:repos-to-stats`
- Generic repo stats
- Commit history strings for scroller

## Generate stats from WhatsApp group chat
- Refactor storage
  - `storage/sources/whatsapp/{date}.txt` (source)
  - `storage/instances/{instance_id}/whatsapp/` (reports)
- Refactor entry command
  - `npm run tools:whatsapp-to-stats`
- Use current date as filter, override in config
- Generic stats
  - Stats per author as json (done)
  - Top 10 links (done)
  - Top 10 media (broken)
  - Top 10 messages (done)
  - Top 10 words (broken)
  - Word list image (done)
- Commit history strings for scroller
- Anonymize the data by default, i.e. 'Hendrik' = 'Alias 1'
  - See `~/cowboy/modules/local/sentiment/sentiment.py`

## Open Broadcaster Software (OBS)
- Create sample scene and config (done)
- Create standard layouts
- Draft tutorial guide

## Create web interface for OBS
- Create SPA scaffolding with Nuxt (done)
- POC with interactive view (done)
- Core
  - Control context with local storage
  - Use date as main filter - router maybe
- MVP components
  - Horizontal scrolling banner of commits per repo
  - Alias with avatar
  - WhatsApp static content
- MVP layouts
  - Studio main
  - Weather

## Future ideas
- Consider express API for web sockets, this will allow direct interaction with the interface for simpler recording
 - Move screens
 - Transitions
 - Etc
- Steal from https://github.com/HendrikPrinsZA/cowboy/tree/main/modules/core/api
- Sample templates in OBS for funny adds
- Symlink latest instance_id dir to latest, for simplified pathing
