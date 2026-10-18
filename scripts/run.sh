#!/usr/bin/env bash
# scripts/run.sh - Supervisor loop for Telegram Video Cover Changer Bot
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

VENV_PYTHON="$PROJECT_ROOT/venv/bin/python3"
LOG_FILE="$PROJECT_ROOT/bot.log"
PID_FILE="$PROJECT_ROOT/bot.pid"

echo $$ > "$PID_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting supervisor (PID: $$) for Telegram Video Cover Changer Bot..." >> "$LOG_FILE"

# Trap termination signals to clean up PID file
cleanup() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Supervisor received termination signal. Cleaning up..." >> "$LOG_FILE"
    rm -f "$PID_FILE"
    pkill -P $$ || true
    exit 0
}
trap cleanup SIGTERM SIGINT SIGHUP

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Launching bot process from src/bot.py..." >> "$LOG_FILE"
    
    # Run unbuffered python from src/bot.py and pipe output to log file
    "$VENV_PYTHON" -u "$PROJECT_ROOT/src/bot.py" >> "$LOG_FILE" 2>&1 || true
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bot process exited. Restarting in 3 seconds..." >> "$LOG_FILE"
    sleep 3
done
