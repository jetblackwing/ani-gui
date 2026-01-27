#!/usr/bin/env python3
"""
Direct anime streamer using multiple sources.
Falls back to ani-cli for actual streaming.
"""

import subprocess
import json
import re
import urllib.parse
from typing import Optional, Callable, List, Dict
import threading
import time

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


class DirectStreamer:
    """Stream anime from multiple sources."""
    
    def __init__(self):
        self.current_process = None
        # Use Jikan API (most reliable) for search
        self.jikan_api = "https://api.jikan.moe/v4"
        self.consumet_api = "https://api.consumet.org/anime/gogoanime"
    
    def search_anime(self, query: str) -> List[Dict]:
        """Search for anime by name using ani-cli.
        
        Returns list of dicts with: _id, name, episodes
        """
        try:
            # Use ani-cli to search for anime
            # Run non-interactively using rofi fake
            import os
            
            # Try using ani-cli's internal search
            cmd = [
                "/usr/bin/ani-cli",
                "--quality", "best",
                "--select-nth", "1",
                query
            ]
            
            # Run with a timeout and rofi fake
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env={**os.environ, "ROFI_COMMAND": "/usr/bin/fzf"}
                )
            except subprocess.TimeoutExpired:
                # If timeout, anime might have been found
                pass
            
            # For now, return a placeholder that will use ani-cli for playback
            # Real solution: parse ani-cli output to extract anime list
            return [{
                '_id': f"ani_cli_{query.lower().replace(' ', '_')}",
                'name': query,
                'episodes': 12
            }]
        
        except Exception as e:
            print(f"[DirectStreamer] Search error: {e}")
            return []
    
    def get_episodes(self, anime_id: str) -> List[str]:
        """Get list of episode numbers for an anime."""
        try:
            if anime_id.startswith("ani_cli_"):
                # Using ani-cli, return default episodes
                return [str(i) for i in range(1, 13)]
            
            # Try to get episode count from API
            # For now, return defaults
            print(f"[DirectStreamer] Using default 12 episodes")
            return [str(i) for i in range(1, 13)]
        
        except Exception as e:
            print(f"[DirectStreamer] Get episodes error: {e}")
            return self._default_episodes()
    
    def _default_episodes(self) -> List[str]:
        """Return default episode list."""
        return [str(i) for i in range(1, 25)]
    
    def get_episode_links(self, anime_id: str, ep_no: str) -> Optional[str]:
        """Get the playable link for an episode.
        
        Returns ani-cli marker for playback.
        """
        try:
            # Extract anime name from ID
            if anime_id.startswith("ani_cli_"):
                anime_name = anime_id.replace("ani_cli_", "").replace("_", " ")
                # Return ani-cli marker
                return f"ani-cli|{anime_name}|{ep_no}"
            
            # Default fallback
            print(f"[DirectStreamer] Could not get link, using ani-cli")
            return f"ani-cli|Unknown|{ep_no}"
        
        except Exception as e:
            print(f"[DirectStreamer] Get links error: {e}")
            return None
    
    def play_direct(self, anime_name: str, episode: str = "1",
                   callback: Optional[Callable] = None,
                   video_player = None):
        """Search for anime and play directly (auto-select first result).
        
        Args:
            anime_name: Anime name to search
            episode: Episode number
            callback: Status callback (success, message)
            video_player: VideoPlayerWidget to use for playback (if provided)
        """
        
        def play_thread():
            try:
                # Search
                if callback:
                    GLib.idle_add(callback, None, f"🔍 Searching for '{anime_name}'...")
                
                results = self.search_anime(anime_name)
                if not results:
                    if callback:
                        GLib.idle_add(callback, False, f"❌ '{anime_name}' not found")
                    return
                
                # Auto-select first result
                anime = results[0]
                anime_id = anime['_id']
                title = anime['name']
                
                if callback:
                    GLib.idle_add(callback, None, f"📺 Selected: {title}")
                
                # Get link for episode
                if callback:
                    GLib.idle_add(callback, None, f"⏳ Fetching episode {episode}...")
                
                link = self.get_episode_links(anime_id, episode)
                if not link:
                    if callback:
                        GLib.idle_add(callback, False, f"❌ Episode {episode} not available")
                    return
                
                if callback:
                    GLib.idle_add(callback, None, f"▶️ Loading video...")
                
                # Play with embedded player or mpv
                if video_player:
                    # Use embedded video player - load and show
                    def load_video():
                        try:
                            video_player.play(link, f"{title} - Episode {episode}")
                            if callback:
                                callback(True, f"▶️ Playing: {title} Episode {episode}")
                        except Exception as e:
                            if callback:
                                callback(False, f"❌ Playback error: {str(e)}")
                    GLib.idle_add(load_video)
                else:
                    # Fallback to mpv
                    self.current_process = subprocess.Popen(
                        ["mpv", "--force-media-title=" + title + f" Ep {episode}", link],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    
                    print(f"[DirectStreamer] Started mpv, PID: {self.current_process.pid}")
                    
                    # Wait for playback to finish
                    self.current_process.wait()
                    
                    if callback:
                        GLib.idle_add(callback, True, f"✅ Finished: {title} Episode {episode}")
                
            except FileNotFoundError as e:
                if callback:
                    GLib.idle_add(callback, False, f"❌ mpv not found\nInstall: sudo apt install mpv")
                print(f"[DirectStreamer] File not found: {e}")
            except Exception as e:
                if callback:
                    GLib.idle_add(callback, False, f"❌ Error: {str(e)}")
                print(f"[DirectStreamer] Play error: {e}")
        
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()
    
    def stop_playback(self):
        """Stop current playback."""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except:
                try:
                    self.current_process.kill()
                except:
                    pass
            self.current_process = None

