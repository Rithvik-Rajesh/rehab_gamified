# Ballon_pop.py

import pygame
import random
import sys
import os
from rehab_gamification.games.base_game import BaseGame
import cv2

# --- Constants ---
HAND_CURSOR_SIZE = 25 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# --- Balloon Class ---
class Balloon:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = random.randint(30, 50) 
        self.x = random.randint(self.radius, self.screen_width - self.radius)
        self.y = self.screen_height + self.radius 
        self.speed = random.randint(2, 5)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def move(self):
        self.y -= self.speed
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius)

    def is_popped_by(self, pos):
        return self.rect.collidepoint(pos)

# --- BalloonPopGame Class ---
class BalloonPopGame(BaseGame):
    def __init__(self, screen, hand_tracker, cap, calibration_data=None):
        super().__init__(screen, hand_tracker, cap, calibration_data)
        self.balloons = []
        self.score = 0
        self.font = pygame.font.Font(None, 50)
        self.game_over_font = pygame.font.Font(None, 75)
        
        # Tracking metrics
        self.max_speed = 0
        self.last_hand_pos = None
        self.hand_speeds = []
        self.min_pinch_distance = float('inf')
        self.max_pinch_distance = 0
        self.pinch_distances = []
        
        try:
            self.pop_sound = pygame.mixer.Sound('./rehab_gamification/assets/pop.wav')
        except pygame.error:
            print("Warning: 'pop.wav' not found. Sound will not play.")
            self.pop_sound = None

    def spawn_balloon(self):
        if len(self.balloons) < 15:
            self.balloons.append(Balloon(self.screen_width, self.screen_height))

    def run(self):
        cam_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        cam_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        while not self.game_over:
            success, frame = self.cap.read()
            if not success:
                print("Failed to grab camera frame.")
                continue
            
            processed_frame = self.display_camera_feed(frame, draw=True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_over = True

            # --- Game Logic ---
            if random.randint(1, 15) == 1:
                self.spawn_balloon()

            lm_list = self.hand_tracker.get_landmark_positions(processed_frame, draw=False)
            hand_pos = self.hand_tracker.get_hand_position(lm_list)
            
            # Calculate hand speed (keeping existing logic for compatibility)
            if self.last_hand_pos and hand_pos != (0, 0):
                speed = ((hand_pos[0] - self.last_hand_pos[0])**2 + (hand_pos[1] - self.last_hand_pos[1])**2)**0.5
                self.hand_speeds.append(speed)
                self.max_speed = max(self.max_speed, speed)
            self.last_hand_pos = hand_pos
            
            # Calculate pinch distance (keeping existing logic for compatibility)
            if len(lm_list) >= 9:
                thumb_tip = lm_list[4]
                index_tip = lm_list[8]
                pinch_distance = self.hand_tracker.calculate_distance(thumb_tip, index_tip)
                self.pinch_distances.append(pinch_distance)
                self.min_pinch_distance = min(self.min_pinch_distance, pinch_distance)
                self.max_pinch_distance = max(self.max_pinch_distance, pinch_distance)
            
            is_pinching, pinch_pos = self.hand_tracker.get_pinch_gesture(
                lm_list, 
                pinch_threshold=self.calibration_data.get("pinch_threshold", 40)
            )

            if cam_w > 0 and cam_h > 0:
                pinch_pos = (int(pinch_pos[0] * self.screen_width / cam_w), int(pinch_pos[1] * self.screen_height / cam_h))

            # Check for balloon popping
            balloon_popped = False
            for balloon in self.balloons[:]:
                balloon.move()
                if balloon.y < -balloon.radius:
                    self.balloons.remove(balloon)
                
                if is_pinching:
                    if balloon.is_popped_by(pinch_pos):
                        self.balloons.remove(balloon)
                        self.score += 1
                        balloon_popped = True
                        if self.pop_sound:
                            self.pop_sound.play()
                        break  # Only pop one balloon per pinch
            
            # Track pinch event with enhanced analytics
            if is_pinching:
                self.track_pinch_event(lm_list, was_successful=balloon_popped, target_position=pinch_pos)

            # --- Drawing ---
            for balloon in self.balloons:
                balloon.draw(self.screen)

            # Draw the pinch cursor on top of the skeleton
            if is_pinching:
                pygame.draw.circle(self.screen, BLUE, pinch_pos, HAND_CURSOR_SIZE)

            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            self.clock.tick(60)

        self.show_game_over_screen()
        return self.get_session_data()

    def show_game_over_screen(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.game_over_font.render("Game Over", True, WHITE)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        
        self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2, self.screen_height // 2 - 50))
        self.screen.blit(final_score_text, (self.screen_width // 2 - final_score_text.get_width() // 2, self.screen_height // 2 + 50))
        
        continue_text = self.font.render("Click to return to menu", True, WHITE)
        self.screen.blit(continue_text, (self.screen_width // 2 - continue_text.get_width() // 2, self.screen_height - 100))
        pygame.display.flip()

        waiting_for_click = True
        while waiting_for_click:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting_for_click = False

    def get_session_data(self):
        # Get enhanced session data from base class
        enhanced_data = self.get_enhanced_session_data()
        
        # Add balloon-specific game metrics
        avg_speed = sum(self.hand_speeds) / len(self.hand_speeds) if self.hand_speeds else 0
        avg_pinch_distance = sum(self.pinch_distances) / len(self.pinch_distances) if self.pinch_distances else 0
        
        # Combine with existing balloon pop specific data
        balloon_specific_data = {
            "score": self.score,
            "balloons_popped": self.score,
            "max_speed": round(self.max_speed, 2),
            "avg_speed": round(avg_speed, 2),
            "min_pinch_distance": round(self.min_pinch_distance, 2) if self.min_pinch_distance != float('inf') else 0,
            "max_pinch_distance": round(self.max_pinch_distance, 2),
            "avg_pinch_distance": round(avg_pinch_distance, 2)
        }
        
        # Merge enhanced data with game-specific data
        enhanced_data["game_specific_metrics"] = balloon_specific_data
        enhanced_data["game_name"] = "BalloonPop"
        
        return enhanced_data
