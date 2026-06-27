#!/bin/bash

# strict mode
set -Eeuo pipefail

# rm tmp files function
function rm_tmp_files {
    :
}

# Cleanup function
function cleanup {
    local exit_code="$?"
    echo "Script install-service.sh interrupted or failed. Cleaning up..."

    # remove tmp files
    rm_tmp_files
    # exit the script, preserving the exit code
    exit "$exit_code"
}

# trap errors
trap 'echo "Error on line $LINENO in install-service.sh: command \"$BASH_COMMAND\" exited with status $?" >&2' ERR
# trap signals
trap 'cleanup' INT TERM ERR

function check_args {
    :
}

function init {
    # config dir
    CONFIG_DIR="${CONFIG_DIR:-${XDG_CONFIG_HOME-${HOME}/.config/}}"
    export CONFIG_DIR="${CONFIG_DIR%/}"
    # data dir
    VIDSIFT_DATA_DIR="${VIDSIFT_DATA_DIR:-${XDG_DATA_HOME:-$HOME/.local/share/vidsift/}}"
    export VIDSIFT_DATA_DIR="${VIDSIFT_DATA_DIR%/}"
    # vidsift bin dir
    VIDSIFT_BIN_DIR="${VIDSIFT_BIN_DIR:-${XDG_BIN_HOME:-"$HOME/.local/bin/"}}"
    export VIDSIFT_BIN_DIR="${VIDSIFT_BIN_DIR%/}"

    mkdir -p "$CONFIG_DIR"
    mkdir -p "$VIDSIFT_DATA_DIR"
    mkdir -p "$VIDSIFT_BIN_DIR"
}

function mv_service {
    cat <<EOF >"${CONFIG_DIR}/systemd/${USER}/vidsift.service"
[Unit]
Description=Vidsift YouTube pipeline service

[Service]
Type=simple
ExecStart=${VIDSIFT_BIN_DIR}/vidsift schedule
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
}

function enable_service {
    systemctl --user daemon-reload
    systemctl --user enable vidsift.service
}

function check_bin {
    if [[ ! -e "$VIDSIFT_BIN_DIR/vidsift" ]]; then
        echo "ERROR: Vidsifts bin Path is not executable or does not exist: $VIDSIFT_BIN_DIR/vidsift"
        exit 1
    fi
}

function main {
    #check_args "$@"
    init "$@"
    mv_service
    check_bin
    echo "The service has been set up properly. Start it using 'systemctl --user start vidsift.service'"
}

# call main with all args, as given
main "$@"
