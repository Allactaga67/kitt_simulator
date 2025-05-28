from drift import Drift
import pygame
import os
import random

class MusicPlayer:
    def __init__(self):
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(1)  # Use a single channel for music
            self.is_playing = False
            self.current_song = None
            self.music_dir = "music"  # Directory for music files
            
            # Create music directory if it doesn't exist
            if not os.path.exists(self.music_dir):
                os.makedirs(self.music_dir)
                print(f"'{self.music_dir}' directory created. Please add your music files to this folder.")
        except Exception as e:
            print(f"Error initializing music player: {str(e)}")

    def get_song_list(self):
        """Get list of available songs"""
        if not os.path.exists(self.music_dir):
            return []
        return [f for f in os.listdir(self.music_dir) if f.endswith(('.mp3', '.wav'))]

    def start(self):
        """Start the music player"""
        if not self.is_playing:
            try:
                # Initialize pygame mixer if not already initialized
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                    pygame.mixer.set_num_channels(1)
                self.is_playing = True
                print("Music player started")
                return True
            except Exception as e:
                print(f"Error starting music player: {str(e)}")
                return False
        print("Music player is already running")
        return False

    def stop_player(self):
        """Stop the music player"""
        if self.is_playing:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                self.is_playing = False
                self.current_song = None
                print("Music player stopped")
                return True
            except Exception as e:
                print(f"Error stopping music player: {str(e)}")
                return False
        print("Music player is already stopped")
        return False

    def play(self, song_name=None):
        """Play a specific song or random song"""
        if not self.is_playing:
            print("Please start the music player first")
            return False

        if not os.path.exists(self.music_dir):
            print("Music directory not found")
            return False

        music_files = self.get_song_list()
        
        if not music_files:
            print("No songs found in music directory")
            return False

        if song_name:
            if song_name in music_files:
                self.current_song = song_name
            else:
                print(f"Song '{song_name}' not found")
                return False
        else:
            self.current_song = random.choice(music_files)

        try:
            # Stop any currently playing music
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            # Load and play the new song
            song_path = os.path.join(self.music_dir, self.current_song)
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            print(f"Now playing: {self.current_song}")
            return True
        except Exception as e:
            print(f"Error playing song: {str(e)}")
            return False

class MainController:
    def __init__(self):
        self.music_player = MusicPlayer()
        self.drift = Drift()
        self.is_running = False

    def print_menu(self):
        """Show main menu"""
        print("\n=== KITT 2.0 Control Panel ===")
        print("1. Music Control")
        print("2. Drift Mode")
        print("3. Simulation")
        print("4. AI Mode")
        print("5. Exit")
        print("\nEnter your choice (1-5):")

    def handle_music_control(self):
        """Handle music control commands"""
        while True:
            print("\n=== Music Control ===")
            print("1. Start music player")
            print("2. Stop music player")
            print("3. Play random song")
            print("4. Play specific song")
            print("5. Back to main menu")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                self.music_player.start()
            elif choice == "2":
                self.music_player.stop_player()
            elif choice == "3":
                self.music_player.play()
            elif choice == "4":
                while True:
                    print("\n=== Song Selection ===")
                    print("1. Show all songs")
                    print("2. Search songs")
                    print("3. Back to music control")
                    
                    sub_choice = input("\nEnter your choice (1-3): ")
                    
                    if sub_choice == "1":
                        songs = self.music_player.get_song_list()
                        if songs:
                            print("\nAvailable songs:")
                            for i, song in enumerate(songs, 1):
                                print(f"{i}. {song}")
                            song_choice = input("\nEnter song number (or press Enter to go back): ").strip()
                            if song_choice.isdigit() and 1 <= int(song_choice) <= len(songs):
                                if not self.music_player.is_playing:
                                    self.music_player.start()
                                self.music_player.play(songs[int(song_choice)-1])
                                break
                            elif song_choice:
                                print("Invalid song number!")
                        else:
                            print("No songs available")
                    
                    elif sub_choice == "2":
                        search_term = input("\nEnter search term: ").strip().lower()
                        if search_term:
                            songs = self.music_player.get_song_list()
                            matching_songs = [song for song in songs if search_term in song.lower()]
                            
                            if matching_songs:
                                print("\nMatching songs:")
                                for i, song in enumerate(matching_songs, 1):
                                    print(f"{i}. {song}")
                                
                                # Automatically play the first matching song
                                if not self.music_player.is_playing:
                                    self.music_player.start()
                                selected_song = matching_songs[0]
                                print(f"\nPlaying: {selected_song}")
                                self.music_player.play(selected_song)
                                break
                            else:
                                print("No matching songs found")
                        else:
                            print("Search term cannot be empty")
                    
                    elif sub_choice == "3":
                        break
                    else:
                        print("Invalid choice!")
            
            elif choice == "5":
                return
            else:
                print("Invalid choice!")

    def handle_drift_control(self):
        """Handle drift control commands"""
        print("\n=== Drift Control ===")
        print("1. Start drift mode")
        print("2. Stop drift mode")
        print("3. Back to main menu")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            self.drift.start()
            self.drift.run()  # Start drift game
        elif choice == "2":
            self.drift.stop()
        elif choice == "3":
            return
        else:
            print("Invalid choice!")

    def run(self):
        """Main program loop"""
        self.is_running = True
        
        while self.is_running:
            self.print_menu()
            choice = input("\n> ")
            
            if choice == "1":
                self.handle_music_control()
            elif choice == "2":
                self.handle_drift_control()
            elif choice == "3":
                import os
                os.system('python main_simulation.py')
            elif choice == "4":
                print("\n=== AI Mode Settings ===")
                print("1. Run with voice")
                print("2. Run without voice")
                print("3. Back to main menu")
                
                ai_choice = input("\nEnter your choice (1-3): ")
                
                if ai_choice == "1":
                    import os
                    os.system('python ai.py --voice')
                elif ai_choice == "2":
                    import os
                    os.system('python ai.py --no-voice')
                elif ai_choice == "3":
                    continue
                else:
                    print("Invalid choice!")
            elif choice == "5":
                self.is_running = False
            else:
                print("Invalid choice! Please try again.")
        
        # Cleanup when closing
        self.music_player.stop_player()
        self.drift.stop()

def main():
    controller = MainController()
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Ensure pygame mixer is properly quit
        pygame.mixer.quit()

if __name__ == "__main__":
    main()