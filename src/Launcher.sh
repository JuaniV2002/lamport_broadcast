#!/usr/bin/env bash
set -euo pipefail
PS4='+ $BASH_SOURCE:$LINENO: ' && set -x

# Lista de comandos...
comandos=(
  "python3 application.py p1"
  "python3 application.py p2"
)

OS=$(uname -s)

case $OS in
  Linux|Darwin)
    session="my_session"
    tmux kill-session -t "$session" 2>/dev/null || true

    # 1) crear sesión en background con un shell
    tmux new-session -d -s "$session" -c "$(pwd)" bash

    # 2) enviar primer comando al panel 0
    tmux send-keys -t "$session:0.0" "${comandos[0]}" C-m

    # 3) splits para los restantes
    for cmd in "${comandos[@]:1}"; do
      tmux split-window -h -t "$session"
      tmux send-keys -t "$session" "$cmd" C-m
    done

    # 4) organizar y adjuntar
    tmux select-layout -t "$session" tiled
    tmux attach-session -t "$session"
    ;;
  *)
    echo "SO no soportado: $OS" >&2
    exit 1
    ;;
esac