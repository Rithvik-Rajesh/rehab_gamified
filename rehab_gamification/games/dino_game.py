import pygame
import os
import random
import sys
import cv2
from rehab_gamification.games.base_game import BaseGame

# --- Constants ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
RUNNING = [pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Dino", "DinoJump.png"))

SMALL_CACTUS = [pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("rehab_gamification/assets/dino_game/Other", "Track.png"))


# --- Dinosaur Class ---
class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5

    def __init__(self):
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.dino_run = True
        self.dino_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, is_pinching):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if is_pinching and not self.dino_jump:
            self.dino_run = False
            self.dino_jump = True
        elif not self.dino_jump:
            self.dino_run = True
            self.dino_jump = False

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, screen):
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


# --- Cloud Class ---
class Cloud:
    def __init__(self, screen_width, game_speed):
        self.x = screen_width + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()
        self.game_speed = game_speed

    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = 1100 + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


# --- Obstacle Class ---
class Obstacle:
    def __init__(self, image, type, screen_width):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = screen_width

    def update(self, game_speed):
        self.rect.x -= game_speed

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, screen_width):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, screen_width)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image, screen_width):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, screen_width)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image, screen_width):
        self.type = 0
        super().__init__(image, self.type, screen_width)
        self.rect.y = 250
        self.index = 0

    def draw(self, screen):
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[self.index // 5], self.rect)
        self.index += 1


# --- DinoGame Class ---
class DinoGame(BaseGame):
    def __init__(self, screen, hand_tracker, cap, calibration_data=None):
        super().__init__(screen, hand_tracker, cap, calibration_data)
        self.player = Dinosaur()
        self.cloud = Cloud(self.screen_width, 16)
        self.game_speed = 16
        self.x_pos_bg = 0
        self.y_pos_bg = 380
        self.points = 0
        self.obstacles = []
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.game_over_font = pygame.font.Font('freesansbold.ttf', 75)
        
        # Tracking metrics
        self.total_jumps = 0
        self.successful_jumps = 0
        self.max_speed = 0
        self.pinch_count = 0
        self.last_pinch_state = False

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

            # --- Hand Tracking ---
            lm_list = self.hand_tracker.get_landmark_positions(processed_frame, draw=False)
            is_pinching, pinch_pos = self.hand_tracker.get_pinch_gesture(
                lm_list,
                pinch_threshold=self.calibration_data.get("pinch_threshold", 40)
            )

            # Count pinches
            if is_pinching and not self.last_pinch_state:
                self.pinch_count += 1
                self.total_jumps += 1
            self.last_pinch_state = is_pinching

            # --- Game Logic ---
            self.player.update(is_pinching)

            if len(self.obstacles) == 0:
                rand = random.randint(0, 2)
                if rand == 0:
                    self.obstacles.append(SmallCactus(SMALL_CACTUS, self.screen_width))
                elif rand == 1:
                    self.obstacles.append(LargeCactus(LARGE_CACTUS, self.screen_width))
                elif rand == 2:
                    self.obstacles.append(Bird(BIRD, self.screen_width))

            for obstacle in self.obstacles[:]:
                obstacle.update(self.game_speed)
                if obstacle.rect.x < -obstacle.rect.width:
                    self.obstacles.remove(obstacle)
                    self.successful_jumps += 1

                if self.player.dino_rect.colliderect(obstacle.rect):
                    self.game_over = True

            # Update score
            self.points += 1
            if self.points % 100 == 0:
                self.game_speed += 1
            self.max_speed = max(self.max_speed, self.game_speed)

            # --- Drawing ---
            self.draw_background()
            self.cloud.update(self.game_speed)
            self.cloud.draw(self.screen)
            
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            
            self.player.draw(self.screen)
            self.draw_score()

            pygame.display.flip()
            self.clock.tick(30)

        self.show_game_over_screen()
        return self.get_session_data()

    def draw_background(self):
        image_width = BG.get_width()
        self.screen.blit(BG, (self.x_pos_bg, self.y_pos_bg))
        self.screen.blit(BG, (image_width + self.x_pos_bg, self.y_pos_bg))
        if self.x_pos_bg <= -image_width:
            self.screen.blit(BG, (image_width + self.x_pos_bg, self.y_pos_bg))
            self.x_pos_bg = 0
        self.x_pos_bg -= self.game_speed

    def draw_score(self):
        text = self.font.render("Points: " + str(self.points), True, BLACK)
        textRect = text.get_rect()
        textRect.center = (self.screen_width - 100, 40)
        self.screen.blit(text, textRect)

    def show_game_over_screen(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.game_over_font.render("Game Over", True, WHITE)
        final_score_text = self.font.render(f"Final Score: {self.points}", True, WHITE)

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
        success_rate = (self.successful_jumps / self.total_jumps * 100) if self.total_jumps > 0 else 0
        return {
            "score": self.points,
            "max_speed": self.max_speed,
            "total_jumps": self.total_jumps,
            "successful_jumps": self.successful_jumps,
            "success_rate": round(success_rate, 2),
            "pinch_count": self.pinch_count
        }