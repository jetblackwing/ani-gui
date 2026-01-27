# window.py
#
# Copyright 2024 Amal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Main window with navigatable pages.
"""

from gi.repository import Gtk, GLib
import threading
from .direct_streamer import DirectStreamer
from .ani_cli_wrapper import AniCliWrapper
from .gstreamer_player import GStreamerPlayer
from .watch_history import WatchHistory


class AniGuiWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'AniGuiWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.set_default_size(1600, 900)
        self.set_title("Ani-GUI - Anime Streaming")
        
        self.streamer = DirectStreamer()
        self.wrapper = AniCliWrapper()
        self.history = WatchHistory()
        
        # Stack widget for page navigation
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        # Page 1: Selection + Details (side by side)
        selection_page = self.create_selection_page()
        self.stack.add_named(selection_page, "selection")
        
        # Page 2: Video Player
        self.player = GStreamerPlayer()
        self.player.set_on_close_callback(self.on_player_closed)
        self.stack.add_named(self.player, "player")
        
        self.set_child(self.stack)
        self.stack.set_visible_child_name("selection")
    
    def create_selection_page(self) -> Gtk.Box:
        """Create selection page with left and right panels."""
        page = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        # Left panel: Anime selector
        left_panel = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=15,
            margin_bottom=15,
            margin_start=15,
            margin_end=15
        )
        left_panel.set_size_request(450, -1)
        
        # Search
        left_title = Gtk.Label(label="Search Anime", css_classes=["title-1"])
        left_panel.append(left_title)
        
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.search_entry = Gtk.SearchEntry(placeholder_text="Search anime...")
        self.search_entry.connect("activate", self.on_search_activated)
        search_box.append(self.search_entry)
        
        search_button = Gtk.Button(label="🔍 Search")
        search_button.connect("clicked", self.on_search_clicked)
        search_box.append(search_button)
        left_panel.append(search_box)
        
        # Status
        self.search_status = Gtk.Label(label="Enter anime name or click recommendations", css_classes=["dim-label"])
        left_panel.append(self.search_status)
        
        # Results
        results_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        results_scroll.set_child(self.results_box)
        left_panel.append(results_scroll)
        
        # Recommendations section
        self.recs_label = Gtk.Label(label="📺 Recommended", css_classes=["heading"])
        left_panel.append(self.recs_label)
        
        recs_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.recs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        recs_scroll.set_child(self.recs_box)
        left_panel.append(recs_scroll)
        
        # Load recommendations on init
        self.load_recommendations()
        
        # Right panel: Anime details
        right_panel = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=15,
            margin_bottom=15,
            margin_start=15,
            margin_end=15
        )
        right_panel.set_size_request(450, -1)
        
        # Anime info
        self.anime_title = Gtk.Label(label="Select anime", css_classes=["title-1"])
        right_panel.append(self.anime_title)
        
        # Episodes heading
        self.episodes_heading = Gtk.Label(label="Episodes", css_classes=["heading"])
        right_panel.append(self.episodes_heading)
        
        # Episodes list
        episodes_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.episodes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        episodes_scroll.set_child(self.episodes_box)
        right_panel.append(episodes_scroll)
        
        # Quality selector
        quality_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        quality_label = Gtk.Label(label="Quality:")
        quality_box.append(quality_label)
        
        self.quality_combo = Gtk.ComboBoxText()
        self.quality_combo.append("best", "🎯 Best")
        self.quality_combo.append("1080", "1080p")
        self.quality_combo.append("720", "720p")
        self.quality_combo.set_active_id("best")
        quality_box.append(self.quality_combo)
        right_panel.append(quality_box)
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        
        # Combine panels
        page.append(left_panel)
        page.append(separator)
        page.append(right_panel)
        
        # Store for later
        self.right_panel = right_panel
        self.current_anime = None
        
        return page
    
    def on_search_activated(self, entry):
        """Search when Enter is pressed."""
        self.on_search_clicked(None)
    
    def on_search_clicked(self, button):
        """Handle search."""
        query = self.search_entry.get_text().strip()
        if not query:
            self.search_status.set_text("❌ Enter anime name")
            return
        
        self.search_status.set_text("🔍 Searching...")
        
        def search_thread():
            results = self.streamer.search_anime(query)
            GLib.idle_add(self.display_results, results)
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
    
    def display_results(self, results):
        """Display search results."""
        # Clear
        while (child := self.results_box.get_first_child()):
            self.results_box.remove(child)
        
        if not results:
            self.search_status.set_text("❌ No results")
            return
        
        self.search_status.set_text(f"✅ Found {len(results)}")
        
        # Show results
        for anime in results:
            btn = Gtk.Button(label=f"{anime['name']}\n{anime['episodes']} eps")
            btn.set_hexpand(True)
            btn.connect("clicked", lambda b, a=anime: self.on_anime_selected(a))
            self.results_box.append(btn)
    
    def on_anime_selected(self, anime: dict):
        """Selected an anime - show details and episodes."""
        self.current_anime = anime
        self.anime_title.set_text(f"▶️ {anime['name']}")
        
        # Clear episodes
        while (child := self.episodes_box.get_first_child()):
            self.episodes_box.remove(child)
        
        # Show loading
        loading = Gtk.Label(label="Loading episodes...")
        loading.add_css_class("dim-label")
        self.episodes_box.append(loading)
        
        # Fetch episodes
        def fetch_thread():
            episodes = self.streamer.get_episodes(anime['id'])
            GLib.idle_add(self.display_episodes, episodes)
        
        thread = threading.Thread(target=fetch_thread, daemon=True)
        thread.start()
    
    def display_episodes(self, episodes):
        """Display available episodes."""
        # Clear
        while (child := self.episodes_box.get_first_child()):
            self.episodes_box.remove(child)
        
        if not episodes:
            error = Gtk.Label(label="❌ No episodes found")
            error.add_css_class("dim-label")
            self.episodes_box.append(error)
            return
        
        # Show episodes
        for ep in episodes[:30]:  # Show first 30
            btn = Gtk.Button(label=f"Episode {ep}")
            btn.set_hexpand(True)
            btn.connect("clicked", lambda b, e=ep: self.on_episode_selected(e))
            self.episodes_box.append(btn)
    
    def on_episode_selected(self, episode: str):
        """Play selected episode."""
        if not self.current_anime:
            return
        
        # Go to player page
        self.stack.set_visible_child_name("player")
        
        # Fetch and play
        anime = self.current_anime
        
        def play_thread():
            try:
                link = self.streamer.get_episode_links(anime['id'], episode)
                if not link:
                    GLib.idle_add(lambda: self.player.title_label.set_text(
                        f"❌ Episode {episode} unavailable"
                    ))
                    return
                
                # Play video
                GLib.idle_add(
                    lambda: self.player.play(link, f"{anime['name']} - EP {episode}")
                )
                
                # Add to history
                self.history.add_watch(
                    anime_id=hash(anime['id']) % 1000000,
                    anime_title=anime['name'],
                    episode=episode,
                    categories=["Streamed"]
                )
            except Exception as e:
                GLib.idle_add(lambda: self.player.title_label.set_text(f"❌ Error: {str(e)}"))
                print(f"[Window] Play error: {e}")
        
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()
    
    def on_player_closed(self):
        """Return to selection when player closes."""
        self.stack.set_visible_child_name("selection")
    
    def load_recommendations(self):
        """Load anime recommendations."""
        recs = self.wrapper.get_recommendations()
        
        # Clear
        while (child := self.recs_box.get_first_child()):
            self.recs_box.remove(child)
        
        # Show recommendations
        for anime in recs:
            btn = Gtk.Button(label=f"🎬 {anime['name']}\n{anime['episodes']} eps")
            btn.set_hexpand(True)
            btn.connect("clicked", lambda b, a=anime: self.on_anime_selected(a))
            self.recs_box.append(btn)
