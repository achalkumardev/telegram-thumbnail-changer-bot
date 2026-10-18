# Deployment Guide 🚀

This document outlines the standard deployment workflows for production VPS environments.

---

## 🛠️ Prerequisites

- Linux Server (Ubuntu 22.04 / 24.04 LTS recommended)
- Python 3.10 or higher
- Git

---

## 1. Local VPS Supervisor Deployment (Included)

The repository includes a battle-tested background supervisor loop (`scripts/run.sh`) and a control script (`scripts/manage.sh`).

### Setup:
```bash
git clone https://github.com/achalkumardev/telegram-thumbnail-changer-bot.git
cd telegram-thumbnail-changer-bot

# Setup virtual environment and install dependencies
make install
# Or manually:
# python3 -m venv venv && ./venv/bin/pip install .

# Configure environment
cp .env.example .env
nano .env

# Make scripts executable
chmod +x scripts/*.sh

# Start daemon
./scripts/manage.sh start
# Or via Makefile:
make start
```

### Management Commands:
- **Status:** `./scripts/manage.sh status` (or `make status`)
- **Live Logs:** `./scripts/manage.sh logs` (or `make logs`)
- **Restart:** `./scripts/manage.sh restart` (or `make restart`)
- **Stop:** `./scripts/manage.sh stop` (or `make stop`)

---

## 2. Systemd Service Deployment

For systems utilizing systemd for service orchestration:

1. Copy the provided unit file:
   ```bash
   sudo cp scripts/coverbot.service /etc/systemd/system/coverbot.service
   ```

2. Edit paths and user if needed:
   ```bash
   sudo nano /etc/systemd/system/coverbot.service
   ```

3. Reload and enable:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now coverbot
   ```

4. Monitor service:
   ```bash
   sudo systemctl status coverbot
   sudo journalctl -u coverbot -f
   ```

---

## 3. Docker Deployment

### Using Docker Compose:
```bash
# Build and run
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```
