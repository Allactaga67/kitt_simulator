# main_simulation.py

import random
import time
import os # For clear_terminal (can also be called from road_management.py)

# Import necessary classes from our other Python files
from vehicles import KITT # Import KITT class directly
from road_management import Road # Import Road class

# If drift module is in a separate file, you can import it too:
# import drift_module # Example: from drift_game import start_drift_game

def start_interactive_simulation():
    """
    Starts and manages the main simulation loop.
    """
    clear_terminal = lambda: os.system('cls' if os.name == 'nt' else 'clear') # Simple clear function

    print("=== KNIGHT RIDER - KITT Simulation Starting... ===")
    time.sleep(1)

    # Simulation Settings
    road_length_m = 2000  # Total road length (meters)
    lane_count = 3
    road_speed_limit_kmh = 120
    sim_time_step_s = 0.4 # Duration of each simulation step (seconds) - for smoother movement
    new_ai_vehicle_probability = 0.10 # Probability of adding new AI vehicle each step

    # Create Objects
    main_road = Road(road_length_m, lane_count, road_speed_limit_kmh)
    
    # Start KITT in random lane at beginning of road
    kitt_starting_lane = random.randint(1, main_road.lane_count)
    kitt_starting_position = 50.0 # Start a bit ahead on the road
    kitt = KITT(lane=kitt_starting_lane, position=kitt_starting_position)
    
    main_road.add_kitt_reference(kitt) # Introduce KITT object to Road class

    # Add some random AI vehicles to road initially
    for _ in range(random.randint(3, 6)): # Initial AI vehicle count
        main_road.add_random_ai_vehicle()

    while True:
        # First let KITT's autopilot run (if active)
        if kitt.autopilot_active:
            kitt.run_autopilot_logic(main_road)

        main_road.show_text_based_road() # Draw the road (KITT argument removed)

        # Intersection Check (for KITT)
        at_intersection, intersection_pos = main_road.check_intersection_for_kitt()
        if at_intersection and not main_road.intersection_drift_done.get(intersection_pos):
            print(f"KITT: You're at an intersection Michael ({intersection_pos}m)! Time to drift! (Command: d)")

        # User Commands
        print("\n--- CONTROL PANEL ---")
        print("COMMANDS: h <speed> | f <brake> | s <lane_no> | t (turbo) | k (shield) | o (autopilot)")
        print("          m (music) | d (drift) | sp (speak) | r (radar) | a (step) | x (exit)")
        command_input = input(f"KITT [Speed:{kitt.speed:.0f} Pos:{kitt.position:.0f} Damage:{kitt.damage:.0f}%] > ").strip().lower()

        main_action = "a" # Default action is to advance step
        parameter = ""

        if not command_input: # Empty input is accepted as "a" (step)
            main_action = "a"
        elif " " in command_input:
            try:
                main_action, parameter = command_input.split(" ", 1)
            except ValueError:
                print("Invalid command format.")
                main_action = "invalid_command" # Invalid operation
        else:
            main_action = command_input

        if main_action == "x":
            print("Exiting simulation...")
            break
        elif main_action == "a":
            print("> Advancing step...")
            # pass # Just advance step (will happen at end of loop)
        elif main_action == "h":
            try:
                kitt.accelerate(float(parameter))
            except ValueError:
                print("Invalid speed value!")
        elif main_action == "f":
            try:
                kitt.brake(float(parameter))
            except ValueError:
                print("Invalid brake value!")
        elif main_action == "s":
            try:
                if kitt.change_lane(int(parameter), main_road.lane_count):
                    print(f"KITT moved to lane {parameter}.")
                # else: # change_lane already gives message
                #     print(f"! Could not move to lane {parameter}.") 
            except ValueError:
                print("Invalid lane number!")
        elif main_action == "t":
            kitt.activate_turbo_boost()
        elif main_action == "k":
            kitt.toggle_shield()
        elif main_action == "o":
            kitt.toggle_autopilot()
        elif main_action == "m": # Music (Radio Mode)
            kitt.start_radio_mode()
        elif main_action == "r": # Radar
            kitt.radar_scan(main_road)
            input("\nRadar results displayed. Press Enter to continue...")
        elif main_action == "d": # Drift
            if at_intersection and not main_road.intersection_drift_done.get(intersection_pos):
                print("KITT: Attempting intersection drift...")
                if kitt.activate_drift(road_object=main_road): 
                    main_road.intersection_drift_done[intersection_pos] = True
                    kitt.score += 20 # Extra points for intersection drift
                    print("KITT: Successful intersection drift! Bonus points! (+20)")
            else:
                print("KITT: Manual free drift attempt...")
                kitt.activate_drift() # Can be called without road object (optional)
        elif main_action == "sp": # Speak (without message)
            kitt.speak() # Makes KITT speak with default message
        elif main_action == "invalid_command":
            pass # Message already given
        else:
            print(f"Invalid command: '{command_input}'")
            time.sleep(1)

        # Advance Simulation Step and Update Other Vehicles
        if not main_road.advance_simulation_step(time_step_seconds=sim_time_step_s, new_ai_vehicle_probability=new_ai_vehicle_probability):
            print("Simulation ended for some reason (e.g: KITT took damage or road ended).")
            break
        
        # Update KITT's turbo and other states (damage etc. might be in advance_simulation_step)
        kitt.update_turbo_step()
        kitt.drift_mode_active_temporary = False # Reset drift mode after each step (was one-time)

        # Collision Check (between KITT and AI vehicles)
        main_road.check_and_handle_collisions(kitt)

        # Check if intersection passed and reset drift message
        if at_intersection and main_road.intersection_drift_done.get(intersection_pos) and kitt.position > intersection_pos + 10:
            main_road.active_intersection_message = None # Clear intersection message

        # Short wait (to improve playability)
        time.sleep(0.3)

    print(f"\n--- SIMULATION ENDED ---")
    print(f"KITT Final Status: Score: {kitt.score}, Damage: {kitt.damage:.0f}%")

if __name__ == "__main__":
    start_interactive_simulation()
