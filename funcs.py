import base64
import os
from bs4 import BeautifulSoup
import requests
import re
# from time import time
# import pypyodbc


try:
    SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
    SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
except KeyError:
    with open('config.txt') as f:
        lines = f.read().splitlines()
        SPOTIFY_CLIENT_ID = lines[0][lines[0].index('=')+2:]
        SPOTIFY_SECRET = lines[1][lines[1].index('=')+2:]

SPOTIFY_AUTH_STR = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET}'
SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()


# def database():
#     cwd = os.getcwd()
#     print(cwd)
#     file = cwd + r'\Information.accdb'
#     print(file)
#     pypyodbc.lowercase = False
#     conn = pypyodbc.connect(
#         r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
#         r"Dbq=C:\Users\maste\Documents\Python Projects\Website\Information.accdb;")
#     cur = conn.cursor()
#     cur.execute("SELECT ID, First_Name, Last_Name, Pw, Date_of_Birth FROM Information")
#     while True:
#         row = cur.fetchone()
#         if row[1] is None: break
#         birth_date = row.get('Date_of_Birth').date()  # get date from datetime.datetime
#         print(f"User {row.get('ID')} is {row.get('First_Name')} {row.get('Last_Name')}")
#         print(f"User {row.get('ID')} has password {row.get('pw')}")
#         print(f"User {row.get('ID')} was born on {birth_date}")
#     cur.close()
#     conn.close()


def get_album_art(artist, track, access_token=None) -> str:
    """Gets url of album art for the track"""
    artist, track = urllib.parse.quote_plus(artist), urllib.parse.quote_plus(track)
    if access_token is None:
        header = {'Authorization': 'Basic ' + SPOTIFY_B64_AUTH_STR}
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
        access_token = access_token_response.json()['access_token']
    header = {'Authorization': 'Bearer ' + access_token}
    r = requests.get(f'https://api.spotify.com/v1/search?q={track}+artist:{artist}&type=track', headers=header)
    return r.json()['tracks']['items'][0]['album']['images'][0]['url']
