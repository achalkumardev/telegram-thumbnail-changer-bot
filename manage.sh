#!/usr/bin/env bash
# manage.sh - Helper script to start, stop, restart, check status, and view logs
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/bot.pid"
LOG_FILE="$SCRIPT_DIR/bot.log"

start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Bot is already running (PID: $(cat "$PID_FILE"))."
        exit 0
    fi
    echo "Starting Telegram Video Cover Changer Bot in background..."
    setsid "$SCRIPT_DIR/run.sh" </dev/null >/dev/null 2>&1 &
    sleep 2
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Bot started successfully! (Supervisor PID: $(cat "$PID_FILE"))"
    else
        echo "Failed to start bot. Check $LOG_FILE for details."
        exit 1
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Stopping Bot supervisor (PID: $PID)..."
            kill "$PID" 2>/dev/null || true
            sleep 1
        fi
        rm -f "$PID_FILE"
    fi
    echo "Stopping any running bot processes..."
    pkill -f "python3.*(src/bot\.py|bot\.py)" 2>/dev/null || true
    echo "Bot stopped."
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Bot supervisor is RUNNING (PID: $(cat "$PID_FILE"))."
        echo "Active processes:"
        pgrep -af "telegram_cover_bot" || true
    else
        echo "Bot is STOPPED."
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -n 50 "$LOG_FILE"
    else
        echo "No log file found at $LOG_FILE yet."
    fi
}

case "${1:-status}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
