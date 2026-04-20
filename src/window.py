# window.py
#
# Copyright 2024 Amal J Krishnan <amaljk80@gmail.com> (@jetblackwing)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Main window with navigatable pages.
"""

from gi.repository import Gtk, GLib, Gio
import threading
from .ani_cli_direct import AniCliDirect
from .gstreamer_player import GStreamerPlayer
from .watch_history import WatchHistory


class AniGuiWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'AniGuiWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(1600, 900)
        self.set_title("Ani-GUI - Anime Streaming")
        self.add_css_class("ani-window")
        self._load_css()

        # Create header bar
        self._create_header_bar()

        # Add window actions
        self.create_action('show-help', self.on_help_clicked, ['F1'])
        self.create_action('focus-search', self.on_focus_search, ['<Primary>f'])

        # Set up help overlay
        builder = Gtk.Builder()
        builder.add_from_file("/home/user/ani-gui/src/gtk/help-overlay.ui")
        help_overlay = builder.get_object("help_overlay")
        self.set_help_overlay(help_overlay)

        self.streamer = AniCliDirect()
        self.history = WatchHistory()

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Stack widget for page navigation
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)

        # Page 1: Selection + Details (side by side)
        selection_page = self.create_selection_page()
        self.stack.add_named(selection_page, "selection")

        # Page 2: Video Player
        self.player = GStreamerPlayer()
        self.player.set_on_close_callback(self.on_player_closed)
        self.stack.add_named(self.player, "player")

        main_box.append(self.stack)
        self.set_child(main_box)
        self.stack.set_visible_child_name("selection")

    def _load_css(self):
        """Load app-level CSS styling."""
        css = """
        window.ani-window {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        headerbar.header-bar {
            background: rgba(255, 255, 255, 0.95);
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            padding: 8px 16px;
        }

        headerbar.header-bar .title {
            color: #2d3748;
            font-weight: bold;
            font-size: 1.2em;
        }

        .page-shell {
            padding: 24px;
            border-spacing: 20px;
            background: rgba(255, 255, 255, 0.05);
        }

        .pane-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            border: 1px solid rgba(0, 0, 0, 0.08);
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            backdrop-filter: blur(10px);
        }

        .app-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 8px;
        }

        .search-header {
            margin-bottom: 16px;
        }

        .search-icon {
            color: #667eea;
            opacity: 0.8;
        }

        .star-icon {
            color: #fbbf24;
        }

        .title-1 {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2d3748;
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #4a5568;
            margin-top: 8px;
            margin-bottom: 4px;
        }

        .muted {
            color: rgba(74, 85, 104, 0.8);
            font-size: 0.95rem;
        }

        .dim-label {
            color: rgba(74, 85, 104, 0.7);
            font-size: 0.9rem;
        }

        .heading {
            font-size: 1.1rem;
            font-weight: 600;
            color: #4a5568;
        }

        entry {
            border-radius: 12px;
            padding: 10px 12px;
            border: 2px solid rgba(0, 0, 0, 0.1);
            background: rgba(255, 255, 255, 0.9);
            transition: all 0.2s ease;
        }

        entry:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        button.search-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            border-radius: 12px;
            font-weight: 600;
            padding: 10px 20px;
            border: none;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        button.search-button:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }

        button.list-item {
            border-radius: 12px;
            border: 1px solid rgba(0, 0, 0, 0.08);
            background: rgba(255, 255, 255, 0.8);
            padding: 12px 16px;
            margin: 2px 0;
            transition: all 0.2s ease;
            text-align: left;
        }

        button.list-item:hover {
            background: rgba(102, 126, 234, 0.1);
            border-color: rgba(102, 126, 234, 0.3);
            transform: translateX(2px);
        }

        /* Scrollbar styling */
        scrollbar {
            background: rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        scrollbar slider {
            background: rgba(102, 126, 234, 0.6);
            border-radius: 8px;
        }

        scrollbar slider:hover {
            background: rgba(102, 126, 234, 0.8);
        }

        .player-title-bar {
            background: rgba(0, 0, 0, 0.8);
            border-radius: 8px;
            padding: 8px 12px;
            margin: 8px;
        }

        .player-title-bar .heading {
            color: #ffffff;
            font-weight: bold;
        }

        .player-controls {
            background: rgba(0, 0, 0, 0.8);
            border-radius: 8px;
            padding: 8px 12px;
            margin: 8px;
            justify-content: center;
        }

        .player-controls button {
            margin: 0 4px;
        }
        """

        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _create_header_bar(self):
        """Create and set up the header bar with menus."""
        header_bar = Gtk.HeaderBar()
        header_bar.add_css_class("header-bar")

        # Application menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.add_css_class("flat")

        # Create menu model
        menu = Gio.Menu()
        menu.append("About", "app.about")
        menu.append("Help", "win.show-help")
        menu.append("Quit", "app.quit")

        menu_button.set_menu_model(menu)
        header_bar.pack_end(menu_button)

        # Help button
        help_button = Gtk.Button()
        help_button.set_icon_name("help-browser-symbolic")
        help_button.set_tooltip_text("Help")
        help_button.add_css_class("flat")
        help_button.connect("clicked", self.on_help_clicked)
        header_bar.pack_end(help_button)

        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span font-weight='bold' font-size='large'>Ani-GUI</span>")
        title_label.add_css_class("title")
        header_bar.set_title_widget(title_label)

        self.set_titlebar(header_bar)

    def on_help_clicked(self, button):
        """Show help dialog."""
        help_dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Ani-GUI Help",
            secondary_text="Ani-GUI is a graphical interface for streaming anime using ani-cli.\n\n"
                          "• Search for anime by title in the search box\n"
                          "• Browse recommendations on the left\n"
                          "• Select an anime to view episodes\n"
                          "• Choose your preferred quality\n"
                          "• Click an episode to start streaming\n\n"
                          "Use Ctrl+Q to quit the application."
        )
        help_dialog.connect("response", lambda d, r: d.destroy())
        help_dialog.present()

    def on_focus_search(self, action, param):
        """Focus the search entry."""
        if hasattr(self, 'search_entry'):
            self.search_entry.grab_focus()

    def create_action(self, name, callback, shortcuts=None):
        """Add a window action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.get_application().set_accels_for_action(f"win.{name}", shortcuts)

    def create_selection_page(self) -> Gtk.Box:
        """Create selection page with left and right panels."""
        page = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        page.add_css_class("page-shell")

        # Left panel: Anime selector
        left_panel = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            hexpand=True
        )
        left_panel.add_css_class("pane-card")
        left_panel.set_size_request(450, -1)

        # Search
        search_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        search_header.add_css_class("search-header")

        search_icon = Gtk.Image()
        search_icon.set_from_icon_name("system-search-symbolic")
        search_icon.add_css_class("search-icon")
        search_header.append(search_icon)

        left_title = Gtk.Label(label="Discover Anime")
        left_title.set_halign(Gtk.Align.START)
        left_title.add_css_class("app-title")
        search_header.append(left_title)

        left_panel.append(search_header)

        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.search_entry = Gtk.SearchEntry(placeholder_text="Search by title...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("activate", self.on_search_activated)
        search_box.append(self.search_entry)

        search_button = Gtk.Button()
        search_button.add_css_class("search-button")

        search_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_icon = Gtk.Image()
        search_icon.set_from_icon_name("system-search-symbolic")
        search_btn_box.append(search_icon)
        search_btn_box.append(Gtk.Label(label="Search"))

        search_button.set_child(search_btn_box)
        search_button.connect("clicked", self.on_search_clicked)
        search_box.append(search_button)
        left_panel.append(search_box)

        # Status
        self.search_status = Gtk.Label(label="Search by title or pick from recommendations")
        self.search_status.set_halign(Gtk.Align.START)
        self.search_status.add_css_class("muted")
        left_panel.append(self.search_status)

        # Results section
        results_title = Gtk.Label(label="Search Results")
        results_title.set_halign(Gtk.Align.START)
        results_title.add_css_class("section-title")
        left_panel.append(results_title)

        results_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        results_scroll.set_child(self.results_box)
        left_panel.append(results_scroll)

        # Recommendations section
        self.recs_label = Gtk.Label(label="Recommended For You")
        self.recs_label.set_halign(Gtk.Align.START)
        self.recs_label.add_css_class("section-title")
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
            hexpand=True
        )
        right_panel.add_css_class("pane-card")
        right_panel.set_size_request(450, -1)

        # Anime info
        self.anime_title = Gtk.Label(label="Select An Anime")
        self.anime_title.set_halign(Gtk.Align.START)
        self.anime_title.add_css_class("app-title")
        right_panel.append(self.anime_title)

        # Episodes heading
        self.episodes_heading = Gtk.Label(label="Episodes")
        self.episodes_heading.set_halign(Gtk.Align.START)
        self.episodes_heading.add_css_class("section-title")
        right_panel.append(self.episodes_heading)

        # Episodes list
        episodes_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.episodes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        episodes_scroll.set_child(self.episodes_box)
        right_panel.append(episodes_scroll)

        # Quality selector
        quality_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        quality_label = Gtk.Label(label="Playback Quality")
        quality_label.set_halign(Gtk.Align.START)
        quality_label.add_css_class("section-title")
        quality_box.append(quality_label)

        self.quality_combo = Gtk.ComboBoxText()
        self.quality_combo.append("best", "🎯 Best")
        self.quality_combo.append("1080", "1080p")
        self.quality_combo.append("720", "720p")
        self.quality_combo.set_active_id("best")
        quality_box.append(self.quality_combo)
        right_panel.append(quality_box)

        # Combine panels
        page.append(left_panel)
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
            self.search_status.set_text("Enter an anime title to search.")
            return

        self.search_status.set_text("Searching...")
        
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
            self.search_status.set_text("No results found.")
            return

        self.search_status.set_text(f"Found {len(results)} result(s).")
        
        # Show results
        for anime in results:
            result_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            anime_icon = Gtk.Image()
            anime_icon.set_from_icon_name("video-display-symbolic")
            anime_icon.set_pixel_size(16)
            result_box.append(anime_icon)
            
            title_label = Gtk.Label(label=anime['name'])
            title_label.set_halign(Gtk.Align.START)
            title_label.set_hexpand(True)
            result_box.append(title_label)
            
            episodes_label = Gtk.Label(label=f"{anime.get('episodes', '?')} eps")
            episodes_label.add_css_class("dim-label")
            result_box.append(episodes_label)
            
            btn = Gtk.Button()
            btn.set_child(result_box)
            btn.add_css_class("list-item")
            btn.set_hexpand(True)
            btn.connect("clicked", lambda b, a=anime: self.on_anime_selected(a))
            self.results_box.append(btn)
    
    def on_anime_selected(self, anime: dict):
        """Selected an anime - show details and episodes."""
        self.current_anime = anime
        self.anime_title.set_text(anime['name'])
        
        # Clear episodes
        while (child := self.episodes_box.get_first_child()):
            self.episodes_box.remove(child)
        
        # Show loading
        loading = Gtk.Label(label="Loading episodes...")
        loading.add_css_class("dim-label")
        self.episodes_box.append(loading)
        
        # Fetch episodes
        def fetch_thread():
            episodes = self.streamer.get_episodes(anime['_id'])
            GLib.idle_add(self.display_episodes, episodes)
        
        thread = threading.Thread(target=fetch_thread, daemon=True)
        thread.start()
    
    def display_episodes(self, episodes):
        """Display available episodes."""
        # Clear
        while (child := self.episodes_box.get_first_child()):
            self.episodes_box.remove(child)
        
        if not episodes:
            error = Gtk.Label(label="No episodes found.")
            error.add_css_class("muted")
            self.episodes_box.append(error)
            return
        
        # Show episodes
        for ep in episodes[:30]:  # Show first 30
            ep_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            play_icon = Gtk.Image()
            play_icon.set_from_icon_name("media-playback-start-symbolic")
            play_icon.set_pixel_size(16)
            ep_box.append(play_icon)
            
            ep_label = Gtk.Label(label=f"Episode {ep}")
            ep_label.set_halign(Gtk.Align.START)
            ep_label.set_hexpand(True)
            ep_box.append(ep_label)
            
            btn = Gtk.Button()
            btn.set_child(ep_box)
            btn.add_css_class("list-item")
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
                # Get the best link for the episode
                link = self.streamer.get_best_link(anime['_id'], episode)
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
                    anime_id=hash(anime['_id']) % 1000000,
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
        # Popular anime with working IDs from AllAnime API
        popular_anime = [
            {"_id": "RezHft5pjutwWcE3B", "name": "Death Note", "episodes": 37},
            {"_id": "GDBxqQvB9MpNqn2ct", "name": "Steins;Gate", "episodes": 24},
            {"_id": "2oXgpDPd3xKWdgnoz", "name": "Naruto", "episodes": 220},
            {"_id": "ReooPAxPMsHM4KPMY", "name": "One Piece", "episodes": 1156},
            {"_id": "GoDoALiHc82Jrmcmh", "name": "Bleach", "episodes": 366},
            {"_id": "auvmLg2sG4tcmkkuK", "name": "Monster", "episodes": 74},
        ]
        
        import random
        recs = random.sample(popular_anime, min(6, len(popular_anime)))
        
        # Clear
        while (child := self.recs_box.get_first_child()):
            self.recs_box.remove(child)
        
        # Show recommendations
        for anime in recs:
            rec_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            star_icon = Gtk.Image()
            star_icon.set_from_icon_name("starred-symbolic")
            star_icon.set_pixel_size(16)
            star_icon.add_css_class("star-icon")
            rec_box.append(star_icon)
            
            title_label = Gtk.Label(label=anime['name'])
            title_label.set_halign(Gtk.Align.START)
            title_label.set_hexpand(True)
            rec_box.append(title_label)
            
            episodes_label = Gtk.Label(label=f"{anime['episodes']} eps")
            episodes_label.add_css_class("dim-label")
            rec_box.append(episodes_label)
            
            btn = Gtk.Button()
            btn.set_child(rec_box)
            btn.add_css_class("list-item")
            btn.set_hexpand(True)
            btn.connect("clicked", lambda b, a=anime: self.on_anime_selected(a))
            self.recs_box.append(btn)
