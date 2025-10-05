import pygame
import random
import cv2
import sys
from rehab_gamification.hand_tracking.hand_tracker import HandTracker
from rehab_gamification.games.base_game import BaseGame

class FingerPainterGame(BaseGame):
    """
    A game where the player uses their index finger to 'paint' over targets.
    """
    def __init__(self, screen, hand_tracker, cap):
        """
        Initializes the FingerPainterGame.
        :param screen: The pygame screen to draw on.
        :param hand_tracker: The shared HandTracker instance.
        :param cap: The shared camera capture instance.
        """
        super().__init__(screen, hand_tracker, cap)
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
        return {"time_left": 0}

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
