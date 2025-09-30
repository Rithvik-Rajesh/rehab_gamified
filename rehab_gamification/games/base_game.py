# base_game.py

import pygame
import cv2
# This import path might be different for you, adjust if necessary
from rehab_gamification.hand_tracking.hand_tracker import HandTracker

class BaseGame:
    """
    A base class for games to handle camera feed and hand tracking.
    """
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.hand_tracker = HandTracker()
        self.cap = cv2.VideoCapture(0)
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

    def run(self):
        # This method should be implemented by child game classes
        raise NotImplementedError

    def __del__(self):
        """Release the camera when the game object is destroyed."""
        if self.cap.isOpened():
            self.cap.release()