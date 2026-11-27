# China Gaming Auto Publisher (Bilibili -> Instagram Reels)

A serverless automated pipeline running on **GitHub Actions** that monitors verified Chinese gaming creators on **Bilibili**, converts their clips into 9:16 vertical Instagram Reels with background blur, generates viral English AI captions using **Gemini**, and publishes them to **Instagram**.

---

## 📁 Project Structure

```text
├── .github/
│   └── workflows/
│       └── publisher.yml      # GitHub Actions automation runner (runs every 3 hours)
├── bilibili_service.py        # Official WBI-signed Bilibili API client
├── ai_caption.py              # Gemini AI English caption & hashtag generator
├── video_processor.py         # FFmpeg vertical 9:16 converter with background blur & credits
├── github_storage.py          # Zero-config public video hosting using GitHub Releases
├── instagram_service.py       # Official Meta Instagram Graph API Reels publisher
├── main.py                    # Master orchestrator script
├── creators.json              # List of monitored Bilibili gaming creators
├── posted_history.json        # Deduplication database (prevents reposts)
├── requirements.txt           # Python dependencies
└── .env.example               # Template for environment variables / secrets
```

---

## 🚀 Setup on GitHub

### 1. Push code to your GitHub Repository
```bash
git add .
git commit -m "chore: update config"
git push origin main
```

### 2. Configure GitHub Secrets
Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**:

| Secret Name | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your Google Gemini API Key for viral English captions |
| `INSTAGRAM_ACCOUNT_ID` | Your Instagram Professional/Business Account ID |
| `INSTAGRAM_ACCESS_TOKEN`| Long-lived Instagram Graph API Access Token |

*(No external storage or `PUBLIC_MEDIA_BASE_URL` needed — GitHub Releases handle the hosting automatically!)*

### 3. Automatic Execution
* The workflow will run **automatically every 3 hours** via GitHub Actions cron.
* You can also click **"Run workflow"** anytime in the **Actions** tab of your repository to trigger it manually.
* Once a video is posted, `posted_history.json` is automatically updated and committed back to the repository to prevent duplicate posts.
