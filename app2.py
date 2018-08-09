import os
import flask
from flask import Flask, render_template, request
from flask_compress import Compress

from funcs import get_album_art
from ib_economics import get_template_data
# import redis


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
Compress(app)
home_template_data = get_template_data()


# limiter = Limiter(
#     app,
#     key_func=get_remote_address,
#     default_limits=["200 per day", "50 per hour"]
# )

# try:
#     r = redis.from_url(os.environ.get("REDIS_URL"))
# except KeyError:
#     use local redis
# cache = Cache(config={'CACHE_TYPE': 'simple'})


@app.after_request
def add_header(response):
    # print(response.name)
    # print(response.headers['name'])
    # response.headers['Cache-Control'] = 'public, max-age=1000'  # also works
    if 'Cache-Control' not in response.headers:
        # response.headers['Cache-Control'] = 'public, max-age=1000'
        response.cache_control.max_age = 300
        response.cache_control.public = True
        print(response.headers['Cache-Control'])
    # response.cache_control.max_age = 1000  # you can use strings or integers
    # print(response.headers['Cache-Control'])
    return response


@app.errorhandler(404)
def page_not_found(ERROR): return 'Page not Found', 404  # render_template('page_not_found.html'), 404  # (error)


@app.route('/shift')
def game_shift():
    return render_template('shift.html')


@app.route('/')
def home(): return render_template('new_home.html')


@app.route('/about/')
def about(): return render_template('about.html')


@app.route('/programs/')  # todo: make this a drop down menu as well
def index(): return render_template('programs.html')


@app.route('/contact/')
def contact(): return render_template('contact.html')


@app.route('/resources/')
def resources(): return render_template('resources.html')


@app.route('/search-album-art/', methods=['GET'])
def album_art_finder():
    artist = request.args.get('artist')
    track = request.args.get('track')
    if None in (artist, track) or '' in (artist, track): image_url = 'image not found'
    else:
        try: image_url = get_album_art(artist, track)
        except IndexError: image_url = 'image not found'
    return render_template('search_album_art.html', image_url=image_url)


@app.route('/ib-economics-schedule/')
def ib_economics_schedule():
    return render_template('table.html', data=home_template_data)


# @app.route('/shift-high-scores/new/', methods=['POST'])
# def new_shift_high_score():
#     high_score = request.form['highScore']
#     name = request.form['name']
#     high_scores = []
#     high_scores_users = []
#     for x in rang(1, 11):
#         high_scores.append(redis.get(f'shift_high_score_{x}_value'))
#         high_scores_users.append(redis.get(f'shift_high_score_{x}_user'))
#     for x in rang(10):
#         if high_score < high_scores[x]:
#             high_scores.insert(x, high_score)
#             high_scores.pop()
#             high_scores_users.insert(x, name)
#             for i, v in enumerate(high_scores):
#                 redis.set(f'shift_high_score_{i+1}_value', v)
#             for i, v in enumerate(high_scores_users):
#                 redis.set(f'shift_high_score_{i+1}_user', v)
#             return 'top 10 high score'
#     return 'not a top 10 high score'


# @app.route('/shift-high-scores/)
# def shift-high-scores():  # returns table of highscores, might add level scores
#     # get high scores from db
#     return render_template('shift_high_scores.html')


# @app.route('/reset-shift-high-scores/')
# def test():
#     for x in rang(1, 11):
#         redis.set(f'shift_high_score_{x}_value', 999999999)  # seconds
#         redis.set(f'shift_high_score_{x}_user', "defalt")  # default username is an easter egg
#     return "it's done"


if __name__ == '__main__':
    try:
        os.environ['SPOTIFY_CLIENT_ID']
        app.run()
    except KeyError:  # this will only happen when running locally so yeah
        app.run(host='localhost', port=99)