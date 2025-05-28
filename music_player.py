import os
import json
import pygame
from pathlib import Path
from difflib import get_close_matches

class MusicPlayer:
    def __init__(self):
        # Load config file
        self.config = self.load_config()
        
        # Start pygame
        pygame.init()
        print("Debug: Pygame initialized")
        
        # Start pygame mixer
        try:
            pygame.mixer.quit()  # Clean previous mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            print("Debug: Pygame mixer successfully initialized")
            print(f"Debug: Audio system status: {pygame.mixer.get_init()}")
        except Exception as e:
            print(f"Debug: Error initializing pygame mixer: {str(e)}")
            raise Exception("Audio system could not be started. Please check your audio drivers.")
        
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        
        # Get settings from config
        self.volume = self.config["music_settings"]["default_volume"]
        self.music_dir = Path(self.config["music_settings"]["music_directory"])
        self.supported_formats = self.config["music_settings"]["supported_formats"]
        
        # Create music folder
        self.music_dir.mkdir(exist_ok=True)
        
        # Set volume level
        pygame.mixer.music.set_volume(self.volume)
        print(f"Debug: Initial volume level: {self.volume}")

    def load_config(self):
        """Loads config file"""
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {
                "music_settings": {
                    "default_volume": 1.0,
                    "supported_formats": [".mp3", ".wav", ".ogg"],
                    "music_directory": "music"
                }
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            return default_config

    def save_config(self):
        """Saves config file"""
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def get_available_songs(self):
        """Lists all songs in music folder (as file names)."""
        songs = []
        if self.music_dir.exists() and self.music_dir.is_dir():
            for file in os.listdir(self.music_dir):
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    songs.append(file)
        return sorted(songs) # Sort alphabetically

    def find_song(self, search_term, available_songs_list):
        """
        Finds best match for search term in given song list.
        First searches for exact name (without extension), then checks if contained,
        then uses difflib.get_close_matches for similarity.
        """
        if not available_songs_list:
            return None

        search_term_lower = search_term.lower()

        # 1. Exact match (without extension)
        for song_file in available_songs_list:
            song_name_without_ext = os.path.splitext(song_file)[0].lower()
            if song_name_without_ext == search_term_lower:
                return song_file

        # 2. Search term contained in song name (without extension)
        containing_matches = []
        for song_file in available_songs_list:
            song_name_without_ext = os.path.splitext(song_file)[0].lower()
            if search_term_lower in song_name_without_ext:
                containing_matches.append(song_file)
        
        if containing_matches:
            # Return shortest match (usually more specific)
            return min(containing_matches, key=len)

        # 3. Similarity with difflib
        # Create list of song names without extensions
        song_names_without_ext_list = [os.path.splitext(s)[0] for s in available_songs_list]
        close_matches = get_close_matches(search_term, song_names_without_ext_list, n=1, cutoff=0.6)
        
        if close_matches:
            # Found matching name without extension, now find original file name
            matched_name_without_ext = close_matches[0]
            for original_song_file in available_songs_list:
                if os.path.splitext(original_song_file)[0] == matched_name_without_ext:
                    return original_song_file
        
        return None

    def play_music(self, song_identifier):
        """
        Plays specified song.
        song_identifier can be song name, partial name, or number in list.
        """
        available_songs = self.get_available_songs()
        if not available_songs:
            return False, "No songs found in music folder to play."

        song_to_play = None

        if isinstance(song_identifier, str) and song_identifier.isdigit():
            try:
                song_index = int(song_identifier) - 1
                if 0 <= song_index < len(available_songs):
                    song_to_play = available_songs[song_index]
                else:
                    return False, f"Invalid song number: {song_identifier}. Please enter number between 1 and {len(available_songs)}."
            except ValueError: # Should not happen if isdigit() is true, but as safeguard
                return False, f"'{song_identifier}' is not a valid song number."
        elif isinstance(song_identifier, str):
            # song_identifier is song name or partial name
            found_song_file = self.find_song(song_identifier, available_songs)
            if found_song_file:
                song_to_play = found_song_file
            else:
                return False, f"No song found matching '{song_identifier}'. Use 'list' command to see available songs."
        else:
            return False, "Invalid song identifier. Enter song name or number."

        if not song_to_play: # This shouldn't normally happen but extra check
             return False, f"Song not found with '{song_identifier}'."

        try:
            song_path = self.music_dir / song_to_play
            if not song_path.exists(): # Final check if file exists in filesystem
                 return False, f"Song file not found: {song_to_play}"

            print(f"Debug: Loading song: {song_path}")
            
            if not pygame.mixer.get_init():
                print("Debug: Audio system not initialized, restarting...")
                pygame.mixer.quit()
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            
            if self.is_playing:
                pygame.mixer.music.stop()
            
            pygame.mixer.music.load(str(song_path))
            pygame.mixer.music.set_volume(self.volume) # Set volume for each song load
            pygame.mixer.music.play()
            
            self.current_song = song_to_play
            self.is_playing = True
            self.is_paused = False
            
            return True, f"Now playing: '{self.current_song}'"
            
        except pygame.error as e:
            error_msg = f"Pygame error while playing song ({song_to_play}): {str(e)}"
            print(f"Debug: {error_msg}")
            # Try to reset pygame mixer
            try:
                pygame.mixer.quit()
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
                pygame.mixer.music.set_volume(self.volume)
                print("Debug: Pygame mixer reset.")
            except Exception as reset_e:
                print(f"Debug: Additional error while resetting pygame mixer: {reset_e}")
            return False, error_msg
        except Exception as e:
            print(f"Debug: Error details: {str(e)}")
            return False, f"Error occurred while playing song ({song_to_play}): {str(e)}"

    def stop_music(self):
        """Stops playing music"""
        if not self.is_playing:
            return False, "No music currently playing."
        
        try:
            pygame.mixer.music.stop()
            print("Debug: Music stopped")
            self.is_playing = False
            self.is_paused = False
            return True, "Music stopped."
        except Exception as e:
            print(f"Debug: Stop error: {str(e)}")
            return False, "Error occurred while stopping music."

    def pause_music(self):
        """Pauses playing music"""
        if not self.is_playing:
            return False, "No music currently playing."
        
        if not self.is_paused:
            try:
                pygame.mixer.music.pause()
                print("Debug: Music paused")
                self.is_paused = True
                return True, "Music paused."
            except Exception as e:
                print(f"Debug: Pause error: {str(e)}")
                return False, "Error occurred while pausing music."
        return False, "Music is already paused."

    def unpause_music(self):
        """Resumes paused music"""
        if not self.is_playing:
            return False, "No music currently playing."
        
        if self.is_paused:
            try:
                pygame.mixer.music.unpause()
                print("Debug: Music resumed")
                self.is_paused = False
                return True, "Music resumed."
            except Exception as e:
                print(f"Debug: Resume error: {str(e)}")
                return False, "Error occurred while resuming music."
        return False, "Music is already playing."

    def set_volume(self, volume):
        """Sets volume level (between 0.0 - 1.0)"""
        try:
            volume = float(volume)
            if 0 <= volume <= 1:
                self.volume = volume
                print(f"Debug: Changing volume level: {volume}")
                pygame.mixer.music.set_volume(volume)
                print(f"Debug: New volume level: {pygame.mixer.music.get_volume()}")
                
                # Update config
                self.config["music_settings"]["default_volume"] = volume
                self.save_config()
                return True, f"Volume set to {int(volume * 100)}%."
            return False, "Volume must be between 0 and 1."
        except ValueError:
            return False, "Invalid volume level. Enter value between 0 and 1."
        except Exception as e:
            print(f"Debug: Error setting volume: {str(e)}")
            return False, f"Error occurred while setting volume: {str(e)}"

    def list_songs(self):
        """Returns songs in music folder as numbered list."""
        songs = self.get_available_songs()
        if not songs:
            return False, "No songs found in music folder."
        
        message = "Available Songs:\n"
        for i, song_name in enumerate(songs):
            message += f"  {i+1}. {song_name}\n"
        return True, message.strip() # Remove trailing newline

    def get_current_status_display(self):
        """Returns string showing current status of music player."""
        if self.is_playing:
            if self.is_paused:
                return f"Paused: {self.current_song} (Volume: {int(self.volume*100)}%)"
            return f"Playing: {self.current_song} (Volume: {int(self.volume*100)}%)"
        return f"Not Playing Music (Volume: {int(self.volume*100)}%)"

    def __del__(self):
        """Properly closes pygame."""
        print("Debug: MusicPlayer terminating, closing pygame.")
        pygame.quit()

    def interactive_mode(self):
        """Starts interactive command loop for music player."""
        print("\n--- KITT Music System (Radio Mode) ---")

        # Show song list at start
        list_success, list_message = self.list_songs()
        print(f"\n{list_message}")

        try:
            while True:
                print("\nRadio Commands: play <no/name> | stop | pause | resume | volume <0-100> | list | status | quit (radio)")
                command_input = input("KITT Radio > ").strip().lower()
                
                if not command_input:
                    continue

                parts = command_input.split(maxsplit=1)
                command = parts[0]
                arg = parts[1] if len(parts) > 1 else None

                success = False
                message = ""

                if command == "play":
                    if arg:
                        success, message = self.play_music(arg)
                    else:
                        message = "Please specify the name or number of the song you want to play."
                elif command == "stop":
                    success, message = self.stop_music()
                elif command == "pause":
                    success, message = self.pause_music()
                elif command == "resume" or command == "unpause":
                    success, message = self.unpause_music()
                elif command == "volume":
                    if arg:
                        try:
                            vol_float = float(arg)
                            if not (0 <= vol_float <= 100):
                                message = "Volume must be between 0 and 100."
                            else:
                                success, message = self.set_volume(vol_float / 100.0) # Convert to 0-1 range
                        except ValueError:
                            message = "Invalid volume level. Enter number between 0-100."
                    else:
                        message = f"Current volume level: {int(self.volume * 100)}%. Use 'volume <0-100>' format for new level."
                        success = True # Status display is considered successful
                elif command == "list":
                    success, message = self.list_songs()
                elif command == "status":
                    message = self.get_current_status_display()
                    success = True # Status display is always successful
                elif command == "quit" or command == "exit":
                    message = "Exiting radio mode..."
                    print(message)
                    break # Exit interactive loop
                else:
                    message = "Invalid radio command."
                
                print(message)
                if command in ["play", "stop", "pause", "resume", "unpause"] and success:
                    print(f"New Status: {self.get_current_status_display()}")
        except KeyboardInterrupt:
            print("\nRadio mode interrupted.")
        
        print("--- KITT Music System (Radio Mode) Terminated ---")

if __name__ == "__main__":
    player = None
    try:
        player = MusicPlayer()
        # Main test block now only calls interactive_mode.
        player.interactive_mode()
    except Exception as e:
        print(f"Error in main test block: {e}")
    finally:
        if player: # If player was successfully created
            player.stop_music() # Stop music when application closes
        print("music_player.py terminated after direct testing.")
