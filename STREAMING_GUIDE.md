# Anime Streaming Without Rofi - Complete Guide

## Problem Solved
**Issue**: ani-cli required rofi (GUI selector menu), which wasn't available
**Solution**: Implemented direct ani-cli integration with fzf (terminal-based selector) + GTK4 dialogs

## Architecture

### AnimeStreamer (src/anime_streamer.py)
- **Direct ani-cli wrapper** - no intermediate API calls
- **Uses fzf** - terminal-based menu selection (already installed)
- **Environment-based config** - forces ani-cli to use fzf instead of rofi
- **Streaming flow**:
  1. User enters anime name in GTK4 dialog
  2. User selects episode number (optional)
  3. User selects video quality (best/720p/1080p)
  4. ani-cli runs with these parameters
  5. ani-cli uses fzf to let user select from available streams
  6. mpv plays the selected stream
  7. Watch history auto-updates

### Modified Components

#### watch_interface.py
- **SearchResultsDialog**: Now a simple input dialog for anime name + episode + quality
- **WatchInterfaceWidget**: Simplified to use direct anime name input
- **No complex result parsing** - ani-cli handles all menu interactions

#### No rofi dependency needed!
```
Old flow:  GTK Dialog → ani-cli → rofi (MISSING) ✗
New flow:  GTK Dialog → ani-cli → fzf (AVAILABLE) ✓
```

## How to Use

### Via GUI (Recommended)
1. Launch the application: `bash run.sh`
2. Go to "Watch & History" tab
3. Click the "🔍 Search" button
4. Enter anime name (e.g., "One Piece", "Attack on Titan")
5. Optionally enter episode number
6. Select video quality
7. Click "Stream"
8. fzf selection menu appears in terminal (if multiple options)
9. mpv opens and streams the anime
10. History auto-updates when watching completes

### Key Features
✅ **No rofi required** - uses fzf instead  
✅ **GTK4 interface** - native GUI dialogs  
✅ **Watch history** - automatic tracking with categories  
✅ **Quality selection** - best/720p/1080p options  
✅ **Episode selection** - optional, can also select during playback  
✅ **Full ani-cli support** - all original features work  

## Technology Stack

### Streaming
- **ani-cli v4.10.0** - anime streaming backend
- **fzf** - terminal-based fuzzy selector (replaces rofi)
- **mpv** - video player with fullscreen support

### Application
- **GTK 4.0** - GUI framework
- **Python 3** - application runtime
- **GLib** - event loop for async operations

## File Structure
```
src/
├── anime_streamer.py      (NEW) Simple ani-cli wrapper with fzf
├── watch_interface.py     (MODIFIED) Simplified for direct streaming
├── watch_history.py       (NEW) Persistent watch history
├── window.py              (MODIFIED) Tabbed interface
└── ... (other modules)
```

## Configuration

### Environment Variables (Auto-configured)
- `use_external_menu=0` - Forces ani-cli to use fzf instead of rofi
- `FZF_DEFAULT_OPTS` - Can be customized for fzf appearance

### Watch History Location
- **File**: `~/.local/share/ani-gui/watch_history.json`
- **Format**: JSON with anime ID, title, episode, categories, timestamps
- **Auto-synced**: Updates after each viewing session

## Troubleshooting

### "Command not found" errors
Ensure these are installed:
```bash
sudo apt install ani-cli fzf mpv
```

### fzf not appearing
- fzf requires terminal access
- Make sure terminal is available (not detached)
- Check: `which fzf` should show `/usr/bin/fzf`

### mpv not opening
- Check: `which mpv` should show path to mpv
- Ensure X11/Wayland display is available

### ani-cli streaming issues
- ani-cli itself may have temporary API issues
- Try different anime names
- Check internet connection

## Performance Notes
- **First run**: May take 1-2 seconds for ani-cli to search
- **Stream loading**: Depends on internet speed and provider
- **History sync**: Instant (JSON file write)

## Future Enhancements
- [ ] Direct streaming provider selection in GUI
- [ ] Built-in fullscreen player (GTK4 via mpv)
- [ ] Download episodes feature
- [ ] Batch episode watching
- [ ] Custom fzf themes
- [ ] Multiple provider support UI

## Credits
- **ani-cli**: Original anime streaming CLI tool
- **fzf**: Fuzzy finder selector
- **mpv**: Powerful video player
- **AllAnime**: Streaming data source (via ani-cli)

## License
GNU General Public License v3.0 or later (same as ani-gui)
