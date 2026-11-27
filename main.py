import os
import json
import time
from datetime import datetime
from bilibili_service import fetch_latest_videos, get_video_stream_url
from ai_caption import generate_hinglish_caption
from video_processor import download_bilibili_video, convert_to_vertical_9_16
from instagram_service import InstagramPublisher
from github_storage import upload_to_github_release

CREATORS_FILE = "creators.json"
POSTED_HISTORY_FILE = "posted_history.json"
OUTPUT_DIR = "processed_media"

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] --- China Gaming Auto Publisher Started ---")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    creators = load_json(CREATORS_FILE, [])
    posted_history = set(load_json(POSTED_HISTORY_FILE, []))
    ig_publisher = InstagramPublisher()

    new_posts_count = 0

    for creator in creators:
        if not creator.get("enabled", True):
            continue

        name = creator.get("name")
        uid = creator.get("uid")
        platform = creator.get("platform", "bilibili")

        if platform != "bilibili":
            continue

        print(f"\n[+] Checking creator: {name} (UID: {uid}) on Bilibili...")
        videos = fetch_latest_videos(uid, page_size=3)

        if not videos:
            print(f"[-] No videos found or API returned empty for {name}")
            continue

        for video in videos:
            bvid = video["bvid"]
            title = video["title"]

            if bvid in posted_history:
                print(f"  [-] Already processed video: {bvid} - {title[:30]}")
                continue

            print(f"\n  [★] NEW VIDEO DETECTED!")
            print(f"      ID: {bvid}")
            print(f"      Title: {title}")
            print(f"      URL: {video['url']}")

            # Step 1: AI Hinglish Caption Generation
            print("  [1/4] Generating viral Hinglish caption with AI...")
            caption = generate_hinglish_caption(title, f"{name} ({creator.get('chinese_name', '')})")
            print("      Generated Caption:")
            print("      " + caption.replace('\n', '\n      '))

            # Step 2: Fetch stream URL & Download
            print("  [2/4] Fetching video stream...")
            stream_info = get_video_stream_url(bvid)
            if not stream_info:
                print("  [!] Failed to get stream URL. Skipping for now.")
                continue

            raw_video_path = os.path.join(OUTPUT_DIR, f"raw_{bvid}.mp4")
            vertical_video_path = os.path.join(OUTPUT_DIR, f"vertical_{bvid}.mp4")

            print(f"  [3/4] Downloading original video ({round(stream_info['size'] / (1024*1024), 2)} MB)...")
            if not download_bilibili_video(stream_info["download_url"], raw_video_path):
                continue

            # Step 3: FFmpeg Conversion to 9:16 Vertical Reel
            print("  [4/4] Converting to 9:16 vertical Reel with background blur...")
            watermark = f"Creator: {name} | Bilibili"
            convert_success = convert_to_vertical_9_16(raw_video_path, vertical_video_path, watermark_text=watermark)

            if not convert_success:
                print("  [!] FFmpeg conversion failed or FFmpeg missing. Keeping original.")
                final_video_path = raw_video_path
            else:
                final_video_path = vertical_video_path

            # Step 4: Publish to Instagram
            if ig_publisher.is_configured():
                # Get public download URL using GitHub Releases
                public_video_url = upload_to_github_release(final_video_path)
                
                if public_video_url:
                    try:
                        print(f"  [IG] Publishing to Instagram via Meta Graph API...")
                        post_id = ig_publisher.post(public_video_url, caption)
                        print(f"  [✓] Successfully published to Instagram! Post ID: {post_id}")
                    except Exception as e:
                        print(f"  [!] Instagram publishing failed: {e}")
                else:
                    print("  [!] Could not generate public URL. Skipping Instagram upload.")
            else:
                print("  [i] Instagram credentials not configured. Video saved locally in processed_media/.")

            # Record in posted history to avoid duplicate processing
            posted_history.add(bvid)
            save_json(POSTED_HISTORY_FILE, list(posted_history))
            new_posts_count += 1
            break  # Process only 1 new video per creator per workflow run

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Finished run. Total new videos processed: {new_posts_count}")

if __name__ == "__main__":
    main()
