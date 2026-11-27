import os
import time
import requests

GRAPH_API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class InstagramPublisher:
    def __init__(self, account_id: str = None, access_token: str = None):
        self.account_id = account_id or os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.account_id and self.access_token and "your_" not in self.account_id)

    def create_reel_container(self, video_url: str, caption: str) -> str:
        """Step 1: Create media container for the Reel."""
        print("[IG] Step 1: Creating media container...")
        url = f"{BASE_URL}/{self.account_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token,
        }
        res = requests.post(url, data=payload, timeout=30).json()

        if "id" in res:
            container_id = res["id"]
            print(f"[IG] Container created successfully! Container ID: {container_id}")
            return container_id
        else:
            raise Exception(f"Failed to create Instagram container: {res}")

    def wait_for_processing(self, container_id: str, max_retries: int = 20) -> bool:
        """Step 2: Poll container status until Meta finishes processing the video."""
        print("[IG] Step 2: Waiting for Instagram to transcode container...")
        url = f"{BASE_URL}/{container_id}"
        params = {"fields": "status_code,status", "access_token": self.access_token}

        for attempt in range(max_retries):
            res = requests.get(url, params=params, timeout=15).json()
            status_code = res.get("status_code")
            print(f"[IG] Polling status ({attempt + 1}/{max_retries}): {status_code}")

            if status_code == "FINISHED":
                print("[IG] Video transcoding finished!")
                return True
            elif status_code in ["ERROR", "EXPIRED"]:
                raise Exception(f"Container failed with status: {status_code}")

            time.sleep(10)

        raise TimeoutError("Timed out waiting for Instagram to process the container.")

    def publish_reel(self, container_id: str) -> str:
        """Step 3: Publish the container to the Instagram account feed."""
        print("[IG] Step 3: Publishing Reel to feed...")
        url = f"{BASE_URL}/{self.account_id}/media_publish"
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token,
        }
        res = requests.post(url, data=payload, timeout=30).json()

        if "id" in res:
            post_id = res["id"]
            print(f"[IG] Reel published successfully! Live Post ID: {post_id}")
            return post_id
        else:
            raise Exception(f"Failed to publish Reel: {res}")

    def post(self, video_url: str, caption: str) -> str:
        """Complete 3-step publishing flow."""
        container_id = self.create_reel_container(video_url, caption)
        self.wait_for_processing(container_id)
        post_id = self.publish_reel(container_id)
        return post_id
