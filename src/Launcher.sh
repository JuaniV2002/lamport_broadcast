#!/bin/bash

# Lista de comandos que deseas ejecutar en diferentes terminales
comandos=(
    "python3.10 application.py p1"
    "python3.10 application.py p2"
)

# Determinar el sistema operativo
OS=$(uname -s)

# Llamar a la terminal por defecto según el sistema operativo
case $OS in
    Linux)
        tmux new-session \; \
        for comando in "${comandos[@]}"; do \
            tmux split-window -h \; \
            tmux send-keys "$comando" C-m \; \
        done
        ;;
    Darwin)
        tmux new-session \; \
        for comando in "${comandos[@]}"; do \
            tmux split-window -h \; \
            tmux send-keys "$comando" C-m \; \
        done
        ;;
    CYGWIN*|MSYS*|MINGW*)
        # No se puede utilizar `tmux` en Windows de manera nativa
        # Puedes utilizar `Git Bash` o `WSL` para ejecutar `tmux`
        ;;
    *)
        echo "Sistema operativo no soportado"
        exit 1
        ;;
esac