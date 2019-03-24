import requests
import json
import webbrowser
import time
import os
from os import system

from apscheduler.schedulers.background import BackgroundScheduler

os.system('cls')

system('title Twitch Stalkr v1.0')

streamer_name = input('Streamer to stalk: ')
client_id = '' # your twitch client_id
streamer_url = 'https://twitch.tv/{}'.format(streamer_name)

system('title Stalking {}'.format(streamer_name.capitalize()))

def is_streaming(streamer_name):
    twitch_api_stream_url = 'https://api.twitch.tv/kraken/streams/{}?client_id={}'.format(streamer_name, client_id)
    streamer_html = requests.get(twitch_api_stream_url)
    streamer = json.loads(streamer_html.content)
    return streamer['stream'] is not None

def check_status():
    temp_file = os.path.join('C:/Users/{}/Documents'.format(os.getlogin()), '{}_is_live'.format(streamer_name))

    if is_streaming(streamer_name):
        if os.path.exists(temp_file):
            print('{} is online, checking again in 5 seconds'.format(streamer_name))
            pass

        if not os.path.exists(temp_file):
            print('{} is online, opening in your default browser'.format(streamer_name))
            temp_file = open(temp_file, 'w+')
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
    print('###       V 1.0       ###')
    print('#########################')
    print('')
    check_status()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(the_whole_thing, 'interval', seconds=5, misfire_grace_time=100)
    scheduler.start()

    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
