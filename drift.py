import time
import random
import sys

def play_drift_game():
    """
    Terminal-based simple drift timing game.
    """
    score = 0
    total_rounds = 5  # Total number of drift attempts
    drift_prompt = ">>> PRESS [ENTER] NOW! <<<"

    # Targets and tolerances for drift timing (in seconds)
    # How long after seeing "PRESS NOW!" warning should player press Enter ideally.
    ideal_reaction_time = 0.4  # Ideal reaction time (seconds)
    perfect_window_offset = 0.15 # Deviation of +/- this much from ideal is perfect (e.g: 0.25s - 0.55s)
    good_window_offset = 0.3   # Deviation of +/- this much from ideal is good (e.g: 0.1s - 0.7s)
    max_reaction_time_limit = 1.2 # If pressed after this time, it "crashes"

    # Scoring
    points_perfect_drift = 100
    points_good_drift = 50
    points_early_drift = 10
    points_late_drift = 5 # A bit late but still counts as drift
    points_crash = -50   # Crash or too late

    print("--- Python Drift Master ---")
    print("Get ready! I'll let you know when the turn approaches.")
    print(f"When you see '{drift_prompt}', press [ENTER] as fast and accurately as possible!")
    print("Good luck!\n")
    time.sleep(3) # Give player time to read

    for current_round in range(1, total_rounds + 1):
        print(f"\n--- ROUND {current_round}/{total_rounds} ---")

        # Turn approach time (random)
        approach_delay = random.uniform(1.5, 4.0) # Wait between 1.5 and 4 seconds
        print("Turn approaching...")
        time.sleep(approach_delay)

        # Time to give drift command
        print("\n" + "="*len(drift_prompt))
        print(drift_prompt)
        print("="*len(drift_prompt))
        
        prompt_time = time.time() # Moment command was given

        # Wait for user to press Enter
        input() # Waits on this line until user presses Enter
        reaction_capture_time = time.time() # Moment Enter was pressed

        player_reaction_time = reaction_capture_time - prompt_time # Player's reaction time

        print(f"Your reaction time: {player_reaction_time:.3f} seconds")

        # Evaluation
        time_difference_from_ideal = abs(player_reaction_time - ideal_reaction_time)
        drift_message = ""
        round_score = 0

        if player_reaction_time > max_reaction_time_limit:
            drift_message = f"TOO LATE! ({player_reaction_time:.3f}s) Lost control and CRASHED!"
            round_score = points_crash
        elif time_difference_from_ideal <= perfect_window_offset:
            drift_message = f"PERFECT DRIFT! ({player_reaction_time:.3f}s) Right on time!"
            round_score = points_perfect_drift
        elif time_difference_from_ideal <= good_window_offset:
            drift_message = f"GOOD DRIFT! ({player_reaction_time:.3f}s) Almost perfect!"
            round_score = points_good_drift
        elif player_reaction_time < ideal_reaction_time - good_window_offset: # Even earlier than allowed good range
            drift_message = f"TOO EARLY! ({player_reaction_time:.3f}s) Almost spun out!"
            # Can give low positive or negative points for too early.
            # For now let's give low positive.
            round_score = points_early_drift 
        else: # Outside good range but within crash limit (a bit late)
            drift_message = f"A bit late ({player_reaction_time:.3f}s), but not bad."
            round_score = points_late_drift


        score += round_score
        print(drift_message)
        print(f"Points earned this round: {round_score}")
        print(f"Total Score: {score}")

        if current_round < total_rounds:
            time.sleep(2.5) # Short wait before next round
        else:
            time.sleep(1) # Shorter wait when game ends

    print("\n--- GAME OVER ---")
    print(f"Your total score: {score}")
    if score >= total_rounds * points_good_drift: # Average good drift and above
        print("Great performance, you're a Drift Master!")
    elif score > 0:
        print("Good effort, with a bit more practice you can master it!")
    else:
        print("Maybe drifting isn't for you... But keep trying!")

    return score

if __name__ == "__main__":
    play_drift_game()
