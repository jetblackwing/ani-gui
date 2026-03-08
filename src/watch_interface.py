# watch_interface.py
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

from gi.repository import Gtk, GLib
from typing import List, Optional, Callable, Dict
import threading
from .direct_streamer import DirectStreamer
from .watch_history import WatchHistory
from .video_player import VideoPlayerWidget


class SearchResultsDialog(Gtk.Dialog):
    """Dialog for entering anime search query."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Stream Anime",
            modal=True,
            transient_for=parent
        )
        
        self.anime_name = None
        self.set_default_size(500, 280)
        
        # Main content area
        content = self.get_content_area()
        content.set_spacing(15)
        content.set_margin_top(15)
        content.set_margin_bottom(15)
        content.set_margin_start(15)
        content.set_margin_end(15)
        
        # Instructions
        info = Gtk.Label(
            label="<b>Search and Stream Anime</b>",
            use_markup=True,
            css_classes=["heading"]
        )
        content.append(info)
        
        # Search entry
        search_label = Gtk.Label(label="Anime Name:", xalign=0)
        content.append(search_label)
        self.entry = Gtk.SearchEntry(
            placeholder_text="e.g., Naruto, One Piece, Attack on Titan"
        )
        content.append(self.entry)
        
        # Episode info
        episode_label = Gtk.Label(label="Episode Number:", xalign=0)
        content.append(episode_label)
        episode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.episode_spin = Gtk.SpinButton(
            adjustment=Gtk.Adjustment(1, 1, 9999, 1),
            digits=0,
            width_chars=10
        )
        self.episode_spin.set_hexpand(False)
        episode_box.append(self.episode_spin)
        episode_info = Gtk.Label(
            label="(Leave at 1 for first episode)",
            css_classes=["dim-label"]
        )
        episode_box.append(episode_info)
        content.append(episode_box)
        
        # Quality selector
        quality_label = Gtk.Label(label="Video Quality:", xalign=0)
        content.append(quality_label)
        quality_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.quality_combo = Gtk.ComboBoxText()
        self.quality_combo.append("best", "🎯 Best Available (Auto)")
        self.quality_combo.append("1080", "1080p (Highest)")
        self.quality_combo.append("720", "720p (Standard)")
        self.quality_combo.append("480", "480p (Low)")
        self.quality_combo.set_active_id("best")
        quality_box.append(self.quality_combo)
        content.append(quality_box)
        
        # Action buttons
        self.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Stream", Gtk.ResponseType.OK
        )
        self.set_default_response(Gtk.ResponseType.OK)
    
    def get_anime_name(self) -> str:
        return self.entry.get_text()
    
    def get_episode(self) -> int:
        return int(self.episode_spin.get_value())
    
    def get_quality(self) -> str:
        return self.quality_combo.get_active_id()


class WatchInterfaceWidget(Gtk.Box):
    """Complete watch interface with search, history, and streaming."""
    
    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10
        )
        
        self.streamer = DirectStreamer()
        self.history = WatchHistory()
        self.current_anime = None
        self.current_show_id = None
        self.streaming_links = {}
        
        # Create video player (hidden by default)
        self.video_player = VideoPlayerWidget()
        self.video_player.set_on_close_callback(self.on_video_player_closed)
        self.video_player.set_visible(False)
        
        # Title
        title = Gtk.Label(
            label="Watch Anime (Direct Streaming)",
            css_classes=["title-1"]
        )
        self.append(title)
        
        # Search section
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        search_label = Gtk.Label(label="Search:")
        search_box.append(search_label)
        
        self.search_entry = Gtk.SearchEntry(
            placeholder_text="Enter anime name...",
            hexpand=True
        )
        search_box.append(self.search_entry)
        
        search_button = Gtk.Button(label="🔍 Search")
        search_button.connect("clicked", self.on_search_clicked)
        search_box.append(search_button)
        
        self.append(search_box)
        
        # Add video player (initially hidden, shows when streaming)
        self.append(self.video_player)
        
        # Category filter
        category_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        category_label = Gtk.Label(label="History by Category:")
        category_box.append(category_label)
        
        self.category_combo = Gtk.ComboBoxText()
        self.category_combo.append("all", "All")
        self.category_combo.set_active_id("all")
        self.category_combo.connect("changed", self.on_category_changed)
        category_box.append(self.category_combo)
        
        self.append(category_box)
        
        # Watch history section
        history_label = Gtk.Label(
            label="Watch History",
            css_classes=["heading"]
        )
        self.append(history_label)
        
        # History scrolled window
        history_scrolled = Gtk.ScrolledWindow(
            hexpand=True,
            vexpand=True
        )
        
        self.history_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=5
        )
        history_scrolled.set_child(self.history_box)
        self.append(history_scrolled)
        
        # Control buttons
        controls = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=5
        )
        controls.set_homogeneous(True)
        
        clear_button = Gtk.Button(label="Clear History")
        clear_button.connect("clicked", self.on_clear_history)
        controls.append(clear_button)
        
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", self.on_refresh)
        controls.append(refresh_button)
        
        self.append(controls)
        
        # Status bar
        self.status_label = Gtk.Label(
            label="Ready",
            css_classes=["dim-label"]
        )
        self.append(self.status_label)
        
        self.update_history_display()
        self.update_categories()
    
    def on_search_clicked(self, button):
        """Handle search button click - shows dialog for anime name."""
        dialog = SearchResultsDialog(parent=self.get_root())
        response = dialog.run()
        anime_name = dialog.get_anime_name()
        episode = str(dialog.get_episode()) if dialog.episode_spin.get_value() > 0 else "1"
        dialog.close()
        
        if response == Gtk.ResponseType.OK and anime_name:
            self.current_anime = anime_name
            button.set_sensitive(False)
            
            # Show clear status (player will show when ready)
            self.status_label.set_text(f"🎬 Searching: {anime_name}...")
            
            # Play using direct API with embedded video player
            def play_callback(success, message):
                # Update status with result
                GLib.idle_add(lambda: self.status_label.set_text(message))
                
                # Show video player only when successfully loaded
                if success and "Playing" in message:
                    GLib.idle_add(lambda: self.video_player.set_visible(True))
                
                # Re-enable button when done or failed
                if not success or "Finished" in message or "Error" in message or "not found" in message:
                    GLib.idle_add(lambda: button.set_sensitive(True))
                
                # Add to history only on successful completion
                if success and "Finished" in message:
                    self.history.add_watch(
                        anime_id=hash(anime_name) % 1000000,
                        anime_title=anime_name,
                        episode=episode,
                        categories=["Streamed"]
                    )
                    GLib.idle_add(self.update_history_display)
            
            self.streamer.play_direct(anime_name, episode, play_callback, self.video_player)
    
    def on_video_player_closed(self):
        """Called when video player is closed."""
        self.video_player.set_visible(False)
    
    def on_category_changed(self, combo):
        """Handle category filter change."""
        self.update_history_display()
    
    def on_clear_history(self, button):
        """Clear watch history."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear watch history?"
        )
        
        response = dialog.run()
        dialog.close()
        
        if response == Gtk.ResponseType.YES:
            self.history.clear_history()
            self.update_history_display()
            self.status_label.set_text("History cleared")
    
    def on_refresh(self, button):
        """Refresh history display."""
        self.update_history_display()
        self.update_categories()
        self.status_label.set_text("Refreshed")
    
    def update_history_display(self):
        """Update the watch history display with better formatting."""
        # Clear current display
        while True:
            child = self.history_box.get_first_child()
            if not child:
                break
            self.history_box.remove(child)
        
        # Get filtered history
        category = self.category_combo.get_active_id()
        if category == "all":
            items = self.history.get_all_history()
        else:
            items = self.history.get_by_category(category)
        
        if not items:
            empty_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=5,
                halign=Gtk.Align.CENTER,
                valign=Gtk.Align.CENTER,
                hexpand=True,
                vexpand=True
            )
            empty_label = Gtk.Label(
                label="📭 No watch history",
                css_classes=["title-3"]
            )
            empty_box.append(empty_label)
            empty_hint = Gtk.Label(
                label="Search for an anime and stream to start!",
                css_classes=["dim-label"]
            )
            empty_box.append(empty_hint)
            self.history_box.append(empty_box)
            return
        
        # Add history items with improved styling
        for i, item in enumerate(items):
            # Create expandable row
            row_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=0,
                css_classes=["history-item"]
            )
            row_box.set_margin_top(8)
            row_box.set_margin_bottom(8)
            row_box.set_margin_start(10)
            row_box.set_margin_end(10)
            
            # Header with title and episode
            header = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=15
            )
            
            # Anime title (bold)
            title = Gtk.Label(
                label=f"▶️ {item['anime_title']}",
                xalign=0
            )
            title.set_markup(f"<b>▶️ {item['anime_title']}</b>")
            title.set_hexpand(True)
            header.append(title)
            
            # Episode info
            episode_text = f"EP {item['episode']}"
            episode = Gtk.Label(
                label=episode_text,
                css_classes=["dim-label"]
            )
            header.append(episode)
            
            row_box.append(header)
            
            # Details (subtitle)
            if item.get('categories'):
                categories = ', '.join(item['categories'])
                details = Gtk.Label(
                    label=f"  {categories}",
                    xalign=0,
                    css_classes=["dim-label"]
                )
                row_box.append(details)
            
            # Timestamp
            if item.get('timestamp'):
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(item['timestamp'])
                    time_text = dt.strftime("Last watched: %b %d at %H:%M")
                except:
                    time_text = item['timestamp']
                
                time_label = Gtk.Label(
                    label=f"  {time_text}",
                    xalign=0,
                    css_classes=["dim-label", "small"]
                )
                row_box.append(time_label)
            
            # Add separator
            if i < len(items) - 1:
                separator = Gtk.Separator()
                row_box.append(separator)
            
            self.history_box.append(row_box)
    
    def update_categories(self):
        """Update category filter options."""
        # Keep "All" and add all categories
        categories = self.history.get_categories()
        
        # Clear and rebuild (keep "all" option)
        model = self.category_combo.get_model()
        if model:
            model.clear()
        
        self.category_combo.append("all", "All")
        for cat in categories:
            self.category_combo.append(cat, cat)
        
        self.category_combo.set_active_id("all")

