import pygame
import random
import cv2
import sys
import os

# Add the parent directory to the path to import the hand_tracking module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import hand_tracking

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

# --- Main Game Loop ---
def main():
    pygame.init()
    pygame.mixer.init() # Initialize the mixer
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Balloon Pop")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    game_over_font = pygame.font.SysFont(FONT_NAME, 75)

    # Load sound, with a fallback if the file is missing
    try:
        pop_sound = pygame.mixer.Sound(os.path.join('assets', 'pop.wav'))
    except pygame.error:
        print("Warning: 'pop.wav' not found in 'assets' directory. Sound will not play.")
        pop_sound = None

    balloons = []
    score = 0
    
    cap = cv2.VideoCapture(0)

    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            # --- Hand Tracking ---
            success, frame = cap.read()
            if not success:
                continue
            
            frame = cv2.flip(frame, 1)
            landmarks = hand_tracking.detect_hands(frame)
            is_pinching, pinch_pos = hand_tracking.get_pinch_gesture(landmarks, frame.shape)
            hand_pos = hand_tracking.get_hand_position(landmarks, frame.shape)

            # --- Game Logic ---
            if random.randint(1, 20) == 1:  # Create new balloons randomly
                balloons.append(Balloon())

            for balloon in balloons[:]:
                balloon.move()
                if balloon.y > SCREEN_HEIGHT:
                    balloons.remove(balloon)
                
                if is_pinching and pinch_pos:
                    pinch_rect = pygame.Rect(pinch_pos[0] - HAND_CURSOR_SIZE // 2, 
                                             pinch_pos[1] - HAND_CURSOR_SIZE // 2, 
                                             HAND_CURSOR_SIZE, HAND_CURSOR_SIZE)
                    if balloon.rect.colliderect(pinch_rect):
                        balloons.remove(balloon)
                        score += 1
                        if pop_sound:
                            pop_sound.play()
            
            if score > 10:
                game_over = True

            # --- Drawing ---
            screen.fill(WHITE)

            for balloon in balloons:
                balloon.draw(screen)

            if hand_pos:
                # If pinching, move cursor to pinch position for accurate feedback
                cursor_pos = pinch_pos if is_pinching and pinch_pos else hand_pos
                cursor_color = BLUE if is_pinching else RED
                pygame.draw.circle(screen, cursor_color, cursor_pos, HAND_CURSOR_SIZE)

            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))
            
            # --- Show webcam feed for debugging ---
            if landmarks:
                hand_tracking.draw_hand_landmarks(frame, landmarks)
            cv2.imshow('Webcam Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                 running = False
        else:
            # --- Game Over Screen ---
            screen.fill(WHITE)
            game_over_text = game_over_font.render("Game Over", True, BLACK)
            final_score_text = font.render(f"Final Score: {score}", True, BLACK)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            # Hide the webcam feed when the game is over
            cv2.destroyWindow('Webcam Feed')


        pygame.display.flip()
        clock.tick(60)

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
