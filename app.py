import json
import os
import requests
import time
import schedule
import webbrowser

from configparser import ConfigParser

ver = '0.9'

os.system('cls')
os.system('title Twitch Stalkr v {}'.format(ver))

config = ConfigParser()
config.read('config.ini')

client_id = config.get('default', 'client_id')
check_interval = int(config.get('default', 'interval_in_seconds'))
streamer_name = config.get('default', 'streamer_name')

token = config.get('telegram', 'token')
chat_id = config.get('telegram', 'chat_id')

if not streamer_name:
    streamer_name = input('Streamer to stalk: ')
else:
    streamer_name = streamer_name

streamer_url = 'https://twitch.tv/{}'.format(streamer_name)

os.system('title Stalking {}'.format(streamer_name.capitalize()))


def is_streaming(streamer_name):
    twitch_api_stream_url = 'https://api.twitch.tv/kraken/streams/{}?client_id={}'.format(
        streamer_name, client_id)
    streamer_html = requests.get(twitch_api_stream_url)
    streamer = json.loads(streamer_html.content)
    return streamer['stream'] is not None


def telegram(message):
    send_message = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}'.format(
        token, chat_id, message)
    response = requests.get(send_message)
    return response.json()


def check_status():
    check_interval = int(config.get('default', 'interval_in_seconds'))

    temp_file_dir = config.get('temp_file', 'directory')
    temp_file_suffix = config.get('temp_file', 'file_suffix')
    temp_file = os.path.join(temp_file_dir, '{}.{}'.format(
        streamer_name, temp_file_suffix))

    if is_streaming(streamer_name):
        if os.path.exists(temp_file):

            with open(temp_file, 'r') as start_time:
                start_time = start_time.readline()

            start_time = float(start_time)
            current_time = time.time()

            stream_duration = current_time - start_time
            stream_duration = int(stream_duration)

            duration_hours = stream_duration // 3600
            duration_minutes = (
                stream_duration - (duration_hours * 3600)) // 60
            duration_seconds = stream_duration - \
                ((duration_hours * 3600) + (duration_minutes * 60))

            print('{} has been streaming for: {} hours, {} minutes, and {} seconds.'.format(
                streamer_name.capitalize(), duration_hours, duration_minutes, duration_seconds))

        if not os.path.exists(temp_file):
            if token and chat_id:
                telegram('[{}]({}) is now streaming!'.format(
                    streamer_name.capitalize(), streamer_url))

            print('{} is online, opening in your default browser'.format(streamer_name))

            start_time = time.time()

            with open(temp_file, 'w+') as timestamp:
                timestamp.write(str(start_time))

            webbrowser.open_new_tab(streamer_url)

            time.sleep(30)

    if not is_streaming(streamer_name):
        if os.path.exists(temp_file):
            os.remove(temp_file)

        if not os.path.exists(temp_file):
            while (check_interval):
                if check_interval > 1:
                    print('{} is offline, checking again in {} seconds '.format(
                        streamer_name, str(check_interval)), end='\r')
                    check_interval -= 1
                    time.sleep(1)
                else:
                    print('{} is offline, checking again in {} second '.format(
                        streamer_name, str(check_interval)), end='\r')
                    check_interval -= 1
                    time.sleep(1)


def the_whole_thing():
    os.system('cls')

    print('#########################')
    print('###   Twitch Stalkr   ###')
    print('###       V {}       ###'.format(ver))
    print('#########################\n')

    check_status()


schedule.every(0.5).seconds.do(the_whole_thing)

while True:
    schedule.run_pending()
time.sleep(1)
