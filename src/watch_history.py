# watch_history.py
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

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class WatchHistory:
    """Manages anime watch history with category filtering."""
    
    def __init__(self):
        # Use XDG_DATA_HOME for persistent storage
        data_dir = os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')
        self.history_path = Path(data_dir) / 'ani-gui' / 'watch_history.json'
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history: List[Dict] = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load watch history from file."""
        if self.history_path.exists():
            try:
                with open(self.history_path, 'r') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save watch history to file."""
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Error saving history: {e}")
    
    def add_watch(self, anime_id: int, anime_title: str, episode: int = 0,
                  categories: Optional[List[str]] = None, thumbnail_url: Optional[str] = None):
        """Add or update an anime in watch history.
        
        Args:
            anime_id: AniList anime ID
            anime_title: Title of the anime
            episode: Current episode (0 for all/not specified)
            categories: List of genre/category strings
            thumbnail_url: URL of anime thumbnail
        """
        # Check if already in history
        for item in self.history:
            if item['anime_id'] == anime_id:
                item['last_watched'] = datetime.now().isoformat()
                item['episode'] = episode
                if categories:
                    item['categories'] = categories
                self._save_history()
                return
        
        # Add new entry
        entry = {
            'anime_id': anime_id,
            'anime_title': anime_title,
            'episode': episode,
            'categories': categories or [],
            'thumbnail_url': thumbnail_url,
            'last_watched': datetime.now().isoformat(),
            'date_added': datetime.now().isoformat()
        }
        
        self.history.insert(0, entry)  # Most recent first
        self._save_history()
    
    def get_all_history(self) -> List[Dict]:
        """Get entire watch history (sorted by last watched)."""
        return sorted(self.history, key=lambda x: x.get('last_watched', ''), reverse=True)
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get watch history filtered by category.
        
        Args:
            category: Category/genre name
            
        Returns:
            List of anime in this category
        """
        return [
            item for item in self.history
            if category.lower() in [c.lower() for c in item.get('categories', [])]
        ]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories from watch history."""
        categories = set()
        for item in self.history:
            for cat in item.get('categories', []):
                categories.add(cat)
        return sorted(list(categories))
    
    def remove_watch(self, anime_id: int):
        """Remove an anime from watch history.
        
        Args:
            anime_id: AniList anime ID
        """
        self.history = [item for item in self.history if item['anime_id'] != anime_id]
        self._save_history()
    
    def clear_history(self):
        """Clear entire watch history."""
        self.history = []
        self._save_history()
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get most recent watch history items.
        
        Args:
            limit: Number of items to return
            
        Returns:
            List of recent anime
        """
        return self.get_all_history()[:limit]
    
    def search_history(self, query: str) -> List[Dict]:
        """Search watch history by anime title.
        
        Args:
            query: Search query
            
        Returns:
            Matching anime entries
        """
        query_lower = query.lower()
        return [
            item for item in self.history
            if query_lower in item['anime_title'].lower()
        ]
    
    def get_stats(self) -> Dict:
        """Get watch history statistics.
        
        Returns:
            Dictionary with stats (total watched, categories count, etc)
        """
        return {
            'total_anime_watched': len(self.history),
            'total_categories': len(self.get_categories()),
            'categories': self.get_categories(),
            'most_recent': self.history[0] if self.history else None
        }
