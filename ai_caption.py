import os
import requests

def generate_hinglish_caption(video_title: str, creator_name: str) -> str:
    """
    Generates high-engagement Hinglish gaming caption + 10 trending hashtags using Gemini API.
    Falls back to a well-crafted template if GEMINI_API_KEY is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    prompt = f"""
Act as a viral Indian gaming content creator and social media manager.
Create an engaging, viral Instagram Reels caption in natural Hinglish for a gaming video.

Video Details:
- Original Title: {video_title}
- Original Creator: {creator_name}

Requirements:
1. Hook line in Hinglish (e.g. "Bhai ye move dekho! 😱🔥", "Aisa gameplay pehle kabhi nahi dekha!")
2. Brief engaging context (1-2 short sentences)
3. Call to Action: "Share with your gaming squad & follow for daily pro gaming clips!"
4. Mandatory Creator Credit line: "Original Content Credit: {creator_name} (Bilibili)"
5. 10 trending gaming hashtags: e.g. #gaming #reels #gamingmoments #hindi #hinglishgaming #proplayer #epicmoments

Return ONLY the final ready-to-post caption text.
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
            print(f"[!] Gemini AI generation failed ({e}), using default template")

    # Smart fallback template if API is absent or fails
    fallback_caption = f"""Bhai! {creator_name} ka ye gaming moment dekho! 😱🔥

Aisa reflex aur clutch gameplay pehle kabhi dekha hai kya? Tag your squad! 👇

Original Creator Credit: {creator_name} (Bilibili)
Follow for more insane gaming moments! 🚀

#gaming #gamingreels #gamingcommunity #hinglishgaming #reelsindia #esports #epicmoments #gamerlife #bilibiligaming #viralgaming"""
    
    return fallback_caption
