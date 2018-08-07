import base64
import os
import markdown
from bs4 import BeautifulSoup
import requests
import get_data
import re
# from time import time
# import pypyodbc
# import os

schedule_data = get_data.get_data()
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_AUTH_STR = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET}'
SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()


def get_external_ip2():
    url = 'http://www.whatsmyip.org/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    name = soup.find('span', style="color: blue; font-size: 36px; font-weight: 600;").text
    print(f' External ip: http://{name}:99/')
    return name


def get_external_ip():
    res = requests.get("http://www.whatsmyip.org/")
    ip = re.compile('(\d{1,3}\.){3}\d{1,3}').search(res.text).group()
    if ip != "":
        print(f' External ip: http://{ip}:99/')
        return ip
    print('ERROR occured while getting ip adress')

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


def make_html_friendly(text):
    return markdown.markdown(text).replace('<p>', '').replace('</p>', '')


def info_to_html(month_name, day, info):
    return f'\n<td id={month_name}{day}><i>{month_name} {day}</i><br/>{info}</td>'


def get_template_data():
    template = ''
    last_weekday = 0
    for k, v in schedule_data.items():
        if k.get_weekday_name() == 'Monday':
            if not template.endswith('</tr>'): template += '</tr>'
            template += '\n<tr>'
            template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
        else:
            # if template.endswith('</tr>'):
            #     template += '\n<tr>'
            #     for i in range(k.weekday - 1):
            #         template += '\n<td></td>'
            #     template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
            if k.weekday < last_weekday:
                template += '\n</tr>'
                for i in range(k.weekday):
                    template += '\n<td></td>'
                template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
            else:
                template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
            # if k.weekday == 6: template += '\n</tr>'  # also maybe use 4
        last_weekday = k.weekday
    if not template.endswith('</tr>'): template += '\n</tr>'
    return template


def get_album_art(artist, track, access_token=None) -> str:
    """ Gets url of album art for the track"""
    artist, track = urllib.parse.quote_plus(artist), urllib.parse.quote_plus(track)
    if access_token is None:
        header = {'Authorization': 'Basic ' + SPOTIFY_B64_AUTH_STR}
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
        access_token = access_token_response.json()['access_token']
    header = {'Authorization': 'Bearer ' + access_token}
    r = requests.get(f'https://api.spotify.com/v1/search?q={track}+artist:{artist}&type=track', headers=header)
    return r.json()['tracks']['items'][0]['album']['images'][0]['url']
