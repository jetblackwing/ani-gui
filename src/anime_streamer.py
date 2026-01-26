# anime_streamer.py
#
# Copyright 2024 Amal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Anime streaming wrapper for ani-cli without rofi dependency.
Uses fzf for interactive selection instead of rofi.
"""

import subprocess
import threading
import os
from typing import Optional, Callable

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


class AnimeStreamer:
    """Anime streamer using ani-cli with fzf (no rofi required)."""
    
    def __init__(self):
        self.ani_cli_path = "/usr/bin/ani-cli"
        self.current_process = None
    
    def play_anime(self, anime_name: str, episode: Optional[str] = None,
                   quality: str = "best",
                   callback: Optional[Callable] = None):
        """Play anime using ani-cli with fzf selection.
        
        Args:
            anime_name: Name of anime to play (ani-cli will search)
            episode: Specific episode number (optional)
            quality: Quality preference (best, 720p, 1080p)
            callback: Callback (success, message)
        """
        def play_thread():
            try:
                cmd = [self.ani_cli_path]
                
                if episode:
                    cmd.extend(["-e", str(episode)])
                
                if quality and quality != "best":
                    cmd.extend(["-q", quality])
                
                cmd.append(anime_name)
                
                print(f"[ani-gui] Launching ani-cli: {' '.join(cmd)}")
                
                # Set environment to use fzf instead of rofi
                env = os.environ.copy()
                env["use_external_menu"] = "0"  # Force ani-cli to use fzf
                
                # Start ani-cli process
                # Don't capture output - let it use interactive terminal
                self.current_process = subprocess.Popen(
                    cmd,
                    env=env,
                    # stdin/stdout/stderr connected to terminal for interactivity
                )
                
                if callback:
                    GLib.idle_add(callback, True, f"Streaming: {anime_name}")
                
                # Wait for process to finish
                self.current_process.wait()
                return_code = self.current_process.returncode
                
                if return_code == 0:
                    if callback:
                        GLib.idle_add(callback, True, f"Finished: {anime_name}")
                else:
                    if callback:
                        GLib.idle_add(callback, False, f"Streaming ended (code: {return_code})")
                
            except Exception as e:
                if callback:
                    GLib.idle_add(callback, False, f"Error: {str(e)}")
                print(f"[ani-gui] Streaming error: {e}")
        
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()
    
    def stop_playback(self):
        """Stop current playback."""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except:
                try:
                    self.current_process.kill()
                except:
                    pass
            self.current_process = None


