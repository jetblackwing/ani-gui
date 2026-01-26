# Quick Start: Streaming without rofi

## The Problem You Had
```
ani-cli: command not found: rofi
```

## How It's Fixed
✅ Created `ani-cli-wrapper.sh` that forces ani-cli to use **fzf** instead  
✅ fzf is already installed (`/usr/bin/fzf`)  
✅ Works exactly like rofi but text-based in terminal  

## How to Use

### Step 1: Launch the App
```bash
cd /home/amal/Documents/ani-gui
bash run.sh
```

### Step 2: Go to Watch Tab
- Click the "Watch & History" tab

### Step 3: Search for Anime
- Click the "🔍 Search" button
- A dialog appears

### Step 4: Enter Details
- **Anime Name**: Type anime name (e.g., "One Piece", "Naruto")
- **Episode**: Enter episode number (optional, leave 1 for auto)
- **Quality**: Select quality (Best/1080p/720p)

### Step 5: Stream
- Click "Stream" button
- A **terminal window** will appear with fzf menu
- Use arrow keys to select from available streams
- Press Enter to select
- mpv player opens automatically

### Step 6: Watch History
- After watching, check the "Watch & History" tab
- Your anime will be auto-added to history
- Can filter by category

## Important Details

### What's Happening Behind the Scenes
```
You click "Stream"
    ↓
GTK4 Dialog collects anime name
    ↓
ani-cli-wrapper.sh runs
    ↓
Sets use_external_menu="0" (forces fzf)
    ↓
Calls /usr/bin/ani-cli with your anime
    ↓
ani-cli searches AllAnime
    ↓
fzf shows menu in terminal (you select)
    ↓
mpv plays the video
    ↓
Watch history auto-updates
```

### Files Modified
- ✨ **ani-cli-wrapper.sh** (NEW) - Forces fzf usage
- ✏️ **src/anime_streamer.py** (MODIFIED) - Uses wrapper
- ✏️ **src/watch_interface.py** (MODIFIED) - Shows dialogs
- 📖 **WRAPPER_SETUP.md** (NEW) - Full technical details

## Troubleshooting

### If streaming still doesn't work:

**Check 1: Wrapper exists**
```bash
ls -la ~/Documents/ani-gui/ani-cli-wrapper.sh
# Should show: -rwxr-xr-x
```

**Check 2: fzf installed**
```bash
which fzf
# Should show: /usr/bin/fzf
```

**Check 3: Test manually**
```bash
cd ~/Documents/ani-gui
bash ani-cli-wrapper.sh "One Piece"
# Should show fzf menu in terminal
```

**Check 4: Check ani-cli**
```bash
which ani-cli
# Should show: /usr/bin/ani-cli
```

## Key Differences from Original

| Feature | Before | Now |
|---------|--------|-----|
| Menu system | rofi (GUI) ❌ | fzf (terminal) ✅ |
| Dependency | Requires rofi | Uses fzf (included) |
| Method | Failed silently | Works with wrapper |
| User experience | Blocked | Fully functional |

## No Extra Installation Needed!
- ani-cli: ✅ Already installed
- fzf: ✅ Already installed
- mpv: ✅ Already installed
- Everything: ✅ Ready to go!

## Next Steps
1. Run `bash run.sh`
2. Click "Search" in Watch & History tab
3. Enter anime name like "Attack on Titan"
4. Select episode and quality
5. Enjoy! 🎬

## Support
If you still have issues, check [WRAPPER_SETUP.md](WRAPPER_SETUP.md) for detailed technical documentation.
