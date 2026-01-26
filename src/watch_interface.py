# watch_interface.py
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
            title="Search Anime",
            modal=True,
            transient_for=parent
        )
        
        self.anime_name = None
        self.set_default_size(400, 200)
        
        # Main content area
        content = self.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        
        # Instructions
        info = Gtk.Label(label="Enter anime name to search and stream:")
        info.set_wrap(True)
        content.append(info)
        
        # Search entry
        self.entry = Gtk.SearchEntry(
            placeholder_text="e.g., One Piece, Attack on Titan"
        )
        content.append(self.entry)
        
        # Episode info
        episode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        episode_label = Gtk.Label(label="Episode (optional):")
        episode_box.append(episode_label)
        self.episode_spin = Gtk.SpinButton(
            adjustment=Gtk.Adjustment(1, 1, 999, 1),
            digits=0
        )
        episode_box.append(self.episode_spin)
        content.append(episode_box)
        
        # Quality selector
        quality_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        quality_label = Gtk.Label(label="Quality:")
        quality_box.append(quality_label)
        self.quality_combo = Gtk.ComboBoxText()
        self.quality_combo.append("best", "Best")
        self.quality_combo.append("1080", "1080p")
        self.quality_combo.append("720", "720p")
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
            
            # Show clear status
            self.status_label.set_text(f"🎬 Streaming {anime_name}...")
            
            # Play using direct API (no interactive menus)
            def play_callback(success, message):
                # Re-enable button when done
                GLib.idle_add(lambda: button.set_sensitive(True))
                # Update status with result
                GLib.idle_add(lambda: self.status_label.set_text(message))
                
                # Add to history only on successful completion
                if success and "Finished" in message:
                    self.history.add_watch(
                        anime_id=hash(anime_name) % 1000000,
                        anime_title=anime_name,
                        episode=episode,
                        categories=["Streamed"]
                    )
                    GLib.idle_add(self.update_history_display)
            
            self.streamer.play_direct(anime_name, episode, play_callback)
    
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
        """Update the watch history display."""
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
            empty_label = Gtk.Label(label="No watch history")
            empty_label.add_css_class("dim-label")
            self.history_box.append(empty_label)
            return
        
        # Add history items
        for item in items:
            row = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=3,
                margin_top=5,
                margin_bottom=5,
                margin_start=10,
                margin_end=10
            )
            
            # Title
            title = Gtk.Label(
                label=item['anime_title'],
                xalign=0,
                css_classes=["heading"]
            )
            row.append(title)
            
            # Info
            categories = ', '.join(item.get('categories', []))
            info = Gtk.Label(
                label=f"Categories: {categories} | Last: {item.get('last_watched', 'Unknown')[:10]}",
                xalign=0,
                css_classes=["caption"]
            )
            row.append(info)
            
            self.history_box.append(row)
    
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
