import os
import requests
import json
from  environs import Env

env = Env()
env.read_env()
google_api_key = os.environ['GOOGLE_API']


def get_announcements():
    sheet_id = '1Re7s1xqGNJH89iUTha-nTeerJXN-61C3mvLW6dqttks'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/%20FilteredForm!$A$4:$YY'
    r = requests.get(url, params={'key': google_api_key})
    announcements = json.loads(r.text)['values']
    return announcements