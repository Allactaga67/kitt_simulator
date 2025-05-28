# road_management.py

import random
import os
import json # Import JSON module

# We need to import vehicle classes from vehicles.py
# These lines need vehicles.py file to be in the same directory to work.
from vehicles import Vehicle, Car, Truck, Motorcycle, KITT # Also import KITT since Road class will receive KITT object

# Load vehicle models from JSON config file
CONFIG_FILE = "vehicle_config.cfg"

CAR_MODELS_AI = {}
TRUCK_MODELS_AI = {}
MOTORCYCLE_MODELS_AI = {}

try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        CAR_MODELS_AI = config_data.get("CAR_MODELS_AI", {})
        TRUCK_MODELS_AI = config_data.get("TRUCK_MODELS_AI", {})
        MOTORCYCLE_MODELS_AI = config_data.get("MOTORCYCLE_MODELS_AI", {})
except FileNotFoundError:
    print(f"WARNING: Configuration file ({CONFIG_FILE}) not found. Default empty model lists will be used.")
    # Add default values if config file doesn't exist
    CAR_MODELS_AI = {"Generic": ["Car"]}
    TRUCK_MODELS_AI = {"Generic": ["Truck"]}
    MOTORCYCLE_MODELS_AI = {"Generic": ["Motorcycle"]}
except json.JSONDecodeError:
    print(f"WARNING: Configuration file ({CONFIG_FILE}) is not in valid JSON format. Default empty model lists will be used.")
    CAR_MODELS_AI = {"Generic": ["Car"]}
    TRUCK_MODELS_AI = {"Generic": ["Truck"]}
    MOTORCYCLE_MODELS_AI = {"Generic": ["Motorcycle"]}

# --- Helper Functions (Can be in this file or separate utils.py file) ---
def clear_terminal():
    """Clears terminal according to operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

VEHICLE_ID_COUNTER_ROAD = 0 # Different name to avoid confusion with counter in other files
def generate_unique_ai_vehicle_id():
    """Generates unique ID for AI vehicles."""
    global VEHICLE_ID_COUNTER_ROAD
    VEHICLE_ID_COUNTER_ROAD += 1
    return f"ai_vehicle{VEHICLE_ID_COUNTER_ROAD}"

class Road:
    """
    Manages the simulation road, AI vehicles on it, and general environment.
    """
    def __init__(self, length_meters, lane_count, speed_limit_kmh=120):
        self.length_meters = int(length_meters)
        self.lane_count = int(lane_count)
        self.speed_limit_kmh = int(speed_limit_kmh)
        
        self.ai_vehicles = [] # AI vehicles on road other than KITT
        self.kitt_vehicle = None # KITT object reference
        
        # Intersection positions (meters from road start)
        self.intersection_positions = [int(self.length_meters * 0.35), int(self.length_meters * 0.75)]
        self.active_intersection_message = None # Intersection message to show user
        self.intersection_drift_done = {} # Tracks which intersection had drift: {intersection_pos: True}

        self.display_scale = 25.0 # How many meters each character represents in text display
        self.viewport_width_characters = 30 # Width of road section shown in terminal (in characters)

    def add_kitt_reference(self, kitt_object):
        """Used to introduce KITT object to Road class."""
        if isinstance(kitt_object, KITT):
            self.kitt_vehicle = kitt_object
        else:
            print("Error: Only KITT object can be added to Road (add_kitt_reference).")

    def add_random_ai_vehicle(self, count=1):
        """Adds specified number of random AI vehicles to road."""
        for _ in range(count):
            if len(self.ai_vehicles) >= self.lane_count * 4: # Don't let too many AI vehicles on road
                return

            vehicle_classes = [Car, Truck, Motorcycle]
            SelectedClass = random.choice(vehicle_classes)
            vehicle_id = generate_unique_ai_vehicle_id()
            
            # Position and lane selection to prevent vehicle clustering
            while True:
                starting_lane = random.randint(1, self.lane_count)
                # Start around KITT or in certain section of road
                if self.kitt_vehicle:
                    min_p = max(0, self.kitt_vehicle.position - 250)
                    max_p = min(self.length_meters - 50, self.kitt_vehicle.position + 250)
                    if min_p >= max_p: min_p = 0; max_p = int(self.length_meters * 0.7)
                    starting_position = float(random.randint(int(min_p), int(max_p)))
                else:
                    starting_position = float(random.randint(0, int(self.length_meters * 0.7)))

                no_collision = True
                test_gap = 40 # Minimum gap between vehicles (meters)
                
                # Check collision with KITT
                if self.kitt_vehicle and self.kitt_vehicle.lane == starting_lane and \
                   abs(self.kitt_vehicle.position - starting_position) < test_gap:
                    no_collision = False
                
                # Check collision with other AI vehicles
                if no_collision:
                    for ai_vehicle in self.ai_vehicles:
                        if ai_vehicle.lane == starting_lane and \
                           abs(ai_vehicle.position - starting_position) < test_gap:
                            no_collision = False
                            break
                
                if no_collision:
                    break 
            
            new_ai_vehicle = None
            if SelectedClass == Car:
                brand = random.choice(list(CAR_MODELS_AI.keys()))
                model = random.choice(CAR_MODELS_AI[brand])
                new_ai_vehicle = Car(vehicle_id, brand, model, random.randint(90, 150), starting_lane, starting_position)
            elif SelectedClass == Truck:
                brand = random.choice(list(TRUCK_MODELS_AI.keys()))
                model = random.choice(TRUCK_MODELS_AI[brand])
                new_ai_vehicle = Truck(vehicle_id, brand, model, random.randint(70, 100), starting_lane, starting_position)
            elif SelectedClass == Motorcycle:
                brand = random.choice(list(MOTORCYCLE_MODELS_AI.keys()))
                model = random.choice(MOTORCYCLE_MODELS_AI[brand])
                new_ai_vehicle = Motorcycle(vehicle_id, brand, model, random.randint(110, 170), starting_lane, starting_position)
            
            if new_ai_vehicle:
                # Adjust speed of newly added vehicle based on KITT's speed or road speed limit
                if self.kitt_vehicle:
                    new_ai_vehicle.speed = max(30, min(new_ai_vehicle.max_speed, self.kitt_vehicle.speed + random.randint(-30, 5)))
                else:
                    new_ai_vehicle.speed = max(30, min(new_ai_vehicle.max_speed, self.speed_limit_kmh - random.randint(0, 20)))
                self.ai_vehicles.append(new_ai_vehicle)

    def calculate_crash_risk(self):
        """Calculates crash risk with vehicle ahead for KITT."""
        if not self.kitt_vehicle: return "N/A", None
        
        risk_status = "Low"
        closest_front_vehicle = None
        min_distance_ahead = float('inf')

        for ai_vehicle in self.ai_vehicles:
            if ai_vehicle.lane == self.kitt_vehicle.lane: # Same lane as KITT
                distance = ai_vehicle.position - self.kitt_vehicle.position # Positive if AI vehicle is ahead of KITT
                if 0 < distance < min_distance_ahead: # Ahead of KITT and closest
                    min_distance_ahead = distance
                    closest_front_vehicle = ai_vehicle
        
        if closest_front_vehicle:
            distance_m = min_distance_ahead
            speed_difference_kmh = self.kitt_vehicle.speed - closest_front_vehicle.speed # Positive if KITT is faster
            
            # Safe following distance (e.g. 2 second rule, in meters)
            safe_distance_m = (self.kitt_vehicle.speed / 3.6) * 2.5 # 2.5 seconds
            
            if distance_m < safe_distance_m * 0.35 and speed_difference_kmh > 20: risk_status = "CRITICAL!"
            elif distance_m < safe_distance_m * 0.6 and speed_difference_kmh > 10: risk_status = "High"
            elif distance_m < safe_distance_m * 1.1: risk_status = "Medium"
            
        return risk_status, closest_front_vehicle

    def check_intersection_for_kitt(self):
        """Checks if KITT is approaching an intersection."""
        self.active_intersection_message = None # Reset message each step
        if not self.kitt_vehicle: return False, 0
        
        for intersection_position_m in self.intersection_positions:
            distance_to_intersection_m = intersection_position_m - self.kitt_vehicle.position
            if 0 <= distance_to_intersection_m < 150: # Give warning when 150m from intersection
                self.active_intersection_message = f"{distance_to_intersection_m:.0f}m to intersection!"
                if distance_to_intersection_m < 20: # If at intersection or very close (for drift)
                    return True, intersection_position_m # Drift time and intersection position
        return False, 0 # Not drift time yet or not at intersection

    def show_text_based_road(self):
        """Draws current state of road and vehicles as text in terminal."""
        clear_terminal()

        # Viewport calculations
        kitt_pos_m = self.kitt_vehicle.position if self.kitt_vehicle else self.length_meters / 2
        viewport_width_m = self.viewport_width_characters * self.display_scale
        
        # Try to center KITT, but don't exceed road boundaries
        viewport_start_m = max(0, kitt_pos_m - (viewport_width_m / 2))
        viewport_end_m = min(self.length_meters, viewport_start_m + viewport_width_m)
        
        # If end boundary causes start to shift, adjust (to show full viewport when reaching end of road)
        if viewport_end_m == self.length_meters:
            viewport_start_m = max(0, self.length_meters - viewport_width_m)
        
        # Header
        view_str = f"View: {viewport_start_m:.0f}m - {viewport_end_m:.0f}m"
        print(f"=== KNIGHT RIDER SIMULATION (Road: {self.length_meters}m | Speed Limit: {self.speed_limit_kmh}km/h | Scale: 1char={self.display_scale:.0f}m | {view_str}) ===")
        
        # list_length is now viewport width
        list_length_characters = self.viewport_width_characters 
        road_drawing = [[" . " for _ in range(list_length_characters)] for _ in range(self.lane_count)]

        # First add KITT then AI vehicles to drawing list
        all_vehicles_to_show = []
        if self.kitt_vehicle:
            all_vehicles_to_show.append(self.kitt_vehicle)
        all_vehicles_to_show.extend(self.ai_vehicles)

        for g_vehicle in all_vehicles_to_show:
            vehicle_pos_m = g_vehicle.position
            # Is vehicle within viewport?
            if viewport_start_m <= vehicle_pos_m < viewport_end_m:
                # Vehicle's relative position within viewport (in meters, relative to viewport start)
                vehicle_relative_pos_m = vehicle_pos_m - viewport_start_m
                vehicle_pos_idx = int(vehicle_relative_pos_m / self.display_scale)
                
                # Make sure index is within viewport boundaries
                vehicle_pos_idx = min(max(0, vehicle_pos_idx), list_length_characters - 1)
                vehicle_lane_idx = g_vehicle.lane - 1

                if 0 <= vehicle_lane_idx < self.lane_count: 
                    current_cell_content = road_drawing[vehicle_lane_idx][vehicle_pos_idx]
                    new_symbol = g_vehicle.vehicle_symbol
                    
                    if current_cell_content == " . ":
                        road_drawing[vehicle_lane_idx][vehicle_pos_idx] = new_symbol
                    elif isinstance(g_vehicle, KITT):
                        road_drawing[vehicle_lane_idx][vehicle_pos_idx] = new_symbol
                    elif new_symbol not in current_cell_content and len(current_cell_content.replace(" ","")) < 2:
                        road_drawing[vehicle_lane_idx][vehicle_pos_idx] = (current_cell_content.strip() + new_symbol[0])[:3].center(3)

        # Draw Road
        road_separator_line = "---" * list_length_characters + "-" * (list_length_characters + 1)
        print(road_separator_line)
        for i in range(self.lane_count):
            lane_output = f"L{i+1}|"
            for cell_idx in range(list_length_characters):
                lane_output += f"{road_drawing[i][cell_idx].center(3)}|"
            print(lane_output)
            if i < self.lane_count - 1:
                 print("   |" + "|".join(["---" for _ in range(list_length_characters)]) + "|")
        print(road_separator_line)
        
        # KITT Information (always shown)
        if self.kitt_vehicle:
            print("\n--- KITT Status ---   Michael")
            base_status_list = self.kitt_vehicle.show_status()
            for line in base_status_list:
                print(f"  {line}")
            
            extra_status_list = self.kitt_vehicle.show_extra_status()
            for line in extra_status_list:
                print(f"  {line}")
            
            risk, threat = self.calculate_crash_risk()
            risk_message = f"Crash Risk: {risk}"
            if threat: risk_message += f" (Ahead: {threat.vehicle_id} @ {int(threat.position - self.kitt_vehicle.position)}m)"
            print(f"      {risk_message}")
            
            if self.active_intersection_message: 
                print(f"      {self.active_intersection_message}")

    def advance_simulation_step(self, time_step_seconds=1.0, new_ai_vehicle_probability=0.1):
        """Advances one step of simulation. Updates all vehicle positions, manages AI behaviors."""
        # 1. Update KITT's position
        if self.kitt_vehicle:
            self.kitt_vehicle.update_position(time_step_seconds)
            # Check if KITT reached end of road or took damage
            if self.kitt_vehicle.position >= self.length_meters:
                print("\n### KITT REACHED END OF ROAD! CONGRATULATIONS! ###")
                return False # End simulation
            if self.kitt_vehicle.damage >= 100:
                print("\n### KITT IS UNUSABLE! MISSION FAILED! ###")
                return False # End simulation

        # 2. Update AI Vehicles
        for ai_vehicle_object in self.ai_vehicles[:]: # Work on copy of list (in case of removal)
            ai_vehicle_object.update_position(time_step_seconds)

            # Remove AI vehicles that left the road
            if ai_vehicle_object.position >= self.length_meters + 100 or ai_vehicle_object.position < -150: # Wider margin
                self.ai_vehicles.remove(ai_vehicle_object)
                continue
            
            # Simple AI Behaviors (speed adjustment, lane changing - very basic)
            # Speed adjustment based on speed limit and KITT
            target_speed_ai = self.speed_limit_kmh - random.randint(0, 30)
            if self.kitt_vehicle and abs(ai_vehicle_object.position - self.kitt_vehicle.position) < 100: # If KITT is nearby
                if ai_vehicle_object.position > self.kitt_vehicle.position: # AI is ahead of KITT
                    target_speed_ai = max(30, self.kitt_vehicle.speed - random.randint(5,15) if self.kitt_vehicle.speed > 40 else self.kitt_vehicle.speed + 5)
                else: # AI is behind KITT
                    target_speed_ai = min(ai_vehicle_object.max_speed, self.kitt_vehicle.speed + random.randint(0,10))

            if ai_vehicle_object.speed < target_speed_ai - 5 and random.random() < 0.1:
                ai_vehicle_object.accelerate(random.randint(3, 8))
            elif ai_vehicle_object.speed > target_speed_ai + 5 and random.random() < 0.15:
                ai_vehicle_object.brake(random.randint(3, 8))

        # 3. Add New AI Vehicles
        if random.random() < new_ai_vehicle_probability:
            self.add_random_ai_vehicle()
            
        return True # Continue simulation

    def check_and_handle_collisions(self, kitt):
        """Checks and handles collisions between KITT and AI vehicles."""
        if not kitt:
            return
        
        collision_distance = 15 # Distance threshold for collision (meters)
        
        for ai_vehicle in self.ai_vehicles[:]:
            # Check if in same lane and close enough
            if (ai_vehicle.lane == kitt.lane and 
                abs(ai_vehicle.position - kitt.position) < collision_distance):
                
                print(f"\n!!! COLLISION DETECTED !!!")
                print(f"KITT collided with {ai_vehicle.vehicle_id} ({ai_vehicle.brand} {ai_vehicle.model})")
                
                # Calculate damage based on speed difference
                speed_diff = abs(kitt.speed - ai_vehicle.speed)
                base_damage = 20 + (speed_diff * 0.5)
                
                # KITT takes damage
                critical_damage = kitt.take_damage(base_damage)
                
                # Remove the AI vehicle from road (it's destroyed/disabled)
                self.ai_vehicles.remove(ai_vehicle)
                print(f"{ai_vehicle.vehicle_id} removed from road due to collision.")
                
                if critical_damage:
                    print("KITT has taken critical damage!")
                    return True # Signal critical damage
        
        return False # No critical damage