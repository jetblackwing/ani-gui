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
        
        # Video area (embedded in app)
        self.video_frame = Gtk.Frame(
            hexpand=True,
            vexpand=True,
            margin_start=10,
            margin_end=10
        )
        self.picture = Gtk.Picture(hexpand=True, vexpand=True)
        self.video_frame.set_child(self.picture)
        self.append(self.video_frame)
        
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
        self.pipeline.connect("source-setup", self.on_source_setup)
        self.using_embedded_sink = self._setup_video_sink()

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        
        self.on_close_callback = None
        self.xid = None
        self.play_button.set_sensitive(False)
        self.pause_button.set_sensitive(False)

        if not self.using_embedded_sink:
            self.title_label.set_text("Video Player (install gtk4paintablesink for embedded playback)")

    def _setup_video_sink(self) -> bool:
        """Configure an embedded GTK4 sink if available."""
        sink = Gst.ElementFactory.make("gtk4paintablesink", "gtk4sink")
        if not sink:
            print("[GStreamerPlayer] gtk4paintablesink not available")
            return False

        self.pipeline.set_property("video-sink", sink)
        paintable = sink.get_property("paintable")
        if paintable:
            self.picture.set_paintable(paintable)
        return True

    def on_source_setup(self, playbin, source):
        """Set source headers so streams that require referer keep working."""
        try:
            if source.find_property("user-agent"):
                source.set_property("user-agent", "Mozilla/5.0")
            if source.find_property("referer"):
                source.set_property("referer", "https://allmanga.to")
        except Exception as e:
            print(f"[GStreamerPlayer] source setup warning: {e}")
    
    def play(self, url: str, title: str):
        """Play video from URL inside the application."""
        self.title_label.set_text("⏳ Starting playback...")
        
        try:
            # Validate URL
            if not url or not url.startswith("http"):
                self.title_label.set_text(f"❌ Invalid stream URL")
                print(f"[GStreamerPlayer] Invalid URL: {url}")
                return

            print(f"[GStreamerPlayer] Starting embedded playback: {url[:80]}...")
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline.set_property("uri", url)
            self.pipeline.set_state(Gst.State.PLAYING)

            self.title_label.set_text(f"▶️ {title}")
            self.play_button.set_sensitive(False)
            self.pause_button.set_sensitive(True)

        except Exception as e:
            print(f"[GStreamerPlayer] Error: {e}")
            self.title_label.set_text(f"❌ Error: {str(e)[:50]}")
    
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
            self.play_button.set_sensitive(True)
            self.pause_button.set_sensitive(False)
        elif msg_type == Gst.MessageType.EOS:
            # End of stream
            self.pipeline.set_state(Gst.State.NULL)
            self.title_label.set_text("✅ Playback finished")
            self.play_button.set_sensitive(True)
            self.pause_button.set_sensitive(False)
            if self.on_close_callback:
                self.on_close_callback()
    
    def set_on_close_callback(self, callback: Callable):
        """Set callback for when player closes."""
        self.on_close_callback = callback
