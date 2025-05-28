import random
import time
import pygame
import os
import tempfile

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not available. Install with: pip install gtts")

class Car:
    """Base class for all vehicles in the simulation."""
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0, vehicle_symbol="[A]"):
        self.vehicle_id = vehicle_id
        self.brand = brand
        self.model = model
        self.max_speed = float(max_speed)
        self.speed = float(random.randint(int(self.max_speed * 0.3), int(self.max_speed * 0.7)))
        self.lane = int(lane)
        self.position = float(position)
        self.vehicle_symbol = vehicle_symbol

    def accelerate(self, increase_kmh):
        old_speed = self.speed
        self.speed = min(self.speed + float(increase_kmh), self.max_speed)
        return self.speed - old_speed

    def brake(self, decrease_kmh):
        old_speed = self.speed
        self.speed = max(self.speed - float(decrease_kmh), 0.0)
        return old_speed - self.speed

    def change_lane(self, new_lane, total_lane_count):
        new_lane = int(new_lane)
        if 1 <= new_lane <= total_lane_count and self.lane != new_lane:
            self.lane = new_lane
            return True
        return False

    def update_position(self, time_step_seconds=1.0):
        distance_increase_meters = (self.speed * 1000.0 / 3600.0) * float(time_step_seconds)
        self.position += distance_increase_meters

    def show_status(self):
        return f"ID:{self.vehicle_id} ({self.brand} {self.model}) Speed:{self.speed:.0f}km/h Pos:{self.position:.0f}m Lane:{self.lane}"

class Automobile(Car):
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position, vehicle_symbol="o-o")

class Truck(Car):
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position, vehicle_symbol="[T]")

class Motorcycle(Car):
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position, vehicle_symbol="-M-")

class KITT(Automobile):
    def __init__(self, vehicle_id="KITT", brand="Knight Industries", model="2000", max_speed=320, lane=1, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position)
        self.vehicle_symbol = ">K<"
        
        # Game Mechanics
        self.score = 0
        self.damage = 0.0
        
        # Shield System
        self.shield_active = True
        self.shield_power = 100.0
        self.shield_recharge_rate = 2.0
        
        # Turbo System
        self.normal_max_speed = self.max_speed
        self.turbo_active = False
        self.turbo_remaining_steps = 0
        self.turbo_cooldown_steps = 0
        self.turbo_speed_boost = 150
        self.turbo_duration = 5
        self.turbo_cooldown = 15
        
        # Autopilot System
        self.autopilot_active = False
        self.autopilot_target_speed = 80.0
        self.autopilot_target_lane = self.lane
        self.autopilot_reaction_time = 0
        
        # Music System
        self.music_playing = False
        self.current_song = None
        self.music_directory = "music"
        self.available_songs = self._load_music_files()
        
        # Drift System
        self.drift_skill = 75
        self.drift_cooldown = 0
        
        # Communication System
        self.voice_active = True
        self.speech_enabled = True

    def _load_music_files(self):
        """Load available music files from music directory"""
        if not os.path.exists(self.music_directory):
            os.makedirs(self.music_directory)
            return ["Knight Rider Theme", "Turbo Boost", "Scanner Sweep"]
        
        songs = []
        for file in os.listdir(self.music_directory):
            if file.endswith(('.mp3', '.wav', '.ogg')):
                songs.append(file)
        
        if not songs:
            return ["Knight Rider Theme", "Turbo Boost", "Scanner Sweep"]
        return songs

    def toggle_shield(self):
        """Toggle shield on/off"""
        self.shield_active = not self.shield_active
        status = "ACTIVATED" if self.shield_active else "DEACTIVATED"
        
        if self.shield_active:
            if self.shield_power <= 0:
                self.shield_power = 25.0
                message = f"Shield {status} with emergency power ({self.shield_power:.0f}%)"
                print(f"KITT: {message}")
                self.speak(message)
            else:
                message = f"Shield {status}. Power level: {self.shield_power:.0f} percent"
                print(f"KITT: {message}")
                self.speak(message)
        else:
            message = f"Shield {status}"
            print(f"KITT: {message}")
            self.speak(message)
        
        return self.shield_active

    def take_damage(self, damage_amount):
        """Process incoming damage with shield protection"""
        actual_damage = 0
        
        if self.shield_active and self.shield_power > 0:
            absorbed = min(self.shield_power, damage_amount)
            self.shield_power -= absorbed
            remaining_damage = damage_amount - absorbed
            
            message = f"Shield absorbed {absorbed:.0f} damage! Shield power: {self.shield_power:.0f} percent"
            print(f"KITT: {message}")
            self.speak(message)
            
            if self.shield_power <= 0:
                self.shield_active = False
                warning = "Shield power depleted! Shield offline!"
                print(f"KITT: {warning}")
                self.speak(warning)
            
            actual_damage = remaining_damage
        else:
            actual_damage = damage_amount
        
        if actual_damage > 0:
            self.damage += actual_damage
            self.damage = min(self.damage, 100.0)
            damage_msg = f"Hull damage: {actual_damage:.0f}! Total damage: {self.damage:.0f} percent"
            print(f"KITT: {damage_msg}")
            self.speak(damage_msg)
            
            if self.damage >= 75:
                warning = "Warning! Critical damage levels!"
                print(f"KITT: {warning}")
                self.speak(warning)
            elif self.damage >= 50:
                caution = "Caution! Significant damage detected!"
                print(f"KITT: {caution}")
                self.speak(caution)
        
        return self.damage >= 100.0

    def trigger_turbo_boost(self):
        """Activate turbo boost"""
        if self.turbo_cooldown_steps > 0:
            message = f"Turbo boost charging... {self.turbo_cooldown_steps} seconds remaining"
            print(f"KITT: {message}")
            self.speak(message)
            return False
        
        if self.turbo_active:
            message = "Turbo boost already active!"
            print(f"KITT: {message}")
            self.speak(message)
            return False
        
        message = "TURBO BOOST ACTIVATED!"
        print(f"KITT: {message}")
        self.speak(message)
        self.turbo_active = True
        self.max_speed = self.normal_max_speed + self.turbo_speed_boost
        self.turbo_remaining_steps = self.turbo_duration
        self.turbo_cooldown_steps = self.turbo_cooldown
        
        self.accelerate(50)
        self.score += 20
        
        return True

    def update_turbo_system(self):
        """Update turbo boost system"""
        if self.turbo_cooldown_steps > 0:
            self.turbo_cooldown_steps -= 1
        
        if self.turbo_active:
            self.turbo_remaining_steps -= 1
            if self.turbo_remaining_steps <= 0:
                self.turbo_active = False
                self.max_speed = self.normal_max_speed
                message = "Turbo boost deactivated"
                print(f"KITT: {message}")
                self.speak(message)
                
                if self.speed > self.normal_max_speed:
                    self.speed = min(self.speed, self.normal_max_speed + 30)

    def toggle_autopilot(self):
        """Toggle autopilot on/off"""
        self.autopilot_active = not self.autopilot_active
        status = "ENGAGED" if self.autopilot_active else "DISENGAGED"
        
        if self.autopilot_active:
            self.autopilot_target_speed = min(self.speed + 10, self.normal_max_speed - 20)
            self.autopilot_target_lane = self.lane
            message = f"Autopilot {status}. Target speed: {self.autopilot_target_speed:.0f} kilometers per hour"
            print(f"KITT: Autopilot {status}")
            print(f"      Target speed: {self.autopilot_target_speed:.0f} km/h")
            print(f"      Target lane: {self.autopilot_target_lane}")
            self.speak(message)
        else:
            message = f"Autopilot {status}. Manual control restored"
            print(f"KITT: {message}")
            self.speak(message)
        
        return self.autopilot_active

    def run_autopilot_logic(self, road_object):
        """Execute autopilot behavior"""
        if not self.autopilot_active:
            return
        
        speed_diff = abs(self.speed - self.autopilot_target_speed)
        if speed_diff > 5:
            if self.speed < self.autopilot_target_speed:
                self.accelerate(8)
            else:
                self.brake(8)
        
        risk, front_vehicle = road_object.calculate_collision_risk_for_kitt()
        
        if front_vehicle and risk in ["HIGH", "CRITICAL!"]:
            distance = front_vehicle.position - self.position
            
            if distance < (self.speed / 3.6 * 3):
                message = "Obstacle detected - taking evasive action"
                print(f"KITT (Autopilot): {message}")
                self.speak(message)
                
                lane_changed = False
                
                if self.lane > 1 and self._is_lane_safe(self.lane - 1, road_object):
                    if self.change_lane(self.lane - 1, road_object.lane_count):
                        lane_msg = f"Changed to lane {self.lane}"
                        print(f"KITT (Autopilot): {lane_msg}")
                        self.speak(lane_msg)
                        lane_changed = True
                
                elif self.lane < road_object.lane_count and self._is_lane_safe(self.lane + 1, road_object):
                    if self.change_lane(self.lane + 1, road_object.lane_count):
                        lane_msg = f"Changed to lane {self.lane}"
                        print(f"KITT (Autopilot): {lane_msg}")
                        self.speak(lane_msg)
                        lane_changed = True
                
                if not lane_changed:
                    brake_amount = max(15, (self.speed - front_vehicle.speed) + 10)
                    self.brake(brake_amount)
                    self.autopilot_target_speed = max(30, front_vehicle.speed - 5)
                    brake_msg = f"Braking. New target speed {self.autopilot_target_speed:.0f} kilometers per hour"
                    print(f"KITT (Autopilot): {brake_msg}")
                    self.speak(brake_msg)

    def _is_lane_safe(self, target_lane, road_object):
        """Check if lane change is safe"""
        safety_distance = 80
        
        for vehicle in road_object.ai_vehicles:
            if vehicle.lane == target_lane:
                distance = abs(vehicle.position - self.position)
                if distance < safety_distance:
                    return False
        return True

    def control_music(self, song_name=None):
        """Control music playback"""
        if not self.music_playing:
            if song_name and song_name in self.available_songs:
                self.current_song = song_name
            elif song_name:
                matches = [s for s in self.available_songs if song_name.lower() in s.lower()]
                if matches:
                    self.current_song = matches[0]
                else:
                    self.current_song = random.choice(self.available_songs)
            else:
                self.current_song = random.choice(self.available_songs)
            
            self.music_playing = True
            message = f"Now playing {self.current_song}"
            print(f"KITT: {message}")
            self.speak(message)
            
            try:
                music_path = os.path.join(self.music_directory, self.current_song)
                if os.path.exists(music_path):
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)
            except:
                pass
                
        else:
            self.music_playing = False
            message = "Music stopped"
            print(f"KITT: {message}")
            self.speak(message)
            try:
                pygame.mixer.music.stop()
            except:
                pass
            self.current_song = None

    def execute_drift_maneuver(self):
        """Execute drift maneuver with skill-based success"""
        if self.drift_cooldown > 0:
            message = f"Drift system cooling down... {self.drift_cooldown} steps remaining"
            print(f"KITT: {message}")
            self.speak(message)
            return False
        
        message = "Initiating drift sequence..."
        print(f"KITT: {message}")
        self.speak(message)
        time.sleep(0.5)
        
        base_success_chance = self.drift_skill
        speed_bonus = min(20, self.speed / 10)
        damage_penalty = self.damage / 2
        
        success_chance = base_success_chance + speed_bonus - damage_penalty
        success_chance = max(10, min(95, success_chance))
        
        success = random.randint(1, 100) <= success_chance
        
        if success:
            message = "Drift maneuver executed perfectly!"
            print(f"KITT: {message}")
            self.speak(message)
            self.drift_skill = min(100, self.drift_skill + 1)
            self.drift_cooldown = 3
            return True
        else:
            message = "Drift maneuver failed - traction lost!"
            print(f"KITT: {message}")
            self.speak(message)
            self.brake(20)
            self.drift_cooldown = 5
            return False

    def toggle_speech(self):
        """Toggle speech on/off"""
        self.speech_enabled = not self.speech_enabled
        status = "enabled" if self.speech_enabled else "disabled"
        message = f"Voice synthesis {status}"
        print(f"KITT: {message}")
        if self.speech_enabled:
            self.speak(message)
        return self.speech_enabled

    def speak(self, message):
        """KITT speaks with personality and voice synthesis"""
        if not self.speech_enabled:
            return
            
        # Predefined responses
        responses = {
            "hello": "Hello Michael. All systems are functioning normally.",
            "hi": "Hello Michael. All systems are functioning normally.",
            "status": "All systems operational. Standing by for instructions.",
            "help": "I am here to assist you, Michael. What do you need?",
            "thanks": "You're welcome, Michael. It's my pleasure to serve.",
            "thank you": "You're welcome, Michael. It's my pleasure to serve.",
            "good": "Thank you, Michael. I do my best.",
            "bad": "I apologize, Michael. I'll try to do better.",
            "test": "Voice synthesis test successful, Michael.",
            "how are you": "All systems are functioning within normal parameters, Michael.",
            "what's your status": "All systems operational. Standing by for instructions.",
            "scan": "Scanning area, Michael. All clear.",
            "turbo": "Turbo boost is ready for activation, Michael.",
            "shield": "Shield systems are operational, Michael.",
            "music": "Audio entertainment system is ready, Michael.",
            "drift": "Drift capabilities are online, Michael.",
            "autopilot": "Autopilot systems are standing by, Michael.",
        }
        
        message_lower = message.lower().strip()
        
        # Use predefined response if available
        final_message = None
        for key, response in responses.items():
            if key in message_lower:
                final_message = response
                break
        
        # If no predefined response, use original message
        if not final_message:
            if len(message) > 100:
                final_message = "Message received and acknowledged, Michael."
            else:
                final_message = f"{message}, Michael."
        
        # Always print the message
        print(f"KITT: {final_message}")
        
        # Try voice synthesis
        if GTTS_AVAILABLE:
            try:
                self._synthesize_speech(final_message)
            except Exception as e:
                print(f"KITT: [Speech synthesis error: {str(e)}]")
                self._fallback_speech()
        else:
            self._fallback_speech()

    def _synthesize_speech(self, message):
        """Synthesize speech using gTTS"""
        tts = gTTS(text=message, lang='en', slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
            tts.save(temp_filename)
        
        # Pause music if playing
        music_was_playing = False
        if self.music_playing:
            music_was_playing = True
            try:
                pygame.mixer.music.pause()
            except:
                pass
        
        # Play speech
        try:
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"KITT: [Audio playback error: {str(e)}]")
        
        # Resume music
        if music_was_playing:
            try:
                pygame.mixer.music.unpause()
            except:
                pass
        
        # Cleanup
        try:
            os.unlink(temp_filename)
        except:
            pass

    def _fallback_speech(self):
        """Fallback speech indication"""
        print("🗣️ [KITT speaking...]")
        for i in range(3):
            print(".", end="", flush=True)
            time.sleep(0.3)
        print()

    def update_all_systems(self):
        """Update all KITT systems each simulation step"""
        self.update_turbo_system()
        
        if self.shield_active and self.shield_power < 100:
            self.shield_power = min(100, self.shield_power + self.shield_recharge_rate)
        
        if self.drift_cooldown > 0:
            self.drift_cooldown -= 1
        
        if self.autopilot_reaction_time > 0:
            self.autopilot_reaction_time -= 1

    def show_full_status(self):
        """Display complete KITT status"""
        print("\n" + "="*50)
        print("           KITT SYSTEM STATUS")
        print("="*50)
        print(f"Position: {self.position:.0f}m | Lane: {self.lane} | Speed: {self.speed:.0f} km/h")
        print(f"Score: {self.score} | Damage: {self.damage:.1f}%")
        print()
        
        shield_status = "ONLINE" if self.shield_active else "OFFLINE"
        print(f"Shield: {shield_status} ({self.shield_power:.0f}% power)")
        
        if self.turbo_active:
            turbo_status = f"ACTIVE ({self.turbo_remaining_steps} steps remaining)"
        elif self.turbo_cooldown_steps > 0:
            turbo_status = f"CHARGING ({self.turbo_cooldown_steps} steps)"
        else:
            turbo_status = "READY"
        print(f"Turbo: {turbo_status}")
        
        autopilot_status = "ENGAGED" if self.autopilot_active else "STANDBY"
        print(f"Autopilot: {autopilot_status}")
        if self.autopilot_active:
            print(f"  Target Speed: {self.autopilot_target_speed:.0f} km/h")
            print(f"  Target Lane: {self.autopilot_target_lane}")
        
        music_status = f"Playing: {self.current_song}" if self.music_playing else "SILENT"
        print(f"Music: {music_status}")
        
        speech_status = "ENABLED" if self.speech_enabled else "DISABLED"
        print(f"Speech: {speech_status}")
        
        drift_status = "READY" if self.drift_cooldown == 0 else f"COOLDOWN ({self.drift_cooldown})"
        print(f"Drift: {drift_status} (Skill: {self.drift_skill}%)")
        
        print("="*50)
        
        status_summary = f"All systems operational. Current speed: {self.speed:.0f} kilometers per hour. Shield power: {self.shield_power:.0f} percent."
        self.speak(status_summary)