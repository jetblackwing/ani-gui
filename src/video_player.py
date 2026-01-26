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

from .ani_cli_integration import AniCliIntegration


class VideoPlayerWidget(Gtk.Box):
    """A video player widget using ani-cli and external players."""
    
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
        self.ani_cli = AniCliIntegration()
        
        # Title label
        self.title_label = Gtk.Label(
            label="Select an anime to play",
            css_classes=["title-2"]
        )
        self.title_label.set_wrap(True)
        self.append(self.title_label)
        
        # Status bar for watching/downloading
        self.status_label = Gtk.Label(
            label="",
            css_classes=["dim-label"],
            wrap=True
        )
        self.append(self.status_label)
        
        # Quality selector
        quality_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        quality_label = Gtk.Label(label="Quality:")
        quality_box.append(quality_label)
        
        self.quality_combo = Gtk.ComboBoxText()
        self.quality_combo.append("best", "Best Available")
        self.quality_combo.append("1080p", "1080p")
        self.quality_combo.append("720p", "720p")
        self.quality_combo.append("480p", "480p")
        self.quality_combo.set_active_id("best")
        quality_box.append(self.quality_combo)
        
        self.append(quality_box)
        
        # Episode selector
        episode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        episode_label = Gtk.Label(label="Episode:")
        episode_box.append(episode_label)
        
        self.episode_spin = Gtk.SpinButton(
            adjustment=Gtk.Adjustment(value=1, lower=0, upper=10000, step_increment=1)
        )
        episode_box.append(self.episode_spin)
        
        self.append(episode_box)
        
        # Info box
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        self.info_label = Gtk.Label(
            label="",
            wrap=True,
            xalign=0
        )
        info_box.append(self.info_label)
        
        self.append(info_box)
        
        # Control buttons
        controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Watch button
        watch_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        watch_button_box.set_homogeneous(True)
        
        self.watch_button = Gtk.Button(label="▶ Watch with ani-cli")
        self.watch_button.connect("clicked", self.on_watch_clicked)
        watch_button_box.append(self.watch_button)
        
        self.continue_button = Gtk.Button(label="⏯ Continue Watching")
        self.continue_button.connect("clicked", self.on_continue_clicked)
        watch_button_box.append(self.continue_button)
        
        controls.append(watch_button_box)
        
        # Download and other buttons
        other_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        other_button_box.set_homogeneous(True)
        
        self.download_button = Gtk.Button(label="⬇ Download")
        self.download_button.connect("clicked", self.on_download_clicked)
        other_button_box.append(self.download_button)
        
        self.browser_button = Gtk.Button(label="🌐 Open in Browser")
        self.browser_button.connect("clicked", self.on_browser_clicked)
        other_button_box.append(self.browser_button)
        
        controls.append(other_button_box)
        
        # Stop/Clear button
        control_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        control_button_box.set_homogeneous(True)
        
        self.stop_button = Gtk.Button(label="⏹ Stop")
        self.stop_button.connect("clicked", self.on_stop_clicked)
        self.stop_button.set_sensitive(False)
        control_button_box.append(self.stop_button)
        
        self.clear_button = Gtk.Button(label="✕ Clear")
        self.clear_button.connect("clicked", self.on_clear_clicked)
        control_button_box.append(self.clear_button)
        
        controls.append(control_button_box)
        
        self.append(controls)
        
        # Check ani-cli status
        if self.ani_cli.is_available():
            version = self.ani_cli.get_version()
            status_text = f"ani-cli available"
            if version:
                status_text += f" ({version})"
            self.status_label.set_text(status_text)
        else:
            self.status_label.set_text("⚠ ani-cli not found. Install: sudo apt install ani-cli")
            self.watch_button.set_sensitive(False)
            self.download_button.set_sensitive(False)
            self.continue_button.set_sensitive(False)
        
        self.set_sensitive(False)
    
    def set_anime(self, anime: dict, video_url: Optional[str] = None):
        """Set the anime to display.
        
        Args:
            anime: Anime data dictionary from AniList
            video_url: Optional video streaming URL (not used with ani-cli)
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
        self.set_sensitive(self.ani_cli.is_available())
        
        # Set max episodes
        if anime.get('episodes'):
            self.episode_spin.set_range(0, anime['episodes'])
    
    def on_watch_clicked(self, button):
        """Handle watch button click."""
        if not self.current_anime:
            return
        
        from .anilist_api import AniListAPI
        api = AniListAPI()
        anime_title = api.get_anime_title(self.current_anime)
        
        quality = self.quality_combo.get_active_id()
        episode = int(self.episode_spin.get_value()) if self.episode_spin.get_value() > 0 else None
        
        # Disable buttons while watching
        self.watch_button.set_sensitive(False)
        self.continue_button.set_sensitive(False)
        self.download_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        self.quality_combo.set_sensitive(False)
        self.episode_spin.set_sensitive(False)
        
        self.status_label.set_text(f"Starting ani-cli for: {anime_title}")
        
        self.ani_cli.watch_anime(
            anime_title,
            episode=episode,
            quality=quality,
            callback=self.on_watch_complete,
            terminal_output_callback=self.on_terminal_output
        )
    
    def on_continue_clicked(self, button):
        """Handle continue watching button click."""
        self.watch_button.set_sensitive(False)
        self.continue_button.set_sensitive(False)
        self.download_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        
        self.status_label.set_text("Continuing from history...")
        
        self.ani_cli.continue_watching(
            callback=self.on_watch_complete,
            terminal_output_callback=self.on_terminal_output
        )
    
    def on_download_clicked(self, button):
        """Handle download button click."""
        if not self.current_anime:
            return
        
        from .anilist_api import AniListAPI
        api = AniListAPI()
        anime_title = api.get_anime_title(self.current_anime)
        
        quality = self.quality_combo.get_active_id()
        episode = int(self.episode_spin.get_value()) if self.episode_spin.get_value() > 0 else None
        
        self.watch_button.set_sensitive(False)
        self.continue_button.set_sensitive(False)
        self.download_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        self.quality_combo.set_sensitive(False)
        self.episode_spin.set_sensitive(False)
        
        self.status_label.set_text(f"Downloading: {anime_title}")
        
        self.ani_cli.download_anime(
            anime_title,
            episode=episode,
            quality=quality,
            callback=self.on_download_complete
        )
    
    def on_browser_clicked(self, button):
        """Handle browser button click."""
        if not self.current_anime:
            return
        
        anime_id = self.current_anime.get('id')
        if anime_id:
            url = f"https://anilist.co/anime/{anime_id}"
            Gio.AppInfo.launch_default_for_uri(url, None)
    
    def on_stop_clicked(self, button):
        """Handle stop button click."""
        self.ani_cli.stop_watching()
        self.status_label.set_text("Stopped")
        self.on_watch_complete(False, None)
    
    def on_clear_clicked(self, button):
        """Handle clear button click."""
        self.ani_cli.stop_watching()
        self.current_anime = None
        self.current_url = None
        self.title_label.set_text("Select an anime to play")
        self.info_label.set_text("")
        self.status_label.set_text("")
        self.set_sensitive(False)
    
    def on_watch_complete(self, success: bool, error_msg: Optional[str]):
        """Callback when watching/continuing completes."""
        self.watch_button.set_sensitive(self.ani_cli.is_available())
        self.continue_button.set_sensitive(self.ani_cli.is_available())
        self.download_button.set_sensitive(self.ani_cli.is_available())
        self.stop_button.set_sensitive(False)
        self.quality_combo.set_sensitive(True)
        self.episode_spin.set_sensitive(True)
        
        if success:
            self.status_label.set_text("Finished watching")
        else:
            if error_msg:
                self.status_label.set_text(f"Error: {error_msg}")
            else:
                self.status_label.set_text("Watching stopped")
    
    def on_download_complete(self, success: bool, message: Optional[str]):
        """Callback when download completes."""
        self.watch_button.set_sensitive(self.ani_cli.is_available())
        self.continue_button.set_sensitive(self.ani_cli.is_available())
        self.download_button.set_sensitive(self.ani_cli.is_available())
        self.stop_button.set_sensitive(False)
        self.quality_combo.set_sensitive(True)
        self.episode_spin.set_sensitive(True)
        
        if success:
            self.status_label.set_text("Download completed!")
        else:
            self.status_label.set_text(f"Download failed: {message}")
    
    def on_terminal_output(self, line: str, stream_type: str):
        """Handle output from ani-cli."""
        # Update status with current output
        if line:
            # Only show last line to avoid clutter
            self.status_label.set_text(f"[{stream_type}] {line[:60]}")
