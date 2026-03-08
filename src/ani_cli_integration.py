# ani_cli_integration.py
#
# Copyright 2024 Amal J Krishnan <amaljk80@gmail.com> (@jetblackwing)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import threading
from typing import Optional, Callable
import shutil

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


class AniCliIntegration:
    """Integration with ani-cli bash program for anime watching."""
    
    def __init__(self):
        self.ani_cli_path = shutil.which('ani-cli')
        self.current_process = None
        self.is_watching = False
    
    def is_available(self) -> bool:
        """Check if ani-cli is installed."""
        return self.ani_cli_path is not None
    
    def get_version(self) -> Optional[str]:
        """Get the ani-cli version."""
        try:
            result = subprocess.run([self.ani_cli_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.stdout:
                return result.stdout.strip()
            elif result.stderr:
                return result.stderr.strip()
            return "Unknown"
        except Exception as e:
            return f"Error: {e}"
    
    def watch_anime(self, anime_name: str, episode: Optional[int] = None,
                   quality: str = "best", callback: Optional[Callable] = None,
                   terminal_output_callback: Optional[Callable] = None):
        """Launch ani-cli to watch an anime.
        
        Args:
            anime_name: Name of the anime to watch
            episode: Optional specific episode number
            quality: Video quality (best, 720p, 1080p, etc)
            callback: Callback function for completion (success, error_msg)
            terminal_output_callback: Callback for terminal output (line)
        """
        if not self.is_available():
            if callback:
                GLib.idle_add(callback, False, "ani-cli not found. Install it with: sudo apt install ani-cli")
            return
        
        if self.is_watching:
            if callback:
                GLib.idle_add(callback, False, "Already watching an anime")
            return
        
        self.is_watching = True
        
        def watch_thread():
            try:
                # Build ani-cli command
                cmd = [self.ani_cli_path]
                
                if quality and quality != "best":
                    cmd.extend(['-q', quality])
                
                if episode and episode > 0:
                    cmd.extend(['-e', str(episode)])
                
                # Add anime name at the end
                cmd.append(anime_name)
                
                # Start the process
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Read output
                stdout_data = []
                stderr_data = []
                
                # Read stdout
                if self.current_process.stdout:
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line:
                            stdout_data.append(line.strip())
                            if terminal_output_callback:
                                GLib.idle_add(terminal_output_callback, line.strip(), 'stdout')
                
                # Wait for process to finish
                self.current_process.wait()
                
                # Read stderr if any
                if self.current_process.stderr:
                    stderr_output = self.current_process.stderr.read()
                    if stderr_output:
                        stderr_data.append(stderr_output)
                        if terminal_output_callback:
                            GLib.idle_add(terminal_output_callback, stderr_output, 'stderr')
                
                # Check return code
                success = self.current_process.returncode == 0
                error_msg = ' '.join(stderr_data) if stderr_data else None
                
                if callback:
                    GLib.idle_add(callback, success, error_msg)
            
            except Exception as e:
                print(f"Error running ani-cli: {e}")
                if callback:
                    GLib.idle_add(callback, False, str(e))
            
            finally:
                self.is_watching = False
                self.current_process = None
        
        thread = threading.Thread(target=watch_thread, daemon=True)
        thread.start()
    
    def continue_watching(self, callback: Optional[Callable] = None,
                         terminal_output_callback: Optional[Callable] = None):
        """Continue watching from history using ani-cli -c.
        
        Args:
            callback: Callback function for completion
            terminal_output_callback: Callback for terminal output
        """
        if not self.is_available():
            if callback:
                GLib.idle_add(callback, False, "ani-cli not found")
            return
        
        if self.is_watching:
            if callback:
                GLib.idle_add(callback, False, "Already watching")
            return
        
        self.is_watching = True
        
        def continue_thread():
            try:
                cmd = [self.ani_cli_path, '-c']
                
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Read output
                if self.current_process.stdout:
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line:
                            if terminal_output_callback:
                                GLib.idle_add(terminal_output_callback, line.strip(), 'stdout')
                
                self.current_process.wait()
                success = self.current_process.returncode == 0
                
                if callback:
                    GLib.idle_add(callback, success, None)
            
            except Exception as e:
                if callback:
                    GLib.idle_add(callback, False, str(e))
            
            finally:
                self.is_watching = False
                self.current_process = None
        
        thread = threading.Thread(target=continue_thread, daemon=True)
        thread.start()
    
    def download_anime(self, anime_name: str, episode: Optional[int] = None,
                      quality: str = "best", callback: Optional[Callable] = None):
        """Download anime using ani-cli -d.
        
        Args:
            anime_name: Name of the anime
            episode: Optional episode number
            quality: Video quality
            callback: Callback function (success, message)
        """
        if not self.is_available():
            if callback:
                GLib.idle_add(callback, False, "ani-cli not found")
            return
        
        if self.is_watching:
            if callback:
                GLib.idle_add(callback, False, "Already downloading/watching")
            return
        
        self.is_watching = True
        
        def download_thread():
            try:
                cmd = [self.ani_cli_path, '-d']
                
                if quality and quality != "best":
                    cmd.extend(['-q', quality])
                
                if episode and episode > 0:
                    cmd.extend(['-e', str(episode)])
                
                cmd.append(anime_name)
                
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.current_process.wait()
                success = self.current_process.returncode == 0
                msg = "Download completed successfully"
                
                if callback:
                    GLib.idle_add(callback, success, msg)
            
            except Exception as e:
                if callback:
                    GLib.idle_add(callback, False, str(e))
            
            finally:
                self.is_watching = False
                self.current_process = None
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def stop_watching(self):
        """Stop the current ani-cli process."""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except Exception as e:
                print(f"Error stopping ani-cli: {e}")
                try:
                    self.current_process.kill()
                except:
                    pass
            finally:
                self.current_process = None
                self.is_watching = False
    
    def search_anime_interactive(self, query: str, callback: Optional[Callable] = None):
        """Search anime using ani-cli and get all results interactively.
        
        Shows menu of search results and lets user select one.
        
        Args:
            query: Search query string
            callback: Callback function (selected_anime_name, cancelled)
        """
        if not self.is_available():
            if callback:
                GLib.idle_add(callback, None, "ani-cli not found")
            return
        
        def search_thread():
            try:
                # Use ani-cli in non-interactive mode to search
                # We'll try to get the list by searching
                cmd = [self.ani_cli_path, query]
                
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Read available anime from output
                stdout_lines = []
                if self.current_process.stdout:
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line.strip():
                            stdout_lines.append(line.strip())
                
                # Try to extract anime list from output
                anime_list = [line for line in stdout_lines if line and not line.startswith('[')]
                
                if callback:
                    GLib.idle_add(callback, anime_list, None)
            
            except Exception as e:
                print(f"Error searching: {e}")
                if callback:
                    GLib.idle_add(callback, None, str(e))
            
            finally:
                self.current_process = None
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
