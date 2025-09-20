import pygame
import random
import cv2
from rehab_gamification.hand_tracking.hand_tracker import HandTracker

class PinchRunnerGame:
    """
    A game where the player pinches their fingers to make a character jump over obstacles.
    """
    def __init__(self, screen):
        """
        Initializes the PinchRunnerGame.
        :param screen: The pygame screen to draw on.
        """
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)

        # Player properties
        self.player_size = 50
        self.player_x = 100
        self.player_y = self.screen_height - self.player_size
        self.player_y_velocity = 0
        self.jump_strength = -15
        self.gravity = 0.8
        self.is_jumping = False

        # Obstacle properties
        self.obstacle_width = 30
        self.obstacle_height = 70
        self.obstacle_speed = 5
        self.obstacles = []

        # Hand tracking
        self.cap = cv2.VideoCapture(0)
        self.hand_tracker = HandTracker()
        self.pinch_threshold = 30
        self.pinch_status = "No Pinch"

        # Game state
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False

        # Data recording
        self.pinch_count = 0
        self.pinch_distances = []

    def _create_obstacle(self):
        """Creates a new obstacle at the right edge of the screen."""
        obstacle_y = self.screen_height - self.obstacle_height
        self.obstacles.append(pygame.Rect(self.screen_width, obstacle_y, self.obstacle_width, self.obstacle_height))

    def run(self):
        """The main game loop."""
        clock = pygame.time.Clock()

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
            
            frame = self.hand_tracker.find_hands(frame)
            lm_list = self.hand_tracker.get_landmark_positions(frame, draw=False)

            if lm_list:
                thumb_tip = lm_list[4]
                index_tip = lm_list[8]
                distance = self.hand_tracker.calculate_distance(thumb_tip, index_tip)
                self.pinch_distances.append(distance)

                if distance < self.pinch_threshold:
                    self.pinch_status = "PINCH!"
                    if not self.is_jumping:
                        self.is_jumping = True
                        self.player_y_velocity = self.jump_strength
                        self.pinch_count += 1
                else:
                    self.pinch_status = "Release"
            
            # Game logic
            if self.is_jumping:
                self.player_y_velocity += self.gravity
                self.player_y += self.player_y_velocity
                if self.player_y >= self.screen_height - self.player_size:
                    self.player_y = self.screen_height - self.player_size
                    self.is_jumping = False

            # Obstacles
            if not self.obstacles or self.obstacles[-1].x < self.screen_width - 300:
                self._create_obstacle()

            for obstacle in self.obstacles:
                obstacle.x -= self.obstacle_speed
                if obstacle.right < 0:
                    self.obstacles.remove(obstacle)
                    self.score += 1

            # Collision detection
            player_rect = pygame.Rect(self.player_x, self.player_y, self.player_size, self.player_size)
            for obstacle in self.obstacles:
                if player_rect.colliderect(obstacle):
                    self.game_over = True

            # Drawing
            self.screen.fill(self.white)
            pygame.draw.rect(self.screen, self.green, player_rect)
            for obstacle in self.obstacles:
                pygame.draw.rect(self.screen, self.red, obstacle)

            # UI
            score_text = self.font.render(f"Score: {self.score}", True, self.black)
            pinch_text = self.font.render(self.pinch_status, True, self.black)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(pinch_text, (10, 50))

            pygame.display.flip()
            clock.tick(60)

        self.cap.release()
        return self.get_session_data()

    def get_session_data(self):
        """Returns the recorded data for the session."""
        if not self.pinch_distances:
            min_dist, max_dist = 0, 0
        else:
            min_dist = min(self.pinch_distances)
            max_dist = max(self.pinch_distances)
            
        return {
            "score": self.score,
            "successful_pinches": self.pinch_count,
            "min_pinch_distance": min_dist,
            "max_pinch_distance": max_dist
        }

