# gstreamer_player.py
#
# Copyright 2024 Amal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
GStreamer video player with playbin.
"""

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gst, GstVideo, GLib
from typing import Optional, Callable
import os
import subprocess

# Initialize GStreamer
Gst.init(None)


class GStreamerPlayer(Gtk.Box):
    """Video player using GStreamer playbin."""
    
    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )
        
        # Title bar
        title_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin_start=10,
            margin_end=10,
            margin_top=10
        )
        
        self.title_label = Gtk.Label(
            label="Video Player",
            css_classes=["heading"]
        )
        self.title_label.set_hexpand(True)
        title_box.append(self.title_label)
        
        fullscreen_button = Gtk.Button(label="⛶ Fullscreen")
        fullscreen_button.connect("clicked", self.on_fullscreen_clicked)
        title_box.append(fullscreen_button)
        
        close_button = Gtk.Button(label="✕ Close")
        close_button.connect("clicked", self.on_close_clicked)
        title_box.append(close_button)
        
        self.append(title_box)
        
        # Video drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.append(self.drawing_area)
        
        # Controls
        controls = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin_start=10,
            margin_end=10,
            margin_bottom=10
        )
        
        self.play_button = Gtk.Button(label="▶ Play")
        self.play_button.connect("clicked", self.on_play_clicked)
        controls.append(self.play_button)
        
        self.pause_button = Gtk.Button(label="⏸ Pause")
        self.pause_button.connect("clicked", self.on_pause_clicked)
        controls.append(self.pause_button)
        
        self.stop_button = Gtk.Button(label="⏹ Stop")
        self.stop_button.connect("clicked", self.on_stop_clicked)
        controls.append(self.stop_button)
        
        self.append(controls)
        
        # GStreamer pipeline
        self.pipeline = Gst.ElementFactory.make("playbin", "player")
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        
        self.on_close_callback = None
        self.xid = None
        
        # Get window ID when drawing area is realized
        self.drawing_area.connect("realize", self.on_realize)
    
    def on_realize(self, widget):
        """Get drawing area window ID for video output."""
        try:
            surface = widget.get_native().get_surface()
            if surface and hasattr(surface, '__gpointer__'):
                self.xid = hash(surface) & 0x7fffffff
        except Exception as e:
            print(f"[GStreamerPlayer] Warning: Could not get window ID: {e}")
    
    def play(self, url: str, title: str):
        """Play video from URL using mpv (which handles referrers better)."""
        self.title_label.set_text(f"⏳ Starting playback...")
        
        try:
            # Validate URL
            if not url or not url.startswith("http"):
                self.title_label.set_text(f"❌ Invalid stream URL")
                print(f"[GStreamerPlayer] Invalid URL: {url}")
                return
            
            # Use mpv for playback (handles referrers and various stream types better)
            import subprocess
            import threading
            
            def play_thread():
                try:
                    cmd = [
                        "mpv",
                        "--referrer=https://allmanga.to",
                        f"--title={title}",
                        url
                    ]
                    
                    print(f"[GStreamerPlayer] Playing with mpv: {url[:80]}...")
                    
                    result = subprocess.run(cmd, timeout=3600)  # 1 hour timeout
                    
                    GLib.idle_add(lambda: self.title_label.set_text(f"✅ Playback finished"))
                    
                except FileNotFoundError:
                    print(f"[GStreamerPlayer] mpv not found")
                    GLib.idle_add(lambda: self.title_label.set_text(f"❌ mpv not installed"))
                except subprocess.TimeoutExpired:
                    print(f"[GStreamerPlayer] Playback timeout")
                except Exception as e:
                    print(f"[GStreamerPlayer] Playback error: {e}")
                    GLib.idle_add(lambda: self.title_label.set_text(f"❌ Error: {str(e)[:40]}"))
            
            thread = threading.Thread(target=play_thread, daemon=True)
            thread.start()
            
            GLib.idle_add(lambda: self.title_label.set_text(f"▶️ {title}"))
            
        except Exception as e:
            print(f"[GStreamerPlayer] Error: {e}")
            self.title_label.set_text(f"❌ Error: {str(e)[:50]}")
    
    def set_window_handle(self):
        """Set the window handle for video output."""
        try:
            # Get the X11 window ID
            surface = self.drawing_area.get_native().get_surface()
            if surface:
                # Set the window handle on the video sink
                bus = self.pipeline.get_bus()
                if bus:
                    msg = Gst.Message.new_application(
                        self.pipeline,
                        Gst.Structure.new_empty("gst-window-handle")
                    )
        except:
            pass
    
    def on_play_clicked(self, button):
        """Play."""
        self.pipeline.set_state(Gst.State.PLAYING)
        self.play_button.set_sensitive(False)
        self.pause_button.set_sensitive(True)
    
    def on_fullscreen_clicked(self, button):
        """Toggle fullscreen."""
        root = self.get_root()
        if isinstance(root, Gtk.Window):
            if root.is_fullscreen():
                root.unfullscreen()
            else:
                root.fullscreen()
    
    def on_pause_clicked(self, button):
        """Pause."""
        self.pipeline.set_state(Gst.State.PAUSED)
        self.play_button.set_sensitive(True)
        self.pause_button.set_sensitive(False)
    
    def on_stop_clicked(self, button):
        """Stop."""
        self.pipeline.set_state(Gst.State.NULL)
        self.play_button.set_sensitive(True)
        self.pause_button.set_sensitive(False)
        
        if self.on_close_callback:
            self.on_close_callback()
    
    def on_close_clicked(self, button):
        """Close player."""
        self.pipeline.set_state(Gst.State.NULL)
        
        if self.on_close_callback:
            self.on_close_callback()
    
    def on_message(self, bus, message):
        """Handle GStreamer messages."""
        msg_type = message.type
        
        if msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"[GStreamerPlayer] Error: {err}")
            self.title_label.set_text(f"❌ Playback error: {err.message}")
        elif msg_type == Gst.MessageType.EOS:
            # End of stream
            self.pipeline.set_state(Gst.State.NULL)
            if self.on_close_callback:
                self.on_close_callback()
    
    def set_on_close_callback(self, callback: Callable):
        """Set callback for when player closes."""
        self.on_close_callback = callback
