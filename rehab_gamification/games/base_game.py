# base_game.py

import pygame
import cv2
import time
import math
import numpy as np
# This import path might be different for you, adjust if necessary
from rehab_gamification.hand_tracking.hand_tracker import HandTracker

class BaseGame:
    """
    A base class for games to handle camera feed and hand tracking with enhanced data collection.
    """
    def __init__(self, screen, hand_tracker, cap, calibration_data=None):
        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.hand_tracker = hand_tracker
        self.cap = cap
        self.calibration_data = calibration_data or {"pinch_threshold": 40, "sensitivity": 1.0}
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        
        # Enhanced data tracking
        self.session_start_time = time.time()
        self.hand_movement_data = {
            "total_movements": 0,
            "successful_interactions": 0,
            "hand_positions": [],  # Store (x, y, timestamp) for movement analysis
            "movement_distances": [],  # Distance between consecutive hand positions
            "movement_speeds": [],  # Speed of hand movement
            "hand_detected_frames": 0,
            "total_frames": 0,
            "tracking_lost_count": 0,
            "movement_smoothness_score": 0
        }
        
        self.pinch_data = {
            "total_pinch_attempts": 0,
            "successful_pinches": 0,
            "pinch_distances": [],  # Distance between thumb and index finger during pinches
            "pinch_durations": [],  # How long each pinch was held
            "pinch_positions": [],  # Where pinches occurred
            "pinch_timing": [],  # Time between consecutive pinches
            "failed_pinches": 0,
            "pinch_accuracy": 0
        }
        
        # Internal tracking variables
        self.last_hand_position = None
        self.last_frame_time = time.time()
        self.current_pinch_start = None
        self.last_pinch_time = None
        self.was_hand_detected_last_frame = False

    def display_camera_feed(self, frame, draw=True): # <<< CHANGED: Added draw parameter
        """
        Processes and displays the camera feed on the screen with enhanced tracking.
        :param frame: The camera frame to process.
        :param draw: Whether to draw the full hand skeleton.
        :return: The processed frame (without the skeleton drawn on it).
        """
        # Flip the frame horizontally for a selfie-view display.
        frame = cv2.flip(frame, 1)
        
        # Find hands and draw landmarks (now respects the 'draw' parameter)
        frame_with_hands = self.hand_tracker.find_hands(frame, draw=draw) # <<< CHANGED
        
        # Track hand data for analytics
        self._track_hand_data(frame_with_hands)

        # Convert the BGR image to RGB.
        frame_rgb = cv2.cvtColor(frame_with_hands, cv2.COLOR_BGR2RGB)

        # The transpose is necessary to swap the axes for pygame
        frame_pygame = pygame.surfarray.make_surface(frame_rgb.transpose((1, 0, 2)))
        
        # Scale the camera feed to fit the screen
        frame_scaled = pygame.transform.scale(frame_pygame, (self.screen_width, self.screen_height))

        self.screen.blit(frame_scaled, (0, 0))
        
        # Return the original processed frame (not the pygame surface)
        # for landmark position calculation.
        return frame_with_hands
    
    def _track_hand_data(self, frame):
        """
        Internal method to track hand movement and detection data.
        """
        current_time = time.time()
        self.hand_movement_data["total_frames"] += 1
        
        # Get hand landmarks
        lm_list = self.hand_tracker.get_landmark_positions(frame, draw=False)
        
        if lm_list and len(lm_list) > 8:  # Hand detected
            self.hand_movement_data["hand_detected_frames"] += 1
            
            # Track hand position (using index finger tip as reference point)
            current_pos = (lm_list[8][1], lm_list[8][2])
            
            if self.last_hand_position is not None:
                # Calculate movement distance and speed
                distance = math.sqrt(
                    (current_pos[0] - self.last_hand_position[0])**2 + 
                    (current_pos[1] - self.last_hand_position[1])**2
                )
                time_diff = current_time - self.last_frame_time
                
                if time_diff > 0 and distance > 1:  # Only track significant movements
                    speed = distance / time_diff
                    self.hand_movement_data["movement_distances"].append(distance)
                    self.hand_movement_data["movement_speeds"].append(speed)
                    self.hand_movement_data["total_movements"] += 1
            
            # Store position with timestamp
            self.hand_movement_data["hand_positions"].append((current_pos[0], current_pos[1], current_time))
            
            # Keep only last 1000 positions to avoid memory issues
            if len(self.hand_movement_data["hand_positions"]) > 1000:
                self.hand_movement_data["hand_positions"] = self.hand_movement_data["hand_positions"][-1000:]
            
            self.last_hand_position = current_pos
            
            # Track when hand detection is restored after being lost
            if not self.was_hand_detected_last_frame:
                self.was_hand_detected_last_frame = True
                
        else:  # Hand not detected
            if self.was_hand_detected_last_frame:
                self.hand_movement_data["tracking_lost_count"] += 1
                self.was_hand_detected_last_frame = False
        
        self.last_frame_time = current_time
    
    def track_pinch_event(self, lm_list, was_successful=False, target_position=None):
        """
        Track pinch gesture data for analytics.
        :param lm_list: Hand landmark list
        :param was_successful: Whether the pinch accomplished its intended action
        :param target_position: Position of the target (if applicable)
        """
        if not lm_list or len(lm_list) < 9:
            return
            
        current_time = time.time()
        is_pinching, pinch_pos = self.hand_tracker.get_pinch_gesture(lm_list)
        
        if is_pinching:
            if self.current_pinch_start is None:
                # Start of a new pinch
                self.current_pinch_start = current_time
                self.pinch_data["total_pinch_attempts"] += 1
                
                # Calculate time between pinches
                if self.last_pinch_time is not None:
                    time_between_pinches = current_time - self.last_pinch_time
                    self.pinch_data["pinch_timing"].append(time_between_pinches)
                
                # Store pinch position and distance
                thumb_tip = lm_list[4]
                index_tip = lm_list[8]
                pinch_distance = self.hand_tracker.calculate_distance(thumb_tip, index_tip)
                
                self.pinch_data["pinch_distances"].append(pinch_distance)
                self.pinch_data["pinch_positions"].append(pinch_pos)
                
                if was_successful:
                    self.pinch_data["successful_pinches"] += 1
                    self.hand_movement_data["successful_interactions"] += 1
                else:
                    self.pinch_data["failed_pinches"] += 1
                    
        else:
            if self.current_pinch_start is not None:
                # End of pinch - calculate duration
                pinch_duration = current_time - self.current_pinch_start
                self.pinch_data["pinch_durations"].append(pinch_duration)
                self.last_pinch_time = current_time
                self.current_pinch_start = None
    
    def calculate_movement_smoothness(self):
        """
        Calculate movement smoothness based on speed variations.
        Lower values indicate smoother movement.
        """
        if len(self.hand_movement_data["movement_speeds"]) < 3:
            return 0
            
        speeds = self.hand_movement_data["movement_speeds"]
        speed_changes = [abs(speeds[i+1] - speeds[i]) for i in range(len(speeds)-1)]
        
        if not speed_changes:
            return 0
            
        # Smoothness score: lower variation in speed = higher smoothness
        avg_speed_change = sum(speed_changes) / len(speed_changes)
        avg_speed = sum(speeds) / len(speeds)
        
        # Normalize to 0-100 scale (100 = perfectly smooth)
        if avg_speed > 0:
            smoothness = max(0, 100 - (avg_speed_change / avg_speed * 100))
        else:
            smoothness = 0
            
        return round(smoothness, 2)
    
    def get_enhanced_session_data(self):
        """
        Get comprehensive session data for dashboard analytics.
        """
        session_duration = time.time() - self.session_start_time
        
        # Calculate hand detection rate
        hand_detection_rate = 0
        if self.hand_movement_data["total_frames"] > 0:
            hand_detection_rate = (self.hand_movement_data["hand_detected_frames"] / 
                                 self.hand_movement_data["total_frames"]) * 100
        
        # Calculate movement metrics
        avg_movement_speed = 0
        total_movement_distance = 0
        if self.hand_movement_data["movement_speeds"]:
            avg_movement_speed = sum(self.hand_movement_data["movement_speeds"]) / len(self.hand_movement_data["movement_speeds"])
            total_movement_distance = sum(self.hand_movement_data["movement_distances"])
        
        # Calculate pinch metrics
        pinch_success_rate = 0
        avg_pinch_distance = 0
        avg_pinch_duration = 0
        avg_time_between_pinches = 0
        
        if self.pinch_data["total_pinch_attempts"] > 0:
            pinch_success_rate = (self.pinch_data["successful_pinches"] / 
                                self.pinch_data["total_pinch_attempts"]) * 100
        
        if self.pinch_data["pinch_distances"]:
            avg_pinch_distance = sum(self.pinch_data["pinch_distances"]) / len(self.pinch_data["pinch_distances"])
        
        if self.pinch_data["pinch_durations"]:
            avg_pinch_duration = sum(self.pinch_data["pinch_durations"]) / len(self.pinch_data["pinch_durations"])
            
        if self.pinch_data["pinch_timing"]:
            avg_time_between_pinches = sum(self.pinch_data["pinch_timing"]) / len(self.pinch_data["pinch_timing"])
        
        # Calculate overall interaction effectiveness
        interaction_effectiveness = 0
        if self.hand_movement_data["total_movements"] > 0:
            interaction_effectiveness = (self.hand_movement_data["successful_interactions"] / 
                                       self.hand_movement_data["total_movements"]) * 100
        
        return {
            "session_metadata": {
                "duration_seconds": round(session_duration, 2),
                "total_frames": self.hand_movement_data["total_frames"],
                "hand_detection_rate": round(hand_detection_rate, 2)
            },
            "hand_movement_analytics": {
                "total_movements": self.hand_movement_data["total_movements"],
                "successful_interactions": self.hand_movement_data["successful_interactions"],
                "interaction_effectiveness": round(interaction_effectiveness, 2),
                "avg_movement_speed": round(avg_movement_speed, 2),
                "total_movement_distance": round(total_movement_distance, 2),
                "movement_smoothness_score": self.calculate_movement_smoothness(),
                "tracking_lost_count": self.hand_movement_data["tracking_lost_count"]
            },
            "pinch_analytics": {
                "total_pinch_attempts": self.pinch_data["total_pinch_attempts"],
                "successful_pinches": self.pinch_data["successful_pinches"],
                "failed_pinches": self.pinch_data["failed_pinches"],
                "pinch_success_rate": round(pinch_success_rate, 2),
                "avg_pinch_distance": round(avg_pinch_distance, 2),
                "avg_pinch_duration": round(avg_pinch_duration, 3),
                "avg_time_between_pinches": round(avg_time_between_pinches, 2),
                "pinch_consistency": self._calculate_pinch_consistency()
            }
        }
    
    def _calculate_pinch_consistency(self):
        """
        Calculate how consistent pinch distances are (lower variation = better).
        """
        if len(self.pinch_data["pinch_distances"]) < 2:
            return 0
            
        distances = self.pinch_data["pinch_distances"]
        mean_distance = sum(distances) / len(distances)
        
        if mean_distance == 0:
            return 0
            
        variance = sum((d - mean_distance) ** 2 for d in distances) / len(distances)
        std_dev = math.sqrt(variance)
        
        # Consistency score: lower std deviation relative to mean = higher consistency
        consistency = max(0, 100 - (std_dev / mean_distance * 100))
        return round(consistency, 2)

    def show_game_over_screen(self):
        """Displays a 'Game Over' screen and waits for input to exit."""
        darken_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        darken_surface.fill((0, 0, 0, 150))
        self.screen.blit(darken_surface, (0, 0))

        font = pygame.font.Font(None, 74)
        small_font = pygame.font.Font(None, 40)
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        exit_text = small_font.render("Pinch to Exit", True, (255, 255, 255))

        game_over_rect = game_over_text.get_rect(center=(self.screen_width / 2, self.screen_height / 2 - 50))
        exit_rect = exit_text.get_rect(center=(self.screen_width / 2, self.screen_height / 2 + 50))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(exit_text, exit_rect)
        pygame.display.flip()

        waiting = True
        was_pinching = True 
        while waiting:
            success, frame = self.cap.read()
            if success:
                frame = cv2.flip(frame, 1)
                lm_list = self.hand_tracker.get_landmark_positions(self.hand_tracker.find_hands(frame, draw=False), draw=False)
                is_pinching, _ = self.hand_tracker.get_pinch_gesture(lm_list)
                if is_pinching and not was_pinching:
                    waiting = False
                was_pinching = is_pinching

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.game_over = True # Ensure main loop also exits
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            
            self.clock.tick(20)

    def run(self):
        # This method should be implemented by child game classes
        raise NotImplementedError

    def __del__(self):
        """Release the camera when the game object is destroyed."""
        # Camera is now managed by MainApp, so we don't release it here.
        pass