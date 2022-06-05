#!/usr/bin/env python3

import os

from modules.helpers import *

def repo_to_video(path_to_repo:str) -> None:
    repo_name = os.path.basename(path_to_repo)
    path_to_storage = get_path_to_storage()
    
    instance_id = get_instance_id()
    path_to_videos = f"{path_to_storage}/instances/{instance_id}/videos"
    path_to_video = f"{path_to_videos}/{repo_name}.mp4"
    path_to_avatars = f"{path_to_storage}/avatars/69-final"

    if not os.path.isdir(path_to_videos):
        os.makedirs(path_to_videos, exist_ok=True)
        print(f"Created new dir: {path_to_videos}")
    
    if not os.path.isdir(path_to_repo):
        print(f"Could not find repo at {path_to_repo}")
        exit(1)

    ffmpeg_args = [
        '-y',
        '-r 60',
        '-f image2pipe',
        '-vcodec ppm',
        '-i -',
        '-vcodec libx264',
        '-preset ultrafast',
        '-pix_fmt yuv420p',
        '-crf 1',
        '-threads 0',
        '-bf 0'
    ]
    ffmpeg_cmd = f"ffmpeg {' '.join(ffmpeg_args)} {path_to_video}"

    gource_args = [
        "--start-date '2022-04-01'",
        f"--user-image-dir '{path_to_avatars}'",
        f"--default-user-image '{path_to_avatars}/_default.png'",
        '--fixed-user-size',
        f"--title '{repo_name}'",
        '--date-format "%Y-%m-%d %H:%M:%S"',
        '--hide dirnames,filenames',
        '--seconds-per-day 1',
        '--camera-mode track', # defaults to overview
        '--bloom-multiplier 0.25',
        '--auto-skip-seconds 0.01',
        '--bloom-intensity 0.25',
        '--stop-at-end',
        '-1280x720 -o',
        f"- {path_to_repo}"
    ]
    gource_cmd = f"gource {' '.join(gource_args)} | {ffmpeg_cmd}"
    print(f"Executing: {gource_cmd}")
    os.system(gource_cmd)

repo_paths = get_repo_paths()
for repo_path in repo_paths:
    repo_to_video(repo_path)

