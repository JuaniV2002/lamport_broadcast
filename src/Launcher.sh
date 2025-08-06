#!/usr/bin/env bash
set -euo pipefail
PS4='+ $BASH_SOURCE:$LINENO: ' && set -x

# Command list
commands=(
  "python3 app.py p1"
  "python3 app.py p2"
  "python3 app.py p3"
)

OS=$(uname -s)

case $OS in
  Linux|Darwin)
    session="broadcast_session"
    tmux kill-session -t "$session" 2>/dev/null || true

    # 1) create background session
    tmux new-session -d -s "$session" -c "$(pwd)" bash

    # 2) send first command to panel 0
    tmux rename-window -t "$session:0" "Process-P1"
    tmux send-keys -t "$session:0.0" "${commands[0]}" C-m

    # 3) new windows for the remaining
    i=1
    for cmd in "${commands[@]:1}"; do
      tmux new-window -t "$session" -n "Process-P$((i+1))"
      tmux send-keys -t "$session" "$cmd" C-m
      ((i++))
    done

    # 4) select the first window and attach
    tmux select-window -t "$session:0"
    tmux attach-session -t "$session"
    ;;
  *)
    echo "Unsupported OS: $OS" >&2
    exit 1
    ;;
esac