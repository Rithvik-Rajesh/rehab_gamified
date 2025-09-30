import pygame
from hand_tracking.hand_tracker import HandTracker
from games.base_game import BaseGame
import random

class AngleMasterGame(BaseGame):
    def __init__(self, screen, hand_tracker):
        super().__init__(screen, hand_tracker)
        self.target_angle = 90
        self.current_angle = 0
        self.score = 0
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 50)
        self.game_over = False
        self.achieved_angles = []

    def run(self):
        cap = self.hand_tracker.cap
        while not self.game_over:
            success, frame = cap.read()
            if not success:
                continue

            processed_frame = self.display_camera_feed(frame)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_over = True

            landmarks = self.hand_tracker.get_landmark_positions(processed_frame)
            if landmarks and len(landmarks) > 7:
                p1 = landmarks[5][1:] # MCP
                p2 = landmarks[6][1:] # PIP
                p3 = landmarks[7][1:] # DIP
                self.current_angle = self.hand_tracker.calculate_angle(p1, p2, p3)
                
                # Flip angle for intuitive display
                self.current_angle = 360 - self.current_angle if self.current_angle > 180 else self.current_angle

                if abs(self.current_angle - self.target_angle) < 10:
                    self.score += 1 # Points for holding the angle

            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(30)
            
            if self.score > 500: # Example win condition
                self.achieved_angles.append(self.current_angle)
                self.game_over = True

        avg_deviation = 0
        if self.achieved_angles:
            avg_deviation = sum([abs(self.target_angle - a) for a in self.achieved_angles]) / len(self.achieved_angles)

        session_data = {
            "score": self.score,
            "target_angle": self.target_angle,
            "final_angle": self.current_angle,
            "average_deviation": avg_deviation
        }
        return session_data

    def draw_ui(self):
        target_text = self.font.render(f"Target: {self.target_angle:.0f}°", True, (255, 255, 0))
        self.screen.blit(target_text, (50, 50))

        current_text = self.font.render(f"Your Angle: {self.current_angle:.0f}°", True, (255, 255, 255))
        self.screen.blit(current_text, (50, 150))

        score_text = self.small_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.screen_width - 200, 50))
