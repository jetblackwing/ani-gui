# Ani-CLI Integration Guide

## Overview

Ani-GUI now integrates with **ani-cli**, a powerful command-line tool for streaming anime. This allows you to search for anime in the GUI and watch them directly using ani-cli's streaming capabilities.

## Installation

### Install ani-cli

```bash
# Clone the ani-cli repository
git clone https://github.com/pystardust/ani-cli.git
cd ani-cli
sudo make install

# Or use a package manager (if available for your distro)
sudo apt install ani-cli  # Debian/Ubuntu
```

### Verify Installation

```bash
which ani-cli
ani-cli --version
```

## Features

### 1. Watch Anime
- Search for anime in Ani-GUI
- Click "▶ Watch with ani-cli" to start streaming
- Select specific episodes
- Choose video quality (best, 1080p, 720p, 480p)

### 2. Continue Watching
- Resume from your watch history
- Click "⏯ Continue Watching" to resume last anime

### 3. Download Episodes
- Download episodes for offline viewing
- Select quality and episode count
- Downloaded files saved to your downloads folder

### 4. Quality Selection
- **Best**: Auto-select best available quality
- **1080p**: Full HD (if available)
- **720p**: HD quality
- **480p**: Mobile-friendly quality

### 5. Episode Selection
- Leave at 0 to stream/download all available
- Enter specific number to start from that episode
- Useful for continuing from a specific point

## How to Use

### Basic Workflow

1. **Search**: Type anime name in search box
2. **Select**: Click on anime in results
3. **Configure**: 
   - Choose quality from dropdown
   - Enter episode number (or leave at 0)
4. **Watch**: Click "▶ Watch with ani-cli"
5. **Enjoy**: Video plays in your terminal

### Example Scenarios

#### Watch Latest Episode in Best Quality
1. Search "Attack on Titan"
2. Click result
3. Leave episode at 0
4. Leave quality as "best"
5. Click "Watch with ani-cli"

#### Continue from Last Watched
1. Click any anime
2. Click "⏯ Continue Watching"
3. Window shows you'll resume from saved position

#### Download Specific Episode
1. Search anime
2. Click result
3. Set episode to specific number (e.g., 5)
4. Set quality (e.g., 720p)
5. Click "⬇ Download"

#### Watch in Low Quality (Mobile)
1. Search anime
2. Click result
3. Select "480p" from quality dropdown
4. Click "Watch with ani-cli"

## Video Player Integration

Ani-cli uses your system's default video player:
- **mpv** (recommended) - Lightweight, feature-rich
- **vlc** - Full-featured media player
- **totem** - GNOME default player

### Install a Video Player

```bash
# Install mpv (recommended)
sudo apt install mpv

# Or install VLC
sudo apt install vlc

# Or use GNOME Videos
sudo apt install gnome-videos
```

## Status Indicator

The application shows:
- **ani-cli version** when first selected
- **Current action** (watching, downloading, continuing)
- **Error messages** if something goes wrong
- **"Stopped"** when you click the Stop button

## Keyboard Shortcuts

In the video player window (depends on player):
- **Space**: Play/Pause
- **→/←**: Seek forward/backward
- **+/-**: Volume up/down
- **F**: Fullscreen
- **Q**: Quit player

See your player's documentation for full keybindings.

## Troubleshooting

### "ani-cli not found"
```bash
# Check if ani-cli is installed
which ani-cli

# If not installed, install it
git clone https://github.com/pystardust/ani-cli.git
cd ani-cli
sudo make install
```

### Application crashes when clicking Watch
- Ensure ani-cli is properly installed
- Check that a video player is installed (mpv, vlc, or totem)
- Try installing mpv: `sudo apt install mpv`

### "Episode selection" not working
- Make sure the anime has more episodes than selected
- Check ani-cli's output in the terminal
- Try without specifying episode (leave at 0)

### No subtitles appear
- Ani-cli provides subtitles if available from source
- Check your video player's subtitle settings
- Some shows may not have subtitles available

### Slow downloads or buffering
- Check your internet connection speed
- Try lower quality (480p or 720p)
- Close other applications using bandwidth

### Player doesn't start
- Verify video player is installed: `which mpv`
- Try installing mpv: `sudo apt install mpv`
- Check player works standalone: `mpv --version`

## Configuration

### Video Quality Preferences

Ani-cli automatically selects quality based on your choice:
- **best**: Uses ani-cli's default (usually highest available)
- **1080p**: Full HD resolution
- **720p**: HD resolution (good balance of quality/speed)
- **480p**: Lower quality (faster streaming)

### Episode Range

Ani-cli supports watching/downloading multiple episodes:
- **0** (default): All available episodes
- **1-5**: Episodes 1 through 5
- **10**: Starting from episode 10

## Advanced Usage

### Batch Download

To download multiple episodes at once:
1. Select anime
2. Set quality (e.g., 720p)
3. Set episode to desired range
4. Click "⬇ Download"

### Resuming Downloads

If a download is interrupted:
1. Click "⏯ Continue Watching"
2. Ani-cli will try to resume

### Using Different Providers

Ani-cli uses multiple anime providers. If one source fails:
- Try with different episode number
- Some episodes may be unavailable on certain providers
- Check ani-cli's output for source information

## Performance Tips

1. **Quality Selection**: Start with 720p if connection is slow
2. **Time of Day**: Peak hours may have slower streaming
3. **Download vs Stream**: Download for offline viewing if buffering
4. **Memory**: Close other applications for better performance

## Legal Disclaimer

- Ani-CLI streams content from public sources
- Ensure you have rights to watch content in your region
- The creators of Ani-GUI and ani-cli are not responsible for content
- Respect copyright and supporting official sources when possible

## For More Information

- **Ani-CLI GitHub**: https://github.com/pystardust/ani-cli
- **AniList**: https://anilist.co
- **MPV Player**: https://mpv.io
- **VLC Player**: https://www.videolan.org

## Support

If you encounter issues:

1. Check error messages in the status area
2. Verify ani-cli is installed correctly
3. Try running ani-cli directly: `ani-cli "anime name"`
4. Check logs: `ani-cli --logview`
5. Update ani-cli: `ani-cli --update`
