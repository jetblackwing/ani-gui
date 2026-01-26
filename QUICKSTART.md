# Quick Start Guide - Ani-GUI

## What is Ani-GUI?

Ani-GUI is a GTK4 anime browser for GNOME that lets you:
- 🔍 Search anime from AniList (the ultimate anime database)
- 🖼️ View beautiful cover images with automatic caching
- ▶️ Launch videos with your preferred player (mpv, vlc, etc.)
- 📱 Enjoy a native, responsive desktop experience

## Installation (5 minutes)

### Step 1: Install Dependencies
```bash
# Ubuntu/Debian
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adwaita-1 meson ninja-build python3-pip

# Fedora
sudo dnf install python3-gobject gtk4-devel libadwaita-devel meson ninja-build python3-pip

# Arch
sudo pacman -S python-gobject gtk4 libadwaita meson ninja python-pip
```

### Step 2: Install Python Packages
```bash
cd ~/Documents/ani-gui
pip install --user -r requirements.txt
```

### Step 3: Install Video Player (optional but recommended)
```bash
# Ubuntu/Debian
sudo apt install mpv

# Fedora
sudo dnf install mpv

# Arch
sudo pacman -S mpv
```

### Step 4: Build & Install
```bash
cd ~/Documents/ani-gui
meson build --prefix=$HOME/.local
meson compile -C build
meson install -C build
```

### Step 5: Run
```bash
ani-gui
```

## Usage

1. **Search**: Type anime name in the search bar
2. **Browse**: Scroll through results with thumbnails
3. **Select**: Click any anime to view details
4. **Play**: Click "Open with Web Browser" or provide streaming URL to play

## Development Quick Start

### Running Without Installation
```bash
cd ~/Documents/ani-gui
export PYTHONPATH=$PWD/src:$PYTHONPATH
python3 -m ani_gui.main
```

### Or use the dev script
```bash
cd ~/Documents/ani-gui
./run-dev.py
```

## Key Features Explained

### 🔍 Smart Search
- Real-time search powered by AniList GraphQL API
- Pagination support (12 results per page)
- Shows anime title in English, Romaji, and native language

### 🖼️ Efficient Thumbnail System
- Automatically downloads and caches cover images
- Smart fallback to network if cache missing
- Stored in `~/.cache/ani-gui/thumbnails/`
- No duplication (MD5 hash-based filenames)

### ⚡ Responsive UI
- All network operations in background threads
- UI never freezes during search or image loading
- Instant feedback on user actions

### 🎬 Video Player Integration
- Supports mpv, VLC, and GNOME Videos
- Falls back to opening AniList page in browser
- Easy integration with future streaming sources

## Project Structure

```
src/
├── main.py              ← Start here: GTK Application init
├── window.py            ← Main UI and search logic
├── anilist_api.py       ← AniList API client
├── search_handler.py    ← UI components and async search
├── thumbnail_cache.py   ← Image download & caching
└── video_player.py      ← Video player widget
```

## Common Tasks

### I want to add a new anime source
See [ARCHITECTURE.md](ARCHITECTURE.md) - "Future Extensibility" section

### I want to customize the colors/theme
Edit CSS in the widget construction code in `window.py` and `search_handler.py`

### I want to add a streaming source
Modify `video_player.py` `_play_with_player()` to fetch URLs from your source

### I want to change the default search
Edit the `_trigger_search()` call in `window.py` `__init__`

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install --user requests
```

### "Cannot find Gtk module"
```bash
pip install --user PyGObject
sudo apt install gir1.2-gtk-4.0  # Ubuntu/Debian
```

### Search returns no results
- Check internet connection: `ping graphql.anilist.co`
- Try searching for "Naruto" (common anime)

### No thumbnails showing
```bash
# Check if cache directory exists
ls -la ~/.cache/ani-gui/thumbnails/

# Try clearing cache
rm -rf ~/.cache/ani-gui/thumbnails/
```

### Video player doesn't work
Install at least one player:
```bash
sudo apt install mpv vlc totem  # Ubuntu/Debian
```

## Documentation

- [SETUP.md](SETUP.md) - Detailed installation guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [README.md](README.md) - Full feature documentation

## Contributing

Areas for improvement:
- [ ] Streaming source integration
- [ ] Watchlist/favorites
- [ ] Episode tracking
- [ ] Dark theme support
- [ ] Advanced filters
- [ ] Translations

## License

GNU General Public License v3.0 or later

## Disclaimer

This tool is for educational purposes. Users must respect anime licensing and streaming rights.
