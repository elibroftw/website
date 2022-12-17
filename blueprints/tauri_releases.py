# This file can be copoied/modified without any attribution or license inclusion
# It is licensed under CC0 1.0 https://creativecommons.org/publicdomain/zero/1.0/
# See helpers.py for time_cache implementation which is from stackoverflow

from flask import Blueprint, Response, render_template
from helpers import time_cache
import requests

tauri_releases_bp = Blueprint('tauri_releases', __name__, url_prefix='/tauri-releases', template_folder='blueprints/tauri_releases/templates')

GOOGLE_KEEP_DESKTOP_REPO = 'elibroftw/google-keep-desktop-app'

PLATFORMS = [ # platform, extension
    (('linux-x86_64',), 'amd64.AppImage.tar.gz'),
    (('darwin-x86_64', 'darwin-aarch64'), 'app.tar.gz'),
    (('windows-x86_64',), 'x64_en-US.msi.zip'),
]

@time_cache(60 * 5)  # every 5 minutes
def get_latest_gh_release(repo) -> dict:
    """
        repo: username/project-name
        Return format:
        Note darwin-aarch64 is silicon macOS. Supposed to seperate file but assumed that x64 would work due to Rosetta Stone 2
        {
          "version": "v1.0.8",  (can be any string)
          "notes": "- Test updater",
          "pub_date": "2022-11-13T03:20:32Z",
          "platforms": {
            "linux-x86_64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/google-keep_1.0.8_amd64.AppImage.tar.gz",
              "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWHVmYzVwc2RzZXBkcTdDWmNQNmNiVjBLWUcyUkhMSnlPV3ZqVVhWN3MvaU9QQlFXSVZMQjdScDljM3FZaXhXZnhKejIrWG84bE5KbEFsSDErdjF2aGdNPQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NTU0CWZpbGU6Z29vZ2xlLWtlZXBfMS4wLjhfYW1kNjQuQXBwSW1hZ2UudGFyLmd6CmlpVG9kSzBVNU9BMXRIL3l2MlZ6dnJDNndHeUQrK1NIaDdmbkU1MUNVZFk2eHlneEVCZ255SnI4U3FMR0lSOUFNNHFzUHdJbEZmS2JtZUlpSllWWUNBPT0K"
            },
            "darwin-x86_64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/Google.Keep.app.tar.gz",
              "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWG1qc2paOHJDUnBCVHRuMlRZdFdZeXJURGM2Yk9meVRtSmZlWHBEa0dCcEd0eDd3YVkvZlRxakt1ZTNmbHV6anpQam1SakdSaXc2Y1NEZmFaVXoxaWdrPQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NTE4CWZpbGU6R29vZ2xlIEtlZXAuYXBwLnRhci5negp2S1dwYmszQTRkMXFzb2lneFJPbytmenpLS0g4RXEydVY0MmtUb0VTQXg2ZWpYWXF2QndnTXdUVjZNU29uMW5zZElPMFNkeGxBU1VtUmZCSkkzUHZEZz09Cg=="
            },
            "darwin-aarch64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/Google.Keep.app.tar.gz",
              "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWG1qc2paOHJDUnBCVHRuMlRZdFdZeXJURGM2Yk9meVRtSmZlWHBEa0dCcEd0eDd3YVkvZlRxakt1ZTNmbHV6anpQam1SakdSaXc2Y1NEZmFaVXoxaWdrPQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NTE4CWZpbGU6R29vZ2xlIEtlZXAuYXBwLnRhci5negp2S1dwYmszQTRkMXFzb2lneFJPbytmenpLS0g4RXEydVY0MmtUb0VTQXg2ZWpYWXF2QndnTXdUVjZNU29uMW5zZElPMFNkeGxBU1VtUmZCSkkzUHZEZz09Cg=="
            },
            "windows-x86_64": {
              "url": "https://github.com/elibroftw/google-keep-desktop-app/releases/download/v1.0.8/Google.Keep_1.0.8_x64_en-US.msi.zip",
              "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkKUlVRaDRIdWFLTHYrWG8zdHhmRFBTQndFV0lvWU02YU8vMGwrdUc4NjY4Vm9IbGpyWWU1Z1ZDUVg1L3Y4SUl2YVcxUXNJbW9kUEZkU3lscUhFZXU0MnhWTGMvOXJMY3RNdUE0PQp0cnVzdGVkIGNvbW1lbnQ6IHRpbWVzdGFtcDoxNjY4MzA5NDMyCWZpbGU6R29vZ2xlIEtlZXBfMS4wLjhfeDY0X2VuLVVTLm1zaS56aXAKR2NhK1dwRTJMZFhOZG12dWNTNnNXZHpFSFVoM2g1ZnNlVDJtK2lpMGk2M2pqSUlTRStSN09veVc1U0ZjNzM5blVjWU9oNTlONmFBUmFuYVpVVldBRHc9PQo="
            }
          }
        }
    """
    github_latest_release_url = f'https://api.github.com/repos/{repo}/releases/latest'
    try:
        release = requests.get(github_latest_release_url).json()
    except requests.RequestException:
        return {}
    release_response = {
        'version': release['tag_name'],
        'notes': release['body'].removesuffix('See the assets to download this version and install.').rstrip('\r\n '),
        'pub_date': release['published_at'],
        'platforms': {}}
    for asset in release.get('assets', []):
        for for_platforms, extension in PLATFORMS:
            if asset['name'].endswith(extension):
                for platform in for_platforms:
                    release_response['platforms'][platform] = {**release_response['platforms'].get(platform, {}), 'url': asset['browser_download_url']}
            elif asset['name'].endswith(f'{extension}.sig'):
                try:
                    sig = requests.get(asset['browser_download_url']).text
                except requests.RequestException:
                    sig = ''
                for platform in for_platforms:
                    release_response['platforms'][platform] = {**release_response['platforms'].get(platform, {}), 'signature': sig}
    return release_response


@tauri_releases_bp.route('/google-keep-desktop/<platform>/<current_version>')
def google_keep_desktop_api(platform, current_version):
    latest_release = get_latest_gh_release(GOOGLE_KEEP_DESKTOP_REPO)
    if not latest_release:
        # GH API request failed in get_latest_release for GKD
        # TODO: Push Discord or Element notification (max once) if request failed
        return '', 204
    try:
        # version checks
        latest_version = latest_release['version']
        latest_maj, latest_min, latest_patch = latest_version.lstrip('v').split('.')
        cur_maj, cur_min, cur_patch = current_version.lstrip('v').split('.')
        if cur_maj == latest_maj and cur_min == latest_min and cur_patch == latest_patch:
            raise ValueError
        # NOTE: here you may want to check the current_version or platform (see README.md)
    except ValueError:
        return '', 204
    return latest_release


@tauri_releases_bp.route('/google-keep-desktop/')
def google_keep_desktop_page():
    # TODO: Download Links Page
    return '', 404
