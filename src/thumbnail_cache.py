# thumbnail_cache.py
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

import os
import hashlib
from pathlib import Path
from typing import Optional
import requests
from gi.repository import GLib, GdkPixbuf

class ThumbnailCache:
    """Cache manager for anime thumbnails."""
    
    def __init__(self):
        # Use XDG_CACHE_HOME or fallback to ~/.cache
        cache_dir = os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')
        self.cache_path = Path(cache_dir) / 'ani-gui' / 'thumbnails'
        self.cache_path.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_filename(self, url: str) -> str:
        """Generate a cache filename from URL.
        
        Args:
            url: Image URL
            
        Returns:
            Hash-based filename
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{url_hash}.jpg"
    
    def get_cached_pixbuf(self, url: str, width: int = 220, height: int = 330) -> Optional[GdkPixbuf.Pixbuf]:
        """Get a cached thumbnail as a Pixbuf.
        
        Args:
            url: Image URL
            width: Desired width in pixels
            height: Desired height in pixels
            
        Returns:
            GdkPixbuf.Pixbuf or None if not available
        """
        cache_file = self.cache_path / self._get_cache_filename(url)
        
        if cache_file.exists():
            try:
                return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    str(cache_file),
                    width,
                    height,
                    True
                )
            except Exception as e:
                print(f"Error loading cached pixbuf: {e}")
                return None
        
        return None
    
    def download_and_cache_pixbuf(self, url: str, width: int = 220, height: int = 330) -> Optional[GdkPixbuf.Pixbuf]:
        """Download image from URL and cache it, returning as Pixbuf.
        
        Args:
            url: Image URL
            width: Desired width in pixels
            height: Desired height in pixels
            
        Returns:
            GdkPixbuf.Pixbuf or None if download fails
        """
        cache_file = self.cache_path / self._get_cache_filename(url)
        
        try:
            # Download image
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Save to cache
            cache_file.write_bytes(response.content)
            
            # Load and scale as Pixbuf
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                str(cache_file),
                width,
                height,
                True
            )
        
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")
            return None
    
    def get_thumbnail_async(self, url: str, width: int, height: int, callback):
        """Asynchronously get a thumbnail with callback.
        
        Args:
            url: Image URL
            width: Desired width in pixels
            height: Desired height in pixels
            callback: Function to call with (pixbuf, url) when done
        """
        def load_thumbnail():
            # Try cache first
            pixbuf = self.get_cached_pixbuf(url, width, height)
            
            # If not cached, download
            if pixbuf is None:
                pixbuf = self.download_and_cache_pixbuf(url, width, height)
            
            # Call callback on main thread
            GLib.idle_add(callback, pixbuf, url)
        
        # Run in background thread
        import threading
        thread = threading.Thread(target=load_thumbnail, daemon=True)
        thread.start()
