#!/usr/bin/env bash
# run.sh - Supervisor loop for Telegram Video Cover Changer Bot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
LOG_FILE="$SCRIPT_DIR/bot.log"
PID_FILE="$SCRIPT_DIR/bot.pid"

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
    "$VENV_PYTHON" -u "$SCRIPT_DIR/src/bot.py" >> "$LOG_FILE" 2>&1 || true
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bot process exited. Restarting in 3 seconds..." >> "$LOG_FILE"
    sleep 3
done
