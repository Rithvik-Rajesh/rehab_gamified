# base_game.py

import pygame
import cv2
# This import path might be different for you, adjust if necessary
from rehab_gamification.hand_tracking.hand_tracker import HandTracker

class BaseGame:
    """
    A base class for games to handle camera feed and hand tracking.
    """
    def __init__(self, screen, hand_tracker, cap, calibration_data=None):
        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.hand_tracker = hand_tracker
        self.cap = cap
        self.calibration_data = calibration_data or {"pinch_threshold": 40, "sensitivity": 1.0}
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

    def display_camera_feed(self, frame, draw=True): # <<< CHANGED: Added draw parameter
        """

        Processes and displays the camera feed on the screen.
        :param frame: The camera frame to process.
        :param draw: Whether to draw the full hand skeleton.
        :return: The processed frame (without the skeleton drawn on it).
        """
        # Flip the frame horizontally for a selfie-view display.
        frame = cv2.flip(frame, 1)
        
        # Find hands and draw landmarks (now respects the 'draw' parameter)
        frame_with_hands = self.hand_tracker.find_hands(frame, draw=draw) # <<< CHANGED

        # Convert the BGR image to RGB.
        frame_rgb = cv2.cvtColor(frame_with_hands, cv2.COLOR_BGR2RGB)

        # The transpose is necessary to swap the axes for pygame
        frame_pygame = pygame.surfarray.make_surface(frame_rgb.transpose((1, 0, 2)))
        
        # Scale the camera feed to fit the screen
        frame_scaled = pygame.transform.scale(frame_pygame, (self.screen_width, self.screen_height))

        self.screen.blit(frame_scaled, (0, 0))
        
        # Return the original processed frame (not the pygame surface)
        # for landmark position calculation.
        return frame_with_hands

    def show_game_over_screen(self):
        """Displays a 'Game Over' screen and waits for input to exit."""
        darken_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        darken_surface.fill((0, 0, 0, 150))
        self.screen.blit(darken_surface, (0, 0))

        font = pygame.font.Font(None, 74)
        small_font = pygame.font.Font(None, 40)
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        exit_text = small_font.render("Pinch to Exit", True, (255, 255, 255))

        game_over_rect = game_over_text.get_rect(center=(self.screen_width / 2, self.screen_height / 2 - 50))
        exit_rect = exit_text.get_rect(center=(self.screen_width / 2, self.screen_height / 2 + 50))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(exit_text, exit_rect)
        pygame.display.flip()

        waiting = True
        was_pinching = True 
        while waiting:
            success, frame = self.cap.read()
            if success:
                frame = cv2.flip(frame, 1)
                lm_list = self.hand_tracker.get_landmark_positions(self.hand_tracker.find_hands(frame, draw=False), draw=False)
                is_pinching, _ = self.hand_tracker.get_pinch_gesture(lm_list)
                if is_pinching and not was_pinching:
                    waiting = False
                was_pinching = is_pinching

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.game_over = True # Ensure main loop also exits
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            
            self.clock.tick(20)

    def run(self):
        # This method should be implemented by child game classes
        raise NotImplementedError

    def __del__(self):
        """Release the camera when the game object is destroyed."""
        # Camera is now managed by MainApp, so we don't release it here.
        pass