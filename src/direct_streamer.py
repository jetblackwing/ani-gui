#!/usr/bin/env python3
"""
Direct anime streamer using AllAnime API.
No rofi/fzf menus - just search and play automatically.
"""

import subprocess
import json
import re
import urllib.parse
from typing import Optional, Callable, List, Dict
import threading

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


class DirectStreamer:
    """Stream anime directly from AllAnime API without interactive menus."""
    
    def __init__(self):
        self.allanime_api = "https://api.allanime.day"
        self.allanime_refr = "https://allmanga.to"
        self.agent = "Mozilla/5.0"
        self.current_process = None
    
    def search_anime(self, query: str) -> List[Dict]:
        """Search for anime by name using AllAnime API.
        
        Returns list of dicts with: id, name, episodes
        """
        try:
            search_gql = 'query( $search: SearchInput $limit: Int $page: Int $translationType: VaildTranslationTypeEnumType $countryOrigin: VaildCountryOriginEnumType ) { shows( search: $search limit: $limit page: $page translationType: $translationType countryOrigin: $countryOrigin ) { edges { _id name availableEpisodes __typename } } }'
            
            variables = {
                "search": {
                    "allowAdult": False,
                    "allowUnknown": False,
                    "query": query
                },
                "limit": 40,
                "page": 1,
                "translationType": "sub",
                "countryOrigin": "ALL"
            }
            
            cmd = [
                "curl",
                "-e", self.allanime_refr,
                "-s",
                "-G", f"{self.allanime_api}/api",
                "--data-urlencode", f"variables={json.dumps(variables)}",
                "--data-urlencode", f"query={search_gql}",
                "-A", self.agent
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print(f"[DirectStreamer] Search failed: {result.stderr}")
                return []
            
            response = result.stdout
            
            # Parse results
            animes = []
            pattern = r'"_id":"([^"]*)".*?"name":"([^"]*)".*?"sub":([0-9]+)'
            for match in re.finditer(pattern, response):
                anime_id, name, episodes = match.groups()
                name = name.replace('\\"', '"')
                animes.append({
                    'id': anime_id,
                    'name': name,
                    'episodes': int(episodes)
                })
            
            print(f"[DirectStreamer] Found {len(animes)} results for '{query}'")
            return animes
        
        except Exception as e:
            print(f"[DirectStreamer] Search error: {e}")
            return []
    
    def get_episodes(self, anime_id: str) -> List[str]:
        """Get list of episode numbers for an anime."""
        try:
            episodes_gql = 'query($showId: String!) { show(id: $showId) { _id availableEpisodesDetail } }'
            
            variables = {
                "showId": anime_id
            }
            
            cmd = [
                "curl",
                "-e", self.allanime_refr,
                "-s",
                "-G", f"{self.allanime_api}/api",
                "--data-urlencode", f"variables={json.dumps(variables)}",
                "--data-urlencode", f"query={episodes_gql}",
                "-A", self.agent
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return []
            
            response = result.stdout
            
            # Parse episode list
            pattern = r'"sub":\[([0-9.,]*)\]'
            match = re.search(pattern, response)
            if match:
                episodes_str = match.group(1)
                episodes = [ep.strip() for ep in episodes_str.split(',') if ep.strip()]
                return episodes
            
            return []
        
        except Exception as e:
            print(f"[DirectStreamer] Get episodes error: {e}")
            return []
    
    def get_episode_links(self, anime_id: str, ep_no: str) -> Optional[str]:
        """Get the playable link for an episode."""
        try:
            embed_gql = 'query($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) { show(id: $showId) { _id seasonPlacement episodes(translationType: $translationType) { edges { _id epNum sourceUrls(translationType: $translationType) { sourceUrl sourceName } } } } }'
            
            variables = {
                "showId": anime_id,
                "translationType": "sub",
                "episodeString": ep_no
            }
            
            cmd = [
                "curl",
                "-e", self.allanime_refr,
                "-s",
                "-G", f"{self.allanime_api}/api",
                "--data-urlencode", f"variables={json.dumps(variables)}",
                "--data-urlencode", f"query={embed_gql}",
                "-A", self.agent
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return None
            
            response = result.stdout
            
            # Find first available source URL
            pattern = r'"sourceUrl":"--([^"]*)"'
            match = re.search(pattern, response)
            if match:
                link = match.group(1)
                return link
            
            return None
        
        except Exception as e:
            print(f"[DirectStreamer] Get links error: {e}")
            return None
    
    def play_direct(self, anime_name: str, episode: str = "1",
                   callback: Optional[Callable] = None):
        """Search for anime and play directly (auto-select first result)."""
        
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
                anime_id = anime['id']
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
                    GLib.idle_add(callback, None, f"▶️  Starting playback...")
                
                # Play with mpv
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
