# rehab-gamification/games/maze_game/main.py

import pygame
import sys
import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime

# --- Game Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
MAZE_SCALE_FACTOR = 0.8 # How much of the screen the maze takes
CAMERA_FEED_SCALE = 0.25 # Scale of camera feed in corner (top right)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
WALL_COLOR = (50, 50, 50)
PATH_COLOR = (200, 200, 200)
START_COLOR = (0, 200, 0)
END_COLOR = (200, 0, 0)
PLAYER_COLOR = (255, 165, 0) # Orange
COLLISION_COLOR = (255, 0, 0) # Red for collision feedback

# Hand tracking settings
INDEX_FINGER_TIP_ID = 8 # MediaPipe landmark ID for index finger tip
PLAYER_RADIUS = 15 # Size of the player circle

# --- Maze Data (Moved from maze_data.py) ---
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
    "medium_maze_1": [
        "1111111111111",
        "1S00010000001",
        "1110110111011",
        "1000000100001",
        "1011111110101",
        "1010000000101",
        "1010111110101",
        "1000100010001",
        "1110101011101",
        "1000001000101",
        "1011111110101",
        "10000000000E1",
        "1111111111111",
    ],
    # Add more mazes here!
}

def parse_maze_layout(layout_str_list):
    """
    Parses a string list maze layout into a 2D list of (is_wall, is_start, is_end)
    and returns maze_data, start_pos, end_pos.
    """
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

# --- HandTracker Class (Moved from core/hand_tracking.py) ---
class HandTracker:
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
            max_num_hands=1 # We usually only need one hand for this type of game
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0) # Initialize webcam (0 is default)
        if not self.cap.isOpened():
            print("Error: Could not open video stream. Make sure webcam is connected and not in use.")
            self.cap = None 
        
        # Get actual camera resolution for scaling in Pygame
        self.cam_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) if self.cap else 640
        self.cam_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) if self.cap else 480

    def process_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None, None, None # Indicate camera not ready

        success, frame = self.cap.read()
        if not success:
            print("Warning: Could not read frame from camera.")
            return None, None, None

        # Flip the image horizontally for a selfie-view display.
        frame = cv2.flip(frame, 1)
        
        # Convert the BGR image to RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands.
        results = self.hands.process(rgb_frame)

        landmarks = None
        annotated_frame = frame.copy() # Frame to draw on

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks # Assuming only one hand, take the first one
                self.mp_drawing.draw_landmarks(
                    annotated_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
        return annotated_frame, landmarks, results.multi_hand_landmarks # Return all results for flexibility

    def get_landmark_pixel_coords(self, landmark_id, game_width, game_height, landmarks):
        """
        Converts a specific normalized landmark coordinate to pixel coordinates
        relative to the game screen dimensions.
        """
        if landmarks and landmark_id < len(landmarks.landmark):
            lm = landmarks.landmark[landmark_id]
            # Map normalized coordinates to game screen dimensions
            cx, cy = int(lm.x * game_width), int(lm.y * game_height)
            return cx, cy
        return None, None

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.hands.close()

# --- Game State Variables ---
game_active = False
game_won = False
wall_touches = 0
start_time = None
current_maze_name = "easy_maze_1" # Default maze
current_maze_data = None
start_cell_pos = None
end_cell_pos = None
maze_rects = [] # Store Pygame Rect objects for walls
player_pos_x, player_pos_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
last_valid_player_pos = (player_pos_x, player_pos_y) # To keep player in place if hand lost

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Rehab Gamification")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # Default font, size 36

# --- HandTracker Initialization ---
hand_tracker = HandTracker()
if not hand_tracker.cap: # Check if camera failed to open
    print("Exiting due to camera error.")
    pygame.quit()
    sys.exit()

# --- Functions ---

def load_maze(maze_name):
    """Loads a maze from MAZE_LAYOUTS and prepares it for drawing."""
    global current_maze_data, start_cell_pos, end_cell_pos, maze_rects, wall_touches, start_time, game_won, game_active

    layout_str = MAZE_LAYOUTS.get(maze_name)
    if not layout_str:
        raise ValueError(f"Maze '{maze_name}' not found.")
    
    current_maze_data, start_cell_pos, end_cell_pos = parse_maze_layout(layout_str)
    
    num_cols = len(current_maze_data[0])
    num_rows = len(current_maze_data)

    # Calculate maze drawing dimensions
    max_maze_width = SCREEN_WIDTH * MAZE_SCALE_FACTOR
    max_maze_height = SCREEN_HEIGHT * MAZE_SCALE_FACTOR
    
    cell_size_w = max_maze_width / num_cols
    cell_size_h = max_maze_height / num_rows
    
    cell_size = min(cell_size_w, cell_size_h) # Ensure cells are square
    
    maze_draw_width = num_cols * cell_size
    maze_draw_height = num_rows * cell_size

    # Calculate top-left corner of the maze to center it
    global maze_offset_x, maze_offset_y, cell_width, cell_height
    maze_offset_x = (SCREEN_WIDTH - maze_draw_width) // 2
    maze_offset_y = (SCREEN_HEIGHT - maze_draw_height) // 2
    cell_width = cell_size
    cell_height = cell_size

    maze_rects.clear() # Clear previous maze walls
    for r_idx, row in enumerate(current_maze_data):
        for c_idx, cell in enumerate(row):
            x = maze_offset_x + c_idx * cell_size
            y = maze_offset_y + r_idx * cell_size
            if cell['is_wall']:
                maze_rects.append(pygame.Rect(x, y, cell_size, cell_size))
    
    # Reset game state
    wall_touches = 0
    start_time = None
    game_won = False
    game_active = False # Will start once player enters start zone

    # Initial player position should be within the start cell
    global player_pos_x, player_pos_y
    player_pos_x = maze_offset_x + start_cell_pos[0] * cell_size + cell_size // 2
    player_pos_y = maze_offset_y + start_cell_pos[1] * cell_size + cell_size // 2


def draw_maze():
    """Draws the current maze on the screen."""
    if not current_maze_data:
        return

    num_cols = len(current_maze_data[0])
    num_rows = len(current_maze_data)
    
    # Use pre-calculated offsets and cell size from load_maze
    # These are global because they are needed for collision detection too
    global maze_offset_x, maze_offset_y, cell_width, cell_height 

    for r_idx, row in enumerate(current_maze_data):
        for c_idx, cell in enumerate(row):
            x = maze_offset_x + c_idx * cell_width
            y = maze_offset_y + r_idx * cell_height
            
            rect = pygame.Rect(x, y, cell_width, cell_height)

            if cell['is_wall']:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            else:
                pygame.draw.rect(screen, PATH_COLOR, rect) # Draw path background
            
            if cell['is_start']:
                pygame.draw.rect(screen, START_COLOR, rect)
            elif cell['is_end']:
                pygame.draw.rect(screen, END_COLOR, rect)

def display_info():
    """Displays game info like time and touches."""
    if start_time and game_active:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        time_text = font.render(f"Time: {elapsed_time:.1f}s", True, WHITE)
    elif game_won:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        time_text = font.render(f"FINISHED! Time: {elapsed_time:.1f}s", True, GREEN)
    else:
        time_text = font.render("Time: 0.0s", True, WHITE)

    touches_text = font.render(f"Touches: {wall_touches}", True, WHITE)
    instructions_text = font.render("Guide your index finger from START (green) to END (red).", True, WHITE)
    restart_text = font.render("Press 'R' to Restart, 'Q' to Quit.", True, WHITE)

    screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 20))
    screen.blit(touches_text, (SCREEN_WIDTH - touches_text.get_width() - 20, 60))
    screen.blit(instructions_text, (20, SCREEN_HEIGHT - instructions_text.get_height() - 20))
    screen.blit(restart_text, (20, SCREEN_HEIGHT - restart_text.get_height() - 60))


def draw_camera_feed(frame):
    """Draws the camera feed in a corner of the screen."""
    if frame is not None:
        # Convert OpenCV image to Pygame surface
        # OpenCV uses BGR, Pygame uses RGB, so convert and swap axes for correct orientation
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame) # Rotate to make it fit Pygame surface usually
        frame_surface = pygame.surfarray.make_surface(frame)

        # Scale down for corner display
        cam_display_width = int(SCREEN_WIDTH * CAMERA_FEED_SCALE)
        cam_display_height = int(SCREEN_HEIGHT * CAMERA_FEED_SCALE)
        frame_surface = pygame.transform.scale(frame_surface, (cam_display_width, cam_display_height))
        
        screen.blit(frame_surface, (SCREEN_WIDTH - cam_display_width, 0)) # Top-right corner


# --- Main Game Loop ---
load_maze(current_maze_name) # Load the initial maze

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Restart game
                load_maze(current_maze_name)
            if event.key == pygame.K_q: # Quit game (also ESC)
                running = False
            if event.key == pygame.K_ESCAPE: # Quit game
                running = False

    # Get hand tracking data
    annotated_frame, landmarks_obj, _ = hand_tracker.process_frame()

    # Update player position if hand is detected
    if landmarks_obj and not game_won:
        finger_x, finger_y = hand_tracker.get_landmark_pixel_coords(
            INDEX_FINGER_TIP_ID, SCREEN_WIDTH, SCREEN_HEIGHT, landmarks_obj
        )
        if finger_x is not None and finger_y is not None:
            player_pos_x, player_pos_y = finger_x, finger_y
            last_valid_player_pos = (player_pos_x, player_pos_y) # Store last good position
        else: # If a specific landmark is not found (e.g., partial hand view)
            player_pos_x, player_pos_y = last_valid_player_pos
    elif not game_won: # No hand detected, use last known position
        player_pos_x, player_pos_y = last_valid_player_pos

    # Create player collision circle
    player_rect = pygame.Rect(
        player_pos_x - PLAYER_RADIUS, player_pos_y - PLAYER_RADIUS,
        PLAYER_RADIUS * 2, PLAYER_RADIUS * 2
    )
    
    current_player_color = PLAYER_COLOR

    # --- Game Logic ---
    if not game_won:
        collided = False
        for wall_rect in maze_rects:
            if player_rect.colliderect(wall_rect):
                if game_active: # Only count touches if game has started
                    wall_touches += 1
                    current_player_color = COLLISION_COLOR # Flash red on collision
                collided = True
                # For this game, we allow player to move out of the wall,
                # just counting touches. For a "hard" mode, you might
                # push them back or end the game.
                break
        
        # Check if player is in the start zone to activate the game
        start_cell_rect = pygame.Rect(
            maze_offset_x + start_cell_pos[0] * cell_width,
            maze_offset_y + start_cell_pos[1] * cell_height,
            cell_width, cell_height
        )
        if start_cell_rect.colliderect(player_rect) and not game_active:
            game_active = True
            start_time = datetime.now()

        # Check for win condition (player in end zone)
        end_cell_rect = pygame.Rect(
            maze_offset_x + end_cell_pos[0] * cell_width,
            maze_offset_y + end_cell_pos[1] * cell_height,
            cell_width, cell_height
        )
        if end_cell_rect.colliderect(player_rect) and game_active:
            game_won = True
            # Optional: Send data to backend here (Phase 4)
            # Example: backend_api.save_score(user_id, current_maze_name, elapsed_time, wall_touches)


    # --- Drawing ---
    screen.fill(BLACK) # Clear screen

    draw_maze()
    
    # Draw player
    pygame.draw.circle(screen, current_player_color, (int(player_pos_x), int(player_pos_y)), PLAYER_RADIUS)

    display_info()
    draw_camera_feed(annotated_frame)

    pygame.display.flip()
    clock.tick(FPS)

# --- Cleanup ---
hand_tracker.release()
pygame.quit()
sys.exit()