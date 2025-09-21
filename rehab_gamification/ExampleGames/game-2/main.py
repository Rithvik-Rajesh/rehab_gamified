import pygame
import sys
from core.hand_tracking import HandTracker # Import your hand tracking module
# from core.gestures import detect_pinch # If gestures are in a separate module

# Pygame setup
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Balloon Pop Rehab")
clock = pygame.time.Clock()

# Hand tracking setup
hand_tracker = HandTracker()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get hand tracking data
    annotated_frame, landmarks, _ = hand_tracker.process_frame()

    current_finger_pos = None
    if landmarks:
        # Get specific landmark positions (e.g., tip of index finger)
        # Assuming you've implemented get_landmark_coordinates in HandTracker
        pixel_coords = hand_tracker.get_landmark_coordinates(landmarks, SCREEN_WIDTH, SCREEN_HEIGHT)
        if pixel_coords:
            # Example: Use the tip of the index finger (landmark ID 8)
            current_finger_pos = pixel_coords.get(8)

        # Example: Detect a pinch gesture
        # if detect_pinch(landmarks): # if you have a gestures module
        #    print("Pinch detected!")
        #    # Perform game action: pop balloon, etc.

    # --- Pygame Game Logic ---
    screen.fill((0, 0, 0)) # Clear screen

    # Display annotated camera feed (optional, for debugging/feedback)
    if annotated_frame is not None:
        # Convert OpenCV image to Pygame surface
        frame_surface = pygame.surfarray.make_surface(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB).swapaxes(0,1))
        screen.blit(pygame.transform.scale(frame_surface, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3)), (0,0)) # Scale down for corner

    # Draw game elements based on hand position
    if current_finger_pos:
        pygame.draw.circle(screen, (255, 0, 0), current_finger_pos, 20) # Red circle at finger tip

    # Add balloon drawing, movement, collision detection here...

    pygame.display.flip()
    clock.tick(60)

# Cleanup
hand_tracker.release()
pygame.quit()
sys.exit()