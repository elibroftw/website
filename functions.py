import base64
import os
import requests
from urllib import parse

try:
    SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
    SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
except KeyError:
    with open('config.txt') as f:
        lines = f.read().splitlines()
        SPOTIFY_CLIENT_ID = lines[0][lines[0].index('=') + 2:]
        SPOTIFY_SECRET = lines[1][lines[1].index('=') + 2:]

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
 