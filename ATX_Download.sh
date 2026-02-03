#!/bin/bash

# Define the target directory
BASE_DIR="/var/www/html/Antenna_Info"
cd "$BASE_DIR" || { echo "Base directory not found"; exit 1; }

# Get the mode from the first argument (converted to uppercase)
MODE=$(echo "$1" | tr '[:lower:]' '[:upper:]')

# --- Helper Functions ---

process_ngs() {
    logger "NGS Antenna Processing starts"
    mkdir -p NGS20
    cd NGS20 || return 1
    rm -f ngs20.atx
    wget -O ngs20.atx "https://geodesy.noaa.gov/ANTCAL/LoadFile?file=ngs20.atx"
    /home/Trimble-CEC/Antenna_atx.py < ngs20.atx > index.html.new
    mv -f index.html.new index.html
    cd ..
    logger "NGS Antenna Processing completed"
}

process_igs() {
    logger "IGS Antenna Processing starts"
    mkdir -p IGS20
    cd IGS20 || return 1
    rm -f igs20.atx
    wget -O igs20.atx "https://files.igs.org/pub/station/general/igs20.atx"
    /home/Trimble-CEC/Antenna_atx.py < igs20.atx > index.html.new
    mv -f index.html.new index.html
    cd ..
    logger "IGS Antenna Processing completed"
}

# --- Execution Logic ---

case "$MODE" in
    "NGS")
        process_ngs
        ;;
    "IGS")
        process_igs
        ;;
    *)
        # Default: Process both if no parameter or an unknown parameter is passed
        process_ngs
        process_igs
        ;;
esac
