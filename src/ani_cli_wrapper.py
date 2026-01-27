# ani_cli_wrapper.py
#
# Copyright 2024 Amal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Wrapper around ani-cli to fetch anime streams.
"""

import subprocess
import json
import re
from typing import List, Optional, Dict
from .direct_streamer import DirectStreamer


class AniCliWrapper:
    """Use ani-cli to get anime streams."""
    
    def __init__(self):
        self.ani_cli = "/usr/bin/ani-cli"
        self.streamer = DirectStreamer()
    
    def get_anime_stream(self, anime_name: str, episode: str) -> Optional[str]:
        """Get stream link for anime episode using ani-cli logic."""
        try:
            # First search for anime using DirectStreamer API
            results = self.streamer.search_anime(anime_name)
            if not results:
                print(f"[AniCliWrapper] No anime found: {anime_name}")
                return None
            
            anime = results[0]
            anime_id = anime['id']
            
            print(f"[AniCliWrapper] Found: {anime['name']} (ID: {anime_id})")
            
            # Get stream link
            link = self.streamer.get_episode_links(anime_id, episode)
            
            if link:
                print(f"[AniCliWrapper] Got stream: {link[:80]}...")
            else:
                print(f"[AniCliWrapper] No stream found for episode {episode}")
            
            return link
        
        except Exception as e:
            print(f"[AniCliWrapper] Error: {e}")
            return None
    
    def get_recommendations(self) -> List[Dict]:
        """Get random anime recommendations."""
        # Popular anime list (could be expanded)
        popular_anime = [
            {"name": "Naruto", "episodes": 220},
            {"name": "One Piece", "episodes": 1000},
            {"name": "Attack on Titan", "episodes": 139},
            {"name": "Death Note", "episodes": 37},
            {"name": "Demon Slayer", "episodes": 55},
            {"name": "Jujutsu Kaisen", "episodes": 64},
            {"name": "My Hero Academia", "episodes": 149},
            {"name": "Sword Art Online", "episodes": 100},
            {"name": "Tokyo Ghoul", "episodes": 48},
            {"name": "Bleach", "episodes": 366},
            {"name": "Fullmetal Alchemist", "episodes": 51},
            {"name": "Code Geass", "episodes": 50},
            {"name": "Steins;Gate", "episodes": 24},
            {"name": "Cowboy Bebop", "episodes": 26},
            {"name": "Neon Genesis Evangelion", "episodes": 26},
        ]
        
        import random
        # Randomize and return 6 recommendations
        recommendations = random.sample(popular_anime, min(6, len(popular_anime)))
        return recommendations
