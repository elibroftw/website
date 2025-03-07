import io
import mimetypes
import os
import random
import shutil
import pyqrcode
import threading
import time
import zipfile
from contextlib import suppress
from datetime import date, datetime
from pathlib import Path

from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
    Response
)
from flask_compress import Compress
from flask_socketio import SocketIO, emit
from flask_caching import Cache
from git import Repo
from PyPDF2 import PdfFileReader, PdfFileWriter
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

import metadata_setter as MetadataSetter
from blueprints.stripe import stripe_bp
from blueprints.tauri_releases import tauri_releases_bp
from helpers import get_album_art, get_announcements, get_wlu_pool_schedule

# import psycopg2
# compress is a fallback
# best practice is to let the webserver like nginx handle the serving of static files

# DATABASE_URL = os.environ.get('DATABASE_URL', False)
# DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', '')
# if DATABASE_URL: conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# else:
#     try:
#         conn = psycopg2.connect(database='mywebsite', user='postgres', password=DATABASE_PASSWORD)
#     except psycopg2.OperationalError:
#         conn = psycopg2.connect(database='postgres', user='postgres', password=DATABASE_PASSWORD)
#         conn.autocommit = True
#         cursor = conn.cursor()
#         cursor.execute(f'CREATE DATABASE mywebsite;')
#         cursor.close()
#         conn.close()
#         conn = psycopg2.connect(database='mywebsite', user='postgres', password=DATABASE_PASSWORD)

# conn.autocommit = True
# cursor = conn.cursor()
# cursor.execute('CREATE TABLE IF NOT EXISTS visitors (date TIMESTAMPTZ, ip_address TEXT, user_agent TEXT, page_accessed TEXT);')

announcements, wlu_pool_timings, wlu_gym_timings = [], [], []
pool_schedule = ""
metadata_setter_dir = "static/metadataSetter"
shutil.rmtree(metadata_setter_dir, ignore_errors=True)
with suppress(FileExistsError):
    os.mkdir(metadata_setter_dir)

app = Flask(__name__)
app.register_blueprint(tauri_releases_bp)
app.register_blueprint(stripe_bp)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.config["JSON_SORT_KEYS"] = False
if not app.debug:
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 604800
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)
Compress(app)
socketio = SocketIO(app)


try:
    head_rev = os.environ["HEROKU_SLUG_COMMIT"]
except KeyError:
    head_rev = Repo(".").rev_parse("HEAD")


@app.context_processor
def get_style_links():
    return {
        "style_base": f"/static/css/base.css?v={head_rev}",
        "style_light": f"/static/css/light.css?v={head_rev}",
        "style_dark": f"/static/css/dark.css?v={head_rev}",
    }


@app.before_request
def force_https():
    if not request.is_secure and not app.debug and request.path != "/music-caster/":
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


# @app.before_request
# def save_ip():
#     requested_url = request.url
#     if 'static' not in requested_url and 'visitors' not in requested_url and 'favicon' not in requested_url:
#         cursor.execute(f"INSERT INTO visitors VALUES ('{datetime.now()}','{request.remote_addr}','{request.headers.get('User-Agent')}','{requested_url}')")


# @app.after_request
# def add_header(response):
#     if "Cache-Control" not in response.headers:
#         response.headers["Cache-Control"] = "no-cache"
#     return response


@app.errorhandler(404)
def page_not_found(_):
    return render_template("404.html"), 404


@app.get("/apple-touch-icon.png")
@app.get("/android-chrome-192x192.png")
@app.get("/android-chrome-512x512.png")
@app.get("/mstile-150x150.png")
@app.get("/favicon-32x32.png")
@app.get("/favicon-16x16.png")
@app.get("/site.webmanifest")
@app.get("/safari-pinned-tab.svg")
@app.get("/favicon.ico")
def favicons():
    return send_from_directory(Path(app.static_folder) / "favicons", request.path[1:])


@app.route("/robots.txt")
@app.route("/sitemap.xml")
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route("/index/")
def index():
    return render_template("index.html")


with open(Path(app.static_folder) / 'elijahllopezz@gmail.com.gpg') as f:
    GPG_KEY = f.read()


@app.route("/gpg")
def gpg():
    return Response(GPG_KEY, mimetype='text/plain')


@app.route("/")
def home():
    return render_template("home.html", welcome_msg="Ambitious ... without the time")


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/resume/")
def resume():
    return render_template("resume.html")


@app.route("/formula-calculator/")
@app.route("/repls/")
@app.route("/programs/")
def formula_calculator():
    return redirect("https://repl.it/@elilopez/formulas")


@app.route("/social/")
@app.route("/donate/")
@app.route("/contact/")
def contact():
    xmr_addr = "42hpQgwfvFw6RXpmcXHBJ85cZs9yF97kqfV3JpycnanG7JazfdL4WHkVLuR8rcM64q6LHt547nKeeYaixBdCQYaHSuEnAuj"
    return render_template("social.html", xmr_addr=xmr_addr)


@app.route("/resources/")
def resources():
    return render_template("resources.html")


@app.route("/blog/")
@app.route("/articles/")
def articles():
    return render_template("blog.html")


@app.get("/qr-code-generator/")
def qr_code():
    text = request.args.get("text")
    image_data = ''
    if text is not None:
        qr_code = pyqrcode.create(text)
        image_data = qr_code.png_as_base64_str(scale=15, module_color=(0, 0, 0, 255), background=(255, 255, 255, 255), quiet_zone=1)
    return render_template("qr_code.html", image_data=image_data)


@app.get("/search-album-art/")
def search_album_art():
    artist = request.args.get("artist")
    track = request.args.get("track")
    try:
        if None in (artist, track) or "" in (artist, track):
            raise IndexError
        image_url, alt_text = get_album_art(artist, track), f"{track} Album Cover"
    except IndexError:
        image_url, alt_text = "", ""
    return render_template(
        "search_album_art.html", image_url=image_url, alt_text=alt_text
    )


def delete_file(filename):
    time.sleep(600)  # 10 minutes
    with suppress(OSError):
        os.remove(filename)


@app.route("/metadata-setter/", methods=["GET", "POST"])
def metadata_setter():
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file.filename != "":
            filename = secure_filename(file.filename)
            save_name = filename.replace("_", " ")
            save_path = os.path.join(metadata_setter_dir, save_name).replace("\\", "/")
            file.save(save_path)
            threading.Thread(
                target=delete_file, args=(f"{metadata_setter_dir}/{save_name}",)
            ).start()  # delete file in 10 minutes
            try:
                MetadataSetter.set_simple_meta(save_path)
            except Exception as e:
                return {
                    "filename": save_name,
                    "url": url_for("static", filename=f"metadataSetter/{save_name}"),
                    "error": str(e),
                }
            return {
                "filename": save_name,
                "url": url_for("static", filename=f"metadataSetter/{save_name}"),
            }
    return render_template("metadata_setter.html")


@app.route("/metadata-setter/<filename>", methods=["GET", "POST"])
def upload():
    return str("file" in request.files)


@app.route("/split-pdf/", methods=["GET", "POST"])
def split_pdf():
    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename.endswith(".pdf"):
            filename = secure_filename(request.files["file"].filename)[:-4]
            template = request.values.get("template", "")
            use_template = template.endswith(".pdf")
            inputpdf = PdfFileReader(request.files["file"].stream)
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(
                zip_buffer, "w", compression=zipfile.ZIP_DEFLATED
            ) as zip_file:
                for i in range(inputpdf.numPages):
                    output = PdfFileWriter()
                    output.addPage(inputpdf.getPage(i))
                    if use_template:
                        page_name = template.replace("{i}", str(i))
                    else:
                        page_name = f"{filename}_pg_{i}.pdf"
                    data = io.BytesIO()
                    output.write(data)
                    zip_file.writestr(page_name, data.getvalue())
            zip_filename = filename + ".zip"  # replace pdf with zip
            zip_buffer.seek(0)
            return send_file(zip_buffer, download_name=zip_filename, as_attachment=True)
        return redirect("/split-pdf/")
    return render_template("split_pdf.html")


@app.route("/combine-pdf/", methods=["GET", "POST"])
def combine_pdf():
    if request.method == "POST":
        if "files" in request.files and request.files["files"].filename.endswith(
            ".pdf"
        ):
            filename = secure_filename(request.files["files"].filename)[:-4]  # default
            new_name = request.values.get("new-name", "")
            dl_name = (
                new_name if new_name.endswith(".pdf") else filename + "_combined.pdf"
            )
            data = io.BytesIO()
            output = PdfFileWriter()
            for file in request.files.getlist("files"):
                inputpdf = PdfFileReader(file.stream)
                for i in range(inputpdf.numPages):
                    output.addPage(inputpdf.getPage(i))
            output.write(data)
            # data.seek(0)
            return send_file(data, download_name=dl_name, as_attachment=True)
        return redirect("/combine-pdf/")
    return render_template("combine_pdf.html")


@app.route("/krunker/", methods=["GET"])
@app.route("/krunker-stats/", methods=["GET"])
def krunker_stats():
    krunker_username = request.args.get("krunker-username")
    if krunker_username in (None, ""):
        return render_template("krunker_stats.html")
    return redirect(f"https://krunker.io/social.html?p=profile&q={krunker_username}")


@app.route("/shift/")
def shift():
    return redirect("https://elijahlopez.itch.io/shift")


@app.route("/projects/")
@app.route("/software/")
def software():
    return render_template("software.html", title=request.path[1:-1].capitalize())


@app.route("/consulting/")
def consulting():
    return render_template("consulting.html")


@app.route("/cloud-copy/")
def cloud_copy():
    return render_template("cloud_copy.html")


@app.route("/music-caster/")
def music_caster():
    if request.args and "args" in request.args:
        args = ";".join(request.args.getlist("args"))
        return redirect(f"music-caster:{args}")
    # second var is width
    images = [
        (
            "https://github.com/elibroftw/music-caster/blob/master/resources/screenshots/main.webp?raw=true",
            "Main",
        ),
        (
            "https://github.com/elibroftw/music-caster/blob/master/resources/screenshots/mini.webp?raw=true",
            "Mini-Mode",
        ),
        (
            "https://github.com/elibroftw/music-caster/blob/master/resources/screenshots/tray.webp?raw=true",
            "Tray",
        ),
        (
            "https://github.com/elibroftw/music-caster/blob/master/resources/screenshots/web.webp?raw=true",
            "Web GUI",
        ),
    ]
    return render_template("music_caster.html", images=images)


@app.route("/rbhs/")
def rbhs():
    global announcements
    today = date.today()
    d2 = os.environ.get("RBHS")
    if d2 is not None:
        d2 = datetime.strptime(d2, "%d/%m/%Y").date()
    if d2 is None or not announcements or d2 < today:
        announcements = get_announcements()
        if announcements:
            temp = ""
            for i, info in enumerate(announcements):
                title, desc = info
                temp += f'<button class="accordion" id="no.{i + 1}">{title}</button><div class="panel"><p id="panel-text">{desc}</p></div>'
            os.environ["RBHS"] = today.strftime("%d/%m/%Y")
            announcements = temp
        else:
            announcements = (
                "<p style='color: white;'>There are no announcements for today</p>"
            )
    return render_template("rbhs.html", announcements=announcements)


@app.route("/wlu-pool/")
@app.route("/wlu-pool-schedule/")
def wlu_pool_schedule():
    schedule = get_wlu_pool_schedule()
    resp = make_response(render_template("wlu_pool.html", schedule=schedule.items()))
    resp.cache_control.max_age = 60 * 60 * 12
    return resp


@app.route("/socketio/")
@app.route("/socket/")
def socketio_example():
    return render_template("socket.html")


@socketio.on("get_quote")
def return_random_quote():
    emit("return_quote", random.choice(["quote1", "quote2", "quote3"]))


@socketio.on("print_message")
def return_random_quote_other(dictionary):
    print(dictionary.items())


@socketio.on("disconnect")
def socketio_disconnect():
    print("client disconnected")


@app.route("/graphic-design/")
@app.route("/creative-works/")
@app.route("/creations/")
@app.route("/wallpapers/")
def creative_works():
    return render_template("creations.html")


@app.route("/new-tab/")
def new_tab():
    return render_template("new_tab.html")


# @app.route('/photos/')  # TODO
# def photos():
#     return render_template('photos.html')


# @app.route('/menus/')  # TODO
# def menus():
#     return render_template('menus.html')


# @app.route('/stats/')
# def stats():
#     # all time should only be updated daily later onwards...
#     # SELECT * from table where date >= '2010-03-01' AND date < '2010-04-01'
#     cursor.execute('SELECT COUNT(DISTINCT ip_address) FROM visitors')
#     all_time = cursor.fetchone()[0]
#     return render_template('stats.html', all_time=all_time, monthly='N/A', today='N/A')


# @app.route('/visitors/')
# def visitors():
#     cursor.execute('SELECT * FROM visitors')
#     rows = cursor.fetchall()
#     temp = ''
#     for row in rows:
#         row = [str(item) for item in row]
#         temp += ', '.join(row)
#         temp += '<br>'
#     return temp


# @app.route('/to_ico/')
# def to_ico():
#     return render_template('to_ico.html')


# @app.route('/get_ico/', methods=['POST'])
# def get_ico():
#     file = request.args.get('track')
#     if file is None:
#         file = ''
#     return render_template('to_ico.html')


if __name__ == "__main__" or app.debug:
    print("development")
    # guaranteed to be running locally
    assert os.path.exists(".env")
    # TODO: subprocess the react app?

    # DEV configuration
    # app.config["PROFILE"] = True
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    REACT_DISTR_DIR = "react-app/dist"

    @app.route("/react/<path:path>")
    def react_static(path):
        return send_from_directory(REACT_DISTR_DIR, path)

    @app.route("/react/")
    def react():
        return send_from_directory(REACT_DISTR_DIR, "index.html")

    @app.route("/test/")
    def test_page():
        return render_template("test.html")

    host = "127.0.0.1"  # ''
    port = 5001
    print(f"Running on http://{host}:{port}")

if __name__ == "__main__":
    app.run(debug=True, host=host, port=port)
    # socketio.run(app, debug=True, host='', port=5000)
