import pygame
import random
import cv2
import sys
from rehab_gamification.hand_tracking.hand_tracker import HandTracker
from rehab_gamification.games.base_game import BaseGame

class FingerPainterGame(BaseGame):
    def __init__(self, screen, hand_tracker, cap, calibration_data=None):
        """
        Initializes the FingerPainterGame.
        :param screen: The pygame screen to draw on.
        :param hand_tracker: The shared HandTracker instance.
        :param cap: The shared camera capture instance.
        :param calibration_data: Calibration parameters.
        """
        super().__init__(screen, hand_tracker, cap, calibration_data)
        self.screen_width, self.screen_height = screen.get_size()

        # Colors and Fonts
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.font = pygame.font.Font(None, 36)

        # Game state
        self.score = 0
        self.game_over = False
        self.targets = []
        self.cursor_pos = (0, 0)
        self.start_time = pygame.time.get_ticks()
        self.time_limit = 15000  # 15 seconds

        # Data recording
        self.targets_hit = 0
        self.total_targets = 0

        # Drawing state
        self.is_drawing = False
        self.last_pos = None
        self.timer = 15  # 15-second timer
        self.last_tick = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 50)
        
        # Tracking metrics
        self.max_speed = 0
        self.last_hand_pos = None
        self.hand_speeds = []
        self.min_pinch_distance = float('inf')
        self.max_pinch_distance = 0
        self.pinch_distances = []

        self._create_targets(5)

    def _create_targets(self, count):
        """Creates a number of targets at random positions."""
        self.targets.clear()
        for _ in range(count):
            target_rect = pygame.Rect(
                random.randint(50, self.screen_width - 100),
                random.randint(50, self.screen_height - 100),
                50, 50
            )
            self.targets.append(target_rect)
        self.total_targets += count

    def run(self):
        """The main game loop."""
        clock = pygame.time.Clock()
        draw_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        while not self.game_over:
            # --- Timer Logic ---
            if self.timer > 0:
                if pygame.time.get_ticks() - self.last_tick >= 1000:
                    self.timer -= 1
                    self.last_tick = pygame.time.get_ticks()
            else:
                self.game_over = True
                continue

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_over = True

            # Hand tracking
            success, frame = self.cap.read()
            if not success:
                continue

            processed_frame = self.display_camera_feed(frame, draw=False)
            lm_list = self.hand_tracker.get_landmark_positions(processed_frame, draw=False)
            is_pinching, pinch_pos = self.hand_tracker.get_pinch_gesture(
                lm_list,
                pinch_threshold=self.calibration_data.get("pinch_threshold", 40)
            )
            
            hand_pos = self.hand_tracker.get_hand_position(lm_list)
            
            # Calculate hand speed
            if self.last_hand_pos and hand_pos != (0, 0):
                speed = ((hand_pos[0] - self.last_hand_pos[0])**2 + (hand_pos[1] - self.last_hand_pos[1])**2)**0.5
                self.hand_speeds.append(speed)
                self.max_speed = max(self.max_speed, speed)
            self.last_hand_pos = hand_pos
            
            # Calculate pinch distance
            if len(lm_list) >= 9:
                thumb_tip = lm_list[4]
                index_tip = lm_list[8]
                pinch_distance = self.hand_tracker.calculate_distance(thumb_tip, index_tip)
                self.pinch_distances.append(pinch_distance)
                self.min_pinch_distance = min(self.min_pinch_distance, pinch_distance)
                self.max_pinch_distance = max(self.max_pinch_distance, pinch_distance)

            if lm_list:
                # Use index finger tip (landmark 8)
                index_finger_tip = lm_list[8]
                self.cursor_pos = (index_finger_tip[1], index_finger_tip[2])

                # Collision detection
                cursor_rect = pygame.Rect(self.cursor_pos[0] - 10, self.cursor_pos[1] - 10, 20, 20)
                for target in self.targets[:]:
                    if cursor_rect.colliderect(target):
                        self.targets.remove(target)
                        self.score += 10
                        self.targets_hit += 1

            # Check if all targets are hit
            if not self.targets:
                self._create_targets(5)

            # Drawing
            self.screen.fill(self.white)
            
            # Draw targets
            for target in self.targets:
                pygame.draw.rect(self.screen, self.green, target)

            # Draw cursor
            pygame.draw.circle(self.screen, self.blue, self.cursor_pos, 15)

            # Draw UI
            score_text = self.font.render(f"Score: {self.score}", True, self.black)
            time_left = (self.time_limit - (pygame.time.get_ticks() - self.start_time)) // 1000
            time_text = self.font.render(f"Time: {time_left}", True, self.black)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(time_text, (self.screen_width - 150, 10))

            pygame.display.flip()
            clock.tick(60)

        # Show game over screen before returning
        self.show_game_over_screen()
        # Return session data (can be expanded later)
        avg_speed = sum(self.hand_speeds) / len(self.hand_speeds) if self.hand_speeds else 0
        avg_pinch_distance = sum(self.pinch_distances) / len(self.pinch_distances) if self.pinch_distances else 0
        return {
            "time_left": 0,
            "max_speed": round(self.max_speed, 2),
            "avg_speed": round(avg_speed, 2),
            "min_pinch_distance": round(self.min_pinch_distance, 2) if self.min_pinch_distance != float('inf') else 0,
            "max_pinch_distance": round(self.max_pinch_distance, 2),
            "avg_pinch_distance": round(avg_pinch_distance, 2),
            "score": 0  # Could track number of strokes or coverage
        }

if __name__ == '__main__':
    # This part is for testing the game directly
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Finger Painter Test")
    
    # Initialize HandTracker and camera here for testing
    hand_tracker = HandTracker()
    cap = cv2.VideoCapture(0)
    
    game = FingerPainterGame(screen, hand_tracker, cap)
    session_data = game.run()
    
    print("Game Over!")
    print("Session Data:", session_data)
    
    pygame.quit()
    sys.exit()
