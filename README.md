# ThumbSwap Bot 🎬⚡

[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers%20Serverless-F38020?logo=cloudflare&logoColor=white)](https://workers.cloudflare.com/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![Max File Size](https://img.shields.io/badge/Max%20Video%20Size-Up%20to%204GB-brightgreen.svg)](#-zero-download-server-side-pointer-swap-architecture)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, ultra-fast Telegram Video Cover/Thumbnail Changer Bot built on a **Zero-Download Server-Side Pointer Swap Architecture**. Replaces video thumbnails in **1 to 5 seconds** for streaming videos up to **4GB** without downloading, re-encoding, or re-uploading a single byte.

Available in both **Dual Deployment Architectures**:
1. 🌐 **100% Serverless Cloud:** Deploy on **Cloudflare Workers** with **Cloudflare KV** (Free 24/7, 0ms cold starts, no VPS required).
2. 🖥️ **VPS / Container:** Run on any Linux VPS with background supervisor, Docker Compose, or Systemd.

---

## ⚡ Zero-Download Server-Side Pointer Swap Architecture

### Why Traditional Bots Fail
Traditional Telegram thumbnail changer bots download the incoming video to disk, invoke `ffmpeg` to re-encode or attach the thumbnail, and then re-upload the binary file. This legacy method has critical limitations:
1. **Fails on files > 20MB/50MB:** Telegram Bot API download limits strictly prevent local downloading of large videos.
2. **Heavy Resource Consumption:** Demands gigabytes of VPS RAM, massive CPU spikes, high disk I/O, and consumes server bandwidth.
3. **Severe Quality & Metadata Loss:** Transcoding alters original codecs, degrades bitrate, breaks streaming metadata, and strips audio channels.
4. **Extreme Latency:** Downloading and uploading 1GB to 4GB files takes several minutes to hours.

### The Modern Solution (Method 5)
ThumbSwap Bot leverages Telegram's modern `cover` parameter in the `sendVideo` Bot API endpoint:
- **Streaming Video Metadata Delivery:** When a user sends any streaming video (up to 4GB), Telegram's update delivers its native `video.file_id`.
- **In-Memory Thumbnail Registration:** When a user sends a photo, its highest-resolution `photo.file_id` is cached instantly in Cloudflare KV or RAM.
- **Server-Side Pointer Binding:** When the user sends a streaming video, the bot sends an asynchronous JSON HTTP payload back to Telegram DC:
  ```json
  {
    "chat_id": 123456789,
    "video": "<EXISTING_VIDEO_FILE_ID>",
    "cover": "<EXISTING_PHOTO_FILE_ID>",
    "supports_streaming": true
  }
  ```
- **100% Quality & Stream Metadata Preservation:** Telegram's Data Centers link the new cover pointer directly to the existing video asset. Zero bytes are downloaded to or uploaded from the server. The round-trip completes in **0.5 to 2 seconds**.

```
  +---------+                 +-------------------+                 +-------------------+
  |  User   |                 |   ThumbSwap Bot   |                 |  Telegram DC      |
  +---------+                 +-------------------+                 +-------------------+
       |                                |                                     |
       | 1. Send Photo                  |                                     |
       |------------------------------->| (Extract photo.file_id -> KV/RAM)   |
       |                                |                                     |
       |    ✅ "Thumbnail Saved!"        |                                     |
       |<-------------------------------|                                     |
       |                                |                                     |
       | 2. Send Video (up to 4GB)      |                                     |
       |------------------------------->| (Receive video.file_id metadata)    |
       |                                |                                     |
       |                                | 3. sendVideo(video_id, cover_id)    |
       |                                |------------------------------------>|
       |                                |                                     | (Swap pointer
       |                                |                                     |  server-side)
       | 4. Video with New Cover (1-5s) |                                     |
       |<---------------------------------------------------------------------|
```

---

## 📂 Project Structure

```
.
├── .github/
│   ├── dependabot.yml        # Automated dependency updates
│   └── pull_request_template.md # PR review checklist
├── cloudflare_worker/        # 🌐 100% Serverless Cloudflare Edition
│   ├── index.js              # Serverless webhook engine & KV pointer swap
│   ├── wrangler.toml         # Cloudflare Worker & KV namespace configuration
│   └── package.json          # Worker deployment tools
├── docs/
│   ├── ARCHITECTURE.md       # Deep dive into Server-Side Pointer Swap Architecture
│   └── DEPLOYMENT.md         # Detailed VPS & Serverless deployment guides
├── scripts/
│   ├── run.sh                # Auto-restarting background supervisor
│   ├── manage.sh             # Background service manager (start, stop, status, logs)
│   └── coverbot.service      # Linux systemd service unit template
├── src/                      # 🖥️ Python VPS / Container Edition
│   ├── __init__.py           # Package marker
│   ├── __main__.py           # Modular execution entry point (python -m src)
│   ├── bot.py                # Main Telegram Bot logic & event handlers
│   ├── config.py             # Robust environment configuration loader
│   └── storage.py            # High-speed in-memory RAM thumbnail cache
├── tests/
│   ├── __init__.py           # Test package marker
│   ├── conftest.py           # Shared test fixtures & sys.path configuration
│   ├── test_bot.py           # Bot handlers & pointer swap tests
│   └── test_storage.py       # RAM storage unit tests
├── .env.example              # Sample environment template with placeholders
├── .gitignore                # Comprehensive ignore rules for secrets and caches
├── Dockerfile                # Production-ready multi-stage Dockerfile
├── docker-compose.yml        # Docker Compose service definition
├── Makefile                  # Developer workflow automation (install, test, run, clean)
├── pyproject.toml            # PEP 518/621 modern package specification & dependencies
├── README.md                 # Project overview and documentation
└── LICENSE                   # MIT License
```

---

## 🚀 Deployment Options

### 🌟 Option 1: 100% Free Serverless on Cloudflare Workers (Recommended)

Deploy globally with 0ms cold starts, 24/7 uptime, and **zero server costs**:

```bash
cd cloudflare_worker

# 1. Install Wrangler
npm install

# 2. Deploy to Cloudflare Edge
npx wrangler deploy

# 3. Add your Bot Token securely
npx wrangler secret put BOT_TOKEN

# 4. Set Telegram Webhook to your worker URL
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -d "url=https://thumbswap-bot.<YOUR_SUBDOMAIN>.workers.dev/"
```

---

### 🖥️ Option 2: Linux VPS Background Supervisor (`make`)

The included management script handles background daemonization and auto-restarting:

```bash
# Setup virtual environment & install dependencies
make install

# Configure environment
cp .env.example .env
nano .env

# Start bot in background (supervisor auto-restarts on crash)
make start
# Or directly: ./scripts/manage.sh start

# Check status
make status

# View live logs
make logs

# Restart bot
make restart

# Stop bot
make stop
```

---

### 🐳 Option 3: Docker / Docker Compose

```bash
# Build and run in background
docker compose up -d --build

# View real-time logs
docker compose logs -f

# Stop container
docker compose down
```

---

### ⚙️ Option 4: Linux Systemd Service

```bash
# Copy service file to systemd directory
sudo cp scripts/coverbot.service /etc/systemd/system/coverbot.service

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable --now coverbot

# Check status
sudo systemctl status coverbot
```

---

## ⚙️ Environment Variables (`.env`)

For VPS / Docker deployments, configure your `.env` file:

```ini
# Bot token from @BotFather
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567

# Display name for your bot
BOT_NAME="ThumbSwap Bot"

# Telegram API credentials from https://my.telegram.org
API_ID=12345678
API_HASH=your_api_hash_here
```

---

## 🧪 Testing

Run the automated test suite verifying storage operations, media filtering, and zero-download payload delivery:

```bash
# Run pytest test suite via Makefile
make test

# Or manually:
./venv/bin/pytest -v tests/
```

---

## 🛡️ Security & Privacy

- **Zero Disk Writes:** Video files and photo binaries are never saved to disk.
- **Volatile Storage:** User thumbnails are stored in volatile RAM / Cloudflare KV and can be cleared at any time via `/clear`.
- **Strict File Filtering:** Uncompressed documents, raw `.mkv`, audio files, stickers, and animations are automatically rejected.
- **No Token Leakage:** Secrets are strictly loaded via environment variables and excluded by `.gitignore`.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
