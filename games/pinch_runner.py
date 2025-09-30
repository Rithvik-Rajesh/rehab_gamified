import pygame
from hand_tracking.hand_tracker import HandTracker
from games.base_game import BaseGame
import random

class PinchRunnerGame(BaseGame):
    def __init__(self, screen, hand_tracker):
        super().__init__(screen, hand_tracker)
        # Game specific initializations
        self.player_y = self.screen_height - 100
        self.player_vel = 0
        self.is_jumping = False
        self.gravity = 1
        self.jump_height = -20
        self.obstacles = []
        self.score = 0
        self.pinch_count = 0
        self.min_pinch_dist = float('inf')
        self.max_pinch_dist = 0
        self.font = pygame.font.Font(None, 50)
        self.game_over = False

    def run(self):
        cap = self.hand_tracker.cap
        obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(obstacle_timer, 1500)

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
                if event.type == obstacle_timer:
                    self.obstacles.append(self.create_obstacle())

            landmarks = self.hand_tracker.get_landmark_positions(processed_frame)
            if landmarks:
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                dist = self.hand_tracker.calculate_distance(thumb_tip[1:], index_tip[1:])
                
                self.min_pinch_dist = min(self.min_pinch_dist, dist)
                selfmax_pinch_dist = max(self.max_pinch_dist, dist)

                if dist < 30 and not self.is_jumping:
                    self.is_jumping = True
                    self.player_vel = self.jump_height
                    self.pinch_count += 1

            # Game logic update
            self.update_player()
            self.update_obstacles()
            self.check_collisions()

            # Drawing
            self.draw_elements()

            pygame.display.flip()
            self.clock.tick(30)

        session_data = {
            "score": self.score,
            "pinch_count": self.pinch_count,
            "min_pinch_dist": self.min_pinch_dist if self.min_pinch_dist != float('inf') else 0,
            "max_pinch_dist": self.max_pinch_dist
        }
        return session_data

    def create_obstacle(self):
        height = random.randint(50, 150)
        return pygame.Rect(self.screen_width, self.screen_height - height, 50, height)

    def update_player(self):
        if self.is_jumping:
            self.player_vel += self.gravity
            self.player_y += self.player_vel
            if self.player_y >= self.screen_height - 100:
                self.player_y = self.screen_height - 100
                self.is_jumping = False
                self.player_vel = 0

    def update_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.x -= 10
            if obstacle.right < 0:
                self.obstacles.remove(obstacle)
                self.score += 1

    def check_collisions(self):
        player_rect = pygame.Rect(100, self.player_y, 50, 50)
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle):
                self.game_over = True

    def draw_elements(self):
        # Player
        pygame.draw.rect(self.screen, (0, 255, 0), (100, self.player_y, 50, 50))
        # Obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, (255, 0, 0), obstacle)
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
