import pygame
import random
import cv2
import sys
import os
from rehab_gamification.hand_tracking.hand_tracker import HandTracker

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BALLOON_SIZE = 50
HAND_CURSOR_SIZE = 20
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FONT_NAME = 'arial'
FONT_SIZE = 30

# --- Balloon Class ---
class Balloon:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - BALLOON_SIZE)
        self.y = 0
        self.speed = random.randint(1, 3)
        self.rect = pygame.Rect(self.x, self.y, BALLOON_SIZE, BALLOON_SIZE)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def move(self):
        self.y += self.speed
        self.rect.top = self.y

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

# --- BalloonPopGame Class ---
class BalloonPopGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.game_over_font = pygame.font.SysFont(FONT_NAME, 75)
        
        self.balloons = []
        self.score = 0
        self.game_over = False
        
        self.hand_tracker = HandTracker()
        self.cap = cv2.VideoCapture(0)

        # Load sound, with a fallback if the file is missing
        try:
            self.pop_sound = pygame.mixer.Sound(os.path.join('rehab_gamification', 'assets', 'pop.wav'))
        except pygame.error:
            print("Warning: 'pop.wav' not found. Sound will not play.")
            self.pop_sound = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if not self.game_over:
                self.update()
                self.draw()
            else:
                self.show_game_over_screen()

            pygame.display.flip()
            self.clock.tick(60)

        self.cap.release()
        cv2.destroyAllWindows()
        return self.get_session_data()

    def update(self):
        success, frame = self.cap.read()
        if not success:
            return

        frame = cv2.flip(frame, 1)
        frame = self.hand_tracker.find_hands(frame, draw=False)
        lm_list = self.hand_tracker.get_landmark_positions(frame, draw=False)
        
        is_pinching, pinch_pos = self.hand_tracker.get_pinch_gesture(lm_list)

        if random.randint(1, 20) == 1:
            self.balloons.append(Balloon())

        for balloon in self.balloons[:]:
            balloon.move()
            if balloon.y > SCREEN_HEIGHT:
                self.balloons.remove(balloon)
            
            if is_pinching and pinch_pos:
                pinch_rect = pygame.Rect(pinch_pos[0] - HAND_CURSOR_SIZE // 2, 
                                         pinch_pos[1] - HAND_CURSOR_SIZE // 2, 
                                         HAND_CURSOR_SIZE, HAND_CURSOR_SIZE)
                if balloon.rect.colliderect(pinch_rect):
                    self.balloons.remove(balloon)
                    self.score += 1
                    if self.pop_sound:
                        self.pop_sound.play()
        
        if self.score > 10: # Game over condition
            self.game_over = True

    def draw(self):
        self.screen.fill(WHITE)

        for balloon in self.balloons:
            balloon.draw(self.screen)

        # This part is tricky because we need the hand position for the cursor
        # Let's just show the pinch position for now
        lm_list = self.hand_tracker.get_landmark_positions(self.hand_tracker.find_hands(cv2.flip(self.cap.read()[1], 1), draw=False), draw=False)
        is_pinching, pinch_pos = self.hand_tracker.get_pinch_gesture(lm_list)
        
        if pinch_pos:
            cursor_color = BLUE if is_pinching else RED
            pygame.draw.circle(self.screen, cursor_color, pinch_pos, HAND_CURSOR_SIZE)

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

    def show_game_over_screen(self):
        self.screen.fill(WHITE)
        game_over_text = self.game_over_font.render("Game Over", True, BLACK)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, BLACK)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Add a "Click to continue" message
        continue_text = self.font.render("Click to return to menu", True, BLACK)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))

        # Wait for a click to exit the game over screen
        waiting_for_click = True
        while waiting_for_click:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting_for_click = False
            pygame.display.flip()


    def get_session_data(self):
        return {
            "score": self.score,
            "balloons_popped": self.score 
        }
