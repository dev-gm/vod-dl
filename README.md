# vod-dl
A highly customizable and fast command line program to download twitch vods
^^^
Usage:

     vod-dl [OPTIONS]

    Options:\n
     -g GAMES         games you want the vods to have (optional, default is any)

     -s STREAMERS     the streamers whose vods you want to download, you can 
                      specify "all" (optional, default is all)

     -d DATES         the dates to download from, options are: "today", "yesterday", 
                      or "month/day/year" (optional, default is today)

     -f FOLDER        the folder to download the vods to (optional, default is current 
                      dir)

     -q QUALITY       the quality you want your downloaded vods, options are: high, 
                      medium, low (optional, default is you have to choose)

     -m FILETYPE      the filetype of the vods you want to download (optional, default 
                      is mp4)

     -c CONFIG        the xml file(s) that include the streamers whose vods you want to 
                      download from, it is a more permanent and shortened version of streamers, 
                      to choose from this specify all for streamers (optional, default is config.xml 
                      in current directory)

     -h               display this help message and exit^^^
