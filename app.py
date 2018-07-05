from flask import Flask, render_template, request
import flask
from flask_compress import Compress
from funcs import get_template_data, get_album_art
# from flask import request
# import threading
# from funcs import get_external_ip, get_external_ip2
# from flask_cache import Cache
variables = {'name': 'Elijah'}
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
# cache = Cache(config={'CACHE_TYPE': 'simple'})
Compress(app)
home_template_data = get_template_data()
# app.config['CACHE_TYPE'] = 'simple'
# app.cache = Cache(app)


#  render_template('file.html', func=FUNCNAME) works
@app.after_request
def add_header(response):
    # print(response.name)
    # print(response.headers['name'])
    # response.headers['Cache-Control'] = 'public, max-age=1000'  # also works
    if 'Cache-Control' not in response.headers:
        # print(response.headers['Cache-Control'])
        # response.headers['Cache-Control'] = 'public, max-age=1000'
        response.cache_control.max_age = 1000  # this doesn't work here
    # response.cache_control.max_age = 1000  # you can use strings or integers
    # print(response.headers['Cache-Control'])
    return response


@app.errorhandler(404)
def page_not_found(ERROR): return 'Page not Found', 404  # render_template('page_not_found.html'), 404  # (error)


@app.route('/shift')
def game_shift():
    resp = flask.Response(render_template('shift.html'))
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    # resp.headers['Cache-Control'] = 100  # doesn't work
    # resp.cache_control.max_age = 100  # doesn't work
    return resp
    # return render_template('shift.html')


@app.route('/')
def home(): return render_template('home.html', name=variables['name'])

# <!--{{nav.top_nav.render()}}-->


@app.route('/about/')
def about(): return render_template('about.html')


@app.route('/programs/')  # todo: make this a drop down menu as well
def index(): return render_template('programs.html')


@app.route('/contact/')
def contact(): return 'This page is still in development'


@app.route('/resources/')
def resources(): return render_template('resources.html')


@app.route('/search-album-art/', methods=['GET'])
def album_art_finder():
    artist = request.args.get("artist")
    track = request.args.get("track")
    if None in (artist, track) or "" in (artist, track): image_url = '://0'
    else: image_url = get_album_art(artist, track)
    return render_template('search_album_art.html', image_url=image_url)


@app.route('/ib-economics-schedule/')
def ib_economics_schedule():
    return render_template('table.html', data=home_template_data)


# @app.route('/user/<username>')
# def show_user_profile(username):
#     # show the user profile for that user
#     return f'User {username}'
#
#
# @app.route('/post/<int:post_id>')
# def show_post(post_id):
#     # show the post with the given id, the id is an integer
#     return f'Post {post_id}'


if __name__ == '__main__':
    # threading.Thread(target=get_external_ip).start()
    # print('http://elibro.asuscomm.com:99/')
    # request.headers.get('Cache-Control')
    # app.run(host='192.168.2.219', port=99)
    # app.run(host='localhost', port=99)
    app.run()
