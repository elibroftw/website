import os
from flask import Flask, render_template, request, redirect, send_from_directory, send_file, url_for
from flask_compress import Compress
from datetime import datetime, date
from contextlib import suppress
from functions import get_album_art, get_announcements
from werkzeug.utils import secure_filename
import sys
import requests
# from ib_economics import get_template_data
announcements = []

url = 'https://cssminifier.com/raw'
data = {'input': open('static/css/style.css', 'rb').read()}
r = requests.post(url, data=data)
with open('static/css/style.css', 'w') as f:
    f.write(r.text)

data = {'input': open('static/css/dark.css', 'rb').read()}
r = requests.post(url, data=data)
with open('static/css/dark.css', 'w') as f:
    f.write(r.text)


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 if os.environ.get('DEVELOPMENT', False) else 604800
Compress(app)


@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.cache_control.max_age = 300
        response.cache_control.public = True
    return response


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


@app.route('/')
def home(): return render_template('home.html')


@app.route('/about/')
def about(): return render_template('about.html')


@app.route('/resume/')
def resume():
    return render_template('resume.html')


@app.route('/repls/')
@app.route('/programs/')  # todo: turn this into a drop down menu
def repls(): return render_template('repls.html')


@app.route('/programs/exxon/')  # todo
def exxon(): return render_template('404.html')


@app.route('/contact/')
def contact(): return render_template('contact.html')


@app.route('/resources/')
def resources(): return render_template('resources.html')


@app.route('/search-album-art/', methods=['GET'])
def search_album_art():
    artist = request.args.get('artist')
    track = request.args.get('track')
    if None in (artist, track) or '' in (artist, track):
        image_url, alt_text = 'image not found', ''
    else:
        try:
            image_url, alt_text = get_album_art(artist, track), f'{track} Album Cover'
        except IndexError:
            image_url, alt_text = 'image not found', ''
    return render_template('search_album_art.html', image_url=image_url, alt_text=alt_text)


@app.route('/krunker/', methods=['GET'])
@app.route('/krunker-stats/', methods=['GET'])
def krunker_stats():
    krunker_username = request.args.get('krunker-username')
    if krunker_username in (None, ''):
        return render_template('krunker_stats.html')
    return redirect(f'https://krunker.io/social.html?p=profile&q={krunker_username}')


@app.route('/shift/')
def shift():
    return redirect('https://elijahlopez.itch.io/shift')


if os.environ.get('DEVELOPMENT', False):
    @app.route('/test/', methods=['GET', 'POST'])
    def test():
        if request.method == 'POST' and 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                with open('test.txt', 'w') as f:
                    f.write('test\n')
                filename = secure_filename(file.filename)
                save_name = filename.replace('_', ' ')
                save_path = os.path.join('static/MP3Editor', save_name)
                file.save(save_path)
                # do other stuff
                return url_for('static', filename=f'MP3Editor/{save_name}')
        return render_template('test.html')
    
    @app.route('/test2/')
    def test2():
        return render_template('test2.html')


@app.route('/done/<filename>', methods=['GET', 'POST'])
def upload():
    return str('file' in request.files)


@app.route('/projects/')
@app.route('/software/')
def software():
    return render_template('software.html')


@app.route('/todo/')
def todo():
    # TODO: I want this to be a todo list that will automatically update the github repo so that it gets carried on
    # TODO: I would have to implement a username and password to only allow me to edit it
    # TODO: Learn databases
    return render_template('404.html')


@app.route('/menus/')
def menus():
    return render_template('menus.html')


@app.route('/rbhs/')
def rbhs():
    global announcements
    today = date.today()
    d2 = os.environ.get('RBHS')
    if d2 is not None: d2 = datetime.strptime(d2, '%d/%m/%Y').date()
    if d2 is None or not announcements or d2 < today:
        announcements = get_announcements()
        if announcements:
            temp = ''
            i = 1
            for title, desc in announcements:
                temp += f'<button class="accordion" id="no.{i}">{title}</button><div class="panel"><p>{desc}</p></div>'
            os.environ['RBHS'] = today.strftime('%d/%m/%Y')
            announcements = temp
        else: announcements = "<p style='color: white;'>There are no announcements for today</p>"
    return render_template('rbhs.html', announcements=announcements)


@app.route('/to_ico/')
def to_ico():
    return render_template('to_ico.html')

# @app.route('/get_ico/', methods=['POST'])
# def get_ico():
#     file = request.args.get('track')
#     if file is None:
#         file = ''
#     return render_template('to_ico.html')

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
# def shift-high-scores():  # returns table of high scores, might add level scores
#     # get high scores from db
#     return render_template('shift_high_scores.html')


# @app.route('/reset-shift-high-scores/')
# def reset():
#     for x in rang(1, 11):
#         redis.set(f'shift_high_score_{x}_value', 999999999)  # seconds
#         redis.set(f'shift_high_score_{x}_user', "default")  # default username is an easter egg
#     return "it's done"


if __name__ == '__main__':
    if not os.path.exists('static/MP3Editor'): os.mkdir('static/MP3Editor')
    app.run(debug=True, host='', port=5000)
