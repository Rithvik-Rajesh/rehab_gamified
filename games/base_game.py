import pygame
import cv2

class BaseGame:
    def __init__(self, screen, hand_tracker):
        self.screen = screen
        self.hand_tracker = hand_tracker
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.game_over = False

    def display_camera_feed(self, frame):
        # Flip the frame horizontally for a selfie-view display.
        frame = cv2.flip(frame, 1)
        
        # Find hands and draw landmarks
        frame_with_hands = self.hand_tracker.find_hands(frame, draw=True)

        # Convert the BGR image to RGB.
        frame_rgb = cv2.cvtColor(frame_with_hands, cv2.COLOR_BGR2RGB)

        # Rotate and scale to fit the screen
        frame_pygame = pygame.surfarray.make_surface(frame_rgb.transpose([1, 0]))
        frame_pygame = pygame.transform.scale(frame_pygame, (self.screen_width, self.screen_height))
        
        self.screen.blit(frame_pygame, (0, 0))
        return frame

    def run(self):
        # This method should be implemented by child game classes
        raise NotImplementedError
