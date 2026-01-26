# Ani-GUI - Quick Reference Card

## 📱 User Interface Layout

```
┌─────────────────────────────────────────────────────┐
│ Ani-GUI - Anime Streaming                    [≡]   │  ← Title Bar
├─────────────────────────────────────────────────────┤
│  🔍 [Search anime by title...        ]              │  ← Search Bar
├──────────────────────┬───────────────────────────────┤
│                      │                               │
│  Search Results      │ 🎬 Video Player               │
│  ┌─────────────────┐ │                               │
│  │ ┌─────────────┐ │ │ Title: Jujutsu Kaisen        │
│  │ │  [Thumb]    │ │ │                               │
│  │ │ Jujutsu     │ │ │ Episodes: 48 • Status: Done  │
│  │ │ Kaisen      │ │ │ Genres: Action, Supernatural │
│  │ │ Dark, gory  │ │ │ Rating: 86/100               │
│  │ │ Ep: 48 ⭐86│ │ │                               │
│  │ └─────────────┘ │ │ [Play with System Player]    │
│  │                 │ │ [Open with Web Browser]      │
│  │ ┌─────────────┐ │ │ [Clear]                      │
│  │ │  [Thumb]    │ │ │                               │
│  │ │ Attack on   │ │ │                               │
│  │ │ Titan       │ │ │                               │
│  │ │ Dark, epic  │ │ │                               │
│  │ │ Ep: 139 ⭐95│ │ │                               │
│  │ └─────────────┘ │ │                               │
│  │  (scroll...)    │ │                               │
│  └─────────────────┘ │                               │
├──────────────────────┴───────────────────────────────┤
│ [← Previous]         [Next →]                        │  ← Pagination
└──────────────────────────────────────────────────────┘
```

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Quit | Ctrl+Q |
| Focus Search | Ctrl+F |
| Next Page | Alt+Right |
| Previous Page | Alt+Left |
| Show Help | Ctrl+? |
| Show Menu | F10 |

## 🔌 API Integration

```
┌────────────────────────────────────────┐
│   AniList GraphQL API                  │
│   graphql.anilist.co                   │
├────────────────────────────────────────┤
│ SearchAnime Query                      │
│ ├─ Input: query string, page number   │
│ └─ Output: 12 anime results             │
│                                         │
│ GetAnime Query                          │
│ ├─ Input: anime ID                      │
│ └─ Output: Full anime details           │
│                                         │
│ Cover Image CDN                         │
│ ├─ AniList: s4.anilist.co/...         │
│ └─ Cached locally (MD5 hash)           │
└────────────────────────────────────────┘
```

## 💾 Cache System

```
~/.cache/ani-gui/
└── thumbnails/
    ├── 5d41402abc4b2a76b9719d911017c592.jpg  (150x225)
    ├── 6512bd43d9caa6e02c990b0a82652dca.jpg  (150x225)
    ├── 5f4dcc3b5aa765d61d8327deb882cf99.jpg  (150x225)
    └── ... (one per unique image)
```

## 🔄 Data Flow Diagram

```
User Input
   ↓
[Window: search text entered]
   ↓
[SearchHandler: async search in thread]
   ↓
[AniListAPI: GraphQL request]
   ↓
[Response: 12 anime + page info]
   ↓
[Main thread: display results]
   ├─→ [For each result: load thumbnail]
   │     ├─→ [ThumbnailCache: check local]
   │     ├─→ [If missing: download from CDN]
   │     └─→ [Scale: 150x225, cache, display]
   │
   └─→ [Create AnimeSearchRow widgets]
        └─→ [Display with thumbnail]
```

## 📦 Python Module Dependencies

```
main.py
  └─→ window.py
       ├─→ search_handler.py
       │    ├─→ anilist_api.py (requests)
       │    └─→ thumbnail_cache.py (requests, threading)
       │
       └─→ video_player.py
            └─→ anilist_api.py (subprocess)

External:
  ├─ requests (HTTP/GraphQL)
  ├─ PyGObject (GTK bindings)
  ├─ threading (background tasks)
  └─ GLib (main thread callbacks)
```

## 🎨 Theme & Styling

All widgets use GTK4 standard CSS classes:

| Component | CSS Classes |
|-----------|------------|
| Search Bar | `.search` |
| Section Titles | `.heading`, `.title-1`, `.title-2` |
| Disabled Text | `.dim-label` |
| Cards/Frames | `.card` |
| Buttons | (standard GTK defaults) |

## ⚙️ Configuration Files

```
meson.build          ← Project metadata
src/meson.build      ← Python module installation
data/
├── com.ajk.anigui.desktop.in     ← Desktop entry
├── com.ajk.anigui.gschema.xml    ← Settings schema
└── com.ajk.anigui.metainfo.xml   ← App info
```

## 🚨 Error Handling

```
Network Error
  └─→ requests.RequestException → Log & return None
      
API Error  
  └─→ GraphQL errors → Log & return empty results
  
Missing Player
  └─→ No player found → Show AlertDialog

Cache Error
  └─→ File not found → Download again
```

## 🧵 Threading Model

```
Main Thread (GTK)
  │
  ├─→ Search Thread (daemon)
  │     └─→ GLib.idle_add() callback
  │
  └─→ Thumbnail Thread (per image, daemon)
        └─→ GLib.idle_add() callback
```

All GLib callbacks ensure thread-safe UI updates!

## 📊 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Search | 0.5-2s | Network dependent |
| Load 12 thumbnails | 2-5s | First time; cached after |
| UI Response | <100ms | All async operations |
| Memory per result | ~2MB | Pixbuf cached on disk |
| Cache Size | ~5-10MB | Per 50 anime covers |

## 🎯 Common Use Cases

### Case 1: Search & Browse
```
1. Launch ani-gui
2. Type "Demon Slayer"
3. Click result
4. View details
5. Pagination if needed
```

### Case 2: Play Anime
```
1. Search anime
2. Click result
3. Provide streaming URL (future)
4. Click Play
5. mpv launches
```

### Case 3: Visit AniList
```
1. Search anime
2. Click result  
3. Click "Open with Web Browser"
4. Browser opens anime page
```

## 🔗 Useful Links

- **AniList Website**: https://anilist.co
- **AniList API Docs**: https://anilist.gitbook.io/
- **GTK4 Docs**: https://docs.gtk.org/gtk4/
- **PyGObject Docs**: https://pygobject.readthedocs.io/

## 📋 Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| No results | Check internet; try "Naruto" |
| No images | Delete ~/.cache/ani-gui/thumbnails/ |
| Frozen UI | Should never happen (async) |
| No video player | `sudo apt install mpv` |
| Import errors | `pip install --user -r requirements.txt` |

## 🎓 Development Cheatsheet

```python
# Add new search field
self.api.SEARCH_QUERY += "newField\n"

# Change thumbnail size
ThumbnailCache.get_cached_pixbuf(url, width=300, height=450)

# Add new button
btn = Gtk.Button(label="Click me")
btn.connect("clicked", self.on_click)
container.append(btn)

# Run async task
GLib.idle_add(callback, result)

# Make box grow
box.set_hexpand(True)
box.set_vexpand(True)
```

---

**Keep this handy while developing!** Refer to full docs in:
- QUICKSTART.md - User guide
- ARCHITECTURE.md - Technical deep-dive  
- IMPLEMENTATION.md - What was built
