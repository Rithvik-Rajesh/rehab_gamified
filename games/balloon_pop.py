import pygame
import random
from games.base_game import BaseGame

class Balloon:
    def __init__(self, x, y, radius=30):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (255, 0, 0) # Red
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        # If you have a balloon image in assets:
        # self.image = pygame.image.load('assets/balloon.png').convert_alpha()
        # self.image = pygame.transform.scale(self.image, (radius*2, radius*2))
        # self.rect = self.image.get_rect(center=(x,y))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # If using an image:
        # screen.blit(self.image, self.rect)

    def is_popped_by(self, pos):
        return self.rect.collidepoint(pos)

class BalloonPopGame(BaseGame):
    def __init__(self, screen, hand_tracker):
        super().__init__(screen, hand_tracker)
        self.balloons = []
        self.score = 0
        self.pinch_count = 0
        self.last_pop_time = 0
        self.font = pygame.font.Font(None, 50)
        self.spawn_balloon()

    def spawn_balloon(self):
        if len(self.balloons) < 5: # Max 5 balloons on screen
            x = random.randint(50, self.screen_width - 50)
            y = random.randint(50, self.screen_height - 50)
            self.balloons.append(Balloon(x, y))

    def run(self):
        cap = self.hand_tracker.cap
        while not self.game_over:
            success, frame = cap.read()
            if not success:
                continue

            # Display camera feed as background
            processed_frame = self.display_camera_feed(frame)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_over = True

            # Game logic
            landmarks = self.hand_tracker.get_landmark_positions(processed_frame)
            if landmarks:
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                
                # Flip coordinates to match flipped view
                thumb_x, thumb_y = self.screen_width - thumb_tip[1], thumb_tip[2]
                index_x, index_y = self.screen_width - index_tip[1], index_tip[2]

                pinch_dist = self.hand_tracker.calculate_distance((thumb_x, thumb_y), (index_x, index_y))

                if pinch_dist < 30: # Pinch detected
                    self.pinch_count += 1
                    pinch_pos = ((thumb_x + index_x) // 2, (thumb_y + index_y) // 2)
                    
                    # Check for balloon pop
                    for balloon in self.balloons[:]:
                        if balloon.is_popped_by(pinch_pos):
                            self.balloons.remove(balloon)
                            self.score += 10
                            self.spawn_balloon()
                            break

            # Spawn new balloons periodically
            if pygame.time.get_ticks() - self.last_pop_time > 2000: # every 2 seconds
                self.spawn_balloon()
                self.last_pop_time = pygame.time.get_ticks()

            # Draw balloons
            for balloon in self.balloons:
                balloon.draw(self.screen)

            # Display score
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            self.clock.tick(30)

        session_data = {
            "score": self.score,
            "pinch_count": self.pinch_count
        }
        return session_data
