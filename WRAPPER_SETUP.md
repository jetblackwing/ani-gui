# ani-cli Wrapper Setup

## Problem & Solution

**Problem**: ani-cli tries to use `rofi` for interactive menus, but rofi isn't installed  
**Solution**: `ani-cli-wrapper.sh` forces ani-cli to use `fzf` instead (which is installed)

## How It Works

### ani-cli-wrapper.sh
```bash
#!/bin/bash
# Checks if rofi is available
# If NOT found → forces fzf
# If found → still prefers fzf for better compatibility
# Calls /usr/bin/ani-cli with all arguments
```

### Key Points
✅ **Transparent**: Acts as a drop-in replacement for ani-cli  
✅ **Environment-based**: Sets `use_external_menu=0` to force fzf  
✅ **Fallback handling**: Checks for fzf availability  
✅ **Error messages**: Shows helpful errors if dependencies missing  

## Integration with ani-gui

The `AnimeStreamer` class automatically:
1. Detects the wrapper script location
2. Uses wrapper if available, otherwise falls back to /usr/bin/ani-cli
3. Sets environment variables to ensure fzf is used
4. Handles interactive terminal I/O properly

## Usage

### Via GUI
1. Run `bash run.sh`
2. Go to "Watch & History" tab
3. Click "Search" button
4. Enter anime name (e.g., "One Piece")
5. Select episode (optional) and quality
6. Click "Stream"
7. **fzf appears in terminal** → select from menu → mpv plays

### Manual Testing
```bash
# Test wrapper directly
./ani-cli-wrapper.sh "anime name"

# Test with specific episode
./ani-cli-wrapper.sh -e 1 "anime name"

# Test with quality
./ani-cli-wrapper.sh -q 720p "anime name"
```

## Requirements

Must have these installed:
- **ani-cli** - `/usr/bin/ani-cli` (already installed)
- **fzf** - terminal fuzzy finder (`/usr/bin/fzf`)
- **mpv** - video player (`/usr/bin/mpv`)

Verify with:
```bash
which ani-cli fzf mpv
```

## Debugging

If you see "rofi not found" error:

1. **Check wrapper exists**:
   ```bash
   ls -la ~/Documents/ani-gui/ani-cli-wrapper.sh
   ```

2. **Check wrapper executable**:
   ```bash
   bash ~/Documents/ani-gui/ani-cli-wrapper.sh --version
   ```

3. **Check fzf available**:
   ```bash
   which fzf
   ```

4. **Test ani-cli directly**:
   ```bash
   export use_external_menu="0"
   /usr/bin/ani-cli "test"
   ```

## Technical Details

### Environment Variable
- `use_external_menu=0` → uses fzf
- `use_external_menu=1` → uses rofi (which fails here)

### ani-cli Bash Code (relevant part)
```bash
launcher() {
    [ "$use_external_menu" = "0" ] && fzf "$1" --reverse --cycle --prompt "$2"
    [ "$use_external_menu" = "1" ] && external_menu "$1" "$2" "$external_menu_args"
}
```

Our wrapper ensures `use_external_menu=0` is always set.

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Wrapper | `./ani-cli-wrapper.sh` | Forces fzf usage |
| AnimeStreamer | `./src/anime_streamer.py` | Uses wrapper |
| Watch UI | `./src/watch_interface.py` | Calls AnimeStreamer |
| Main App | `./run.sh` | Starts everything |

## Status

✅ Wrapper installed  
✅ AnimeStreamer configured  
✅ fzf available  
✅ Ready to stream  

**No rofi needed!**
