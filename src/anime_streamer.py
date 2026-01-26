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
    """Anime streamer using ani-cli with fzf (via fake rofi wrapper)."""
    
    def __init__(self):
        # Use the real ani-cli (rofi is now a fzf wrapper in /usr/local/bin)
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
                # Verify ani-cli available
                import subprocess as sp
                check = sp.run(
                    [self.ani_cli_path, "--version"],
                    capture_output=True,
                    timeout=5
                )
                if check.returncode != 0:
                    if callback:
                        GLib.idle_add(callback, False, "❌ ani-cli not responding")
                    return
                
                cmd = [self.ani_cli_path]
                
                if episode:
                    cmd.extend(["-e", str(episode)])
                
                if quality and quality != "best":
                    cmd.extend(["-q", quality])
                
                cmd.append(anime_name)
                
                print(f"[ani-gui] Starting: {' '.join(cmd)}")
                
                # Set environment for fzf
                env = os.environ.copy()
                # ani-cli will find /usr/local/bin/rofi (our fake rofi that uses fzf)
                
                # Start ani-cli - don't capture I/O so fzf/mpv can interact with terminal
                self.current_process = sp.Popen(
                    cmd,
                    env=env,
                    # stdin/stdout/stderr inherit from parent (terminal)
                )
                
                print(f"[ani-gui] Process started, PID: {self.current_process.pid}")
                
                # Wait for process to complete
                # This will block until user finishes selecting and watching
                self.current_process.wait()
                return_code = self.current_process.returncode
                
                print(f"[ani-gui] Process exited with code: {return_code}")
                
                if callback:
                    if return_code == 0:
                        GLib.idle_add(callback, True, f"✅ Finished: {anime_name}")
                    elif return_code == 130:
                        GLib.idle_add(callback, False, "⏹️ Stopped by user")
                    else:
                        GLib.idle_add(callback, False, f"⚠️ Playback ended")
                
            except FileNotFoundError as e:
                if callback:
                    msg = f"❌ ani-cli not found\nEnsure installed: sudo apt install ani-cli"
                    GLib.idle_add(callback, False, msg)
                print(f"[ani-gui] File not found: {e}")
            except Exception as e:
                if callback:
                    msg = f"❌ Error: {str(e)}"
                    GLib.idle_add(callback, False, msg)
                print(f"[ani-gui] Error: {e}")
        
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


