# media_player.py
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

import subprocess
from typing import Optional, Callable

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class MediaPlayer(Gtk.Box):
    """Built-in media player with fullscreen support using mpv."""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.mpv_process = None
        self.current_url = None
        self.is_fullscreen = False
        self.on_closed: Optional[Callable] = None
        
        # Player container
        self.player_frame = Gtk.Frame()
        self.player_frame.set_child(Gtk.Label(label="Player will load here"))
        self.append(self.player_frame)
        
        # Control bar
        controls = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=5,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5
        )
        
        self.play_button = Gtk.Button(label="▶ Play")
        self.play_button.connect("clicked", self.on_play)
        controls.append(self.play_button)
        
        self.pause_button = Gtk.Button(label="⏸ Pause")
        self.pause_button.connect("clicked", self.on_pause)
        controls.append(self.pause_button)
        
        self.fullscreen_button = Gtk.Button(label="⛶ Fullscreen")
        self.fullscreen_button.connect("clicked", self.on_fullscreen)
        controls.append(self.fullscreen_button)
        
        self.stop_button = Gtk.Button(label="⏹ Stop")
        self.stop_button.connect("clicked", self.on_stop)
        controls.append(self.stop_button)
        
        self.append(controls)
    
    def play_url(self, url: str, title: str = ""):
        """Play a URL with mpv.
        
        Args:
            url: Media URL to play
            title: Optional title for the window
        """
        self.current_url = url
        
        try:
            # Build mpv command with socket for IPC
            cmd = [
                'mpv',
                '--player-operation-mode=pseudo-gui',
                '--force-window=immediate',
                url
            ]
            
            if title:
                cmd.extend(['--title', title])
            
            self.mpv_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            print("Error: mpv not found. Install with: sudo apt install mpv")
    
    def on_play(self, button):
        """Play button clicked."""
        if self.mpv_process and self.mpv_process.poll() is None:
            # Send play command via dbus or similar
            pass
    
    def on_pause(self, button):
        """Pause button clicked."""
        if self.mpv_process and self.mpv_process.poll() is None:
            pass
    
    def on_fullscreen(self, button):
        """Fullscreen button clicked."""
        if self.mpv_process and self.mpv_process.poll() is None:
            # mpv supports fullscreen via key press
            pass
    
    def on_stop(self, button):
        """Stop button clicked."""
        self.stop_playback()
    
    def stop_playback(self):
        """Stop current playback."""
        if self.mpv_process:
            try:
                self.mpv_process.terminate()
                self.mpv_process.wait(timeout=2)
            except Exception as e:
                print(f"Error stopping playback: {e}")
                try:
                    self.mpv_process.kill()
                except:
                    pass
            finally:
                self.mpv_process = None
        
        if self.on_closed:
            self.on_closed()
