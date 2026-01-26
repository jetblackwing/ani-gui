# SETUP.md - Ani-GUI Setup Instructions

## Quick Start

### 1. Install System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install \
  python3-gi \
  python3-gi-cairo \
  gir1.2-gtk-4.0 \
  gir1.2-adwaita-1 \
  meson \
  ninja-build \
  python3-pip
```

#### Fedora:
```bash
sudo dnf install \
  python3-gobject \
  gtk4-devel \
  libadwaita-devel \
  meson \
  ninja-build \
  python3-pip
```

#### Arch:
```bash
sudo pacman -S \
  python-gobject \
  gtk4 \
  libadwaita \
  meson \
  ninja \
  python-pip
```

### 2. Install Python Dependencies

```bash
cd /home/amal/Documents/ani-gui
pip install --user -r requirements.txt
```

### 3. Install Optional Video Players

Choose at least one:
```bash
# Ubuntu/Debian
sudo apt install mpv vlc

# Fedora
sudo dnf install mpv vlc

# Arch
sudo pacman -S mpv vlc
```

### 4. Build with Meson

```bash
cd /home/amal/Documents/ani-gui
meson build --prefix=$HOME/.local
meson compile -C build
meson install -C build
```

### 5. Run the Application

```bash
ani-gui
```

Or from source directory:
```bash
python3 -m ani_gui.main
```

## Troubleshooting

### "No module named 'requests'"
```bash
pip install --user requests
```

### "Cannot find Gtk module"
Ensure pygobject and GTK4 bindings are installed:
```bash
pip install --user PyGObject
sudo apt install gir1.2-gtk-4.0
```

### Application won't start
Check if you can import the modules:
```bash
python3 -c "from gi.repository import Gtk; print(Gtk.__version__)"
python3 -c "import requests; print(requests.__version__)"
```

### No thumbnails appearing
Check cache directory:
```bash
ls -la ~/.cache/ani-gui/thumbnails/
```

If empty, check network connection and AniList API:
```bash
python3 -c "from ani_gui.anilist_api import AniListAPI; api = AniListAPI(); print(api.search_anime('Jujutsu Kaisen'))"
```

## Development

### Project Structure
```
ani-gui/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # App entry point
│   ├── window.py             # Main window
│   ├── anilist_api.py        # AniList API client
│   ├── search_handler.py     # Search UI components
│   ├── thumbnail_cache.py    # Image caching
│   └── video_player.py       # Video player widget
├── data/
│   ├── com.ajk.anigui.desktop.in    # Desktop entry
│   ├── com.ajk.anigui.gschema.xml   # Settings schema
│   └── icons/                        # Application icons
├── po/                       # Translations
├── meson.build              # Build configuration
├── requirements.txt         # Python dependencies
└── README.md               # User documentation
```

### Running in Development Mode

```bash
cd /home/amal/Documents/ani-gui
export PYTHONPATH=$PWD/src:$PYTHONPATH
python3 -m ani_gui.main
```

### Code Style
- Follow PEP 8
- Use type hints for function arguments
- Add docstrings to all public functions
- Use GTK CSS classes for styling

## Features Implemented

✅ AniList API integration
✅ Anime search with pagination
✅ Thumbnail caching system
✅ Responsive GTK4 UI
✅ Video player integration
✅ Async operations (non-blocking UI)

## Planned Features

- [ ] Streaming source integration
- [ ] Watchlist/tracking
- [ ] Episode management
- [ ] User preferences
- [ ] Dark/Light theme toggle
- [ ] Keyboard shortcuts
- [ ] Advanced search filters
