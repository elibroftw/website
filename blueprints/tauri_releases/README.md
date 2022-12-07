# Tauri Updater REST API for GitHub Releases

[Rust Rocket.rs sample code](../../rocket-rs-sample/src/)

The contents of this directory is licensed under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) meaning the code and this README
can be freely copied/modified without attribution or license inclusion.

To test if auto-update works, you can add a localhost url like "http://[::1]:5001/tauri-releases/google-keep-desktop/{{target}}/{{current_version}}" to the start of the endpoints array. Your app version MUST be lower than the latest available version. The 204 return code is only a short-circuit, as there is also a version comparison done.

`__init__.py` provides Python code that can convert a Tauri GitHub release with assets from the artifiacts of Tauri GitHub action into
an updater compatible server-side response format. There is also code for checking whether or not to return this response.

The get_latest_release function can be called for many different apps, and for each app the function response is cached for 5 minutes.

The get_latest_release function and the REST API function are simple enough to be edited for your app and even translated for
different backend languages. I'm intersted in rocket.rs, lithium (C++), and Vlang, so when I make videos on them, I'll convert this code to work with rocket.rs, lithium, and Vlang.

## Intermediate Versions

If you need to check what the current version or target is, this guide may be helpful.

For example, if you made major changes which requires users to update to an intermediate version before updating to the latest, add the check here before tagging the breaking release.
If that is indeed the case, you may want to disable the dialog update so that the app is guaranteed to run the patch mechanism before updating to the latest version.
You may want to follow an update pattern of:
 e.g. 4.1.0 (installed) -> 4.9.9 (latest v4) -> 5.9.9 (latest v5) -> v6.2.0 (latest v6)

This update pattern guarantees that if the user doesn't or can't update to v5, they can still use the latest v4

- v5 takes care of migration for any v4 features for users who did update
- v6 can remove additional migration code in v5 without worries
- The app or downloads page would need to inform the user to not skip major versions
- The app should be able to tell if the user skipped at least one major version and avoid tinkering/migrating
