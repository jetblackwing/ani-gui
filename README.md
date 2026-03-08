# Ani-GUI

A GTK-based anime streaming player for GNOME that integrates with AniList to show anime results with thumbnails, and **ani-cli** for direct anime streaming.

## Features

- **AniList Integration**: Search and browse anime from AniList database
- **Thumbnail Display**: View anime cover images and posters
- **Ani-CLI Streaming**: Watch anime directly using ani-cli (with quality selection)
- **Download Support**: Download episodes for offline viewing
- **Continue Watching**: Resume from your watch history
- **GTK4/GNOME Native**: Built with GTK4 for GNOME desktop environment
- **Quality Selection**: Choose between best, 1080p, 720p, 480p
- **Responsive UI**: Split-view layout with search results and player controls
- **Thumbnail Caching**: Efficient caching of downloaded thumbnails in `~/.cache/ani-gui/`
- **Pagination**: Browse through multiple pages of search results

## Requirements

- Python 3.8+
- GTK 4.0+
- libadwaita (GNOME theme support)
- Internet connection (for AniList API)
- **ani-cli** (for streaming anime)

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

### Optional but Recommended

#### Ani-CLI (for streaming anime)

```bash
git clone https://github.com/pystardust/ani-cli.git
cd ani-cli
sudo make install
```

#### Video Players

Install one of the following for video playback (required by ani-cli):
- `mpv` - Lightweight and powerful (recommended)
- `vlc` - Full-featured media player
- `totem` - GNOME default player

```bash
# Install mpv (recommended)
sudo apt install mpv
```

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
3. **Select Anime**: Click on an anime to view details and controls
4. **Watch with ani-cli**: 
   - Choose video quality (best, 1080p, 720p, 480p)
   - Specify episode (or 0 for all)
   - Click "▶ Watch with ani-cli" to start streaming
5. **Download**: Click "⬇ Download" to save episodes offline
6. **Continue**: Click "⏯ Continue Watching" to resume from history
7. **Browser**: Click "🌐 Open in Browser" to visit AniList page

For detailed ani-cli usage, see [ANI_CLI_GUIDE.md](ANI_CLI_GUIDE.md)

## Architecture

### Core Modules

- `anilist_api.py` - GraphQL client for AniList API
- `search_handler.py` - Async search handling and result management
- `thumbnail_cache.py` - Intelligent thumbnail downloading and caching
- `video_player.py` - Video player widget with ani-cli integration
- `ani_cli_integration.py` - Ani-CLI wrapper and execution
- `window.py` - Main application window and UI layout
- `main.py` - Application entry point

### Key Features

**AniList Integration**
- Queries anime information including title, description, episodes, ratings
- Fetches cover images and metadata
- No authentication required

**Ani-CLI Integration**
- Direct anime streaming through ani-cli
- Quality selection (best, 1080p, 720p, 480p)
- Episode selection and range support
- Download capability for offline viewing
- Continue watching from history
- Automatic player detection and launching

**Async Operations**
- Search queries run in background threads
- Ani-cli execution in background threads
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

Copyright 2024 Amal J Krishnan <amaljk80@gmail.com> (@jetblackwing)

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Disclaimer

This tool is for my own purposes. Users are responsible for ensuring they have proper rights to stream content.
