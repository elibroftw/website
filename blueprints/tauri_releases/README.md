# Tauri Updater REST API for GitHub Releases

The contents of this directory is licensed under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

The code provided converts a GitHub release with assets added by our GitHub build action into a Tauri updater-compatible JSON response.
This avoids painstakingly updating the update server yourself whenever you release your apps.
If you are using private repositories, you will most likely need an API key for GitHub otherwise you will get 403ed.

## Languages

- `rocket-rs-sample/src/` for Rust Rocket code
- `__init__.py` for Python Flask code
- The code provided is not that simple but I was able to port it to Rust over 2 days so maybe like a week for everyone else. My experience porting the Python Flask code to Rust was painful and I learned enough to stick with Rust. Since I'm going to stick with rocket.rs, I most likely won't be able to port the code into C++ Lithium and V.

## Testing

To test if auto-update works, in your `tauri.conf.json` file, add a localhost url like "http://[::1]:5001/tauri-releases/google-keep-desktop/{{target}}/{{current_version}}" to the start of the endpoints array.

Your app version MUST be lower than the latest available version.
The 204 return is only a short-circuit because the Tauri updater will perform a version check nonetheless.

## Caching

The response for the latest Tauri github release has a cached time to live (TTL) of 5 minutes. This means that there is a 5 minute delay whenever a release is published. There is no worries however as Tauri performs a version check so even if you return an older version, Tauri is smart enough to know that a newer version would have a higher version number.

## Intermediate Versions

If you need to check what the current version or target is, this guide may be helpful.

For example, if you made major changes which requires users to update to an intermediate version before updating to the latest,
add a check in the code after the latest version check before publishing a breaking release.

If that is indeed the case, you may want to disable the dialog update so that the app is guaranteed to run the patch mechanism before updating to the latest version.

You may want to follow an update pattern of:
 e.g. 4.1.0 (installed) -> 4.9.9 (latest v4) -> 5.9.9 (latest v5) -> v6.2.0 (latest v6)

This update pattern guarantees that if the user doesn't or can't update to v5, they can still use the latest v4

- v5 takes care of migration for any v4 features for users who did update
- v6 can remove additional migration code in v5 without worries
- The app or downloads page would need to inform the user to not skip major versions
- The app should be able to tell if the user skipped at least one major version and avoid tinkering/migrating
