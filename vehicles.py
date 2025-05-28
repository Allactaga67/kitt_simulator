import random
import time

# If you have a separate drift_module.py file and KITT will use it:
# import drift_module # Example import

class Vehicle:
    """
    Base class for all vehicles in the simulation.
    """
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0, vehicle_symbol="[A]"):
        self.vehicle_id = vehicle_id
        self.brand = brand
        self.model = model
        self.max_speed = float(max_speed) # Maximum speed (km/h)
        self.speed = float(random.randint(int(self.max_speed * 0.3), int(self.max_speed * 0.7))) # Current speed (km/h)
        self.lane = int(lane) # Lane number
        self.position = float(position) # Position on road (meters)
        self.vehicle_symbol = vehicle_symbol # Symbol for text-based display

    def accelerate(self, increase_kmh):
        self.speed = min(self.speed + float(increase_kmh), self.max_speed)

    def brake(self, decrease_kmh):
        self.speed = max(self.speed - float(decrease_kmh), 0.0)

    def change_lane(self, new_lane, total_lane_count):
        new_lane = int(new_lane)
        if 1 <= new_lane <= total_lane_count:
            if self.lane != new_lane:
                self.lane = new_lane
                return True
        return False

    def update_position(self, time_step_seconds=1.0):
        distance_increase_meters = (self.speed * 1000.0 / 3600.0) * float(time_step_seconds)
        self.position += distance_increase_meters

    def show_status(self):
        return [
            f"ID        : {self.vehicle_id} ({self.brand} {self.model})",
            f"Speed     : {self.speed:.0f} km/h",
            f"Position  : {self.position:.0f} m",
            f"Lane      : {self.lane}"
        ]

# --- Other Vehicle Types ---
class Car(Vehicle):
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position, vehicle_symbol="o-o")

class Truck(Vehicle):
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position, vehicle_symbol="[T]")

class Motorcycle(Vehicle):
    def __init__(self, vehicle_id, brand, model, max_speed, lane, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position, vehicle_symbol="-M-")

# --- KITT Class ---
from music_player import MusicPlayer # Import MusicPlayer class

class KITT(Car):
    def __init__(self, vehicle_id="KITT", brand="Knight Ind.", model="Industries 2000", max_speed=320, lane=1, position=0.0):
        super().__init__(vehicle_id, brand, model, max_speed, lane, position)
        self.vehicle_symbol = ">K<"
        
        self.score = 0
        self.damage = 0 

        self.shield_active = True
        self.shield_power = 100

        self.normal_max_speed = self.max_speed
        self.turbo_active = False
        self.turbo_remaining_steps = 0
        self.turbo_cooldown_steps = 0
        self.turbo_speed_increase = 150
        self.turbo_duration_steps = 3
        self.turbo_cooldown_duration = 10

        self.autopilot_active = False
        self.autopilot_target_speed = 80.0
        self.autopilot_target_lane = self.lane

        self.drift_mode_active_temporary = False

        # Initialize MusicPlayer object
        try:
            self.music_player = MusicPlayer()
        except Exception as e:
            print(f"KITT WARNING: Music system could not be started: {e}. Music features disabled.")
            self.music_player = None
        
        self.chatbot_message = None
        self.radar_max_range_m = 500 # Maximum radar range in meters

    def toggle_shield(self):
        self.shield_active = not self.shield_active
        status = "ACTIVE" if self.shield_active else "DISABLED"
        print(f"KITT: Shield is now {status}.")
        if self.shield_active and self.shield_power <= 0:
            self.shield_power = 10
            print(f"KITT: Shield reactivated with minimum power ({self.shield_power:.0f}%).")
        return self.shield_active

    def take_damage(self, damage_amount):
        damage_taken = 0
        if self.shield_active and self.shield_power > 0:
            absorbed_damage = min(self.shield_power, damage_amount)
            self.shield_power -= absorbed_damage
            remaining_damage = damage_amount - absorbed_damage
            
            print(f"KITT: Shield absorbed {absorbed_damage:.0f} damage! Shield Power: {self.shield_power:.0f}%")
            
            if self.shield_power <= 0:
                self.shield_active = False
                print("KITT: Shield power depleted! Shield disabled!")
            
            if remaining_damage > 0:
                damage_taken = remaining_damage
        else:
            damage_taken = damage_amount

        if damage_taken > 0:
            self.damage += damage_taken
            self.damage = min(self.damage, 100)
            print(f"KITT: {damage_taken:.0f} damage taken! Total Damage: {self.damage:.0f}%")
        
        if self.damage >= 100:
            print("KITT: Critical damage! Systems in danger!")
        
        return self.damage >= 100

    def activate_turbo_boost(self):
        if self.turbo_cooldown_steps > 0:
            print(f"KITT: Turbo Boost not ready yet! Remaining time: {self.turbo_cooldown_steps} steps.")
            return False
        
        if not self.turbo_active:
            print("KITT: TURBO BOOST ACTIVE!!!")
            self.turbo_active = True
            self.max_speed = self.normal_max_speed + self.turbo_speed_increase
            self.accelerate(self.turbo_speed_increase)
            self.speed = min(self.speed, self.max_speed)
            self.turbo_remaining_steps = self.turbo_duration_steps
            self.score += 25
            return True
        return False

    def update_turbo_step(self):
        if self.turbo_cooldown_steps > 0:
            self.turbo_cooldown_steps -= 1

        if self.turbo_active:
            self.turbo_remaining_steps -= 1
            if self.turbo_remaining_steps <= 0:
                self.turbo_active = False
                self.max_speed = self.normal_max_speed
                self.speed = min(self.speed, self.normal_max_speed + 20)
                print("KITT: Turbo Boost ended.")
                self.turbo_cooldown_steps = self.turbo_cooldown_duration

    def toggle_autopilot(self):
        self.autopilot_active = not self.autopilot_active
        status = "ACTIVE" if self.autopilot_active else "DISABLED"
        if self.autopilot_active:
            self.autopilot_target_speed = min(self.speed + 10, self.normal_max_speed - 20)
            self.autopilot_target_lane = self.lane
            print(f"KITT: Autopilot now {status}. Target speed: {self.autopilot_target_speed:.0f} km/h, Lane: {self.autopilot_target_lane}")
        else:
            print(f"KITT: Autopilot now {status}.")
        return self.autopilot_active

    def run_autopilot_logic(self, road_object):
        if not self.autopilot_active:
            return

        if abs(self.speed - self.autopilot_target_speed) > 5:
            if self.speed < self.autopilot_target_speed:
                self.accelerate(5)
            else:
                self.brake(5)
        
        risk, front_vehicle = road_object.calculate_crash_risk()
        
        if front_vehicle and (front_vehicle.position - self.position) < (self.speed / 3.6 * 4):
            print("KITT (Autopilot): Slow vehicle detected ahead.")
            lane_changed = False
            if self.lane > 1 and self._autopilot_is_lane_safe(self.lane - 1, road_object):
                self.change_lane(self.lane - 1, road_object.lane_count)
                lane_changed = True
            elif self.lane < road_object.lane_count and self._autopilot_is_lane_safe(self.lane + 1, road_object):
                self.change_lane(self.lane + 1, road_object.lane_count)
                lane_changed = True
            
            if not lane_changed:
                self.autopilot_target_speed = max(30, front_vehicle.speed - 10)
                self.brake(10)
        elif not front_vehicle and self.speed < self.normal_max_speed - 30:
             self.autopilot_target_speed = self.normal_max_speed - 30

    def _autopilot_is_lane_safe(self, target_lane, road_object):
        for vehicle in road_object.vehicles:
            if vehicle.lane == target_lane and abs(vehicle.position - self.position) < 75:
                return False
        return True

    def speak(self, message="Analyzing..."):
        """
        KITT's AI-powered speech function.
        Takes user's message and responds through AI module.
        """
        from AI import client, kitt_config, conversation_history # Import AI module and conversation_history
        
        try:
            # 1. Add user's message to global history in AI module
            conversation_history.append({"role": "user", "parts": [{"text": message}]})
            
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=conversation_history, # Use history from AI module
                config=kitt_config
            )
            
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                ai_response = response.candidates[0].content.parts[0].text
                print(f"KITT: {ai_response}")
                self.chatbot_message = ai_response
                # 2. Add model's response to global history in AI module
                conversation_history.append({"role": "model", "parts": [{"text": ai_response}]})
            else:
                error_detail = "Model response is empty or not in expected format."
                if response.prompt_feedback:
                    error_detail += f" Reason: {response.prompt_feedback}"
                print(f"KITT: Sorry Michael, I cannot generate a response right now. ({error_detail})")
                self.chatbot_message = "Could not generate response."
                # Remove last user message from history after failed API call
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()
                
        except Exception as e:
            print(f"KITT: I'm experiencing a communication problem Michael. Error: {e}")
            self.chatbot_message = f"Error occurred: {e}"
            # Remove last added user message from history if API call failed
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history.pop()

    def activate_drift(self, road_object=None):
        """
        This method is called from the main simulation loop (when intersection detected).
        Starts drift game and gives points based on result.
        """
        from drift import play_drift_game # Import game from drift.py
        
        print("KITT: Activating drift mode...")
        # input("Press Enter for drift...") # We can get user input here
                                         # Or it can stay in main loop. For now in main loop.
        try:
            score = play_drift_game() # play_drift_game should return score
            
            # Process based on drift success
            # Scoring and messages can be in play_drift_game,
            # KITT class can just take result and update its own score.
            # Or decisions can be made here based on score ranges.
            # For example, let's give KITT-specific messages based on scoring in drift.py.
            if score >= 300: # Example threshold, can be adjusted based on "Perfect" x turn count in drift.py
                print("KITT: Perfect drift Michael! Like a true master!")
                self.score += 75 # Higher score
                self.drift_mode_active_temporary = True # Main loop can set this to false
                return True
            elif score >= 150: # Example "Good" threshold
                print("KITT: Good attempt Michael, you're improving!")
                self.score += 40
                self.drift_mode_active_temporary = True
                return True
            elif score > 0 : # At least positive score
                print("KITT: Not bad Michael, keep practicing.")
                self.score += 15
                self.drift_mode_active_temporary = True # Drift was attempted.
                return True
            else: # Failed or negative score
                print("KITT: Didn't work this time Michael, but don't worry, we can try again.")
                # Can reduce score for failed drift or keep it same.
                # self.score -= 10 
                self.drift_mode_active_temporary = False
                return False
                
        except ImportError:
            print("KITT: Drift module (drift.py) not found Michael.")
            self.drift_mode_active_temporary = False
            return False
        except Exception as e:
            print(f"KITT: A problem occurred in drift mode Michael: {e}")
            self.drift_mode_active_temporary = False
            return False

    def start_radio_mode(self):
        """Starts KITT's interactive radio mode."""
        if self.music_player:
            print("KITT: Starting radio mode Michael. Controls are yours...")
            # Main simulation loop will pause here, music player will manage its own loop.
            self.music_player.interactive_mode()
            # After exiting interactive mode, KITT can give a message.
            print("KITT: Exited radio mode. Returning to main controls Michael.")
        else:
            print("KITT: Sorry Michael, there seems to be a problem with our music system.")

    def radar_scan(self, road_object):
        """
        Scans surrounding AI vehicles and reports information to KITT.
        Only shows vehicles within certain range in front and behind KITT.
        """
        if not road_object or not hasattr(road_object, 'ai_vehicles'):
            print("KITT: Radar system cannot access road information Michael.")
            return

        print(f"KITT: Starting radar scan... (Range: {self.radar_max_range_m}m)")
        nearby_vehicles = []
        for ai_vehicle in road_object.ai_vehicles:
            if ai_vehicle == self: # Don't scan itself
                continue

            distance = ai_vehicle.position - self.position # Positive: ahead, Negative: behind
            
            if abs(distance) <= self.radar_max_range_m:
                direction = "Ahead" if distance > 0 else "Behind"
                nearby_vehicles.append({
                    "id": ai_vehicle.vehicle_id,
                    "model": f"{ai_vehicle.brand} {ai_vehicle.model}",
                    "distance_m": abs(distance),
                    "direction": direction,
                    "lane": ai_vehicle.lane,
                    "speed_kmh": ai_vehicle.speed
                })
        
        if not nearby_vehicles:
            print("KITT: Radar scan complete. No other vehicles detected in vicinity Michael.")
            return

        sorted_nearby_vehicles = sorted(nearby_vehicles, key=lambda x: x["distance_m"])

        print("\n--- KITT RADAR RESULTS ---")
        for vehicle_info in sorted_nearby_vehicles:
            print(f"  - ID: {vehicle_info['id']} ({vehicle_info['model']})")
            print(f"    Distance: {vehicle_info['distance_m']:.0f}m ({vehicle_info['direction']}), Lane: {vehicle_info['lane']}, Speed: {vehicle_info['speed_kmh']:.0f}km/h")
        print("--- END RADAR RESULTS ---")

    def show_extra_status(self):
        shield_status = f"ACTIVE ({self.shield_power:.0f}%)" if self.shield_active and self.shield_power > 0 else "DISABLED"
        turbo_status = "ACTIVE" if self.turbo_active else (f"Cooling down ({self.turbo_cooldown_steps} steps)" if self.turbo_cooldown_steps > 0 else "READY")
        autopilot_status = f"ACTIVE (Target: {self.autopilot_target_speed:.0f}km/h)" if self.autopilot_active else "DISABLED"
        
        music_status_str = "Music System Disabled" 
        if self.music_player:
            music_status_str = self.music_player.get_current_status_display()

        drift_status = "IN PROGRESS" if self.drift_mode_active_temporary else "STANDBY"
        radar_status = "READY" # Radar status is now "READY"

        return [
            f"Score     : {self.score}",
            f"Damage    : {self.damage:.0f}%",
            f"Shield    : {shield_status}",
            f"Turbo     : {turbo_status}",
            f"Autopilot : {autopilot_status}",
            f"Music     : {music_status_str}",
            f"Drift     : {drift_status}",
            f"Radar     : {radar_status}"
        ]
