#!/usr/bin/env python
import os, sys, shutil
from datetime import date, datetime, timedelta

channels = [
    'michaelreeves',
    'ludwig',
    'baboabe',
    'lilypichu',
    'valkyrae',
    'disguisedtoast',
    'kkatamina',
    'sykkuno',
    'itshafu',
    'peterparktv',
    'masayoshi',
    'fuslie',
    'quarterjade',
    'yvonnie',
    'itsryanhiga',
    'nasumiii',
    'tinakitten',
    'eajparkofficial'
]

def display_help(error=''):
    if error:
        print(error)
    print('''    Usage:\n
     vod-dl [OPTIONS]\n
    Options:\n
     -g GAMES         games you want the vods to have (optional, default is any)\n
     -s STREAMERS     the streamers whose vods you want to download, you can specify
                      "all" (optional, default is all)\n
     -d DATES         the dates to download from, options are: "today", "yesterday",
                      or "month/day/year" (optional, default is today)\n
     -f FOLDER        the folder to download the vods to (optional, default is current dir)\n
     -q QUALITY       the quality you want your downloaded vods, options are: high,
                      medium, low (optional, default is you have to choose)\n
     -m FILETYPE      the filetype of the vods you want to download (optional,
                      default is mp4)\n
     -h               display this help message and exit\n''')
    sys.exit()

def check_args(input, all):
    games = []
    streamers = []
    quality = ''
    delta = timedelta(hours=6)
    now = datetime.now()
    day = now - delta
    filetype = 'mp4'
    folder = ''
    quality_count = 0
    filetype_count = 0
    date_count = 0
    qualities = {'high':'source', 'medium':'720', 'low':'480'}
    option = 's'
    for arg in input:
        if arg[0] == '-':
            option = arg[1]
        else:
            if option == 's':
                streamers.append(arg)
            elif option == 'g':
                games.append(arg)
            elif option == 'q':
                if quality_count >= 1:
                    display_help('Entered more than one argument for quality! Incorrect usage!')
                quality = qualities[arg]
                quality_count += 1
            elif option == 'f':
                if arg[-1] != '/':
                    folder = arg + '/'
                else:
                    folder = arg
            elif option == 'm':
                if filetype_count >= 1:
                    display_help('Entered more than one argument for filetypes! Incorrect usage!')
                filetype = arg
                filetype_count += 1
            elif option == 'd':
                if date_count >= 1:
                    display_help('Entered more than one argument for date! Incorrect usage!')
                if arg == 'today':
                    day = now - delta
                elif arg == 'yesterday':
                    day = (now - delta) - timedelta(days=1)
                else:
                    day = datetime.strptime(arg, '%d/%m/%y') - delta
                date_count += 1
        if option == 'h':
            display_help()
        elif option not in 'sgqfmd':
            display_help('Entered an incorrect option! Incorrect usage!')
    if 'all' in streamers or not streamers:
        streamers = all
    return streamers, games, folder, day, quality, filetype

def get_raw_vods(streamers, games, folder):
    results = {}
    search = ''
    for game in games:
        search += f'--game "{game}"'
    for streamer in streamers:
        filename = f'{folder}tmp/{streamer}.txt'
        os.system(f'twitch-dl videos {search} {streamer} > {filename}')
        with open(filename, 'r') as file:
            results[streamer] = file.read().split('\n')
    return results

def get_vods(streamers, games, day, folder):
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
                vods[streamer] = result[i-3][4:-4]
            else:
                break
    print('THE VODS ARE: ', vods)
    return vods

def download_vods(vods, quality, filetype, folder):
    os.chdir(folder)
    for streamer, vod in vods.items():
        if quality:
            temp_quality = '-q ' + quality
        os.system(f'TMP={folder}/tmp twitch-dl download {temp_quality} -f {filetype} {vod}')
        print(f'DONE WITH DOWNLOADING {vod}')

def make_folder(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

def erase_folder(folder):
    make_folder(folder)
    for filename in os.listdir(folder):
        if not filename.endswith('.kdenlive'):
            os.remove(f'{folder}/{filename}')

if __name__ == '__main__':
    streamers, games, template, day, quality, filetype = check_args(sys.argv[1:], channels)
    folder = f'{template}{day.strftime("%y-%m-%d")}'
    make_folder(template)
    erase_folder(folder)
    os.chdir(folder)
    vods = get_vods(streamers, games, day, template)
    download_vods(vods, quality, filetype, folder)
