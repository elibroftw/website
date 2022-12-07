use lru_time_cache::LruCache;
use reqwest;
use reqwest::Client;
use rocket::http::uri::Origin;
use rocket::http::Status;
use rocket::response::Redirect;
use rocket::State;
use serde_json;
use serde_json::json;
use std::collections::HashMap;
use std::convert::Into;
use std::sync::{Arc, Mutex};
use std::time::Duration;

#[macro_use]
extern crate rocket;

type StringValueCache = LruCache<String, serde_json::Value>;
type GitHubReleaseCache = Arc<Mutex<StringValueCache>>;

// TTL: time to live
static RELEASE_TTL: u64 = 5 * 60;
const GOOGLE_KEEP_DESKTOP_REPO: &str = "elibroftw/google-keep-desktop-app";
const TAURI_UPDATER_PREFIX: Origin<'static> = uri!("/tauri-releases");

fn remove_suffix<'a>(s: &'a str, suffix: &str) -> &'a str {
    match s.strip_suffix(suffix) {
        Some(s) => s,
        None => s,
    }
}

#[derive(Debug)]
enum GitHubReleaseError {
    ReqwestError(reqwest::Error),
    JsonError(String),
}

impl From<reqwest::Error> for GitHubReleaseError {
    fn from(e: reqwest::Error) -> Self {
        GitHubReleaseError::ReqwestError(e)
    }
}

impl From<&str> for GitHubReleaseError {
    fn from(e: &str) -> Self {
        GitHubReleaseError::JsonError(String::from(e))
    }
}

async fn ttl_get_latest_release(
    cache: &State<GitHubReleaseCache>,
    client: &State<Client>,
    repo: &str,
) -> serde_json::Value {
    if let Some(release) = cache.lock().unwrap().get(repo) {
        return release.clone();
    }
    let release = get_latest_release(client, repo)
        .await
        .or_else(|error| {
            // TODO: notify someone via Element/Discord/Slack (webhook or bot)
            println!("{error:?}");
            Ok::<serde_json::Value, GitHubReleaseError>(json!({}))
        })
        .unwrap();
    // avoid rate limiting so cache empty json
    cache
        .lock()
        .unwrap()
        .insert(repo.to_string(), release.clone());
    release
}

async fn text_request(client: &State<Client>, url: &str) -> Result<String, reqwest::Error> {
    client.get(url).send().await?.text().await
}

async fn get_latest_release(
    client: &State<Client>,
    repo: &str,
) -> Result<serde_json::Value, GitHubReleaseError> {
    // repo is of the form 'user/project'
    // https://docs.rs/serde_json/latest/serde_json/value/enum.Value.html#

    // fetch and parse
    let url = format!("https://api.github.com/repos/{repo}/releases/latest");
    // hack since try and catch doesn't exist
    let response = client.get(&url).send().await?;
    let github_release = response.json::<serde_json::Value>().await?;
    let mut release = json!({
        "version": github_release["tag_name"].as_str().ok_or("tag_name not found")?,
        "notes": remove_suffix(&github_release["body"].as_str().ok_or("body not found")?, "See the assets to download this version and install.").trim_end_matches(['\r', '\n', ' ']),
        "pub_date": github_release["published_at"].as_str().ok_or("pub_date not found")?,
        "platforms": {}
    });

    // extension : platforms
    let platforms: HashMap<&str, Vec<&str>> = HashMap::from([
        ("amd64.AppImage.tar.gz", vec!["linux-x86_64"]),
        ("app.tar.gz", vec!["darwin-x86_64", "darwin-aarch64"]),
        ("x64_en-US.msi.zip", vec!["windows-x86_64"]),
    ]);
    println!("pass 2");
    let release_platforms = release["platforms"].as_object_mut().unwrap();
    for asset in github_release["assets"]
        .as_array()
        .ok_or("assets not found")?
        .iter()
    {
        let asset = asset.as_object().ok_or("asset not found")?;
        for (extension, for_platforms) in platforms.iter() {
            let asset_name = asset["name"].as_str().ok_or("no asset name")?;
            if asset_name.ends_with(extension) {
                for platform in for_platforms.iter() {
                    if !release_platforms.contains_key(*platform) {
                        release_platforms.insert(platform.to_string(), json!({}));
                    }
                    release_platforms[*platform]
                        .as_object_mut()
                        .unwrap()
                        .insert("url".to_string(), asset["browser_download_url"].clone());
                }
            } else if asset_name.ends_with(&format!("{extension}.sig")) {
                let signature = match text_request(
                    client,
                    asset["browser_download_url"]
                        .as_str()
                        .ok_or("DL not found")?,
                )
                .await
                {
                    Ok(s) => s,
                    _ => String::new(),
                };
                for platform in for_platforms.iter() {
                    if !release_platforms.contains_key(*platform) {
                        release_platforms.insert(platform.to_string(), json!({}));
                    }
                    release_platforms[*platform]
                        .as_object_mut()
                        .unwrap()
                        .insert(
                            "signature".to_string(),
                            serde_json::Value::String(signature.clone()),
                        );
                }
            }
        }
    }
    Ok(release)
}

#[get("/google-keep-desktop")]
fn google_keep_desktop_page() -> Status {
    // TODO: test rocket templates
    Status::NotFound
}

#[get("/google-keep-desktop/<_platform>/<current_version>")]
async fn google_keep_desktop_api(
    _platform: String,
    current_version: String,
    cache: &State<GitHubReleaseCache>,
    client: &State<Client>,
) -> Result<serde_json::Value, Status> {
    let latest_release = ttl_get_latest_release(cache, client, GOOGLE_KEEP_DESKTOP_REPO).await;

    // input checks
    let response = move || -> Option<_> {
        let semvers: Vec<&str> = current_version.split('.').collect();
        let cur_maj = semvers.get(0)?;
        let cur_min = semvers.get(1)?;
        let cur_patch = semvers.get(2)?;
        let mut latest_version = latest_release["version"].as_str()?;
        latest_version = latest_version.trim_start_matches('v');
        let semvers: Vec<&str> = latest_version.split('.').collect();
        let latest_maj = semvers.get(0)?;
        let latest_min = semvers.get(1)?;
        let latest_patch = semvers.get(2)?;
        if cur_maj == latest_maj && cur_min == latest_min && cur_patch == latest_patch {
            return None;
        }
        // NOTE: can do platform and additional version checks here
        return Some(latest_release);
    }();
    response.ok_or(Status::NoContent)
}

#[get("/")]
fn index() -> Redirect {
    // this is only to demo the API
    Redirect::to(uri!(
        TAURI_UPDATER_PREFIX,
        google_keep_desktop_api("win64", "1.18.0")
    ))
}

#[launch]
fn rocket() -> _ {
    let github_release_cache = Arc::new(Mutex::new(StringValueCache::with_expiry_duration(
        Duration::from_secs(RELEASE_TTL),
    )));
    rocket::build()
        .manage(github_release_cache)
        .manage(
            reqwest::Client::builder()
                .user_agent("reqwest")
                .build()
                .unwrap(),
        )
        .mount("/", routes![index])
        .mount(TAURI_UPDATER_PREFIX, routes![google_keep_desktop_api, google_keep_desktop_page])
}
