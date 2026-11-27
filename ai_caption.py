import os
import requests

def generate_english_caption(video_title: str, creator_name: str) -> str:
    """
    Generates high-engagement viral English gaming caption + 10 trending hashtags using Gemini API.
    Falls back to a well-crafted English gaming template if GEMINI_API_KEY is not set or fails.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    prompt = f"""
Act as a viral global gaming content creator and social media strategist.
Create an engaging, viral Instagram Reels caption in clean, energetic English for a gaming clip.

Video Details:
- Original Title: {video_title}
- Original Creator: {creator_name}

Requirements:
1. High-energy hook line in English (e.g. "Wait for this insane clutch! 😱🔥", "Have you ever seen a play like this?!")
2. Brief engaging context (1-2 short sentences highlighting pro reflexes or gameplay)
3. Call to Action: "Tag your duo & follow for daily pro gaming highlights!"
4. Mandatory Creator Credit line: "Original Content Credit: {creator_name} (Bilibili)"
5. 10 trending global gaming hashtags: e.g. #gaming #reels #gamingcommunity #gamer #esports #proplayer #gaminghighlights #epicclips #gameplay #pcgaming

Return ONLY the final ready-to-post caption text without any introductory explanation.
"""

    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ]
            }
            res = requests.post(url, json=payload, timeout=20)
            data = res.json()
            caption = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return caption
        except Exception as e:
            print(f"[!] Gemini AI generation failed ({e}), using default English template")

    # High-converting fallback template in English
    fallback_caption = f"""Wait for this insane play by {creator_name}! 😱🔥

Have you ever seen reflexes and timing like this? Rate this play 1-10 in the comments! 👇

Original Content Credit: {creator_name} (Bilibili)
Follow for daily insane gaming clips and highlights! 🚀

#gaming #gamingreels #gamingcommunity #esports #proplayer #epicmoments #gamerlife #bilibiligaming #viralgaming #gamingclips"""
    
    return fallback_caption
