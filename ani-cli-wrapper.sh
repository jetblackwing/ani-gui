#!/bin/bash
#
# ani-cli wrapper - ensures fzf usage with fallback
# This wrapper forces ani-cli to use fzf and handles rofi failures
#

# Check if rofi is available
if ! command -v rofi &> /dev/null; then
    # rofi not found, force fzf
    export use_external_menu="0"
else
    # rofi exists, still prefer fzf for better compatibility
    export use_external_menu="0"
fi

# Ensure fzf is available as fallback
if ! command -v fzf &> /dev/null; then
    echo "ERROR: Neither rofi nor fzf found!" >&2
    echo "Please install fzf: sudo apt install fzf" >&2
    exit 1
fi

# Call the original ani-cli with all arguments
# Use full path to avoid recursive calls
/usr/bin/ani-cli "$@"

