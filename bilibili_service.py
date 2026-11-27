import os
import json
import time
import hashlib
import requests
from functools import reduce

# Permutation table for Bilibili WBI key generation
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62,
    11, 36, 20, 34, 44, 52
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com"
}

def get_mixin_key(orig: str) -> str:
    """Derives the 32-character mixin key from img/sub hash strings."""
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, "")[:32]

def get_wbi_keys() -> tuple:
    """Fetches dynamic WBI keys from Bilibili nav API."""
    try:
        resp = requests.get("https://api.bilibili.com/x/web-interface/nav", headers=HEADERS, timeout=10)
        res_json = resp.json()
        wbi_img = res_json.get("data", {}).get("wbi_img", {})
        img_url = wbi_img.get("img_url", "")
        sub_url = wbi_img.get("sub_url", "")
        img_key = img_url.split("/")[-1].split(".")[0]
        sub_key = sub_url.split("/")[-1].split(".")[0]
        return img_key, sub_key
    except Exception as e:
        print(f"[!] Warning: Could not fetch WBI keys ({e}), falling back to direct query")
        return None, None

def sign_wbi_params(params: dict, img_key: str, sub_key: str) -> dict:
    """Signs parameters dict using WBI algorithm."""
    if not img_key or not sub_key:
        return params
    
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = int(time.time())
    params["wts"] = curr_time

    # Sort parameters alphabetically
    sorted_params = sorted(params.items())
    query = "&".join([f"{k}={v}" for k, v in sorted_params])
    w_rid = hashlib.md5((query + mixin_key).encode("utf-8")).hexdigest()
    params["w_rid"] = w_rid
    return params

def fetch_latest_videos(mid: str, page_size: int = 5) -> list:
    """
    Fetches latest videos for a Bilibili creator (MID) using official WBI-signed API.
    Returns list of dicts: [{'bvid': ..., 'title': ..., 'pic': ..., 'length': ..., 'created': ...}]
    """
    img_key, sub_key = get_wbi_keys()
    params = {
        "mid": str(mid),
        "ps": page_size,
        "pn": 1,
        "order": "pubdate"
    }
    
    signed_params = sign_wbi_params(params, img_key, sub_key)
    req_headers = HEADERS.copy()
    req_headers["Referer"] = f"https://space.bilibili.com/{mid}/video"

    try:
        url = "https://api.bilibili.com/x/space/wbi/arc/search"
        resp = requests.get(url, params=signed_params, headers=req_headers, timeout=15)
        data = resp.json()
        
        if data.get("code") != 0:
            print(f"[-] Bilibili API returned code {data.get('code')}: {data.get('message')}")
            return []

        vlist = data.get("data", {}).get("list", {}).get("vlist", [])
        videos = []
        for v in vlist:
            videos.append({
                "bvid": v.get("bvid"),
                "title": v.get("title"),
                "description": v.get("description"),
                "pic": v.get("pic"),
                "length": v.get("length"),
                "created": v.get("created"),
                "url": f"https://www.bilibili.com/video/{v.get('bvid')}"
            })
        return videos
    except Exception as e:
        print(f"[!] Error fetching videos for MID {mid}: {e}")
        return []

def get_video_stream_url(bvid: str) -> dict:
    """
    Fetches the downloadable stream URL for a given BVID video.
    Bilibili requires Referer header when accessing CDN URLs.
    """
    try:
        # 1. Fetch CID (chunk ID) for the video
        view_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        view_res = requests.get(view_url, headers=HEADERS, timeout=10).json()
        if view_res.get("code") != 0:
            return None
        
        cid = view_res["data"]["cid"]

        # 2. Fetch playurl stream
        play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=64&fnval=1"
        play_res = requests.get(play_url, headers=HEADERS, timeout=10).json()
        
        if play_res.get("code") == 0 and "durl" in play_res.get("data", {}):
            durl = play_res["data"]["durl"][0]
            return {
                "download_url": durl.get("url"),
                "backup_url": durl.get("backup_url", []),
                "size": durl.get("size")
            }
        return None
    except Exception as e:
        print(f"[!] Error fetching video stream for {bvid}: {e}")
        return None
