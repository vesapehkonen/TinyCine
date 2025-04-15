#!/bin/bash
# play_video.sh
# Run mpv in a new terminal window with specified video and subtitles

# Check if video filename is provided
if [ -z "$1" ]; then
  echo "No video filename provided"
  exit 1
fi

# Get the full video path
VIDEO_PATH="$1"

# Generate subtitle path by replacing .mp4 with .srt (or adjust for other video formats)
SUBTITLE_PATH="${VIDEO_PATH%.*}.srt"

# Cache size in seconds
CACHE_SECONDS=120

# Check if subtitle file exists
if [ ! -f "$SUBTITLE_PATH" ]; then
  echo "Subtitle file not found: $SUBTITLE_PATH"
  # Optionally, you can continue without subtitles or handle this case
  SUBTITLE_OPTION=""
else
  # Use the subtitle path if it exists
  SUBTITLE_OPTION="--sub-file=$SUBTITLE_PATH"
fi

# Run mpv in a new terminal window
echo "mpv --cache=yes --cache-secs=$CACHE_SECONDS --cache-pause=yes $SUBTITLE_OPTION $VIDEO_PATH &"
mpv --cache=yes --cache-secs=$CACHE_SECONDS --cache-pause=yes $SUBTITLE_OPTION $VIDEO_PATH &
