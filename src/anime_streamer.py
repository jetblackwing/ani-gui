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
        # Use wrapper script that forces fzf instead of rofi
        import os as os_module
        wrapper_path = os_module.path.join(
            os_module.path.dirname(os_module.path.dirname(__file__)),
            "ani-cli-wrapper.sh"
        )
        self.ani_cli_path = wrapper_path if os_module.path.exists(wrapper_path) else "/usr/bin/ani-cli"
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
                # Verify wrapper and ani-cli available
                import subprocess as sp
                check = sp.run(
                    [self.ani_cli_path, "--version"],
                    capture_output=True,
                    timeout=5
                )
                if check.returncode != 0:
                    raise Exception("ani-cli not responding")
                
                cmd = [self.ani_cli_path]
                
                if episode:
                    cmd.extend(["-e", str(episode)])
                
                if quality and quality != "best":
                    cmd.extend(["-q", quality])
                
                cmd.append(anime_name)
                
                print(f"[ani-gui] Command: {' '.join(cmd)}")
                print(f"[ani-gui] Using ani-cli path: {self.ani_cli_path}")
                
                # Set environment to use fzf
                env = os.environ.copy()
                env["use_external_menu"] = "0"  # Force fzf
                
                # Start ani-cli process - DON'T capture I/O so interactive menus work
                self.current_process = subprocess.Popen(
                    cmd,
                    env=env,
                    # Let stdin/stdout/stderr connect to terminal for fzf/mpv interaction
                )
                
                if callback:
                    GLib.idle_add(callback, True, f"▶️  Streaming: {anime_name}")
                
                # Wait for process to finish
                self.current_process.wait()
                return_code = self.current_process.returncode
                
                if return_code == 0:
                    if callback:
                        GLib.idle_add(callback, True, f"✅ Finished: {anime_name}")
                else:
                    if callback:
                        if return_code == 130:
                            msg = "⏹️ Playback stopped by user"
                        else:
                            msg = f"⚠️ Playback ended (code: {return_code})"
                        GLib.idle_add(callback, False, msg)
                
            except FileNotFoundError as e:
                if callback:
                    msg = f"❌ ani-cli wrapper not found at {self.ani_cli_path}\nEnsure ani-cli-wrapper.sh exists"
                    GLib.idle_add(callback, False, msg)
                print(f"[ani-gui] File not found: {e}")
            except Exception as e:
                if callback:
                    msg = f"❌ Error: {str(e)}\nMake sure ani-cli and fzf are installed"
                    GLib.idle_add(callback, False, msg)
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


