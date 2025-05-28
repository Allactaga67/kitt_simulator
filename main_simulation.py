import random
import time
import os
import pygame

# Import necessary classes from other Python files
from vehicles import KITT
from road_management import Road

class Simulation:
    def __init__(self):
        self.is_running = False
        self.speed = 0
        self.lane = 1
        self.shield_active = False
        self.autopilot_active = False

def start_interactive_simulation():
    """
    Starts and manages the main simulation loop with all mechanics working.
    """
    terminal_clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

    print("=== KNIGHT RIDER - KITT Simulation Starting... ===")
    time.sleep(1)

    # Initialize pygame for music
    pygame.mixer.init()

    # Simulation Settings
    road_length_m = 1500
    number_of_lanes = 3
    speed_limit_kmh = 120
    sim_time_step_s = 0.4
    new_ai_vehicle_probability = 0.10

    # Create Objects
    main_road = Road(road_length_m, number_of_lanes, speed_limit_kmh)
    
    # Start KITT in a random lane at the beginning of the road
    kitt_start_lane = random.randint(1, main_road.lane_count)
    kitt_start_position = 50.0
    kitt = KITT(lane=kitt_start_lane, position=kitt_start_position)
    
    main_road.add_kitt_reference(kitt)

    # Add initial AI vehicles
    for _ in range(random.randint(3, 6)):
        main_road.add_random_ai_vehicle()

    running = True
    last_command_process_time = time.time()

    print("\n=== KITT SYSTEMS INITIALIZED ===")
    print("All systems online and ready!")
    time.sleep(1)

    while running:
        terminal_clear()
        main_road.show_text_based_road()

        # Intersection Control and Drift Triggering
        can_drift_at_intersection, intersection_position = main_road.check_intersection_for_kitt()
        if can_drift_at_intersection and not main_road.intersection_drift_completed.get(intersection_position, False):
            print("\n!!████ INTERSECTION DETECTED! ████!!")
            print("KITT: Drift opportunity detected!")
            print("Press ENTER NOW for drift maneuver!")
            
            user_response = input(">>> DRIFT NOW (Enter) or SKIP (any key): ")
            if user_response == "":
                print("KITT: Initiating drift sequence...")
                drift_success = kitt.execute_drift_maneuver()
                if drift_success:
                    print("KITT: Drift maneuver successful! +50 points!")
                    kitt.score += 50
                else:
                    print("KITT: Drift failed. -10 points.")
                    kitt.score -= 10
                main_road.intersection_drift_completed[intersection_position] = True
            else:
                print("KITT: Intersection passed without drift.")
                main_road.intersection_drift_completed[intersection_position] = True
            time.sleep(2)

        # User Commands
        print("\n--- KITT CONTROL PANEL ---")
        print("COMMANDS:")
        print("  h <speed>  - Accelerate    | f <brake>  - Brake")
        print("  s <lane>   - Change Lane   | t          - Turbo Boost")
        print("  k          - Toggle Shield | o          - Toggle Autopilot") 
        print("  m [song]   - Music Control | d          - Manual Drift")
        print("  speak <msg>- KITT Speak    | voice      - Toggle Voice")
        print("  a          - Advance Step  | status     - Full Status")
        print("  c          - Exit")
        
        # Show current status in command prompt
        shield_status = "ON" if kitt.shield_active else "OFF"
        autopilot_status = "ON" if kitt.autopilot_active else "OFF"
        music_status = "♪" if kitt.music_playing else "♫"
        voice_status = "🔊" if kitt.speech_enabled else "🔇"
        
        command_input = input(f"KITT [{kitt.speed:.0f}km/h|S{kitt.lane}|Score:{kitt.score}|DMG:{kitt.damage:.0f}%|Shield:{shield_status}|AP:{autopilot_status}|{music_status}|{voice_status}] > ").strip()

        if not command_input and (time.time() - last_command_process_time < 0.2):
            time.sleep(0.1)
            continue
        
        last_command_process_time = time.time()
        command_parts = command_input.split()
        main_action = command_parts[0].lower() if command_parts else "a"

        try:
            if main_action == "c":
                print("KITT: Shutting down systems...")
                kitt.speak("Shutting down systems, Michael. Goodbye.")
                running = False
                
            elif main_action == "h" and len(command_parts) > 1:
                speed_increase = float(command_parts[1])
                kitt.accelerate(speed_increase)
                message = f"Accelerating by {speed_increase} kilometers per hour"
                print(f"KITT: {message}")
                kitt.speak(message)
                
            elif main_action == "f" and len(command_parts) > 1:
                brake_amount = float(command_parts[1])
                kitt.brake(brake_amount)
                message = f"Braking by {brake_amount} kilometers per hour"
                print(f"KITT: {message}")
                kitt.speak(message)
                
            elif main_action == "s" and len(command_parts) > 1:
                new_lane = int(command_parts[1])
                if kitt.change_lane(new_lane, main_road.lane_count):
                    message = f"Successfully changed to lane {new_lane}"
                    print(f"KITT: {message}")
                    kitt.speak(message)
                else:
                    message = f"Cannot change to lane {new_lane}. Lane occupied or invalid"
                    print(f"KITT: {message}")
                    kitt.speak(message)
                    
            elif main_action == "t":
                if kitt.trigger_turbo_boost():
                    print("KITT: TURBO BOOST ACTIVATED!")
                    # speak() already called in trigger_turbo_boost()
                else:
                    print("KITT: Turbo boost not available")
                    # speak() already called in trigger_turbo_boost()
                    
            elif main_action == "k":
                kitt.toggle_shield()
                # speak() already called in toggle_shield()
                
            elif main_action == "o":
                kitt.toggle_autopilot()
                # speak() already called in toggle_autopilot()
                
            elif main_action == "m":
                song_name = " ".join(command_parts[1:]) if len(command_parts) > 1 else None
                kitt.control_music(song_name)
                # speak() already called in control_music()
                
            elif main_action == "d":
                print("KITT: Manual drift test initiated...")
                if kitt.execute_drift_maneuver():
                    print("KITT: Manual drift successful! +25 points")
                    kitt.score += 25
                else:
                    print("KITT: Manual drift failed. -5 points")
                    kitt.score -= 5
                # speak() already called in execute_drift_maneuver()
                    
            elif main_action == "speak" and len(command_parts) > 1:
                message = " ".join(command_parts[1:])
                kitt.speak(message)
                
            elif main_action == "voice":
                kitt.toggle_speech()
                
            elif main_action == "status":
                kitt.show_full_status()
                input("Press Enter to continue...")
                
            elif main_action == "a" or main_action == "":
                print("KITT: Systems updating...")
                
            elif main_action == "addvehicle":
                main_road.add_random_ai_vehicle()
                message = "New vehicle detected on scanners"
                print(f"KITT: {message}")
                kitt.speak(message)
                
            # Help command
            elif main_action == "help":
                help_message = "Available commands: accelerate, brake, change lane, turbo boost, shield, autopilot, music, drift, speak, voice toggle, status, and exit"
                print(f"KITT: {help_message}")
                kitt.speak(help_message)
                
            # Test speak command
            elif main_action == "test":
                test_message = "All systems functioning normally, Michael"
                print(f"KITT: {test_message}")
                kitt.speak(test_message)
                
            else:
                error_message = "Unknown command. Say 'help' for available commands"
                print(f"KITT: {error_message}")
                kitt.speak(error_message)
                time.sleep(1)

        except ValueError:
            error_msg = "Invalid parameter. Numeric value expected"
            print(f"KITT: {error_msg}")
            kitt.speak(error_msg)
            time.sleep(1)
        except IndexError:
            error_msg = "Missing parameter for command"
            print(f"KITT: {error_msg}")
            kitt.speak(error_msg)
            time.sleep(1)
        except Exception as e:
            error_msg = f"System error occurred: {str(e)}"
            print(f"KITT: {error_msg}")
            kitt.speak("A system error has occurred, Michael")
            time.sleep(1)

        # Update Simulation Step and KITT's Modules
        if running and kitt:
            # Update KITT's systems
            kitt.update_all_systems()
            
            # Run autopilot if active
            if kitt.autopilot_active:
                kitt.run_autopilot_logic(main_road)

            # Advance simulation
            if not main_road.advance_simulation_step(time_step_seconds=sim_time_step_s, 
                                                  new_ai_vehicle_probability=new_ai_vehicle_probability):
                running = False

        # Collision Detection
        if running and kitt:
            risk_status, threatening_vehicle = main_road.calculate_collision_risk_for_kitt()
            
            if risk_status == "CRITICAL!" and threatening_vehicle:
                collision_distance = threatening_vehicle.position - kitt.position
                if collision_distance < (kitt.speed / 3.6 * 0.3):  # Collision imminent
                    terminal_clear()
                    main_road.show_text_based_road()
                    print(f"\n!!!!!! COLLISION DETECTED !!!!!!")
                    print(f"KITT collided with {threatening_vehicle.vehicle_id}!")
                    kitt.speak("Collision detected!")
                    
                    collision_severity = random.randint(30, 80)
                    print(f"Collision severity: {collision_severity}")
                    
                    if kitt.take_damage(collision_severity):
                        print("KITT: Critical systems failure!")
                        kitt.speak("Critical systems failure!")
                        running = False
                    
                    # Affect other vehicle
                    if hasattr(threatening_vehicle, 'brake'):
                        threatening_vehicle.brake(threatening_vehicle.speed * 0.7)
                    
                    time.sleep(3)

        # Check win condition
        if kitt.position >= main_road.length_meters:
            print("\n🏁 MISSION ACCOMPLISHED! 🏁")
            print("KITT has successfully reached the destination!")
            kitt.speak("Mission accomplished, Michael! We have reached our destination.")
            running = False

    # Cleanup
    pygame.mixer.quit()
    
    if not running:
        print("\n=== SIMULATION ENDED ===")
        if kitt:
            print(f"KITT Final Status:")
            print(f"  Score: {kitt.score}")
            print(f"  Damage: {kitt.damage:.1f}%")
            print(f"  Distance Traveled: {kitt.position:.0f}m")
            
            final_message = ""
            if kitt.score > 200:
                final_message = "Excellent performance, Michael!"
                print("🌟 EXCELLENT PERFORMANCE!")
            elif kitt.score > 100:
                final_message = "Good job, Michael!"
                print("👍 GOOD JOB!")
            else:
                final_message = "There is room for improvement, Michael."
                print("📈 ROOM FOR IMPROVEMENT")
            
            kitt.speak(final_message)

if __name__ == "__main__":
    start_interactive_simulation()