import base64
import json
import os
from PIL import Image
import requests
from urllib import parse
from bs4 import BeautifulSoup
from pprint import pprint  # FOR DEBUGGING: DO NOT REMOVE
from contextlib import suppress
from functools import lru_cache, wraps
import threading
import time
from dotenv import load_dotenv
from fake_headers import Headers

load_dotenv()

logger = logging.getLogger(__name__)

for key in {'SPOTIFY_CLIENT_ID', 'SPOTIFY_SECRET', 'GOOGLE_API'}:
    if key not in os.environ:
        print(f'Some features may be missing due to missing environment variable: {key}')


def time_cache(max_age, maxsize=None, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.
    Args:
        max_age: Time to live for cached results (in seconds).
        maxsize: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """

    def _decorator(fn):
        @lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @wraps(fn)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / max_age))

        return _wrapped

    return _decorator


def background_refresh(interval, default=None):
    """Decorator that refreshes a fetcher's result in a background thread.

    A daemon thread calls the wrapped function every `interval` seconds and stores the
    result. The wrapped function itself just returns the last cached value, so callers
    (e.g. request handlers) never block on the fetch.

    Works for both zero-arg fetchers and ones taking (hashable) arguments: each distinct
    set of arguments gets its own cached value and its own refresh thread, started lazily
    on the first call with those arguments.

    Args:
        interval: Seconds between background refreshes.
        default: Value returned before the first successful fetch completes. If callable,
            it is called to produce the initial value (e.g. `dict` for an empty mapping).
    """

    def _decorator(fn):
        cache = {}  # args-key -> last good value (presence also marks "thread spawned")
        lock = threading.Lock()

        def _spawn(key, args, kwargs):
            thread_name = f'{fn.__name__}-refresh'
            def _loop():
                logger.info('started thread %s: args = (%s) kwargs = %s) {args}', thread_name, *args, **kwargs)
                while True:
                    try:
                        value = fn(*args, **kwargs)
                    except Exception:
                        logger.exception('background_refresh(%s, %s, %s) failed', fn.__name__, *args, **kwargs)
                        value = None
                    if value:  # keep the last good value instead of clobbering on a failed fetch
                        with lock:
                            logger.info('%s: args = %s cache updated key = %s', thread_name, args, key)
                            cache[key] = value
                    time.sleep(interval)

            threading.Thread(target=_loop, name=thread_name, daemon=True).start()

        @wraps(fn)
        def _wrapped(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            with lock:
                is_new = key not in cache
                if is_new:
                    cache[key] = default() if callable(default) else default
            if is_new:  # first call for these args: kick off its refresh thread
                _spawn(key, args, kwargs)
            with lock:
                return cache[key]

        return _wrapped

    return _decorator


@lru_cache(maxsize=1)
def spotify_b64_auth_str():
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_SECRET = os.getenv('SPOTIFY_SECRET')
    SPOTIFY_AUTH_STR = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET}'
    SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()
    return SPOTIFY_B64_AUTH_STR


def get_album_art(artist, title, access_token=None):
    """ Gets the url of album art for the track and artist """
    artist, track = parse.quote_plus(artist), parse.quote_plus(title)
    if access_token is None:
        header = {'Authorization': 'Basic ' + spotify_b64_auth_str()}
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
    r = requests.get(url, params={'key': os.getenv('GOOGLE_API')})
    announcements = json.loads(r.text)['values']
    for a in announcements.copy():
        if len(a) != 2: announcements.remove(a)
    return announcements  # [ [TITLE, DESC], [TITLE, DESC] ]


@background_refresh(60 * 60 * 12, default=dict)
def get_wlu_pool_schedule() -> dict:
    """Scrapes a list of timings for each day (order is Sunday to Saturday)
        from the laurier athletics website and

    Returns:
        dict: {'day': ['timings']}
    """
    days = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
    schedule = {day: [] for day in days}
    data = requests.get('https://recreation.laurierathletics.com/sports/2021/6/30/57_132695382453994610.aspx', headers=Headers(browser='firefox', os='win', headers=True).generate()).text
    soup = BeautifulSoup(data, features='html.parser')
    table = soup.findAll('tr')[1:]
    for row in table:
        cols = row.findAll('td')
        for (day, timing) in zip(schedule, cols):
            if timing.text:
                schedule[day].append(timing.text.strip())
    return schedule


get_wlu_pool_schedule()  # prime the cache / start its refresh thread at import (non-blocking)


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
    print(get_wlu_pool_schedule())
