import os
import json
import pygame
import random
import time
from pathlib import Path
from difflib import get_close_matches

class MusicPlayer:
    def __init__(self):
        self.is_running = False
        self.current_song = None
        self.songs = []
        self.volume = 0.5
        self.music_dir = 'music'
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load configuration
        self.load_config()
        
        # Load available songs
        self.load_songs()
        
        print("Music Player initialized")

    def load_config(self):
        """Loads configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.music_dir = config.get('music_dir', 'music')
                self.volume = config.get('volume', 0.5)
        except FileNotFoundError:
            print("Config file not found, using defaults")
        except json.JSONDecodeError:
            print("Error reading config file, using defaults")

    def save_config(self):
        """Saves current configuration to config.json"""
        config = {
            'music_dir': self.music_dir,
            'volume': self.volume
        }
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_songs(self):
        """Loads available songs from the music directory"""
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)
            print(f"Created music directory: {self.music_dir}")
            return

        self.songs = []
        for file in os.listdir(self.music_dir):
            if file.endswith(('.mp3', '.wav', '.ogg')):
                self.songs.append(file)
        
        print(f"Loaded {len(self.songs)} songs")

    def list_songs(self):
        """Lists all available songs"""
        if not self.songs:
            print("No songs available")
            return []
        
        print("\nAvailable songs:")
        for i, song in enumerate(self.songs, 1):
            print(f"{i}. {song}")
        return self.songs

    def find_song(self, song_name):
        """Finds a song by name or number"""
        if not song_name:
            return None
            
        # Try to find by number
        try:
            index = int(song_name) - 1
            if 0 <= index < len(self.songs):
                return self.songs[index]
        except ValueError:
            pass
            
        # Try to find by name
        for song in self.songs:
            if song_name.lower() in song.lower():
                return song
        return None

    def play(self, song_name=None):
        """Plays a specific song or random song if none specified"""
        if not self.songs:
            print("No songs available")
            return False
            
        if song_name:
            song = self.find_song(song_name)
            if not song:
                print(f"Song not found: {song_name}")
                return False
        else:
            # Play random song if no song specified
            song = random.choice(self.songs)
            
        try:
            pygame.mixer.music.load(os.path.join(self.music_dir, song))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.current_song = song
            print(f"Now playing: {song}")
            return True
        except Exception as e:
            print(f"Error playing song: {e}")
            return False

    def stop(self):
        """Stops the current song"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.current_song = None
            print("Music stopped")
            return True
        return False

    def pause(self):
        """Pauses the current song"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            print("Music paused")
            return True
        return False

    def unpause(self):
        """Unpauses the current song"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
            print("Music resumed")
            return True
        return False

    def set_volume(self, volume):
        """Sets the volume (0.0 to 1.0)"""
        try:
            volume = float(volume)
            if 0.0 <= volume <= 1.0:
                self.volume = volume
                pygame.mixer.music.set_volume(volume)
                print(f"Volume set to {volume:.2f}")
                self.save_config()
                return True
            else:
                print("Volume must be between 0.0 and 1.0")
                return False
        except ValueError:
            print("Invalid volume value")
            return False

    def start(self):
        """Starts the music player"""
        self.is_running = True
        print("Music Player started")
        return True

    def stop_player(self):
        """Stops the music player"""
        self.stop()
        self.is_running = False
        print("Music Player stopped")
        return True

if __name__ == "__main__":
    player = MusicPlayer()
    player.start()
    
    while True:
        command = input("\nEnter command (play/stop/pause/unpause/volume/list/end): ").lower()
        
        if command == "end":
            break
        elif command == "play":
            song = input("Enter song name or number (or press Enter for random): ")
            player.play(song)
        elif command == "stop":
            player.stop()
        elif command == "pause":
            player.pause()
        elif command == "unpause":
            player.unpause()
        elif command == "volume":
            vol = input("Enter volume (0.0-1.0): ")
            player.set_volume(vol)
        elif command == "list":
            player.list_songs()
        else:
            print("Unknown command")
    
    player.stop_player()