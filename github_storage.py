import os
import requests

def upload_to_github_release(file_path: str, tag_name: str = "media-cache") -> str:
    """
    Uploads a local media file to a GitHub Release asset in the current repository,
    generating a 100% public, direct HTTPS download URL that Meta's Instagram
    Graph API servers can directly pull from.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")  # format: 'owner/repo' e.g. 'Tejasv7/auto-v-uploader'

    if not token or not repo:
        print("[!] GITHUB_TOKEN or GITHUB_REPOSITORY not set. Cannot upload to GitHub Release.")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # 1. Get or create release for tag_name
    release_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag_name}"
    resp = requests.get(release_url, headers=headers)

    if resp.status_code == 200:
        release_data = resp.json()
        upload_url_template = release_data.get("upload_url")
    else:
        # Create release if it doesn't exist
        print(f"[GH] Creating temporary media release '{tag_name}'...")
        create_url = f"https://api.github.com/repos/{repo}/releases"
        payload = {
            "tag_name": tag_name,
            "name": "Temporary Instagram Media Cache",
            "body": "Automated media storage for Meta Graph API container fetching.",
            "draft": False,
            "prerelease": False
        }
        create_resp = requests.post(create_url, headers=headers, json=payload)
        if create_resp.status_code not in [200, 201]:
            print(f"[!] Failed to create release: {create_resp.text}")
            return None
        release_data = create_resp.json()
        upload_url_template = release_data.get("upload_url")

    # upload_url comes formatted as: https://uploads.github.com/.../assets{?name,label}
    upload_url = upload_url_template.split("{")[0]

    filename = os.path.basename(file_path)

    # 2. Upload asset
    print(f"[GH] Uploading {filename} to GitHub Release for public URL generation...")
    upload_headers = headers.copy()
    upload_headers["Content-Type"] = "video/mp4"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    asset_resp = requests.post(
        f"{upload_url}?name={filename}",
        headers=upload_headers,
        data=file_bytes
    )

    if asset_resp.status_code in [200, 201]:
        asset_data = asset_resp.json()
        public_url = asset_data.get("browser_download_url")
        print(f"[GH] Public Media URL successfully created: {public_url}")
        return public_url
    elif asset_resp.status_code == 422:
        # Asset already exists, construct download URL directly
        public_url = f"https://github.com/{repo}/releases/download/{tag_name}/{filename}"
        print(f"[GH] Asset already exists. Public URL: {public_url}")
        return public_url
    else:
        print(f"[!] Error uploading asset to release: {asset_resp.text}")
        return None
