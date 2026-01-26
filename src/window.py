# window.py
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
from .search_handler import SearchHandler, AnimeSearchRow
from .video_player import VideoPlayerWidget
from .watch_interface import WatchInterfaceWidget


class AniGuiWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'AniGuiWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.set_default_size(1400, 800)
        self.set_title("Ani-GUI - Anime Streaming Player")
        
        self.search_handler = SearchHandler()
        self.current_page = 1
        self.has_next_page = False
        
        # Main container with tabs
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Create notebook (tabbed interface)
        self.notebook = Gtk.Notebook()
        
        # Tab 1: Search and Browse
        search_tab = self._create_search_tab()
        self.notebook.append_page(search_tab, Gtk.Label(label="🔍 Search & Browse"))
        
        # Tab 2: Watch Interface (ani-cli with search results)
        watch_tab = WatchInterfaceWidget()
        self.notebook.append_page(watch_tab, Gtk.Label(label="▶ Watch & History"))
        
        main_box.append(self.notebook)
        
        self.set_child(main_box)
        
        # Search on initial load (in first tab)
        self._trigger_search("Jujutsu Kaisen")
    
    def _create_search_tab(self) -> Gtk.Box:
        """Create the search and browse tab."""
        tab_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header with search
        header_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10
        )
        
        # Search bar
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.search_entry = Gtk.SearchEntry(
            hexpand=True,
            placeholder_text="Search anime by title...",
            css_classes=["search"]
        )
        self.search_entry.connect("search-changed", self.on_search_changed)
        search_box.append(self.search_entry)
        
        header_box.append(search_box)
        tab_box.append(header_box)
        
        # Content area with paned layout
        paned = Gtk.Paned(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            vexpand=True,
            wide_handle=True
        )
        
        # Left side: Search results
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Results scrolled window
        scrolled = Gtk.ScrolledWindow(
            hexpand=True,
            vexpand=True
        )
        
        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scrolled.set_child(self.results_box)
        left_box.append(scrolled)
        
        # Pagination buttons
        pagination_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=5,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10
        )
        pagination_box.set_homogeneous(True)
        
        self.prev_button = Gtk.Button(label="← Previous")
        self.prev_button.connect("clicked", self.on_prev_page)
        self.prev_button.set_sensitive(False)
        pagination_box.append(self.prev_button)
        
        self.next_button = Gtk.Button(label="Next →")
        self.next_button.connect("clicked", self.on_next_page)
        self.next_button.set_sensitive(False)
        pagination_box.append(self.next_button)
        
        left_box.append(pagination_box)
        
        paned.set_start_child(left_box)
        paned.set_resize_start_child(True)
        
        # Right side: Video player and details
        self.video_player = VideoPlayerWidget()
        paned.set_end_child(self.video_player)
        paned.set_resize_end_child(True)
        paned.set_position(700)
        
        tab_box.append(paned)
        return tab_box
    
    def on_search_changed(self, entry):
        """Handle search entry changes."""
        query = entry.get_text()
        if query:
            self.current_page = 1
            self._trigger_search(query)
    
    def _trigger_search(self, query: str):
        """Trigger anime search."""
        # Clear previous results
        while True:
            child = self.results_box.get_first_child()
            if not child:
                break
            self.results_box.remove(child)
        
        # Show loading indicator
        loading_label = Gtk.Label(label="Searching...")
        loading_label.add_css_class("dim-label")
        self.results_box.append(loading_label)
        
        self.search_handler.search_anime(
            query,
            self.on_search_results,
            page=self.current_page
        )
    
    def on_search_results(self, results: list, has_next_page: bool):
        """Handle search results."""
        self.has_next_page = has_next_page
        
        # Clear loading indicator
        while True:
            child = self.results_box.get_first_child()
            if not child:
                break
            self.results_box.remove(child)
        
        if not results:
            empty_label = Gtk.Label(label="No results found")
            empty_label.add_css_class("dim-label")
            self.results_box.append(empty_label)
        else:
            for anime in results:
                row = AnimeSearchRow(
                    anime,
                    self.search_handler,
                    self.on_anime_selected
                )
                self.results_box.append(row)
        
        # Update pagination buttons
        self.prev_button.set_sensitive(self.current_page > 1)
        self.next_button.set_sensitive(has_next_page)
    
    def on_anime_selected(self, anime: dict):
        """Handle anime selection from search results."""
        self.video_player.set_anime(anime)
    
    def on_prev_page(self, button):
        """Handle previous page button."""
        if self.current_page > 1:
            self.current_page -= 1
            query = self.search_entry.get_text()
            if query:
                self._trigger_search(query)
    
    def on_next_page(self, button):
        """Handle next page button."""
        if self.has_next_page:
            self.current_page += 1
            query = self.search_entry.get_text()
            if query:
                self._trigger_search(query)
