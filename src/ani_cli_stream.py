#!/usr/bin/env python3
"""
Stream anime using ani-cli and extract actual stream URLs.
"""

import subprocess
import json
import re
from typing import Optional
import tempfile
import os


class AniCliStreamer:
    """Use ani-cli to get streaming URLs."""
    
    def __init__(self):
        self.ani_cli_path = "/usr/bin/ani-cli"
    
    def get_stream_url(self, anime_name: str, ep_no: str) -> Optional[str]:
        """Get stream URL using ani-cli.
        
        Args:
            anime_name: Name of anime
            ep_no: Episode number (string like "1", "12", etc)
        
        Returns:
            Stream URL or None if not found
        """
        try:
            # Create a temporary script that ani-cli will call
            # We use mpv wrapper to capture the URL before playback
            script_dir = tempfile.gettempdir()
            wrapper_script = os.path.join(script_dir, "ani_stream_wrapper.sh")
            
            # Create wrapper script
            with open(wrapper_script, 'w') as f:
                f.write("""#!/bin/bash
# Wrapper to capture streaming URL
# This will be called by ani-cli with the actual video URL
echo "$1" > /tmp/ani_last_stream_url.txt
# Don't actually play it - ani-cli will handle it
exit 1
""")
            
            os.chmod(wrapper_script, 0o755)
            
            # Use ani-cli to search and get the episode link
            # We use --quality best to ensure good quality
            cmd = [
                self.ani_cli_path,
                "--quality", "best",
                "--select-nth", ep_no,
                anime_name
            ]
            
            # Run in non-interactive mode
            # ani-cli will try to play with mpv, but we capture the URL
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env={**os.environ, "ROFI_COMMAND": "/usr/bin/fzf"}
                )
            except subprocess.TimeoutExpired:
                pass  # It's OK if it times out, we might have the URL
            
            # Check if we captured a URL
            if os.path.exists("/tmp/ani_last_stream_url.txt"):
                with open("/tmp/ani_last_stream_url.txt", 'r') as f:
                    url = f.read().strip()
                    if url and url.startswith("http"):
                        print(f"[AniCliStreamer] Got URL: {url[:80]}...")
                        return url
            
            # If ani-cli output contains a URL, extract it
            if result.stdout:
                # Look for m3u8 or http links in output
                urls = re.findall(r'https?://[^\s]+', result.stdout)
                if urls:
                    return urls[0]
            
            print(f"[AniCliStreamer] Failed to get URL for {anime_name} Ep{ep_no}")
            return None
        
        except FileNotFoundError:
            print(f"[AniCliStreamer] ani-cli not found at {self.ani_cli_path}")
            return None
        except Exception as e:
            print(f"[AniCliStreamer] Error: {e}")
            return None
