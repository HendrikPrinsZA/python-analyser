#!/usr/bin/env python3

import os

BASE_DIR = os.path.realpath(f"{os.path.dirname(__file__)}/../")

def repo_to_video(repo):
    path_to_repo = f"{BASE_DIR}/{repo}"
    path_to_video = f"videos/{repo}.mp4"
    
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
        '--user-image-dir avatars/selfies',
        '--default-user-image avatars/selfies/_default.png',
        '--fixed-user-size',
        f"--title '{repo}'",
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

repo_to_video('repo-name')
