#!/bin/bash
#
# ani-cli wrapper - forces fzf usage (no rofi dependency)
# This wrapper ensures ani-cli uses fzf for interactive menus
#

# Force ani-cli to use fzf instead of rofi
export use_external_menu="0"

# Optional: disable external menu completely to always use fzf
# export external_menu_args=""

# Call the original ani-cli with all arguments
/usr/bin/ani-cli "$@"
