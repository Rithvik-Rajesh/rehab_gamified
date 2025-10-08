# dummy_data_generator.py

import json
import os
import random
from datetime import datetime, timedelta
import numpy as np

class DummyDataGenerator:
    """
    Generate realistic dummy data for rehabilitation gaming dashboard testing.
    
    Creates sessions with:
    - Progressive improvement over time
    - Realistic variation in performance
    - Different game types with appropriate metrics
    - Enhanced analytics data structure
    """
    
    def __init__(self, data_directory: str = "rehab_gamification/data"):
        self.data_directory = data_directory
        self.games = ['BalloonPop', 'MazeGame', 'FingerPainter', 'DinoGame', 'AngleMaster']
        
        # Ensure data directory exists
        os.makedirs(self.data_directory, exist_ok=True)
    
    def generate_dummy_sessions(self, num_days: int = 14, sessions_per_day: int = 2):
        """
        Generate dummy session data for dashboard testing
        
        Args:
            num_days: Number of days to generate data for
            sessions_per_day: Average sessions per day
        """
        print(f"🎲 Generating dummy data for {num_days} days...")
        
        base_date = datetime.now() - timedelta(days=num_days)
        
        # Track progression parameters
        base_accuracy = 65  # Starting accuracy
        base_smoothness = 45  # Starting movement smoothness
        base_detection_rate = 88  # Starting hand detection rate
        
        for day in range(num_days):
            current_date = base_date + timedelta(days=day)
            
            # Skip some days randomly to simulate real usage
            if random.random() < 0.15:  # 15% chance to skip a day
                continue
            
            # Variable sessions per day
            num_sessions = max(1, int(np.random.normal(sessions_per_day, 0.5)))
            
            for session in range(num_sessions):
                # Progressive improvement over time
                progress_factor = day / num_days
                
                # Select random game
                game_name = random.choice(self.games)
                
                # Generate session data
                session_data = self._generate_session_data(
                    game_name, current_date, session, 
                    base_accuracy, base_smoothness, base_detection_rate, 
                    progress_factor
                )
                
                # Save session file
                timestamp = current_date.strftime("%Y%m%d_%H%M%S")
                filename = f"session_{game_name}_{timestamp}.json"
                
                with open(os.path.join(self.data_directory, filename), 'w') as f:
                    json.dump(session_data, f, indent=2)
        
        print(f"✅ Generated dummy data files in {self.data_directory}")
    
    def _generate_session_data(self, game_name: str, date: datetime, session_num: int,
                             base_accuracy: float, base_smoothness: float, 
                             base_detection_rate: float, progress_factor: float) -> dict:
        """Generate realistic session data for a specific game"""
        
        # Apply progression and random variation
        accuracy_boost = progress_factor * 25 + random.uniform(-5, 5)
        smoothness_boost = progress_factor * 30 + random.uniform(-8, 8)
        detection_boost = progress_factor * 10 + random.uniform(-3, 3)
        
        current_accuracy = min(95, max(40, base_accuracy + accuracy_boost))
        current_smoothness = min(95, max(20, base_smoothness + smoothness_boost))
        current_detection = min(99, max(75, base_detection_rate + detection_boost))
        
        # Generate session duration (30 seconds to 3 minutes)
        session_duration = random.uniform(30, 180)
        
        # Generate frame counts based on duration (assuming 30 FPS)
        total_frames = int(session_duration * 30)
        detected_frames = int(total_frames * (current_detection / 100))
        
        # Generate movement data
        movement_count = random.randint(50, 200)
        successful_interactions = int(movement_count * (current_accuracy / 100))
        
        # Generate pinch data
        pinch_attempts = random.randint(5, 25)
        successful_pinches = int(pinch_attempts * (current_accuracy / 100))
        
        # Base session structure with enhanced analytics
        session_data = {
            "game_name": game_name,
            "session_metadata": {
                "duration_seconds": round(session_duration, 2),
                "total_frames": total_frames,
                "hand_detection_rate": round(current_detection, 2)
            },
            "hand_movement_analytics": {
                "total_movements": movement_count,
                "successful_interactions": successful_interactions,
                "interaction_effectiveness": round((successful_interactions / movement_count) * 100, 2),
                "avg_movement_speed": round(random.uniform(8, 25), 2),
                "total_movement_distance": round(random.uniform(1000, 5000), 2),
                "movement_smoothness_score": round(current_smoothness, 2),
                "tracking_lost_count": random.randint(0, 5)
            },
            "pinch_analytics": {
                "total_pinch_attempts": pinch_attempts,
                "successful_pinches": successful_pinches,
                "failed_pinches": pinch_attempts - successful_pinches,
                "pinch_success_rate": round((successful_pinches / max(1, pinch_attempts)) * 100, 2),
                "avg_pinch_distance": round(random.uniform(25, 45), 2),
                "avg_pinch_duration": round(random.uniform(0.2, 0.8), 3),
                "avg_time_between_pinches": round(random.uniform(1.5, 4.0), 2),
                "pinch_consistency": round(random.uniform(60, 95), 2)
            },
            "game_specific_metrics": self._generate_game_specific_metrics(game_name, progress_factor)
        }
        
        return session_data
    
    def _generate_game_specific_metrics(self, game_name: str, progress_factor: float) -> dict:
        """Generate game-specific metrics based on game type"""
        
        if game_name == "BalloonPop":
            base_score = 8
            score = int(base_score + (progress_factor * 12) + random.uniform(-3, 3))
            score = max(0, score)
            
            return {
                "score": score,
                "balloons_popped": score,
                "max_speed": round(random.uniform(15, 45), 2),
                "avg_speed": round(random.uniform(8, 25), 2),
                "min_pinch_distance": round(random.uniform(20, 35), 2),
                "max_pinch_distance": round(random.uniform(40, 55), 2),
                "avg_pinch_distance": round(random.uniform(30, 45), 2)
            }
        
        elif game_name == "MazeGame":
            # Better times with progression
            base_time = 120
            time_taken = base_time - (progress_factor * 40) + random.uniform(-10, 15)
            wall_touches = max(0, int(8 - progress_factor * 6 + random.uniform(-2, 2)))
            completed = time_taken < 100 or random.random() < (0.3 + progress_factor * 0.6)
            
            return {
                "time_taken": round(max(15, time_taken), 2),
                "wall_touches": wall_touches,
                "completed": completed,
                "navigation_accuracy": round(85 + progress_factor * 10 + random.uniform(-5, 5), 2)
            }
        
        elif game_name == "FingerPainter":
            targets_total = random.randint(8, 15)
            hit_rate = 0.5 + progress_factor * 0.4 + random.uniform(-0.1, 0.1)
            targets_hit = int(targets_total * hit_rate)
            
            return {
                "score": targets_hit * 10,
                "targets_hit": targets_hit,
                "total_targets": targets_total,
                "accuracy": round((targets_hit / targets_total) * 100, 2),
                "max_speed": round(random.uniform(12, 35), 2),
                "avg_speed": round(random.uniform(6, 20), 2)
            }
        
        elif game_name == "DinoGame":
            base_score = 50
            score = int(base_score + (progress_factor * 200) + random.uniform(-20, 30))
            
            return {
                "score": max(0, score),
                "jumps_made": random.randint(5, 25),
                "obstacles_avoided": random.randint(3, 20),
                "game_duration": round(random.uniform(20, 120), 2)
            }
        
        elif game_name == "AngleMaster":
            angle_accuracy = 70 + progress_factor * 20 + random.uniform(-5, 5)
            
            return {
                "angle_accuracy": round(angle_accuracy, 2),
                "target_angles_hit": random.randint(3, 12),
                "total_targets": random.randint(8, 15),
                "avg_hold_time": round(random.uniform(1.0, 3.0), 2)
            }
        
        else:
            # Default metrics for unknown games
            return {
                "score": random.randint(50, 300),
                "completion_rate": round(random.uniform(60, 95), 2)
            }
    
    def clear_existing_data(self):
        """Clear existing dummy data files"""
        if os.path.exists(self.data_directory):
            for filename in os.listdir(self.data_directory):
                if filename.startswith('session_') and filename.endswith('.json'):
                    os.remove(os.path.join(self.data_directory, filename))
            print("🗑️  Cleared existing dummy data")
    
    def generate_sample_dataset(self):
        """Generate a complete sample dataset for dashboard testing"""
        print("🎯 Generating comprehensive sample dataset...")
        
        # Clear existing data
        self.clear_existing_data()
        
        # Generate data for different time periods
        # Last 2 weeks - regular usage
        self.generate_dummy_sessions(num_days=14, sessions_per_day=2)
        
        # Add some older sessions for trend analysis
        older_base = datetime.now() - timedelta(days=25)
        for day in range(5):  # 5 days of older data
            current_date = older_base + timedelta(days=day)
            for session in range(random.randint(1, 3)):
                game_name = random.choice(self.games)
                session_data = self._generate_session_data(
                    game_name, current_date, session,
                    55, 35, 82, 0.1  # Lower baseline for older sessions
                )
                
                timestamp = current_date.strftime("%Y%m%d_%H%M%S")
                filename = f"session_{game_name}_{timestamp}.json"
                
                with open(os.path.join(self.data_directory, filename), 'w') as f:
                    json.dump(session_data, f, indent=2)
        
        print("✅ Sample dataset generation complete!")
        print(f"📊 Ready to generate dashboard from {self.data_directory}")

if __name__ == "__main__":
    # Generate sample data for testing
    generator = DummyDataGenerator()
    generator.generate_sample_dataset()
    
    print("\n🎉 Dummy data generation complete!")
    print("📁 Check the data directory for generated session files")
    print("🚀 Ready to run enhanced dashboard!")