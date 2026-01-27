#!/usr/bin/env python3
"""
Direct wrapper around ani-cli using the same scraping logic.
Extracts search and episode link functionality from ani-cli bash script.
"""

import subprocess
import json
import re
from typing import List, Dict, Optional
import os


class AniCliDirect:
    """Use ani-cli's own code to search and get streams."""
    
    def __init__(self):
        self.allanime_refr = "https://allmanga.to"
        self.allanime_api = "https://api.allanime.day"
        self.agent = "Mozilla/5.0"
        self.mode = "sub"  # subtitle mode
        
        # Hex to ASCII mapping from ani-cli
        self.hex_map = {
            '79': 'A', '7a': 'B', '7b': 'C', '7c': 'D', '7d': 'E', '7e': 'F', '7f': 'G',
            '70': 'H', '71': 'I', '72': 'J', '73': 'K', '74': 'L', '75': 'M', '76': 'N',
            '77': 'O', '68': 'P', '69': 'Q', '6a': 'R', '6b': 'S', '6c': 'T', '6d': 'U',
            '6e': 'V', '6f': 'W', '60': 'X', '61': 'Y', '62': 'Z', '59': 'a', '5a': 'b',
            '5b': 'c', '5c': 'd', '5d': 'e', '5e': 'f', '5f': 'g', '50': 'h', '51': 'i',
            '52': 'j', '53': 'k', '54': 'l', '55': 'm', '56': 'n', '57': 'o', '48': 'p',
            '49': 'q', '4a': 'r', '4b': 's', '4c': 't', '4d': 'u', '4e': 'v', '4f': 'w',
            '40': 'x', '41': 'y', '42': 'z', '08': '0', '09': '1', '0a': '2', '0b': '3',
            '0c': '4', '0d': '5', '0e': '6', '0f': '7', '00': '8', '01': '9', '15': '-',
            '16': '.', '67': '_', '46': '~', '02': ':', '17': '/', '07': '?', '1b': '#',
            '63': '[', '65': ']', '78': '@', '19': '!', '1c': '$', '1e': '&', '10': '(',
            '11': ')', '12': '*', '13': '+', '14': ',', '03': ';', '05': '=', '1d': '%'
        }
    
    def _decode_hex_string(self, encoded: str) -> str:
        """Decode hex-encoded string from ani-cli."""
        # Split into pairs
        result = []
        for i in range(0, len(encoded), 2):
            pair = encoded[i:i+2]
            if pair in self.hex_map:
                result.append(self.hex_map[pair])
            else:
                # Keep as-is if not in map
                result.append(pair)
        return ''.join(result)
    
    def search_anime(self, query: str) -> List[Dict]:
        """Search for anime using ani-cli's search logic."""
        try:
            # This is the exact GraphQL query from ani-cli
            search_gql = 'query( $search: SearchInput $limit: Int $page: Int $translationType: VaildTranslationTypeEnumType $countryOrigin: VaildCountryOriginEnumType ) { shows( search: $search limit: $limit page: $page translationType: $translationType countryOrigin: $countryOrigin ) { edges { _id name availableEpisodes __typename } }}'
            
            variables = {
                "search": {
                    "allowAdult": False,
                    "allowUnknown": False,
                    "query": query
                },
                "limit": 40,
                "page": 1,
                "translationType": self.mode,
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
                print(f"[AniCliDirect] Search failed")
                return []
            
            # Parse like ani-cli does: sed 's|Show|\n|g' | sed -nE pattern
            response = result.stdout
            animes = []
            
            # Extract: _id, name, episodes count for the mode (sub)
            pattern = r'_id":"([^"]*)".*?name":"(.+?)".*?availableEpisodes.*?' + f'"{self.mode}":([0-9]+)'
            for match in re.finditer(pattern, response, re.DOTALL):
                anime_id, name, episodes = match.groups()
                name = name.replace('\\"', '"')
                animes.append({
                    '_id': anime_id,
                    'name': name,
                    'episodes': int(episodes)
                })
            
            if not animes:
                # Fallback pattern
                pattern = r'"_id":"([^"]*)"[^}]*"name":"([^"]*)"'
                for match in re.finditer(pattern, response):
                    anime_id, name = match.groups()
                    animes.append({
                        '_id': anime_id,
                        'name': name,
                        'episodes': 12
                    })
            
            print(f"[AniCliDirect] Found {len(animes)} results")
            return animes[:20]  # Limit to 20 results
        
        except Exception as e:
            print(f"[AniCliDirect] Search error: {e}")
            return []
    
    def get_episodes(self, anime_id: str) -> List[str]:
        """Get episode list using ani-cli's logic."""
        try:
            # Get available episodes count
            episodes_gql = 'query($showId: String!) { show(_id: $showId) { availableEpisodes } }'
            
            variables = {"showId": anime_id}
            
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
                return self._default_episodes()
            
            response = result.stdout
            
            # Look for the episode count in the mode (sub)
            pattern = f'"{self.mode}":([0-9]+)'
            match = re.search(pattern, response)
            
            if match:
                count = int(match.group(1))
                episodes = [str(i) for i in range(1, count + 1)]
                print(f"[AniCliDirect] Found {len(episodes)} episodes")
                return episodes
            
            return self._default_episodes()
        
        except Exception as e:
            print(f"[AniCliDirect] Get episodes error: {e}")
            return self._default_episodes()
    
    def _default_episodes(self) -> List[str]:
        """Return default episode list."""
        return [str(i) for i in range(1, 13)]
    
    def get_episode_links(self, anime_id: str, ep_no: str) -> List[Dict]:
        """Get streaming links for an episode (ani-cli's get_links logic).
        
        Returns list of dicts with provider info and URLs.
        """
        try:
            # This is ani-cli's episode_embed_gql from the script
            episode_embed_gql = 'query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) { episode( showId: $showId translationType: $translationType episodeString: $episodeString ) { episodeString sourceUrls }}'
            
            variables = {
                "showId": anime_id,
                "translationType": self.mode,
                "episodeString": ep_no
            }
            
            cmd = [
                "curl",
                "-e", self.allanime_refr,
                "-s",
                "-G", f"{self.allanime_api}/api",
                "--data-urlencode", f"variables={json.dumps(variables)}",
                "--data-urlencode", f"query={episode_embed_gql}",
                "-A", self.agent
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                print(f"[AniCliDirect] Failed to get episode links")
                return []
            
            response = result.stdout
            
            # Extract sourceUrl and sourceName pairs
            # Pattern from ani-cli: sourceUrl":"--([^"]*)" ...sourceName":"([^"]*)"
            links = []
            pattern = r'"sourceUrl":"--([^"]*)"[^}]*?"sourceName":"([^"]*)"'
            
            for match in re.finditer(pattern, response):
                encoded_url, provider = match.groups()
                # Decode the hex-encoded URL
                try:
                    decoded_url = self._decode_hex_string(encoded_url)
                    links.append({
                        'provider': provider,
                        'url': decoded_url
                    })
                    print(f"[AniCliDirect] Decoded {provider}: {decoded_url[:80]}...")
                except Exception as e:
                    print(f"[AniCliDirect] Failed to decode URL: {e}")
            
            if not links:
                print(f"[AniCliDirect] No links found in response")
            
            return links
        
        except Exception as e:
            print(f"[AniCliDirect] Get links error: {e}")
            return []
    
    def get_best_link(self, anime_id: str, ep_no: str) -> Optional[str]:
        """Get the best available link for an episode."""
        links = self.get_episode_links(anime_id, ep_no)
        
        if not links:
            return None
        
        # Prefer direct HTTPS links first
        for link_data in links:
            url = link_data.get('url', '')
            if url.startswith('https://'):
                # Clean up double slashes in path only (not in https://)
                # Replace https:// with placeholder, fix double slashes, restore
                url = url.replace('https://', 'HTTPS_MARKER')
                url = url.replace('//', '/')
                url = url.replace('HTTPS_MARKER', 'https://')
                provider = link_data.get('provider', 'Unknown')
                print(f"[AniCliDirect] Using {provider}: {url[:60]}...")
                return url
        
        # If no HTTPS links, return None (relative paths like /apivtwo need processing)
        print(f"[AniCliDirect] No playable HTTPS links found")
        return None
