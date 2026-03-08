# anilist_api.py
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

import json
import requests
from typing import List, Dict, Optional
from gi.repository import GLib

class AniListAPI:
    """Client for AniList GraphQL API."""
    
    ANILIST_URL = "https://graphql.anilist.co"
    
    # GraphQL query to search for anime
    SEARCH_QUERY = """
    query SearchAnime($search: String, $page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
            }
            media(search: $search, type: ANIME) {
                id
                title {
                    english
                    romaji
                    native
                }
                description
                episodes
                status
                startDate {
                    year
                    month
                    day
                }
                season
                coverImage {
                    large
                    medium
                }
                bannerImage
                averageScore
                popularity
                genres
            }
        }
    }
    """
    
    # Query to get anime details
    DETAILS_QUERY = """
    query GetAnime($id: Int!) {
        Media(id: $id, type: ANIME) {
            id
            title {
                english
                romaji
                native
            }
            description
            episodes
            duration
            status
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            season
            seasonYear
            coverImage {
                large
                medium
            }
            bannerImage
            averageScore
            popularity
            genres
            studios(isMain: true) {
                edges {
                    node {
                        name
                    }
                }
            }
            characters(sort: [ROLE, RELEVANCE], perPage: 5) {
                edges {
                    node {
                        name {
                            full
                        }
                        image {
                            large
                        }
                    }
                    role
                }
            }
            source
            format
            nextAiringEpisode {
                airingAt
                timeUntilAiring
                episode
            }
        }
    }
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def search_anime(self, query: str, page: int = 1, per_page: int = 12) -> Optional[Dict]:
        """Search for anime by title.
        
        Args:
            query: Search query string
            page: Page number (starting from 1)
            per_page: Results per page
            
        Returns:
            Dictionary with search results or None if request fails
        """
        variables = {
            'search': query,
            'page': page,
            'perPage': per_page
        }
        
        return self._make_request(self.SEARCH_QUERY, variables)
    
    def get_anime_details(self, anime_id: int) -> Optional[Dict]:
        """Get detailed information about an anime.
        
        Args:
            anime_id: AniList anime ID
            
        Returns:
            Dictionary with anime details or None if request fails
        """
        variables = {'id': anime_id}
        return self._make_request(self.DETAILS_QUERY, variables)
    
    def _make_request(self, query: str, variables: Dict) -> Optional[Dict]:
        """Make a GraphQL request to AniList API.
        
        Args:
            query: GraphQL query string
            variables: Query variables dictionary
            
        Returns:
            Response data or None if request fails
        """
        try:
            payload = {
                'query': query,
                'variables': variables
            }
            
            response = self.session.post(
                self.ANILIST_URL,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'errors' in data:
                print(f"AniList API error: {data['errors']}")
                return None
            
            return data.get('data')
        
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse response: {e}")
            return None
    
    def extract_anime_from_search(self, search_data: Dict) -> List[Dict]:
        """Extract anime list from search response.
        
        Args:
            search_data: Data from search_anime response
            
        Returns:
            List of anime dictionaries
        """
        if not search_data or 'Page' not in search_data:
            return []
        
        return search_data['Page'].get('media', [])
    
    def get_anime_title(self, anime: Dict) -> str:
        """Get the best available title for an anime.
        
        Args:
            anime: Anime dictionary from API response
            
        Returns:
            Title string
        """
        if not anime or 'title' not in anime:
            return "Unknown"
        
        titles = anime['title']
        return titles.get('english') or titles.get('romaji') or titles.get('native') or "Unknown"
    
    def get_anime_cover_url(self, anime: Dict) -> Optional[str]:
        """Get the cover image URL for an anime.
        
        Args:
            anime: Anime dictionary from API response
            
        Returns:
            Cover image URL or None
        """
        if not anime or 'coverImage' not in anime:
            return None
        
        cover = anime['coverImage']
        return cover.get('large') or cover.get('medium')
