# This game is included in the app
import pygame
import random
import cv2
from rehab_gamification.games.base_game import BaseGame

class AngleMasterGame(BaseGame):
    def __init__(self, screen, hand_tracker, cap, calibration_data=None):
        """
        Initializes the AngleMasterGame.
        :param screen: The pygame screen to draw on.
        :param calibration_data: Calibration parameters.
        """
        super().__init__(screen, hand_tracker, cap, calibration_data)
        self.screen_width, self.screen_height = screen.get_size()

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.blue = (0, 0, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)

        # Game properties
        self.target_angle = random.randint(45, 160)
        self.current_angle = 0
        self.score = 0
        self.hold_time = 0
        self.hold_duration_goal = 120  # 2 seconds at 60 FPS

        # UI
        self.font = pygame.font.Font(None, 48)
        self.feedback_text = ""

        # Data recording
        self.achieved_angles = []
        self.target_angles = []
        self.max_angle = 0
        self.max_speed = 0
        self.last_hand_pos = None
        self.hand_speeds = []
        self.min_pinch_distance = float('inf')
        self.max_pinch_distance = 0
        self.pinch_distances = []

    def run(self):
        """The main game loop."""
        while not self.game_over:
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
            
            processed_frame = self.display_camera_feed(frame, draw=True)
            lm_list = self.hand_tracker.get_landmark_positions(processed_frame, draw=False)

            # Calculate hand speed
            hand_pos = self.hand_tracker.get_hand_position(lm_list)
            if self.last_hand_pos and hand_pos != (0, 0):
                speed = ((hand_pos[0] - self.last_hand_pos[0])**2 + (hand_pos[1] - self.last_hand_pos[1])**2)**0.5
                self.hand_speeds.append(speed)
                self.max_speed = max(self.max_speed, speed)
            self.last_hand_pos = hand_pos

            if len(lm_list) != 0:
                # Calculate pinch distance
                thumb_tip = lm_list[4]
                index_tip = lm_list[8]
                pinch_distance = self.hand_tracker.calculate_distance(thumb_tip, index_tip)
                self.pinch_distances.append(pinch_distance)
                self.min_pinch_distance = min(self.min_pinch_distance, pinch_distance)
                self.max_pinch_distance = max(self.max_pinch_distance, pinch_distance)
                
                # Using index finger landmarks 5, 6, 7 for angle calculation
                p1 = lm_list[5]
                p2 = lm_list[6]
                p3 = lm_list[7]
                self.current_angle = self.hand_tracker.calculate_angle(p1, p2, p3)
                self.max_angle = max(self.max_angle, self.current_angle)

                # Game logic
                angle_difference = abs(self.target_angle - self.current_angle)
                if angle_difference < 10:
                    self.feedback_text = "Perfect!"
                    self.hold_time += 1
                    if self.hold_time >= self.hold_duration_goal:
                        self.score += 100
                        self.achieved_angles.append(self.current_angle)
                        self.target_angles.append(self.target_angle)
                        self.target_angle = random.randint(45, 160)
                        self.hold_time = 0
                elif angle_difference < 20:
                    self.feedback_text = "Almost there!"
                    self.hold_time = 0
                else:
                    self.feedback_text = "Keep trying"
                    self.hold_time = 0
            else:
                self.feedback_text = "Show your hand"

            # Drawing UI Text
            target_text = self.font.render(f"Target Angle: {int(self.target_angle)}", True, self.white)
            your_text = self.font.render(f"Your Angle: {int(self.current_angle)}", True, self.blue)
            score_text = self.font.render(f"Score: {self.score}", True, self.white)
            feedback = self.font.render(self.feedback_text, True, self.green)

            self.screen.blit(target_text, (50, 50))
            self.screen.blit(your_text, (50, 120))
            self.screen.blit(score_text, (50, 190))
            self.screen.blit(feedback, (50, self.screen_height - 100))
            
            # Visual representation of the angle
            self._draw_angle_visuals(lm_list[6] if 'p2' in locals() and len(lm_list) > 6 else (self.screen_width // 2, self.screen_height // 2))


            pygame.display.flip()
            self.clock.tick(60)

        return self.get_session_data()

    def _draw_angle_visuals(self, vertex):
        """Draws lines to represent the target and current angles."""
        import math
        
        start_point = (vertex[0], vertex[1])
        
        # Target angle line
        target_rad = math.radians(180 - self.target_angle)
        target_end_x = start_point[0] + 150 * math.cos(target_rad)
        target_end_y = start_point[1] - 150 * math.sin(target_rad)
        pygame.draw.line(self.screen, self.red, start_point, (start_point[0] + 150, start_point[1]), 3)
        pygame.draw.line(self.screen, self.red, start_point, (target_end_x, target_end_y), 3)

        # Current angle line
        current_rad = math.radians(180 - self.current_angle)
        current_end_x = start_point[0] + 150 * math.cos(current_rad)
        current_end_y = start_point[1] - 150 * math.sin(current_rad)
        pygame.draw.line(self.screen, self.blue, start_point, (current_end_x, current_end_y), 5)


    def get_session_data(self):
        """Returns the recorded data for the session."""
        total_deviation = sum(abs(t - a) for t, a in zip(self.target_angles, self.achieved_angles))
        avg_deviation = total_deviation / len(self.achieved_angles) if self.achieved_angles else 0
        avg_speed = sum(self.hand_speeds) / len(self.hand_speeds) if self.hand_speeds else 0
        avg_pinch_distance = sum(self.pinch_distances) / len(self.pinch_distances) if self.pinch_distances else 0
        
        return {
            "score": self.score,
            "target_angles": self.target_angles,
            "achieved_angles": self.achieved_angles,
            "average_deviation": avg_deviation,
            "max_angle": round(self.max_angle, 2),
            "max_speed": round(self.max_speed, 2),
            "avg_speed": round(avg_speed, 2),
            "min_pinch_distance": round(self.min_pinch_distance, 2) if self.min_pinch_distance != float('inf') else 0,
            "max_pinch_distance": round(self.max_pinch_distance, 2),
            "avg_pinch_distance": round(avg_pinch_distance, 2)
        }
