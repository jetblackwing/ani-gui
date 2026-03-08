# video_player.py
#
# Copyright 2024 Amal J Krishnan <amaljk80@gmail.com> (@jetblackwing)
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
Minimal embedded video player using GTK 4's GtkVideo widget.
"""

from gi.repository import Gtk
from typing import Optional, Callable


class VideoPlayerWidget(Gtk.Box):
    """Minimal embedded video player using GTK 4's GtkVideo."""
    
    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )
        
        # Title bar
        title_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin_start=10,
            margin_end=10,
            margin_top=10
        )
        
        self.title_label = Gtk.Label(
            label="Video Player",
            css_classes=["heading"]
        )
        self.title_label.set_hexpand(True)
        title_box.append(self.title_label)
        
        close_button = Gtk.Button(label="✕")
        close_button.connect("clicked", self.on_close_clicked)
        close_button.set_size_request(40, -1)
        title_box.append(close_button)
        
        self.append(title_box)
        
        # Video player
        self.video = Gtk.Video()
        self.video.set_hexpand(True)
        self.video.set_vexpand(True)
        self.append(self.video)
        
        # Controls bar
        controls = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin_start=10,
            margin_end=10,
            margin_bottom=10
        )
        
        # Play/Pause button
        self.play_pause_button = Gtk.Button(label="▶ Play")
        self.play_pause_button.connect("clicked", self.on_play_pause_clicked)
        self.play_pause_button.set_size_request(80, -1)
        controls.append(self.play_pause_button)
        
        # Progress bar
        self.progress = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0, 100, 0.1
        )
        self.progress.set_hexpand(True)
        self.progress.set_draw_value(False)
        controls.append(self.progress)
        
        # Time label
        self.time_label = Gtk.Label(label="0:00 / 0:00")
        self.time_label.set_size_request(100, -1)
        self.time_label.set_xalign(1.0)
        controls.append(self.time_label)
        
        self.append(controls)
        
        self.is_playing = False
        self.on_close_callback = None
    
    def play(self, url: str, title: str):
        """Load and play a video from URL.
        
        Args:
            url: Direct video URL
            title: Video title to display
        """
        self.title_label.set_text(f"▶️ {title}")
        
        try:
            # Create GtkMediaFile from URL
            media_file = Gtk.MediaFile.new_for_uri(url)
            self.video.set_media_stream(media_file)
            self.video.set_autoplay(True)
            self.is_playing = True
            self.play_pause_button.set_label("⏸ Pause")
            
            print(f"[VideoPlayer] Playing: {title}")
            print(f"[VideoPlayer] URL: {url}")
        except Exception as e:
            print(f"[VideoPlayer] Error loading video: {e}")
            self.title_label.set_text(f"❌ Error: {str(e)}")
    
    def on_play_pause_clicked(self, button):
        """Toggle play/pause."""
        stream = self.video.get_media_stream()
        if not stream:
            return
        
        if self.is_playing:
            stream.pause()
            self.play_pause_button.set_label("▶ Play")
            self.is_playing = False
        else:
            stream.play()
            self.play_pause_button.set_label("⏸ Pause")
            self.is_playing = True
    
    def on_close_clicked(self, button):
        """Close the player."""
        stream = self.video.get_media_stream()
        if stream:
            stream.pause()
        
        self.is_playing = False
        
        if self.on_close_callback:
            self.on_close_callback()
    
    def set_on_close_callback(self, callback: Callable):
        """Set callback for when player is closed."""
        self.on_close_callback = callback
