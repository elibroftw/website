# This file can be copoied/modified without any attribution or license inclusion
# It is licensed under CC0 1.0 https://creativecommons.org/publicdomain/zero/1.0/
# See helpers.py for time_cache implementation which is from stackoverflow

from flask import Blueprint, Response, render_template
import json
import os
from helpers import time_cache
import requests

tauri_releases = Blueprint('tauri_releases', __name__, url_prefix='/tauri-releases', template_folder='blueprints/tauri_releases/templates')

GOOGLE_KEEP_DESKTOP_GITHUB = 'https://api.github.com/repos/elibroftw/google-keep-desktop-app/releases/latest'


@time_cache(60 * 5)  # every 5 minutes
def get_latest_release(github_latest_release_url) -> dict:
    """
        Return format:
        Note darwin-aarch64 is silicon macOS. Supposed to seperate file but assumed that x64 would work due to Rosetta Stone 2
        {
          "version": "v1.0.8",  (can be any string)
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
        release = requests.get(github_latest_release_url).json()
        release_response = {
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
                        release_response['platforms'][platform] = {**release_response['platforms'].get(platform, {}), 'url': asset['browser_download_url']}
                elif asset['name'].endswith(f'{extension}.sig'):
                    for platform in for_platforms:
                        try:
                            sig = requests.get(asset['browser_download_url']).text
                        except requests.RequestException:
                            sig = ''
                        release_response['platforms'][platform] = {**release_response['platforms'].get(platform, {}), 'signature': sig}
        return release_response
    except requests.RequestException:
        return {}


@tauri_releases.route('/google-keep-desktop/<platform>/<current_version>')
def google_keep_desktop_api(platform, current_version):
    latest_release = get_latest_release(GOOGLE_KEEP_DESKTOP_GITHUB)
    if not latest_release:
        # GH API request failed in get_latest_release for GKD
        # TODO: Push Discord or Element notification (max once) if request failed
        return '', 204
    try:
        # version checks
        latest_version = latest_release['version']
        latest_maj, latest_min, latest_patch = latest_version.lstrip('v').split('.')
        cur_maj, cur_min, cur_patch = current_version.lstrip('v').split('.')
        # if running in dev, don't need to downgrade tauri app to test auto-update
        if not os.getenv('DEV', False) and not (latest_maj > cur_maj or latest_min > cur_min or latest_patch > cur_patch):
            raise ValueError
        # NOTE: here you may want to check the current_version or platform (see README.md)
    except ValueError:
        return '', 204
    return Response(json.dumps(latest_release), mimetype='application/json', headers={'Content-disposition': f'attachment; filename=google_keep_desktop_release_{latest_version}.json'})


@tauri_releases.route('/google-keep-desktop/')
def google_keep_desktop_page():
    # TODO: Download Links Page
    return '', 404
