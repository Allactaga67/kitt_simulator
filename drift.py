import time
import random

class Drift:
    def __init__(self):
        self.is_drifting = False
        self.score = 0
        self.total_rounds = 5
        self.current_round = 0
        self.is_running = False
        
        # Timing thresholds (in seconds)
        self.perfect_time = 0.4  # Ideal drift time
        self.perfect_range = 0.1  # Perfect timing range (±0.1s)
        self.good_range = 0.2    # Good timing range (±0.2s)
        self.early_limit = 0.1   # Early drift limit
        self.late_limit = 0.7    # Late drift limit

    def start(self):
        """Start drift mode"""
        if not self.is_drifting:
            self.is_drifting = True
            self.score = 0
            self.current_round = 0
            print("Drift mode started")
            print("\n=== DRIFT GAME ===")
            print("Press Enter as quickly as possible when you see 'DRIFT!'")
            print("You have 5 rounds to score points!")
            print("Perfect timing (0.4s ±0.1s): +50 points")
            print("Good timing (0.4s ±0.2s): +25 points")
            print("Early drift (<0.3s): -10 points")
            print("Late drift (>1.1s): -5 points")
            print("Crash: -50 points")
            print("==================\n")
            return True
        print("Drift mode is already running")
        return False

    def stop(self):
        """Stop drift mode"""
        if self.is_drifting:
            self.is_drifting = False
            print(f"Drift mode stopped. Final score: {self.score}")
            return True
        print("Drift mode is not running")
        return False

    def run(self):
        """Run the drift game"""
        self.is_running = True
        while self.current_round < self.total_rounds and self.is_running:
            self.current_round += 1
            print(f"\nRound {self.current_round}/{self.total_rounds}")
            print("Get ready...")
            time.sleep(random.uniform(1.0, 3.0))
            
            if not self.is_running:  # Check if game was stopped
                print("\nGame stopped by user")
                return self.score
            
            print("\nDRIFT!")
            start_time = time.time()
            input()
            reaction_time = time.time() - start_time
            
            # Calculate time difference from perfect time
            time_diff = abs(reaction_time - self.perfect_time)
            
            # Score based on time difference from perfect time (0.4s)
            if time_diff <= self.perfect_range:  # 0.3s - 0.5s
                points = 50
                message = "PERFECT DRIFT!"
            elif time_diff <= self.good_range:  # 0.2s - 0.6s
                points = 25
                message = "Good drift!"
            elif reaction_time < (self.perfect_time - self.early_limit):  # < 0.3s
                points = -10
                message = "Too early!"
            elif reaction_time > (self.perfect_time + self.late_limit):  # > 1.1s
                points = -5
                message = "Too late!"
            else:
                points = -50
                message = "CRASH!"
            
            self.score += points
            print(f"{message} ({reaction_time:.3f}s)")
            print(f"Points: {points}")
            print(f"Total score: {self.score}")
            
            if self.current_round < self.total_rounds and self.is_running:
                time.sleep(1)
        
        if self.is_running:  # Only show game over if game wasn't stopped
            print("\n=== GAME OVER ===")
            print(f"Final score: {self.score}")
        return self.score

if __name__ == "__main__":
    drift_game = Drift()
    drift_game.start()
    drift_game.run()
    drift_game.stop()