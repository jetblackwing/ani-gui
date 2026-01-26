# search_handler.py
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

import threading
from typing import Callable, List, Optional
from gi.repository import GLib, Gtk, GdkPixbuf

from .anilist_api import AniListAPI
from .thumbnail_cache import ThumbnailCache


class SearchHandler:
    """Handles anime search with async operations."""
    
    def __init__(self):
        self.api = AniListAPI()
        self.cache = ThumbnailCache()
        self.current_results: List[dict] = []
        self.is_searching = False
    
    def search_anime(self, query: str, callback: Callable, page: int = 1):
        """Search for anime asynchronously.
        
        Args:
            query: Search query string
            callback: Function to call with (results, has_next_page)
            page: Page number
        """
        if self.is_searching:
            return
        
        self.is_searching = True
        
        def search_thread():
            try:
                data = self.api.search_anime(query, page=page, per_page=12)
                if data:
                    results = self.api.extract_anime_from_search(data)
                    self.current_results = results
                    
                    has_next = data.get('Page', {}).get('pageInfo', {}).get('hasNextPage', False)
                    
                    # Call callback on main thread
                    GLib.idle_add(callback, results, has_next)
                else:
                    GLib.idle_add(callback, [], False)
            finally:
                self.is_searching = False
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
    
    def load_thumbnail(self, url: Optional[str], width: int = 220, height: int = 330, 
                      callback: Optional[Callable] = None) -> Optional[GdkPixbuf.Pixbuf]:
        """Load thumbnail from cache or download.
        
        Args:
            url: Thumbnail URL
            width: Desired width in pixels
            height: Desired height in pixels
            callback: Optional callback function (pixbuf, url)
            
        Returns:
            GdkPixbuf.Pixbuf or None
        """
        if not url:
            return None
        
        if callback:
            self.cache.get_thumbnail_async(url, width, height, callback)
        else:
            # Synchronous (blocking) load
            pixbuf = self.cache.get_cached_pixbuf(url, width, height)
            if not pixbuf:
                pixbuf = self.cache.download_and_cache_pixbuf(url, width, height)
            return pixbuf


class AnimeSearchRow(Gtk.Box):
    """A single anime result row with thumbnail and info."""
    
    def __init__(self, anime: dict, search_handler: SearchHandler, on_selected: Callable):
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=15,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10
        )
        
        self.anime = anime
        self.search_handler = search_handler
        self.on_selected = on_selected
        
        from .anilist_api import AniListAPI
        api = AniListAPI()
        
        # Thumbnail
        self.thumbnail = Gtk.Image(
            pixel_size=200,
            css_classes=["card"]
        )
        thumbnail_url = api.get_anime_cover_url(anime)
        if thumbnail_url:
            search_handler.load_thumbnail(
                thumbnail_url,
                width=150,
                height=225,
                callback=self.on_thumbnail_loaded
            )
        self.append(self.thumbnail)
        
        # Info box
        info_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            hexpand=True
        )
        
        # Title
        title = api.get_anime_title(anime)
        title_label = Gtk.Label(
            label=title,
            css_classes=["heading"],
            wrap=True,
            xalign=0
        )
        info_box.append(title_label)
        
        # Description
        description = anime.get('description', '')
        if description:
            # Strip HTML tags
            import html
            description = html.unescape(description)
            description = description.replace('<br>', '\n').replace('<i>', '').replace('</i>', '')
            
            # Truncate to 3 lines
            lines = description.split('\n')[:3]
            description = '\n'.join(lines)
            
            desc_label = Gtk.Label(
                label=description,
                wrap=True,
                xalign=0,
                css_classes=["caption"]
            )
            info_box.append(desc_label)
        
        # Metadata row
        meta_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        
        if anime.get('episodes'):
            ep_label = Gtk.Label(label=f"Episodes: {anime['episodes']}")
            meta_box.append(ep_label)
        
        if anime.get('averageScore'):
            score_label = Gtk.Label(label=f"Rating: {anime['averageScore']}/100")
            meta_box.append(score_label)
        
        if anime.get('status'):
            status_label = Gtk.Label(label=f"Status: {anime['status']}")
            meta_box.append(status_label)
        
        info_box.append(meta_box)
        
        self.append(info_box)
        
        # Make clickable
        gesture = Gtk.GestureClick.new()
        gesture.connect("pressed", self.on_click)
        self.add_controller(gesture)
    
    def on_thumbnail_loaded(self, pixbuf: Optional[GdkPixbuf.Pixbuf], url: str):
        """Callback when thumbnail is loaded."""
        if pixbuf:
            self.thumbnail.set_from_pixbuf(pixbuf)
    
    def on_click(self, gesture, n_press, x, y):
        """Handle click on anime row."""
        self.on_selected(self.anime)
