import pygame
import cv2
from rehab_gamification.hand_tracking.hand_tracker import HandTracker

class CalibrationScreen:
    """
    A calibration screen that measures the user's comfortable pinch range and hand movement.
    """
    def __init__(self, screen, hand_tracker, cap):
        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()
        self.hand_tracker = hand_tracker
        self.cap = cap
        self.clock = pygame.time.Clock()
        
        # Calibration settings
        self.duration = 8  # 8 seconds
        self.start_time = pygame.time.get_ticks()
        
        # Data collection
        self.pinch_distances = []
        self.hand_positions = []
        
        # UI
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 35)
        
    def run(self):
        """Runs the calibration for the specified duration."""
        while True:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            remaining = max(0, self.duration - elapsed)
            
            if remaining <= 0:
                break
            
            # Camera and hand tracking
            success, frame = self.cap.read()
            if not success:
                continue
            
            frame = cv2.flip(frame, 1)
            frame_with_hands = self.hand_tracker.find_hands(frame, draw=True)
            frame_rgb = cv2.cvtColor(frame_with_hands, cv2.COLOR_BGR2RGB)
            frame_pygame = pygame.surfarray.make_surface(frame_rgb.transpose((1, 0, 2)))
            self.screen.blit(frame_pygame, (0, 0))
            
            # Get hand data
            lm_list = self.hand_tracker.get_landmark_positions(frame_with_hands, draw=False)
            if len(lm_list) >= 9:
                thumb_tip = lm_list[4]
                index_tip = lm_list[8]
                distance = self.hand_tracker.calculate_distance(thumb_tip, index_tip)
                self.pinch_distances.append(distance)
                
                hand_pos = self.hand_tracker.get_hand_position(lm_list)
                self.hand_positions.append(hand_pos)
            
            # UI overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            # Instructions
            title = self.font.render("Calibration", True, (255, 255, 255))
            instruction1 = self.small_font.render("Move your hand around", True, (255, 255, 255))
            instruction2 = self.small_font.render("and pinch several times", True, (255, 255, 255))
            timer = self.font.render(f"{int(remaining)}s", True, (0, 255, 0))
            
            self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))
            self.screen.blit(instruction1, (self.screen_width // 2 - instruction1.get_width() // 2, 200))
            self.screen.blit(instruction2, (self.screen_width // 2 - instruction2.get_width() // 2, 250))
            self.screen.blit(timer, (self.screen_width // 2 - timer.get_width() // 2, 400))
            
            pygame.display.flip()
            self.clock.tick(30)
            
            # Handle quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self._calculate_calibration()
        
        return self._calculate_calibration()
    
    def _calculate_calibration(self):
        """Calculates calibration parameters from collected data."""
        if not self.pinch_distances:
            return {"pinch_threshold": 40, "sensitivity": 1.0}
        
        # Calculate comfortable pinch threshold
        # Use a percentile approach: set threshold at 70th percentile of observed distances
        sorted_distances = sorted(self.pinch_distances)
        percentile_70_index = int(len(sorted_distances) * 0.7)
        pinch_threshold = sorted_distances[percentile_70_index] if percentile_70_index < len(sorted_distances) else 40
        
        # Add some buffer to make it easier to pinch
        pinch_threshold = min(pinch_threshold * 1.2, 60)  # Max threshold of 60
        
        # Calculate hand movement range for sensitivity
        if self.hand_positions:
            x_positions = [pos[0] for pos in self.hand_positions]
            y_positions = [pos[1] for pos in self.hand_positions]
            x_range = max(x_positions) - min(x_positions)
            y_range = max(y_positions) - min(y_positions)
            avg_range = (x_range + y_range) / 2
            
            # Sensitivity: smaller movements = higher sensitivity
            sensitivity = 1.5 if avg_range < 100 else 1.0
        else:
            sensitivity = 1.0
        
        return {
            "pinch_threshold": pinch_threshold,
            "sensitivity": sensitivity
        }
