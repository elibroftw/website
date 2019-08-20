import base64
import json
import os
import requests
from urllib import parse
from PIL import Image
from environs import Env

env = Env()
env.read_env()


GOOGLE_API_KEY = os.environ['GOOGLE_API']
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_AUTH_STR = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET}'
SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()


def get_album_art(artist, track, access_token=None) -> str:
    """ Gets url of album art for the track"""
    artist, track = parse.quote_plus(artist), parse.quote_plus(track)
    if access_token is None:
        header = {'Authorization': 'Basic ' + SPOTIFY_B64_AUTH_STR}
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
        access_token = access_token_response.json()['access_token']
    header = {'Authorization': 'Bearer ' + access_token}
    r = requests.get(f'https://api.spotify.com/v1/search?q={track}+artist:{artist}&type=track', headers=header)
    return r.json()['tracks']['items'][0]['album']['images'][0]['url']


def img_to_ico(path):
    base = os.path.basename(path)
    img_name = os.path.splitext(base)[0]
    directory = os.path.dirname(path)
    img = Image.open(path)
    img.save(f'{directory}/{img_name}.ico')
    # TODO: upload to https://send.firefox.com/ when API comes out
    # TODO: tell user to upload to send.firefox.com if they want to share the file


def get_announcements():
    sheet_id = '1Re7s1xqGNJH89iUTha-nTeerJXN-61C3mvLW6dqttks'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/%20FilteredForm!$A$4:$YY'
    r = requests.get(url, params={'key': GOOGLE_API_KEY})
    announcements = json.loads(r.text)['values']
    for a in announcements.copy():
        if len(a) != 2: announcements.remove(a)
    return announcements  # [ [TITLE, DESC], [TITLE, DESC] ]
