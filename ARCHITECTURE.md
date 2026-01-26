# Ani-GUI Architecture Documentation

## Overview

Ani-GUI is a GTK4-based anime browser and video player for GNOME that integrates with the AniList GraphQL API. The application provides a responsive, native desktop experience with asynchronous operations to keep the UI responsive during network requests.

## System Architecture

```
┌─────────────────────────────────────────────┐
│         GTK Application (main.py)           │
└────────────────────┬────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼────┐
    │ Window   │          │ Actions  │
    │ (UI)     │          │ Menu     │
    └────┬─────┘          └──────────┘
         │
    ┌────▼──────────────────────────┐
    │   Main Window (window.py)      │
    │  ┌──────────┐  ┌────────────┐  │
    │  │ Search   │  │ Video      │  │
    │  │ Bar      │  │ Player     │  │
    │  └──────────┘  └────────────┘  │
    │  ┌──────────────────────────┐  │
    │  │ Search Results Grid      │  │
    │  │ (AnimeSearchRow)         │  │
    │  └──────────────────────────┘  │
    │  ┌──────────────────────────┐  │
    │  │ Pagination Controls      │  │
    │  └──────────────────────────┘  │
    └────┬────────────────────────────┘
         │
    ┌────┴────────────────┬──────────────┬──────────────┐
    │                     │              │              │
┌───▼────────┐    ┌───────▼─────┐  ┌───▼─────────┐ ┌──▼──────────┐
│ AniList    │    │ Search      │  │ Thumbnail  │ │ Video      │
│ API        │    │ Handler     │  │ Cache      │ │ Player     │
│ (GraphQL)  │    │ (Threading) │  │ (Disk)     │ │ (External) │
└────────────┘    └─────────────┘  └────────────┘ └────────────┘
```

## Module Details

### 1. main.py - Application Entry Point

**Purpose**: Initialize and launch the GTK application

**Key Components**:
- `AniGuiApplication` - Main app singleton inheriting from `Gtk.Application`
- Registers default actions (quit, about, preferences)
- Creates main window on activation
- Handles application-level signals

**Responsibilities**:
- App lifecycle management
- Menu action setup
- Window creation

### 2. window.py - Main UI Container

**Purpose**: Define the main application window and layout

**Key Components**:
- `AniGuiWindow` - Main window class
- Search bar with real-time entry
- Split paned layout:
  - Left: Search results list
  - Right: Video player
- Pagination controls

**Key Methods**:
```python
on_search_changed()      # Triggered when search text changes
on_search_results()      # Callback when API returns results
on_anime_selected()      # When user clicks on an anime
on_prev_page()          # Previous page button handler
on_next_page()          # Next page button handler
_trigger_search()       # Initiates search operation
```

**Layout**:
```
┌─────────────────────────────────┐
│  Search Bar                     │
├──────────────────┬──────────────┤
│                  │              │
│  Search Results  │   Video      │
│  (Scrollable)    │   Player &   │
│                  │   Details    │
├──────────────────┤              │
│  [Prev] [Next]   │              │
└──────────────────┴──────────────┘
```

### 3. anilist_api.py - AniList GraphQL Client

**Purpose**: Handle all communication with AniList API

**Key Components**:
- `AniListAPI` class with requests.Session
- GraphQL query templates for anime search and details
- Error handling and response parsing

**GraphQL Queries**:

**SearchAnime Query**:
- Variables: search, page, perPage
- Returns: 12 results per page with pagination info
- Fields: title, description, episodes, cover image, rating, genres

**GetAnime Query**:
- Variables: anime ID
- Returns: Full anime details including studios, characters, status

**Key Methods**:
```python
search_anime(query, page, per_page)      # Search with pagination
get_anime_details(anime_id)              # Get full anime info
_make_request(query, variables)          # Generic GraphQL request
extract_anime_from_search(data)         # Parse search response
get_anime_title(anime)                  # Extract best title
get_anime_cover_url(anime)              # Get cover image URL
```

**Features**:
- No authentication required
- 10-second timeout per request
- Error logging for failed queries
- Response validation

### 4. search_handler.py - Async Search Management

**Purpose**: Manage search operations asynchronously and UI components for results

**Key Components**:
- `SearchHandler` - Manages search threading and thumbnail loading
- `AnimeSearchRow` - GTK widget for single anime result

**SearchHandler Methods**:
```python
search_anime(query, callback, page)     # Async search
load_thumbnail(url, width, height, callback)  # Async image load
```

**AnimeSearchRow Widget**:
- Displays anime thumbnail, title, description
- Shows metadata (episodes, rating, status)
- Clickable to select anime
- HTML description parsing and truncation
- Responsive to thumbnail loading completion

**Threading Model**:
- Search queries run in daemon threads
- Results returned via `GLib.idle_add()` for thread-safe UI updates
- UI remains responsive during network operations

### 5. thumbnail_cache.py - Image Caching System

**Purpose**: Efficiently cache and manage anime cover images

**Cache Location**: `$XDG_CACHE_HOME/ani-gui/thumbnails/` (default: `~/.cache/ani-gui/thumbnails/`)

**Key Components**:
- `ThumbnailCache` - Manages download and caching

**Key Methods**:
```python
get_cached_pixbuf(url, width, height)          # Load from cache
download_and_cache_pixbuf(url, width, height)  # Download & cache
get_thumbnail_async(url, width, height, callback)  # Async load
```

**Features**:
- MD5 hash-based filename generation
- Automatic scaling to desired dimensions
- Fallback to download if cache miss
- GLib integration for main-thread callbacks
- Persistent across sessions

**Cache Structure**:
```
~/.cache/ani-gui/
└── thumbnails/
    ├── 5d41402abc4b2a76b9719d911017c592.jpg  (Jujutsu Kaisen)
    ├── 6512bd43d9caa6e02c990b0a82652dca.jpg  (Attack on Titan)
    └── ... (one file per unique image URL)
```

### 6. video_player.py - Media Playback Widget

**Purpose**: Display anime info and launch video playback

**Key Components**:
- `VideoPlayerWidget` - GTK container for player controls
- External player integration (mpv, vlc, totem)

**Key Methods**:
```python
set_anime(anime, video_url)     # Set anime to display
on_play_clicked()               # Launch player
on_clear_clicked()              # Clear selection
_play_with_player(url)         # Try available players
```

**Features**:
- Displays anime title and metadata
- Info includes: episodes, status, genres, rating
- Tries multiple video players (mpv → vlc → totem)
- Falls back to opening AniList page in browser
- Error dialogs for missing players

## Data Flow

### Search Operation Flow
```
User Types Query
    ↓
on_search_changed() triggered
    ↓
_trigger_search() called
    ↓
SearchHandler.search_anime() (async in thread)
    ↓
AniListAPI.search_anime() makes GraphQL request
    ↓
Response parsed and results extracted
    ↓
GLib.idle_add() calls on_search_results() on main thread
    ↓
Results displayed as AnimeSearchRow widgets
    ↓
Pagination buttons updated
```

### Thumbnail Loading Flow
```
AnimeSearchRow created
    ↓
thumbnail_url extracted from anime data
    ↓
SearchHandler.load_thumbnail() (async)
    ↓
ThumbnailCache checks local cache (MD5 hash)
    ↓
If cache hit: Load GdkPixbuf from file
If cache miss: Download from AniList CDN
    ↓
Scale to 150x225 pixels
    ↓
GLib.idle_add() callback on main thread
    ↓
on_thumbnail_loaded() updates Image widget
```

### Anime Selection Flow
```
User clicks AnimeSearchRow
    ↓
on_click() gesture handler fires
    ↓
on_selected() callback triggered
    ↓
on_anime_selected() in window.py called
    ↓
VideoPlayerWidget.set_anime(anime_dict)
    ↓
Title, description, metadata displayed
    ↓
Play button enabled and ready
```

## Threading Model

All network I/O runs in background daemon threads to prevent UI blocking:

1. **Search Threads**: `SearchHandler.search_anime()`
   - Created: On each search query
   - Duration: Network latency
   - Callback: `GLib.idle_add()` on main thread

2. **Thumbnail Threads**: `ThumbnailCache.get_thumbnail_async()`
   - Created: Per thumbnail load
   - Duration: Network latency + local disk I/O
   - Callback: Via SearchHandler callback

3. **Main Thread**: All GTK widget updates via `GLib.idle_add()`

## Error Handling

**API Errors**:
- GraphQL errors logged to console
- Search returns empty results on failure
- User sees "No results found" message

**Network Errors**:
- requests exceptions caught
- Timeout: 10 seconds per API request
- Thumbnail download failures logged
- Missing image handled gracefully

**Player Errors**:
- If no video player found, show AlertDialog
- Fallback to opening AniList in browser

## Performance Considerations

**Memory**:
- Pixbufs scaled to display size (150x225)
- Lazy loading of thumbnails on scroll
- Search results limited to 12 per page

**Disk**:
- Thumbnails cached persistently
- Cache automatically created in standard XDG location
- No automatic cleanup (user can delete ~/.cache/ani-gui/)

**Network**:
- Single API request per search
- Thumbnail CDN links from AniList
- Caching reduces subsequent requests to zero

## Security Considerations

- No user authentication stored
- AniList queries public data only
- External player execution: URLs only (no code execution)
- Requests library handles TLS verification

## Future Extensibility

- **Plugin System**: Add streaming source providers
- **Watchlist**: Store user preferences/watchlist
- **History**: Track viewed anime
- **Themes**: Custom GTK CSS themes
- **Localization**: Translation support via gettext (.po files)
- **Streaming Integration**: Hook for external player URLs from streaming services
