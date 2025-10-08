import pygame
from rehab_gamification.games.base_game import BaseGame
import cv2
import numpy as np
from datetime import datetime

# --- Game Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
MAZE_SCALE_FACTOR = 0.8
CAMERA_FEED_SCALE = 0.25

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WALL_COLOR = (50, 50, 50)
PATH_COLOR = (200, 200, 200)
START_COLOR = (0, 200, 0)
END_COLOR = (200, 0, 0)
PLAYER_COLOR = (255, 165, 0)
COLLISION_COLOR = (255, 0, 0)

# Hand tracking settings
INDEX_FINGER_TIP_ID = 8
PLAYER_RADIUS = 15

MAZE_LAYOUTS = {
    "easy_maze_1": [
        "1111111111",
        "1S00000001",
        "1111011101",
        "1001010001",
        "1011010111",
        "1010000001",
        "1010111011",
        "1000010001",
        "11110111E1",
        "1111111111",
    ],
}

class MazeGame(BaseGame):
    """
    A game where the player navigates a maze with their hand.
    """
    def __init__(self, screen, hand_tracker, cap, calibration_data=None):
        """
        Initializes the MazeGame.
        :param screen: The pygame screen to draw on.
        :param hand_tracker: The shared HandTracker instance.
        :param cap: The shared camera capture instance.
        :param calibration_data: Calibration parameters.
        """
        super().__init__(screen, hand_tracker, cap, calibration_data)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.game_active = False
        self.game_won = False
        self.wall_touches = 0
        self.start_time = None
        self.current_maze_name = "easy_maze_1"
        self.maze_rects = []
        self.player_pos_x, self.player_pos_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.last_valid_player_pos = (self.player_pos_x, self.player_pos_y)

        self.load_maze(self.current_maze_name)

    def parse_maze_layout(self, layout_str_list):
        maze = []
        start_pos = None
        end_pos = None
        for r_idx, row_str in enumerate(layout_str_list):
            row_data = []
            for c_idx, char in enumerate(row_str):
                is_wall = char == '1'
                is_start = char == 'S'
                is_end = char == 'E'
                if is_start:
                    start_pos = (c_idx, r_idx)
                if is_end:
                    end_pos = (c_idx, r_idx)
                row_data.append({'is_wall': is_wall, 'is_start': is_start, 'is_end': is_end})
            maze.append(row_data)
        
        if not start_pos or not end_pos:
            raise ValueError("Maze must have a start 'S' and an end 'E'.")
            
        return maze, start_pos, end_pos

    def load_maze(self, maze_name):
        layout_str = MAZE_LAYOUTS.get(maze_name)
        if not layout_str:
            raise ValueError(f"Maze '{maze_name}' not found.")
        
        self.current_maze_data, self.start_cell_pos, self.end_cell_pos = self.parse_maze_layout(layout_str)
        
        num_cols = len(self.current_maze_data[0])
        num_rows = len(self.current_maze_data)

        max_maze_width = SCREEN_WIDTH * MAZE_SCALE_FACTOR
        max_maze_height = SCREEN_HEIGHT * MAZE_SCALE_FACTOR
        
        cell_size_w = max_maze_width / num_cols
        cell_size_h = max_maze_height / num_rows
        
        cell_size = min(cell_size_w, cell_size_h)
        
        maze_draw_width = num_cols * cell_size
        maze_draw_height = num_rows * cell_size

        self.maze_offset_x = (SCREEN_WIDTH - maze_draw_width) // 2
        self.maze_offset_y = (SCREEN_HEIGHT - maze_draw_height) // 2
        self.cell_width = cell_size
        self.cell_height = cell_size

        self.maze_rects.clear()
        for r_idx, row in enumerate(self.current_maze_data):
            for c_idx, cell in enumerate(row):
                x = self.maze_offset_x + c_idx * cell_size
                y = self.maze_offset_y + r_idx * cell_size
                if cell['is_wall']:
                    self.maze_rects.append(pygame.Rect(x, y, cell_size, cell_size))
        
        self.wall_touches = 0
        self.start_time = None
        self.game_won = False
        self.game_active = False

        self.player_pos_x = self.maze_offset_x + self.start_cell_pos[0] * cell_size + cell_size // 2
        self.player_pos_y = self.maze_offset_y + self.start_cell_pos[1] * cell_size + cell_size // 2

    def draw_maze(self):
        if not self.current_maze_data:
            return

        for r_idx, row in enumerate(self.current_maze_data):
            for c_idx, cell in enumerate(row):
                x = self.maze_offset_x + c_idx * self.cell_width
                y = self.maze_offset_y + r_idx * self.cell_height
                
                rect = pygame.Rect(x, y, self.cell_width, self.cell_height)

                if cell['is_wall']:
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                else:
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)
                
                if cell['is_start']:
                    pygame.draw.rect(self.screen, START_COLOR, rect)
                elif cell['is_end']:
                    pygame.draw.rect(self.screen, END_COLOR, rect)

    def display_info(self):
        if self.start_time and self.game_active:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            time_text = self.font.render(f"Time: {elapsed_time:.1f}s", True, WHITE)
        elif self.game_won:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            time_text = self.font.render(f"FINISHED! Time: {elapsed_time:.1f}s", True, START_COLOR)
        else:
            time_text = self.font.render("Time: 0.0s", True, WHITE)

        touches_text = self.font.render(f"Touches: {self.wall_touches}", True, WHITE)
        self.screen.blit(time_text, (20, 20))
        self.screen.blit(touches_text, (20, 60))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            success, frame = self.cap.read()
            if not success:
                continue
            
            frame = cv2.flip(frame, 1)
            frame = self.hand_tracker.find_hands(frame, draw=False)
            lm_list = self.hand_tracker.get_landmark_positions(frame, draw=False)

            if lm_list and not self.game_won:
                finger_x, finger_y = lm_list[INDEX_FINGER_TIP_ID][1], lm_list[INDEX_FINGER_TIP_ID][2]
                self.player_pos_x, self.player_pos_y = finger_x, finger_y
                self.last_valid_player_pos = (self.player_pos_x, self.player_pos_y)
            elif not self.game_won:
                self.player_pos_x, self.player_pos_y = self.last_valid_player_pos

            player_rect = pygame.Rect(
                self.player_pos_x - PLAYER_RADIUS, self.player_pos_y - PLAYER_RADIUS,
                PLAYER_RADIUS * 2, PLAYER_RADIUS * 2
            )
            
            current_player_color = PLAYER_COLOR

            if not self.game_won:
                successful_movement = True
                for wall_rect in self.maze_rects:
                    if player_rect.colliderect(wall_rect):
                        if self.game_active:
                            self.wall_touches += 1
                            current_player_color = COLLISION_COLOR
                            successful_movement = False
                        break
                
                # Track hand movement effectiveness in maze navigation
                if lm_list and self.game_active:
                    # For maze game, successful interaction is moving without hitting walls
                    if successful_movement:
                        self.hand_movement_data["successful_interactions"] += 1
                
                start_cell_rect = pygame.Rect(
                    self.maze_offset_x + self.start_cell_pos[0] * self.cell_width,
                    self.maze_offset_y + self.start_cell_pos[1] * self.cell_height,
                    self.cell_width, self.cell_height
                )
                if start_cell_rect.colliderect(player_rect) and not self.game_active:
                    self.game_active = True
                    self.start_time = datetime.now()

                end_cell_rect = pygame.Rect(
                    self.maze_offset_x + self.end_cell_pos[0] * self.cell_width,
                    self.maze_offset_y + self.end_cell_pos[1] * self.cell_height,
                    self.cell_width, self.cell_height
                )
                if end_cell_rect.colliderect(player_rect) and self.game_active:
                    self.game_won = True
                    self.end_time = datetime.now()

            self.screen.fill(BLACK)
            self.draw_maze()
            pygame.draw.circle(self.screen, current_player_color, (int(self.player_pos_x), int(self.player_pos_y)), PLAYER_RADIUS)
            self.display_info()

            if self.game_won:
                # Show "You Win" message and wait for a click
                win_font = pygame.font.Font(None, 100)
                win_text = win_font.render("You Win!", True, START_COLOR)
                self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - win_text.get_height() // 2))
                pygame.display.flip()
                
                waiting_for_click = True
                while waiting_for_click:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                            waiting_for_click = False
                            running = False # End the game loop
                
            pygame.display.flip()
            self.clock.tick(FPS)

        self.cap.release()
        return self.get_session_data()

    def get_session_data(self):
        # Get enhanced session data from base class
        enhanced_data = self.get_enhanced_session_data()
        
        elapsed_time = (self.end_time - self.start_time).total_seconds() if self.game_won and self.start_time else 0
        
        # Add maze-specific game metrics
        maze_specific_data = {
            "time_taken": round(elapsed_time, 2),
            "wall_touches": self.wall_touches,
            "completed": self.game_won,
            "navigation_accuracy": round((1 - (self.wall_touches / max(1, self.hand_movement_data["total_movements"]))) * 100, 2)
        }
        
        # Merge enhanced data with game-specific data
        enhanced_data["game_specific_metrics"] = maze_specific_data
        enhanced_data["game_name"] = "MazeGame"
        
        return enhanced_data
