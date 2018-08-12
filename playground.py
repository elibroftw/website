import re

import requests
from flask import Flask, render_template, request
from flask_compress import Compress
from bs4 import BeautifulSoup
app = Flask(__name__)


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
Compress(app)


# @app.after_request
# def add_header(response):
#     # print(response.name)
#     # print(response.headers['name'])
#     # response.headers['Cache-Control'] = 'public, max-age=1000'  # also works
#     if 'Cache-Control' not in response.headers:
#         # print(response.headers['Cache-Control'])
#         # response.headers['Cache-Control'] = 'public, max-age=1000'
#         response.cache_control.max_age = 1000  # this doesn't work here
#     # response.cache_control.max_age = 1000  # you can use strings or integers
#     # print(response.headers['Cache-Control'])
#     return response


@app.route('/')
def home(): return render_template('test.html')


@app.route('/', methods=['SEND'])
def my_form_post():
    text = request.form['text']
    print(text)
    processed_text = f'You sent {text}'
    return render_template('test.html', display_text=processed_text)


# @app.route('/user/<username>')
# def show_user_profile(username):
#     # show the user profile for that user
#     return f'User {username}'


# @app.route('/post/<int:post_id>')
# def show_post(post_id):
#     # show the post with the given id, the id is an integer
#     return f'Post {post_id}'


def get_my_ip(alternative=False):
    res = requests.get('http://www.whatsmyip.org/')
    if alternative:
        ip = re.compile('(\d{1,3}\.){3}\d{1,3}').search(res.text).group()
        if ip != "": return ip
    soup = BeautifulSoup(res.content, 'html.parser')
    ip = soup.find('span', style="color: blue; font-size: 36px; font-weight: 600;").text
    return ip


#  render_template('file.html', func=func_name) works

app.run(host='localhost', port='99')
