# video_player.py
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

from gi.repository import Gtk, GLib, Gio
import subprocess
from typing import Optional

class VideoPlayerWidget(Gtk.Box):
    """A simple video player widget using external players."""
    
    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10
        )
        
        self.current_anime = None
        self.current_url = None
        
        # Title label
        self.title_label = Gtk.Label(
            label="Select an anime to play",
            css_classes=["title-2"]
        )
        self.title_label.set_wrap(True)
        self.append(self.title_label)
        
        # Video frame (placeholder)
        self.video_frame = Gtk.Frame(
            label="Video Player",
            margin_top=10,
            margin_bottom=10
        )
        video_placeholder = Gtk.Label(label="Video will play here using your system player")
        self.video_frame.set_child(video_placeholder)
        self.append(self.video_frame)
        
        # Info box
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        self.info_label = Gtk.Label(
            label="",
            wrap=True,
            xalign=0
        )
        info_box.append(self.info_label)
        
        self.append(info_box)
        
        # Controls
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        controls.set_homogeneous(True)
        
        self.play_button = Gtk.Button(label="Play with System Player")
        self.play_button.connect("clicked", self.on_play_clicked)
        controls.append(self.play_button)
        
        self.clear_button = Gtk.Button(label="Clear")
        self.clear_button.connect("clicked", self.on_clear_clicked)
        controls.append(self.clear_button)
        
        self.append(controls)
        
        self.set_sensitive(False)
    
    def set_anime(self, anime: dict, video_url: Optional[str] = None):
        """Set the anime to display.
        
        Args:
            anime: Anime data dictionary from AniList
            video_url: Optional video streaming URL
        """
        self.current_anime = anime
        self.current_url = video_url
        
        # Update title
        from .anilist_api import AniListAPI
        api = AniListAPI()
        title = api.get_anime_title(anime)
        self.title_label.set_text(title)
        
        # Update info
        info_parts = []
        
        if anime.get('episodes'):
            info_parts.append(f"Episodes: {anime['episodes']}")
        
        if anime.get('status'):
            info_parts.append(f"Status: {anime['status']}")
        
        if anime.get('genres'):
            genres = ', '.join(anime['genres'][:3])
            info_parts.append(f"Genres: {genres}")
        
        if anime.get('averageScore'):
            info_parts.append(f"Rating: {anime['averageScore']}/100")
        
        info_text = ' • '.join(info_parts)
        self.info_label.set_text(info_text)
        
        # Update button state
        self.set_sensitive(True)
        if not video_url:
            self.play_button.set_label("Open with Web Browser")
    
    def on_play_clicked(self, button):
        """Handle play button click."""
        if not self.current_anime:
            return
        
        if self.current_url:
            # Try to play with VLC or MPV
            self._play_with_player(self.current_url)
        else:
            # Open AniList page in browser
            anime_id = self.current_anime.get('id')
            if anime_id:
                url = f"https://anilist.co/anime/{anime_id}"
                Gio.AppInfo.launch_default_for_uri(url, None)
    
    def on_clear_clicked(self, button):
        """Handle clear button click."""
        self.current_anime = None
        self.current_url = None
        self.title_label.set_text("Select an anime to play")
        self.info_label.set_text("")
        self.set_sensitive(False)
    
    def _play_with_player(self, url: str):
        """Try to play URL with available video player.
        
        Args:
            url: Video URL to play
        """
        players = ['mpv', 'vlc', 'totem']
        
        for player in players:
            try:
                subprocess.Popen([player, url])
                return
            except FileNotFoundError:
                continue
        
        # If no player found, show error
        dialog = Gtk.AlertDialog(
            message="No video player found",
            detail="Please install mpv, vlc, or another video player."
        )
        dialog.present(None)
