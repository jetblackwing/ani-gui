#!/usr/bin/env python3
# consumer_streamer.py
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

"""
Anime streamer using Consumet/Jikan/GogoAnime API.
"""

import subprocess
import json
import re
import urllib.parse
from typing import Optional, List, Dict
import threading

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


class ConsumerStreamer:
    """Stream anime using Consumet/GogoAnime provider."""
    
    def __init__(self):
        # Try multiple providers
        self.gogo_api = "https://gogoanime.consumet.org"
        self.agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    
    def search_anime(self, query: str) -> List[Dict]:
        """Search for anime by name.
        
        Returns list of dicts with: id, name, image, episodes
        """
        try:
            url = f"{self.gogo_api}/meta/anilist/{urllib.parse.quote(query)}"
            
            cmd = [
                "curl",
                "-s",
                "-A", self.agent,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print(f"[ConsumerStreamer] Search failed")
                return []
            
            try:
                data = json.loads(result.stdout)
                results = data.get("results", [])
                
                animes = []
                for r in results[:20]:
                    animes.append({
                        'id': r.get('id', ''),
                        'name': r.get('title', {}).get('english') or r.get('title', {}).get('romaji', ''),
                        'image': r.get('image', ''),
                        'episodes': r.get('totalEpisodes', 12)
                    })
                
                print(f"[ConsumerStreamer] Found {len(animes)} results for '{query}'")
                return animes
            except json.JSONDecodeError:
                print(f"[ConsumerStreamer] Invalid JSON response")
                return []
        
        except Exception as e:
            print(f"[ConsumerStreamer] Search error: {e}")
            return []
    
    def get_episodes(self, anime_id: str) -> List[str]:
        """Get list of episode numbers for an anime."""
        try:
            url = f"{self.gogo_api}/info?id={anime_id}"
            
            cmd = [
                "curl",
                "-s",
                "-A", self.agent,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return self._default_episodes()
            
            try:
                data = json.loads(result.stdout)
                episodes = data.get("episodes", [])
                
                # Extract episode numbers
                ep_nums = [str(ep.get('number', i+1)) for i, ep in enumerate(episodes)]
                print(f"[ConsumerStreamer] Found {len(ep_nums)} episodes")
                return ep_nums if ep_nums else self._default_episodes()
            except json.JSONDecodeError:
                return self._default_episodes()
        
        except Exception as e:
            print(f"[ConsumerStreamer] Get episodes error: {e}")
            return self._default_episodes()
    
    def _default_episodes(self) -> List[str]:
        """Return default episode list."""
        return [str(i) for i in range(1, 25)]
    
    def get_episode_links(self, anime_id: str, ep_no: str) -> Optional[str]:
        """Get the playable link for an episode."""
        try:
            # Get episode streaming link
            url = f"{self.gogo_api}/watch?id={anime_id}"
            
            cmd = [
                "curl",
                "-s",
                "-A", self.agent,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print(f"[ConsumerStreamer] Failed to get episode info")
                return None
            
            try:
                data = json.loads(result.stdout)
                sources = data.get("sources", [])
                
                if sources:
                    # Prefer m3u8
                    for source in sources:
                        if "m3u8" in source.get("url", "").lower():
                            print(f"[ConsumerStreamer] Got m3u8 source")
                            return source.get("url")
                    
                    # Otherwise use first available
                    print(f"[ConsumerStreamer] Using first available source")
                    return sources[0].get("url")
                
                return None
            except json.JSONDecodeError:
                return None
        
        except Exception as e:
            print(f"[ConsumerStreamer] Get links error: {e}")
            return None
