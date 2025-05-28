import random
import os
from vehicles import Car, Automobile, Truck, Motorcycle, KITT

def clear_terminal():
    """Clear terminal based on operating system"""
    os.system('cls' if os.name == 'nt' else 'clear')

# Vehicle ID counter for AI vehicles
AI_VEHICLE_COUNTER = 0

def generate_unique_ai_vehicle_id():
    """Generate unique ID for AI vehicles"""
    global AI_VEHICLE_COUNTER
    AI_VEHICLE_COUNTER += 1
    return f"AI_VEH_{AI_VEHICLE_COUNTER:03d}"

# Vehicle model databases
CAR_MODELS = {
    "Honda": ["Civic", "Accord", "CR-V"],
    "Toyota": ["Camry", "Corolla", "Prius"],
    "Ford": ["Focus", "Mustang", "Explorer"],
    "BMW": ["3 Series", "5 Series", "X3"],
    "Mercedes": ["C-Class", "E-Class", "GLC"]
}

TRUCK_MODELS = {
    "Ford": ["F-150", "F-250", "Transit"],
    "Chevrolet": ["Silverado", "Colorado"],
    "Ram": ["1500", "2500"],
    "Volvo": ["VNL", "VHD"],
    "Peterbilt": ["579", "389"]
}

MOTORCYCLE_MODELS = {
    "Harley": ["Sportster", "Street Glide"],
    "Honda": ["CBR600", "Gold Wing"],
    "Yamaha": ["YZF-R1", "MT-07"],
    "Kawasaki": ["Ninja", "Versys"],
    "Ducati": ["Panigale", "Monster"]
}

class Road:
    """
    Manages the road, AI vehicles, and general environment of the simulation.
    """
    def __init__(self, length_meters, lane_count, speed_limit_kmh=120):
        self.length_meters = int(length_meters)
        self.lane_count = int(lane_count)
        self.speed_limit_kmh = int(speed_limit_kmh)
        
        self.ai_vehicles = []  # AI vehicles on the road (excluding KITT)
        self.kitt_vehicle = None  # KITT object reference
        
        # Intersection positions (meters from road start)
        self.intersection_positions = [
            int(self.length_meters * 0.25),
            int(self.length_meters * 0.55),
            int(self.length_meters * 0.80)
        ]
        self.active_intersection_message = None
        self.intersection_drift_completed = {}  # Track completed drifts: {position: True}
        
        self.display_scale = 30.0  # How many meters each character represents

    def add_kitt_reference(self, kitt_object):
        """Add KITT object reference to Road class"""
        if isinstance(kitt_object, KITT):
            self.kitt_vehicle = kitt_object
            print("KITT: Road interface established")
        else:
            print("Error: Only KITT objects can be added via add_kitt_reference")

    def add_random_ai_vehicle(self, count=1):
        """Add specified number of random AI vehicles to the road"""
        for _ in range(count):
            if len(self.ai_vehicles) >= self.lane_count * 6:  # Prevent overcrowding
                return

            vehicle_classes = [Automobile, Truck, Motorcycle]
            weights = [0.7, 0.2, 0.1]  # 70% cars, 20% trucks, 10% motorcycles
            SelectedClass = random.choices(vehicle_classes, weights=weights)[0]
            vehicle_id = generate_unique_ai_vehicle_id()
            
            # Position and lane selection to prevent clustering
            attempts = 0
            while attempts < 10:  # Prevent infinite loop
                start_lane = random.randint(1, self.lane_count)
                
                # Position relative to KITT or random
                if self.kitt_vehicle:
                    min_pos = max(0, self.kitt_vehicle.position - 400)
                    max_pos = min(self.length_meters - 100, self.kitt_vehicle.position + 600)
                    if min_pos >= max_pos:
                        min_pos = 0
                        max_pos = int(self.length_meters * 0.8)
                    start_position = float(random.randint(int(min_pos), int(max_pos)))
                else:
                    start_position = float(random.randint(0, int(self.length_meters * 0.7)))

                # Check for collisions
                collision_free = True
                safety_distance = 60  # meters
                
                # Check collision with KITT
                if (self.kitt_vehicle and 
                    self.kitt_vehicle.lane == start_lane and 
                    abs(self.kitt_vehicle.position - start_position) < safety_distance):
                    collision_free = False
                
                # Check collision with other AI vehicles
                if collision_free:
                    for ai_vehicle in self.ai_vehicles:
                        if (ai_vehicle.lane == start_lane and 
                            abs(ai_vehicle.position - start_position) < safety_distance):
                            collision_free = False
                            break
                
                if collision_free:
                    break
                attempts += 1
            
            if attempts >= 10:  # Couldn't find safe position
                continue
            
            # Create vehicle based on class
            new_ai_vehicle = None
            if SelectedClass == Automobile:
                brand = random.choice(list(CAR_MODELS.keys()))
                model = random.choice(CAR_MODELS[brand])
                max_speed = random.randint(100, 180)
                new_ai_vehicle = Automobile(vehicle_id, brand, model, max_speed, start_lane, start_position)
            elif SelectedClass == Truck:
                brand = random.choice(list(TRUCK_MODELS.keys()))
                model = random.choice(TRUCK_MODELS[brand])
                max_speed = random.randint(80, 120)
                new_ai_vehicle = Truck(vehicle_id, brand, model, max_speed, start_lane, start_position)
            elif SelectedClass == Motorcycle:
                brand = random.choice(list(MOTORCYCLE_MODELS.keys()))
                model = random.choice(MOTORCYCLE_MODELS[brand])
                max_speed = random.randint(120, 200)
                new_ai_vehicle = Motorcycle(vehicle_id, brand, model, max_speed, start_lane, start_position)
            
            if new_ai_vehicle:
                # Set realistic speed
                if self.kitt_vehicle:
                    base_speed = max(40, min(new_ai_vehicle.max_speed, 
                                           self.kitt_vehicle.speed + random.randint(-25, 15)))
                else:
                    base_speed = max(40, min(new_ai_vehicle.max_speed, 
                                           self.speed_limit_kmh - random.randint(0, 30)))
                new_ai_vehicle.speed = base_speed
                self.ai_vehicles.append(new_ai_vehicle)

    def calculate_collision_risk_for_kitt(self):
        """Calculate collision risk for KITT with vehicles ahead"""
        if not self.kitt_vehicle:
            return "N/A", None
        
        risk_level = "LOW"
        closest_front_vehicle = None
        min_front_distance = float('inf')

        for ai_vehicle in self.ai_vehicles:
            if ai_vehicle.lane == self.kitt_vehicle.lane:  # Same lane as KITT
                distance = ai_vehicle.position - self.kitt_vehicle.position
                if 0 < distance < min_front_distance:  # Vehicle is ahead of KITT
                    min_front_distance = distance
                    closest_front_vehicle = ai_vehicle
        
        if closest_front_vehicle:
            distance_m = min_front_distance
            speed_diff_kmh = self.kitt_vehicle.speed - closest_front_vehicle.speed
            
            # Safe following distance (e.g., 3 second rule in meters)
            safe_distance_m = (self.kitt_vehicle.speed / 3.6) * 3.0
            
            if distance_m < safe_distance_m * 0.3 and speed_diff_kmh > 30:
                risk_level = "CRITICAL!"
            elif distance_m < safe_distance_m * 0.5 and speed_diff_kmh > 20:
                risk_level = "HIGH"
            elif distance_m < safe_distance_m * 0.8 and speed_diff_kmh > 10:
                risk_level = "MEDIUM"
            elif distance_m < safe_distance_m:
                risk_level = "LOW-MEDIUM"
            
        return risk_level, closest_front_vehicle

    def check_intersection_for_kitt(self):
        """Check if KITT is approaching an intersection"""
        self.active_intersection_message = None
        if not self.kitt_vehicle:
            return False, 0
        
        for intersection_pos in self.intersection_positions:
            distance_to_intersection = intersection_pos - self.kitt_vehicle.position
            if 0 <= distance_to_intersection < 200:  # Within 200m of intersection
                self.active_intersection_message = f"Intersection ahead: {distance_to_intersection:.0f}m"
                if distance_to_intersection < 30:  # Close enough for drift
                    return True, intersection_pos
        return False, 0

    def show_text_based_road(self):
        """Display current road and vehicle status in text format"""
        clear_terminal()
        print(f"=== KNIGHT RIDER SIMULATION ===")
        print(f"Road: {self.length_meters}m | Speed Limit: {self.speed_limit_kmh} km/h | Scale: 1 char = {self.display_scale:.0f}m")
        
        # Calculate display dimensions
        display_length = int(self.length_meters / self.display_scale) + 1
        road_display = [[" · " for _ in range(display_length)] for _ in range(self.lane_count)]

        # Add all vehicles to display
        all_vehicles = []
        if self.kitt_vehicle:
            all_vehicles.append(self.kitt_vehicle)
        all_vehicles.extend(self.ai_vehicles)

        for vehicle in all_vehicles:
            # Ensure position is within bounds
            display_position = max(0, min(vehicle.position, self.length_meters - 1))
            
            lane_idx = vehicle.lane - 1
            pos_idx = int(display_position / self.display_scale)
            pos_idx = min(max(0, pos_idx), display_length - 1)

            if 0 <= lane_idx < self.lane_count:
                current_cell = road_display[lane_idx][pos_idx]
                vehicle_symbol = vehicle.vehicle_symbol
                
                if current_cell == " · ":  # Empty cell
                    road_display[lane_idx][pos_idx] = vehicle_symbol
                elif isinstance(vehicle, KITT):  # KITT has priority
                    road_display[lane_idx][pos_idx] = vehicle_symbol
                elif vehicle_symbol not in current_cell:  # Different vehicle, try to fit
                    road_display[lane_idx][pos_idx] = (current_cell.strip() + vehicle_symbol[0])[:3].center(3)

        # Add intersection markers
        for intersection_pos in self.intersection_positions:
            intersection_idx = int(intersection_pos / self.display_scale)
            if 0 <= intersection_idx < display_length:
                for lane_idx in range(self.lane_count):
                    if road_display[lane_idx][intersection_idx] == " · ":
                        road_display[lane_idx][intersection_idx] = " ╬ "

        # Display the road
        separator_line = "─" * (display_length * 4 + self.lane_count + 1)
        print(separator_line)
        
        for i in range(self.lane_count):
            lane_output = f"L{i+1}│"
            for cell_idx in range(display_length):
                lane_output += f"{road_display[i][cell_idx]}│"
            print(lane_output)
            
            if i < self.lane_count - 1:  # Lane separator
                print("   │" + "│".join(["───" for _ in range(display_length)]) + "│")
        
        print(separator_line)
        
        # KITT Information
        if self.kitt_vehicle:
            print(f"\nKITT STATUS:")
            print(f"  {self.kitt_vehicle.show_status()}")
            
            # System status
            shield_status = f"Shield: {'ON' if self.kitt_vehicle.shield_active else 'OFF'} ({self.kitt_vehicle.shield_power:.0f}%)"
            turbo_status = f"Turbo: {'ACTIVE' if self.kitt_vehicle.turbo_active else 'READY' if self.kitt_vehicle.turbo_cooldown_steps == 0 else f'COOLDOWN({self.kitt_vehicle.turbo_cooldown_steps})'}"
            autopilot_status = f"Autopilot: {'ON' if self.kitt_vehicle.autopilot_active else 'OFF'}"
            music_status = f"Music: {'♪ ' + self.kitt_vehicle.current_song if self.kitt_vehicle.music_playing else 'OFF'}"
            
            print(f"  {shield_status} | {turbo_status}")
            print(f"  {autopilot_status} | {music_status}")
            
            # Risk assessment
            risk, threat = self.calculate_collision_risk_for_kitt()
            risk_message = f"Collision Risk: {risk}"
            if threat:
                distance = int(threat.position - self.kitt_vehicle.position)
                risk_message += f" (Vehicle: {threat.vehicle_id} @ {distance}m)"
            print(f"  {risk_message}")
            
            if self.active_intersection_message:
                print(f"  🚦 {self.active_intersection_message}")
        
        # Nearby Vehicles Information
        print(f"\n--- NEARBY TRAFFIC (Closest 5 vehicles) ---")
        if not self.ai_vehicles:
            print("No other vehicles detected")
        else:
            # Sort AI vehicles by distance to KITT
            kitt_pos = self.kitt_vehicle.position if self.kitt_vehicle else 0
            sorted_vehicles = sorted(self.ai_vehicles, 
                                   key=lambda v: abs(v.position - kitt_pos))
            
            for i, vehicle in enumerate(sorted_vehicles[:5]):
                distance = abs(vehicle.position - kitt_pos) if self.kitt_vehicle else 0
                direction = "ahead" if vehicle.position > kitt_pos else "behind"
                print(f"{i+1}. {vehicle.show_status()} ({distance:.0f}m {direction})")
        
        print("─" * 60)

    def advance_simulation_step(self, time_step_seconds=1.0, new_ai_vehicle_probability=0.1):
        """Advance simulation by one step"""
        # Update KITT position
        if self.kitt_vehicle:
            self.kitt_vehicle.update_position(time_step_seconds)
            
            # Check if KITT reached the end
            if self.kitt_vehicle.position >= self.length_meters:
                return False  # End simulation - success
            
            # Check if KITT is critically damaged
            if self.kitt_vehicle.damage >= 100:
                return False  # End simulation - failure

        # Update AI vehicles
        for ai_vehicle in self.ai_vehicles[:]:  # Work on copy to allow removal
            ai_vehicle.update_position(time_step_seconds)

            # Remove vehicles that left the road
            if (ai_vehicle.position >= self.length_meters + 200 or 
                ai_vehicle.position < -200):
                self.ai_vehicles.remove(ai_vehicle)
                continue
            
            # Simple AI behavior
            target_speed = self.speed_limit_kmh - random.randint(0, 40)
            
            # Adjust speed based on KITT proximity
            if self.kitt_vehicle and abs(ai_vehicle.position - self.kitt_vehicle.position) < 150:
                if ai_vehicle.position > self.kitt_vehicle.position:  # AI ahead of KITT
                    target_speed = max(40, self.kitt_vehicle.speed - random.randint(5, 20))
                else:  # AI behind KITT
                    target_speed = min(ai_vehicle.max_speed, 
                                     self.kitt_vehicle.speed + random.randint(0, 15))

            # Speed adjustments
            if ai_vehicle.speed < target_speed - 10 and random.random() < 0.15:
                ai_vehicle.accelerate(random.randint(5, 12))
            elif ai_vehicle.speed > target_speed + 10 and random.random() < 0.20:
                ai_vehicle.brake(random.randint(5, 12))
            
            # Occasional lane changes (very simple)
            if random.random() < 0.008:  # Low probability
                new_lane = random.randint(1, self.lane_count)
                if new_lane != ai_vehicle.lane:
                    ai_vehicle.change_lane(new_lane, self.lane_count)

        # Add new AI vehicles occasionally
        if random.random() < new_ai_vehicle_probability:
            self.add_random_ai_vehicle()
            
        return True  # Continue simulation