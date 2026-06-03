# This file can be copied/modified without any attribution or license inclusion
# It is licensed under CC0 1.0 https://creativecommons.org/publicdomain/zero/1.0/

import logging

import requests
from flask import Blueprint

from modules.helpers import background_refresh

logger = logging.getLogger(__name__)

bp = Blueprint('tauri_releases', __name__, url_prefix='/tauri-releases', template_folder='blueprints/tauri_releases/templates')

GOOGLE_KEEP_DESKTOP_REPO = 'elibroftw/google-keep-desktop-app'
MUSIC_CASTER_REPO = 'elibroftw/music-caster'
REPOS = (GOOGLE_KEEP_DESKTOP_REPO, MUSIC_CASTER_REPO)

PLATFORMS = [ # platform, extension
    (('linux-x86_64', 'linux-aarch64'), 'amd64.AppImage.tar.gz'),
    (('darwin-x86_64', 'darwin-aarch64'), 'app.tar.gz'),
    (('windows-x86_64', 'windows-aarch64'), 'x64_en-US.msi.zip'),
    (('windows-aarch64'), 'arm64_en-US.msi.zip'),
]

REFRESH_INTERVAL = 60 * 5  # 5 minutes


def _fetch_latest_gh_release(repo) -> dict:
    logger.info('running _fetch_latest_gh_release')
    """
        repo: username/project-name
        Return format:
        Note darwin-aarch64 is silicon macOS. Supposed to separate file but assumed that x64 would work due to Rosetta Stone 2
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
        logger.exception('Failed to fetch latest GitHub release for %s', repo)
        return {}
    try:
        release_response = {
            'version': release['tag_name'],
            'notes': release['body'].removesuffix('See the assets to download this version and install.').rstrip('\r\n '),
            'pub_date': release['published_at'],
            'platforms': {}}
    except (KeyError, TypeError):
        # Malformed payload (e.g. GitHub rate limit / error returns a {"message": ...} dict).
        logger.warning('Unexpected GitHub release payload for %s: %r', repo, release)
        return {}
    for asset in release.get('assets', []):
        for for_platforms, extension in PLATFORMS:
            if asset['name'].endswith(extension):
                for platform in for_platforms:
                    release_response['platforms'][platform] = {**release_response['platforms'].get(platform, {}), 'url': asset['browser_download_url']}
            elif asset['name'].endswith(f'{extension}.sig'):
                try:
                    sig = requests.get(asset['browser_download_url']).text
                except requests.RequestException:
                    logger.exception('Failed to fetch signature for %s asset %s', repo, asset['name'])
                    sig = ''
                for platform in for_platforms:
                    release_response['platforms'][platform] = {**release_response['platforms'].get(platform, {}), 'signature': sig}
    return release_response


# TODO: REDIS CACHE to persist between app runs
@background_refresh(REFRESH_INTERVAL, default=dict)
def get_latest_gh_release(repo) -> dict:
    """Latest GitHub release for `repo`, refreshed in a background thread per repo.

    Non-blocking: returns the last good fetch, or an empty dict until the first
    fetch for `repo` succeeds (e.g. on a cold start). See `_fetch_latest_gh_release`
    for the payload shape.
    """
    return _fetch_latest_gh_release(repo)


def start_gh_release_checkers():
    for repo in REPOS:
        get_latest_gh_release(repo)


def latest_release_for_updater(repo, platform, current_version):
    """Shared Tauri updater response: return the latest release for `repo`, or 204 if up-to-date/unavailable.

    A 204 tells the Tauri updater there is nothing to install.
    """
    latest_release = get_latest_gh_release(repo)
    if not latest_release:
        # Cache is empty: the background fetch for `repo` has not yet succeeded (cold start or
        # repeated GitHub failures, which _fetch_latest_gh_release logs).
        # TODO: Push Discord or Element notification (max once) if request failed
        logger.warning('No cached release for %s; serving 204 to updater', repo)
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


@bp.route('/google-keep-desktop/<platform>/<current_version>')
def google_keep_desktop_api(platform, current_version):
    return latest_release_for_updater(GOOGLE_KEEP_DESKTOP_REPO, platform, current_version)


@bp.route('/music-caster/<platform>/<current_version>')
def music_caster_api(platform, current_version):
    return latest_release_for_updater(MUSIC_CASTER_REPO, platform, current_version)


@bp.route('/google-keep-desktop/')
def google_keep_desktop_page():
    # TODO: Download Links Page
    return '', 404


@bp.route('/healthz/')
def healthz():
    return { repo: get_latest_gh_release(repo) for repo in REPOS }
