from flask import Blueprint, Response, render_template
import json
from jinja2 import TemplateNotFound
from helpers import time_cache, suppress
import requests

tauri_releases = Blueprint('tauri_releases', __name__, url_prefix='/tauri-releases')

@time_cache(60 * 5)  # every 5 minutes
def google_keep_release() -> dict:
    """ Return format:
        Unsure if v is supposed to be used.
        Note darwin-aarch64 is silicon macOS. Supposed to seperate file but assumed that x64 would work due to Rosetta Stone 2
        {
          "version": "v1.0.8",
          "notes": "- Test updater",
          "pub_date": "2022-11-13T03:20:32Z",
          "platforms": {
            "linux-x86_64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/google-keep_1.0.8_amd64.AppImage.tar.gz",
              "sig": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWHVmYzVwc2RzZXBkcTdDWmNQNmNiVjBLWUcyUkhMSnlPV3ZqVVhWN3MvaU9QQlFXSVZMQjdScDljM3FZaXhXZnhKejIrWG84bE5KbEFsSDErdjF2aGdNPQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NTU0CWZpbGU6Z29vZ2xlLWtlZXBfMS4wLjhfYW1kNjQuQXBwSW1hZ2UudGFyLmd6CmlpVG9kSzBVNU9BMXRIL3l2MlZ6dnJDNndHeUQrK1NIaDdmbkU1MUNVZFk2eHlneEVCZ255SnI4U3FMR0lSOUFNNHFzUHdJbEZmS2JtZUlpSllWWUNBPT0K"
            },
            "darwin-x86_64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/Google.Keep.app.tar.gz",
              "sig": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWG1qc2paOHJDUnBCVHRuMlRZdFdZeXJURGM2Yk9meVRtSmZlWHBEa0dCcEd0eDd3YVkvZlRxakt1ZTNmbHV6anpQam1SakdSaXc2Y1NEZmFaVXoxaWdrPQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NTE4CWZpbGU6R29vZ2xlIEtlZXAuYXBwLnRhci5negp2S1dwYmszQTRkMXFzb2lneFJPbytmenpLS0g4RXEydVY0MmtUb0VTQXg2ZWpYWXF2QndnTXdUVjZNU29uMW5zZElPMFNkeGxBU1VtUmZCSkkzUHZEZz09Cg=="
            },
            "darwin-aarch64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/Google.Keep.app.tar.gz",
              "sig": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWG1qc2paOHJDUnBCVHRuMlRZdFdZeXJURGM2Yk9meVRtSmZlWHBEa0dCcEd0eDd3YVkvZlRxakt1ZTNmbHV6anpQam1SakdSaXc2Y1NEZmFaVXoxaWdrPQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NTE4CWZpbGU6R29vZ2xlIEtlZXAuYXBwLnRhci5negp2S1dwYmszQTRkMXFzb2lneFJPbytmenpLS0g4RXEydVY0MmtUb0VTQXg2ZWpYWXF2QndnTXdUVjZNU29uMW5zZElPMFNkeGxBU1VtUmZCSkkzUHZEZz09Cg=="
            },
            "windows-x86_64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/Google.Keep_1.0.8_x64_en-US.msi.zip",
              "sig": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWG8zdHhmRFBTQndFV0lvWU02YU8vMGwrdUc4NjY4Vm9IbGpyWWU1Z1ZDUVg1L3Y4SUl2YVcxUXNJbW9kUEZkU3lscUhFZXU0MnhWTGMvOXJMY3RNdUE0PQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NDMyCWZpbGU6R29vZ2xlIEtlZXBfMS4wLjhfeDY0X2VuLVVTLm1zaS56aXAKR2NhK1dwRTJMZFhOZG12dWNTNnNXZHpFSFVoM2g1ZnNlVDJtK2lpMGk2M2pqSUlTRStSN09veVc1U0ZjNzM5blVjWU9oNTlONmFBUmFuYVpVVldBRHc9PQo="
            }
          }
        }
    """
    try:
        release = requests.get('https://api.github.com/repos/elibroftw/google-keep-desktop-app/releases/latest').json()
        releases = {
            'version': release['tag_name'],
            'notes': release['body'].removesuffix('See the assets to download this version and install.').rstrip('\r\n '),
            'pub_date': release['published_at'],
            'platforms': {}}
        platforms = [ # platform, extension
            (('linux-x86_64',), 'amd64.AppImage.tar.gz'),
            (('darwin-x86_64', 'darwin-aarch64'), 'app.tar.gz'),
            (('windows-x86_64',), 'x64_en-US.msi.zip'),
        ]
        for asset in release.get('assets', []):
            for for_platforms, extension in platforms:
                if asset['name'].endswith(extension):
                    for platform in for_platforms:
                        releases['platforms'][platform] = {**releases['platforms'].get(platform, {}), 'url': asset['browser_download_url']}
                elif asset['name'].endswith(f'{extension}.sig'):
                    for platform in for_platforms:
                        try:
                            sig = requests.get(asset['browser_download_url']).text
                        except requests.RequestException:
                            sig = ''
                        releases['platforms'][platform] = {**releases['platforms'].get(platform, {}), 'sig': sig}
        return releases
    except requests.RequestException:
        return {}


@tauri_releases.route('/google-keep-desktop/')
def google_keep_desktop_page():
    # TODO: Download Links Page
    return '', 404


@tauri_releases.route('/google-keep-desktop/<target>/<current_version>')
def google_keep_desktop_api(target, current_version):
    latest_release = google_keep_release()
    if not latest_release:
        return '', 204
    latest_version = latest_release['version']
    try:
        # VERSION CHECK
        latest_maj, latest_min, latest_patch = latest_version.lstrip('v').split('.')
        cur_maj, cur_min, cur_patch = current_version.lstrip('v').split('.')
        if not (latest_maj > cur_maj or latest_min > cur_min or latest_patch > cur_patch):
            raise ValueError
    except ValueError:
        return '', 204
    return Response(json.dumps(latest_release), mimetype='application/json', headers={'Content-disposition': f'attachment; filename=google_keep_desktop_release_{latest_version}.json'})
