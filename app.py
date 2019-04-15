import json
import os
import sys
import requests
import time
import schedule
import socket
import webbrowser
import cursor

from configparser import ConfigParser

cursor.hide()

appname = 'Twitch Stalkr'
ver = '1.2'

os.system(f'title {appname} v{ver}')

config = ConfigParser()
config.read('config.ini')

client_id = config.get('default', 'client_id')
check_int = int(config.get('default', 'int_in_seconds'))
streamer_name = config.get('default', 'streamer_name')

token = config.get('telegram', 'token')
chat_id = config.get('telegram', 'chat_id')

if not streamer_name:
    streamer_name = input('Streamer to stalk: ').capitalize()
else:
    streamer_name = streamer_name.capitalize()

streamer_url = f'https://twitch.tv/{streamer_name.lower()}'

os.system(f'title Stalking {streamer_name}')


def online():
    try:
        socket.create_connection(('www.google.com', 80))
        return True
    except Exception:
        pass
    return False


def broadcasting(streamer_name):
    twitch_api_stream_url = f'https://api.twitch.tv/kraken/streams/{streamer_name.lower()}?client_id={client_id}'
    streamer_html = requests.get(twitch_api_stream_url)
    streamer = json.loads(streamer_html.content)
    return streamer['stream'] is not None


def telegram(message):
    send_message = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(send_message)
    return response.json()


def status():
    temp_file_dir = config.get('temp_file', 'directory')
    temp_file_suffix = config.get('temp_file', 'file_suffix')
    temp_file = os.path.join(temp_file_dir, f'{streamer_name.lower()}.{temp_file_suffix}')

    if broadcasting(streamer_name):
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as start_t:
                start_t = start_t.readline()

            start_t = float(start_t)
            current_t = time.time()

            dur = current_t - start_t
            dur = int(dur)

            hrs = dur // 3600
            mins = (dur - (hrs * 3600)) // 60
            secs = dur - ((hrs * 3600) + (mins * 60))

            if secs == 1:
                print(
                    f'{streamer_name} has been streaming for: '
                    f'{hrs} hours, {mins} minutes, and '
                    f'{secs} second.', end='\033[K\r', flush=True
                )

            else:
                print(
                    f'{streamer_name} has been streaming for: '
                    f'{hrs} hours, {mins} minutes, and '
                    f'{secs} seconds.', end='\033[K\r', flush=True
                )

        if not os.path.exists(temp_file):
            if token and chat_id:
                telegram(f'[{streamer_name}]({streamer_url}) is now streaming!')

            print(f'{streamer_name} is online, opening in your default browser.', end='\033[K\r', flush=True)
            time.sleep(5)

            start_t = time.time()

            with open(temp_file, 'w+') as timestamp:
                timestamp.write(str(start_t))

            webbrowser.open_new_tab(streamer_url)

            double_protection = int(config.get('default', 'double_protection'))

            while double_protection:
                if double_protection > 1:
                    print(f'{streamer_name} is online, waiting for {double_protection} seconds.', end='\033[K\r', flush=True)
                    double_protection -= 1
                    time.sleep(1)

                else:
                    print(f'{streamer_name} is online, waiting for {double_protection} second.', end='\033[K\r', flush=True)
                    double_protection -= 1
                    time.sleep(1)

    if not broadcasting(streamer_name):
        if os.path.exists(temp_file):
            os.remove(temp_file)

        if not os.path.exists(temp_file):
            check_int = int(config.get('default', 'int_in_seconds'))

            while check_int:
                if check_int > 1:
                    print(f'{streamer_name} is offline, checking again in {check_int} seconds.', end='\033[K\r', flush=True)
                    check_int -= 1
                    time.sleep(1)

                else:
                    print(f'{streamer_name} is offline, checking again in {check_int} second.', end='\033[K\r', flush=True)
                    check_int -= 1
                    time.sleep(1)


def lets_do_this():
    if online():
        try:
            status()
        except Exception:
            pass
    else:
        check_int = int(config.get('default', 'int_in_seconds'))

        while check_int:
            if check_int > 1:
                print(f'You are not connected to the internet. Trying again in {check_int} seconds. ', end='\033[K\r', flush=True)
                check_int -= 1
                time.sleep(1)

            else:
                print(f'You are not connected to the internet. Trying again in {check_int} second.', end='\033[K\r', flush=True)
                check_int -= 1
                time.sleep(1)


print(
    f'#####################\n'
    f'#{appname:^19}#\n'
    f'#{ver:^19}#\n'
    f'#####################\n'
)

schedule.every(0.1).seconds.do(lets_do_this)

while True:
    schedule.run_pending()

time.sleep(0.1)
