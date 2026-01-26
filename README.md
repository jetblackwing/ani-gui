# Ani-GUI

A GTK-based anime streaming player for GNOME that integrates with AniList to show anime results with thumbnails.

## Features

- **AniList Integration**: Search and browse anime from AniList database
- **Thumbnail Display**: View anime cover images and posters
- **GTK4/GNOME Native**: Built with GTK4 for GNOME desktop environment
- **Video Player Integration**: Launch streaming videos with your system player (mpv, vlc, totem)
- **Responsive UI**: Split-view layout with search results and player controls
- **Thumbnail Caching**: Efficient caching of downloaded thumbnails in `~/.cache/ani-gui/`
- **Pagination**: Browse through multiple pages of search results

## Requirements

- Python 3.8+
- GTK 4.0+
- libadwaita (GNOME theme support)
- Internet connection (for AniList API)

## Installation

### From Source

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt install gtk-4-dev libadwaita-1-dev meson

# Clone and build
git clone https://github.com/yourusername/ani-gui.git
cd ani-gui
meson build --prefix=$HOME/.local
meson compile -C build
meson install -C build
```

### Runtime Dependencies

```bash
pip install -r requirements.txt
```

### Optional Video Players

Install one of the following for video playback:
- `mpv` - Lightweight and powerful
- `vlc` - Full-featured media player
- `totem` - GNOME default player

## Usage

```bash
ani-gui
```

Or if installed from source:
```bash
~/.local/bin/ani-gui
```

### How to Use

1. **Search**: Type anime title in the search box
2. **Browse Results**: Scroll through search results with thumbnails
3. **View Details**: Click on an anime to see full details
4. **Play**: Click "Open with Web Browser" to visit AniList page, or provide a streaming URL to play

## Architecture

### Core Modules

- `anilist_api.py` - GraphQL client for AniList API
- `search_handler.py` - Async search handling and result management
- `thumbnail_cache.py` - Intelligent thumbnail downloading and caching
- `video_player.py` - Video player widget with player integration
- `window.py` - Main application window and UI layout
- `main.py` - Application entry point

### Key Features

**AniList Integration**
- Queries anime information including title, description, episodes, ratings
- Fetches cover images and metadata
- No authentication required

**Async Operations**
- Search queries run in background threads
- Thumbnail downloads don't block UI
- Responsive interface during network operations

**Caching Strategy**
- Thumbnails cached locally to reduce bandwidth
- Uses XDG_CACHE_HOME standard
- Persistent across sessions

## Contributing

Pull requests welcome! Areas for improvement:

- Video streaming source integration
- Anime tracking/watchlist
- Episode tracking
- Dark/Light theme support
- Additional metadata display
- Keyboard shortcuts

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Disclaimer

This tool is for my own purposes. Users are responsible for ensuring they have proper rights to stream content.
