#!/usr/bin/python

import os, sys, shutil
from datetime import date, datetime, timedelta
from typing import Dict, Union, Tuple, List


def display_help(error: str = ''):
    """Prints a help menu and exit the program, used when the h arg is called"""
    if error:
        print(error)
    print('''    Usage:\n
     vod-dl [OPTIONS]\n
    Options:\n
     g GAMES         games you want the vods to have (optional, default is any)\n
     s STREAMERS     the streamers whose vods you want to download (mandatory)\n
     d DATES         the dates to download from, options are: "today", "yesterday",
                      or "month/day/year" (optional, default is today)\n
     f FOLDER        the folder to download the vods to (optional, default is /tmp)\n
     q QUALITY       the quality you want your downloaded vods, options are: high,
                      medium, low (optional, default is you have to choose)\n
     m FILETYPE      the filetype of the vods you want to download (optional,
                      default is mp4)\n
     h               display this help message and exit\n''')
    sys.exit()


def get_args() -> Dict[str, str]:
    """"Gets arguments using input"""
    arguments = {}
    while True:
        option = input("Enter an option (ENTER to exit): ")
        if not option:
            break
        elif option == "h":
            arguments[option] = ""
            break
        arg = input("Enter the argument: ")
        arguments[option] = arg
    return arguments


def check_args(arguments: Dict[str, str]) -> Tuple[List[str], List[str], str, datetime, str, str]:
    """Gets arguments and processes them, returns relevant info or calls help and quits"""
    quality = "source"
    folder = "."
    filetype = "mp4"
    streamers = []
    games = []
    now = datetime.now()
    delta = timedelta(hours=6)
    day = now - delta
    qualities = {'high':'source', 'medium':'720', 'low':'480'}
    for option, arg in arguments.items():
        if option == 's':
            streamers.append(arg)
        elif option == 'g':
            games.append(arg)
        elif option == 'q':
            quality = qualities[arg]
        elif option == 'f':
            folder = arg
        elif option == 'm':
            filetype = arg
        elif option == 'd':
            if arg == 'today':
                day = now - delta
            elif arg == 'yesterday':
                day = (now - delta) - timedelta(days=1)
            else:
                day = datetime.strptime(arg, '%d/%m/%y') - delta
        elif option == 'h':
            display_help()
        else:
            display_help('Entered an incorrect option! Incorrect usage!')
    if not streamers:
        display_help('You must enter at least one streamer!')
    return streamers, games, folder, day, quality, filetype


def get_raw_vods(streamers: List[str], games: List[str], folder: str) -> Dict[str, str]:
    """Gets raw vod names from the twitch-dl videos command"""
    results = {}
    search = ''
    for game in games:
        search += f'--game "{game}"'
    for streamer in streamers:
        filename = os.path.join(folder, 'tmp/', 'streamer')
        os.system(f'twitch-dl videos {search} {streamer} > {filename}')
        with open(filename, 'r') as file:
            results[streamer] = file.read().split('\n')
    return results


def get_vods(streamers: List[str], games: List[str], day: datetime, folder: str) -> Dict[str, str]:
    """Gets relevant info, then gets raw vod names, then
    turns that into properly formatted vod names"""
    vods = {}
    results = get_raw_vods(streamers, games, folder)
    strp = '%Y-%m-%d %H:%M:%S'
    start = 8
    if not games:
        start = 7
    for streamer, result in results.items():
        for i in range(start, len(result), 6):
            raw_day = result[i][15:25] + result[i][27:36]
            temp_day = datetime.strptime(raw_day, strp) - timedelta(hours=6)
            if temp_day.date() == day.date():
                vods[streamer] = result[i-3][10:-4]
            else:
                break
    print('THE VODS ARE: ', vods)
    return vods


def download_vods(vods: List[str], quality: str, filetype: str, folder: str):
    """From the properly formatted vod names, download the vods to the tmp directory"""
    for streamer, vod in vods.items():
        if quality:
            quality_arg = '-q ' + quality
        os.system(f'TMP={os.path.join(folder, "tmp/")} twitch-dl download {quality_arg} -f {filetype} {vod}')
        print(f'DONE WITH DOWNLOADING {vod}')


def make_folder(folder: str):
    """Makes a folder if it does not already exist"""
    if not os.path.isdir(folder):
        os.mkdir(folder)


def erase_folder(folder: str):
    """Deletes everything in a folder"""
    make_folder(folder)
    for filename in os.listdir(folder):
        if not filename.endswith('.kdenlive'):
            os.remove(os.path.join(folder, filename))


if __name__ == '__main__':
    arguments = get_args()
    streamers, games, template, day, quality, filetype = check_args(arguments)
    folder = os.path.join(template, day.strftime("%y-%m-%d"))
    make_folder(template)
    erase_folder(os.path.join(template, 'tmp/'))
    erase_folder(folder)
    erase_folder(os.path.join(folder, 'tmp/'))
    os.chdir(folder)
    vods = get_vods(streamers, games, day, template)
    download_vods(vods, quality, filetype, folder)
