import os
import json
import subprocess
import requests

def download_bilibili_video(stream_url: str, output_path: str) -> bool:
    """
    Downloads Bilibili video stream.
    Requires Referer: https://www.bilibili.com to avoid 403 Forbidden.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0",
        "Referer": "https://www.bilibili.com"
    }
    try:
        with requests.get(stream_url, headers=headers, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(f"[!] Error downloading video: {e}")
        return False

def convert_to_vertical_9_16(input_path: str, output_path: str, watermark_text: str = None) -> bool:
    """
    Uses FFmpeg to convert a landscape/horizontal video to Instagram 9:16 vertical (1080x1920)
    with smooth background blur and optional creator credit watermark.
    """
    # Filter: Scale blurred background to 1080x1920, overlay centered sharp original video
    vf_filter = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    if watermark_text:
        # Safe escape for ffmpeg drawtext
        escaped_watermark = watermark_text.replace(":", "\\:").replace("'", "")
        vf_filter += f",drawtext=text='{escaped_watermark}':fontcolor=white:fontsize=32:box=1:boxcolor=black@0.5:boxborderw=8:x=(w-text_w)/2:y=120"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]

    try:
        print(f"[FFmpeg] Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] FFmpeg processing failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print("[!] FFmpeg is not installed on this system.")
        return False
