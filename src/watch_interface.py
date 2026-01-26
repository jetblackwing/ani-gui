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
from typing import List, Optional, Callable
from .ani_cli_integration import AniCliIntegration
from .watch_history import WatchHistory
from .anilist_api import AniListAPI


class SearchResultsDialog(Gtk.Dialog):
    """Dialog showing search results from ani-cli."""
    
    def __init__(self, results: List[str], parent=None):
        super().__init__(
            title="Select Anime",
            modal=True,
            transient_for=parent
        )
        
        self.selected = None
        self.set_default_size(400, 500)
        
        # Main content area
        content = self.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        
        # Instructions
        info = Gtk.Label(label="Found anime. Click to select:")
        info.set_wrap(True)
        content.append(info)
        
        # Scrolled list of results
        scrolled = Gtk.ScrolledWindow(
            hexpand=True,
            vexpand=True
        )
        
        results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        for result in results:
            button = Gtk.Button(label=result)
            button.connect("clicked", self.on_result_selected, result)
            results_box.append(button)
        
        scrolled.set_child(results_box)
        content.append(scrolled)
        
        # Action buttons
        self.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Watch", Gtk.ResponseType.OK
        )
        self.set_default_response(Gtk.ResponseType.OK)
    
    def on_result_selected(self, button, result):
        """Handle result selection."""
        self.selected = result
        self.response(Gtk.ResponseType.OK)


class WatchInterfaceWidget(Gtk.Box):
    """Complete watch interface with search, history, and player controls."""
    
    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10
        )
        
        self.ani_cli = AniCliIntegration()
        self.history = WatchHistory()
        self.api = AniListAPI()
        self.current_anime = None
        
        # Title
        title = Gtk.Label(
            label="Watch Anime with ani-cli",
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
        """Handle search button click."""
        query = self.search_entry.get_text()
        if not query:
            self.status_label.set_text("Please enter a search term")
            return
        
        self.status_label.set_text(f"Searching for '{query}'...")
        
        # Search using ani-cli
        self.ani_cli.search_anime_interactive(query, self.on_search_complete)
    
    def on_search_complete(self, results: Optional[List[str]], error: Optional[str]):
        """Callback when search completes."""
        if error:
            self.status_label.set_text(f"Error: {error}")
            return
        
        if not results:
            self.status_label.set_text("No results found")
            return
        
        # Show results dialog
        dialog = SearchResultsDialog(results, parent=self.get_root())
        response = dialog.run()
        selected = dialog.selected
        dialog.close()
        
        if selected and response == Gtk.ResponseType.OK:
            self.status_label.set_text(f"Selected: {selected}")
            self.current_anime = selected
            
            # Here you would start watching with ani-cli
            # For now just add to history
            if selected:
                self.history.add_watch(
                    anime_id=hash(selected) % 1000000,
                    anime_title=selected,
                    categories=["User Selection"]
                )
                self.update_history_display()
    
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
