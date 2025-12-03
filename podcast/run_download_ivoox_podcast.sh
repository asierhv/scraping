#!/bin/bash

# Activate the conda environment
conda activate scrap

# Define paths
FEED_FILE="feed_rss.json"
OUTPUT_DIR="audios"
ONLY_STATS=false

# Generate a log file with current date and time
LOG_FILE="logs/download_$(date +'%Y%m%d_%H%M%S').log"

# Run the Python script and log output
python download_ivoox_podcast.py \
    --feed_rss_file="$FEED_FILE" \
    --output_dir="$OUTPUT_DIR" \
    --only_stats="$ONLY_STATS" \
    > "$LOG_FILE" 2>&1
