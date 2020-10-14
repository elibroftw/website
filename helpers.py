import base64
from environs import Env
import json
import os
from PIL import Image
import requests
from urllib import parse
from bs4 import BeautifulSoup
from pprint import pprint  # FOR DEBUGGING: DO NOT REMOVE


env = Env()
env.read_env()
GOOGLE_API_KEY = os.getenv('GOOGLE_API')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_SECRET = os.getenv('SPOTIFY_SECRET')
SPOTIFY_AUTH_STR = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET}'
SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()


def get_album_art(artist, title, access_token=None):
    """ Gets the url of album art for the track and artist """
    artist, track = parse.quote_plus(artist), parse.quote_plus(title)
    if access_token is None:
        header = {'Authorization': 'Basic ' + SPOTIFY_B64_AUTH_STR}
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
        access_token = access_token_response.json()['access_token']
    header = {'Authorization': 'Bearer ' + access_token}
    r = requests.get(f'https://api.spotify.com/v1/search?q={title}+artist:{artist}&type=track', headers=header)
    return r.json()['tracks']['items'][0]['album']['images'][0]['url']


def img_to_ico(path):
    base = os.path.basename(path)
    img_name = os.path.splitext(base)[0]
    directory = os.path.dirname(path)
    img = Image.open(path)
    img.save(f'{directory}/{img_name}.ico')
    # TODO: upload to https://send.firefox.com/


def get_announcements():
    sheet_id = '1Re7s1xqGNJH89iUTha-nTeerJXN-61C3mvLW6dqttks'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/%20FilteredForm!$A$4:$YY'
    r = requests.get(url, params={'key': GOOGLE_API_KEY})
    announcements = json.loads(r.text)['values']
    for a in announcements.copy():
        if len(a) != 2: announcements.remove(a)
    return announcements  # [ [TITLE, DESC], [TITLE, DESC] ]


def wlu_pool_schedule_scraper():
    data = requests.get('https://www.laurierathletics.com/generatePage.php?ID=57').text
    soup = BeautifulSoup(data, features='html.parser')
    s1 = soup.findAll('tr')
    schedule = [[] for _ in range(7)]
    for timings in s1[1:]:
        timings = timings.findAll('td')
        for i, timing in enumerate(timings):
            if timing.text: schedule[i].append(timing.text)
    # sunday - saturday
    return schedule


def wlu_gym_schedule_scraper():
    data = requests.get('https://www.laurierathletics.com/generatepage.php?ID=86').text
    soup = BeautifulSoup(data, features='html.parser')
    # soup = soup.find('table')
    # s1 = soup.findAll('p')
    # schedule = [[] for _ in range(7)]
    # # pprint(soup)
    # for timings in s1[1:]:
    #     timings = timings.findAll('td')
    #     for i, timing in enumerate(timings):
    #         if timing.text: schedule[i].append(timing.text)
    # # sunday - saturday
    # return schedule


if __name__ == '__main__':  # TESTS / DEBUGGING
    # print(wlu_pool_schedule_scraper())
    print(wlu_gym_schedule_scraper())
