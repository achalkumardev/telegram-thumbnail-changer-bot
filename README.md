# Telegram Video Cover / Thumbnail Changer Bot 🎬⚡

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-informational.svg)](https://docs.aiogram.dev/)
[![Architecture](https://img.shields.io/badge/Architecture-Server--Side%20Pointer%20Swap-brightgreen.svg)](#-zero-download-server-side-pointer-swap-architecture)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, ultra-fast Telegram Bot designed with a **Zero-Download Server-Side Pointer Swap Architecture** that swaps streaming video covers/thumbnails in **1 to 5 seconds** for video files up to **4GB**.

---

## ⚡ Zero-Download Server-Side Pointer Swap Architecture

### Why Traditional Bots Fail
Traditional Telegram thumbnail changer bots download the incoming video to disk, invoke `ffmpeg` to re-encode or attach the thumbnail, and then re-upload the binary file. This legacy method has critical limitations:
1. **Fails on files > 20MB/50MB:** Bot API download limits strictly prevent local downloading of large videos.
2. **Heavy Resource Consumption:** Demands gigabytes of VPS RAM, massive CPU spikes, high disk I/O, and consumes server bandwidth.
3. **Severe Quality & Metadata Loss:** Transcoding alters original codecs, degrades bitrate, breaks streaming metadata, and strips audio channels.
4. **Extreme Latency:** Downloading and uploading 1GB to 4GB files takes several minutes to hours.

### The Modern Solution (Method 5)
This bot leverages Telegram's modern `cover` parameter in the `sendVideo` Bot API endpoint:
- **Streaming Video Metadata Delivery:** When a user sends any streaming video (up to 4GB), Telegram's Message update delivers its native `video.file_id`.
- **In-Memory Thumbnail Registration:** When a user sends a photo, its highest-resolution `photo.file_id` is cached instantly in RAM.
- **Server-Side Pointer Binding:** When the user sends a streaming video, the bot sends an asynchronous JSON HTTP payload back to Telegram DC:
  ```json
  {
    "chat_id": 123456789,
    "video": "<EXISTING_VIDEO_FILE_ID>",
    "cover": "<EXISTING_PHOTO_FILE_ID>",
    "supports_streaming": true
  }
  ```
- **100% Quality & Stream Metadata Preservation:** Telegram's Data Centers link the new cover pointer directly to the existing video asset. Zero bytes are downloaded to or uploaded from the VPS. The round-trip completes in **0.5 to 2 seconds**.

```
  +---------+                 +-------------------+                 +-------------------+
  |  User   |                 |    Cover Bot      |                 |  Telegram DC      |
  +---------+                 +-------------------+                 +-------------------+
       |                                |                                     |
       | 1. Send Photo                  |                                     |
       |------------------------------->| (Extract photo.file_id -> RAM)      |
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
│   ├── workflows/
│   │   └── ci.yml            # Automated CI pipeline (lint, test across Python 3.10-3.12)
│   └── dependabot.yml        # Automated dependency updates
├── docs/
│   ├── ARCHITECTURE.md       # Deep dive into Server-Side Pointer Swap Architecture
│   └── DEPLOYMENT.md         # Production deployment & service orchestration guide
├── src/
│   ├── __init__.py           # Package marker
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
├── coverbot.service          # Linux systemd service unit template
├── run.sh                    # Auto-restarting background supervisor
├── manage.sh                 # Background service manager (start, stop, status, logs)
├── README.md                 # Project overview and documentation
└── LICENSE                   # MIT License
```

---

## 🚀 Getting Started

### 1. Clone & Configure

```bash
git clone https://github.com/achalkumardev/telegram-thumbnail-changer-bot.git
cd telegram-thumbnail-changer-bot

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Environment Variables (`.env`)

```ini
# Bot token from @BotFather
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567

# Display name for your bot
BOT_NAME="Thumbnail Changer Bot"

# Telegram API credentials from https://my.telegram.org
API_ID=12345678
API_HASH=your_api_hash_here
```

---

## 💻 Running the Bot

### Option A: Built-in Service Manager (`manage.sh`)

The included management script handles background daemonization and auto-restarting:

```bash
# Make scripts executable
chmod +x manage.sh run.sh

# Start bot in background
./manage.sh start

# Check status
./manage.sh status

# View live logs
./manage.sh logs

# Restart bot
./manage.sh restart

# Stop bot
./manage.sh stop
```

---

### Option B: Docker / Docker Compose

```bash
# Build and run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f

# Stop container
docker compose down
```

---

### Option C: Systemd Service (Production VPS)

```bash
# Copy service file to systemd directory
sudo cp coverbot.service /etc/systemd/system/coverbot.service

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable --now coverbot

# Check status
sudo systemctl status coverbot
```

---

## 🧪 Testing

Run the automated test suite verifying storage operations, media filtering, and zero-download payload delivery:

```bash
# Activate virtual environment
source venv/bin/activate

# Run pytest
pytest -v test_bot.py
```

---

## 🛡️ Security & Privacy

- **Zero Disk Writes:** Video files and photo binaries are never saved to disk.
- **In-Memory Cache:** User thumbnails are stored in volatile RAM dictionary (`storage.py`) and cleared on process restart.
- **Strict File Filtering:** Uncompressed documents, raw `.mkv`, audio files, stickers, and animations are automatically rejected.
- **No Token Leakage:** Secrets are strictly loaded via environment variables and excluded by `.gitignore`.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
