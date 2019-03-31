import requests
import json
import webbrowser
import time
import os
from os import system
from configparser import ConfigParser

from apscheduler.schedulers.background import BackgroundScheduler

os.system('cls')
system('title Twitch Stalkr v1.0')

config = ConfigParser()
config.read('config.ini')

client_id = config.get('stalker', 'client_id')
stalking_interval = config.get('stalker', 'interval_in_seconds')
streamer_name = config.get('default', 'streamer_name')

if not streamer_name:
    streamer_name = input('Streamer to stalk: ')
else:
    streamer_name = streamer_name

streamer_url = 'https://twitch.tv/{}'.format(streamer_name)

system('title Stalking {}'.format(streamer_name.capitalize()))

def is_streaming(streamer_name):
    twitch_api_stream_url = 'https://api.twitch.tv/kraken/streams/{}?client_id={}'.format(streamer_name, client_id)
    streamer_html = requests.get(twitch_api_stream_url)
    streamer = json.loads(streamer_html.content)
    return streamer['stream'] is not None

def check_status():
    temp_file_location = config.get('stalker', 'temp_file')
    temp_file = os.path.join('{}.{}'.format(temp_file_location, streamer_name))

    if is_streaming(streamer_name):
        if os.path.exists(temp_file):

            with open(temp_file, 'r') as start_time:
                start_time = start_time.readline()

            start_time = float(start_time)
            current_time = time.time()

            stream_duration = current_time - start_time
            stream_duration = int(stream_duration)

            duration_hours = stream_duration // 3600
            duration_minutes = (stream_duration - (duration_hours * 3600)) // 60
            duration_seconds = stream_duration - ((duration_hours * 3600) + (duration_minutes * 60))

            print('{} has been streaming for: {} hours, {} minutes, and {} seconds.'.format(streamer_name.capitalize(), duration_hours, duration_minutes, duration_seconds))
            pass

        if not os.path.exists(temp_file):
            print('{} is online, opening in your default browser'.format(streamer_name))
            start_time = time.time()

            with open(temp_file, 'w+') as timestamp:
                timestamp.write(str(start_time))

            webbrowser.open_new_tab(streamer_url)

            time.sleep(5)

    if not is_streaming(streamer_name):
        if os.path.exists(temp_file):
            os.remove(temp_file)

        if not os.path.exists(temp_file):
            print('{} is offline, checking again in 5 seconds'.format(streamer_name))
            pass

def the_whole_thing():
    os.system('cls')
    print('#########################')
    print('###   Twitch Stalkr   ###')
    print('###       V 0.5       ###')
    print('#########################\n')
    check_status()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(the_whole_thing, 'interval', seconds=int(stalking_interval), misfire_grace_time=300)
    scheduler.start()

    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
