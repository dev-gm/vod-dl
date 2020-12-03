import os, sys, shutil
from xml.dom import minidom
from datetime import date, datetime, timedelta

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
     -c CONFIG        the xml file(s) that include the streamers whose vods you want to 
                      download from, it is a more permanent and shortened version of streamers,
                      to choose from this specify all for streamers (optional, default is config.xml
                      in current directory)\n
     -h               display this help message and exit\n''')
    sys.exit()

def get_channels(filename):
    try:
        file = minidom.parse(os.path.join(os.getcwd(), filename))
    except IOError:
        return None
    channels = file.getElementsByTagName('channel')
    return channels

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
    all = []
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
                folder = arg
            elif option == 'm':
                if filetype_count >= 1:
                    display_help('Entered more than one argument for filetypes! Incorrect usage!')
                filetype = arg
                filetype_count += 1
            elif option == 'c':
                all.extend(get_streamers(arg))
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
    if not configs:
        all = get_streamers('config.xml')
    if 'all' in streamers or not streamers:
        streamers = all
    return streamers, games, folder, day, quality, filetype

def get_raw_vods(streamers, games, folder):
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
            quality_arg = '-q ' + quality
        os.system(f'TMP={os.path.join(folder, 'tmp/')} twitch-dl download {quality_arg} -f {filetype} {vod}')
        print(f'DONE WITH DOWNLOADING {vod}')

def make_folder(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

def erase_folder(folder):
    make_folder(folder)
    for filename in os.listdir(folder):
        if not filename.endswith('.kdenlive'):
            os.remove(os.path.join(folder, filename))

if __name__ == '__main__':
    streamers, games, template, day, quality, filetype = check_args(sys.argv[1:], channels)
    folder = os.path.join(template, day.strftime("%y-%m-%d"))
    make_folder(template)
    erase_folder(os.path.join(template, 'tmp/'))
    erase_folder(folder)
    erase_folder(os.path.join(folder, 'tmp/'))
    os.chdir(folder)
    vods = get_vods(streamers, games, day, template)
    download_vods(vods, quality, filetype, folder)
