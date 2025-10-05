import pygame
import sys
from datetime import datetime
from rehab_gamification.games.balloon_pop import BalloonPopGame
from rehab_gamification.games.game_2 import FingerPainterGame
from rehab_gamification.games.maze_game import MazeGame
from rehab_gamification.data_manager import DataManager
import cv2
from rehab_gamification.hand_tracking.hand_tracker import HandTracker

class MainApp:
    """
    The main application class that runs the game menu, games, and dashboard.
    """
    def __init__(self, width=1280, height=720):
        """
        Initializes the main application.
        :param width: The width of the screen.
        :param height: The height of the screen.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Rehab Gamification")

        # Colors and Fonts
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.gray = (200, 200, 200)
        self.red = (255, 0, 0)
        self.blue = (0, 0, 255)
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)

        # Data Manager
        self.data_manager = DataManager(data_folder='rehab_gamification/data')

        # Centralized Hand Tracking and Camera
        self.hand_tracker = HandTracker()
        self.cap = cv2.VideoCapture(0)

        # Menu options
        self.menu_options = ["Balloon Pop", "Finger Painter", "Maze Game", "Dashboard", "Quit"]
        self.buttons = []

    def _draw_text(self, text, font, color, surface, x, y):
        """Helper function to draw text on a surface."""
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect(center=(x, y))
        surface.blit(textobj, textrect)

    def _main_menu(self):
        """Displays the main menu and handles user input with hand tracking."""
        was_pinching = False
        cam_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        cam_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        while True:
            # --- Camera and Hand Tracking ---
            success, frame = self.cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            frame_with_hands = self.hand_tracker.find_hands(frame, draw=True)
            frame_rgb = cv2.cvtColor(frame_with_hands, cv2.COLOR_BGR2RGB)
            frame_pygame = pygame.surfarray.make_surface(frame_rgb.transpose((1, 0, 2)))
            self.screen.blit(frame_pygame, (0, 0))

            lm_list = self.hand_tracker.get_landmark_positions(frame_with_hands, draw=False)
            is_pinching, _ = self.hand_tracker.get_pinch_gesture(lm_list)
            hand_pos = self.hand_tracker.get_hand_position(lm_list)

            cursor_pos = (0, 0)
            if cam_w > 0 and cam_h > 0:
                cursor_x = int(hand_pos[0] * self.screen.get_width() / cam_w)
                cursor_y = int(hand_pos[1] * self.screen.get_height() / cam_h)
                cursor_pos = (self.screen.get_width() - cursor_x, cursor_y)

            # --- Menu Drawing ---
            self.buttons.clear()
            self._draw_text('Main Menu', self.font, self.white, self.screen, self.screen.get_width() / 2, 100)

            y_pos = 200
            for option in self.menu_options:
                button_rect = pygame.Rect(self.screen.get_width() / 2 - 150, y_pos, 300, 50)
                self.buttons.append(button_rect)
                
                color = self.blue if button_rect.collidepoint(cursor_pos) else self.gray
                pygame.draw.rect(self.screen, color, button_rect)
                self._draw_text(option, self.small_font, self.black, self.screen, self.screen.get_width() / 2, y_pos + 25)
                y_pos += 70

            # --- Input Handling ---
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cap.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
                    cursor_pos = event.pos

            if is_pinching and not was_pinching:
                click = True
            was_pinching = is_pinching

            if click:
                for i, button in enumerate(self.buttons):
                    if button.collidepoint(cursor_pos):
                        return self.menu_options[i]

            # --- Draw Cursor ---
            cursor_color = self.red if is_pinching else self.blue
            pygame.draw.circle(self.screen, cursor_color, cursor_pos, 15)
            pygame.draw.circle(self.screen, self.white, cursor_pos, 15, 2)

            pygame.display.flip()

    def _run_game(self, game_class, game_name):
        """Runs a game, and saves the session data."""
        game = game_class(self.screen, self.hand_tracker, self.cap)
        session_data = game.run()
        self.data_manager.save_session(game_name, session_data)

    def _show_dashboard(self):
        """Displays the dashboard with data from past sessions."""
        sessions = self.data_manager.load_all_sessions()
        self.screen.fill(self.white)
        self._draw_text('Dashboard', self.font, self.black, self.screen, self.screen.get_width() / 2, 50)

        if not sessions:
            self._draw_text("No data available yet.", self.small_font, self.black, self.screen, self.screen.get_width() / 2, 300)
        else:
            y_pos = 120
            for session in sessions[:15]: # Show last 15 sessions
                game_name = session.get('metadata', {}).get('game_name', 'N/A')
                timestamp_str = session.get('metadata', {}).get('session_start_time', 'N/A')
                
                try:
                    timestamp = datetime.fromisoformat(timestamp_str).strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    timestamp = "Invalid Date"

                metrics = session.get('metrics', {})
                score = metrics.get('score', 'N/A')
                
                display_text = f"{timestamp} - {game_name} - Score: {score}"
                self._draw_text(display_text, self.small_font, self.black, self.screen, self.screen.get_width() / 2, y_pos)
                y_pos += 30

        self._draw_text("Click anywhere to return to menu", self.small_font, self.gray, self.screen, self.screen.get_width() / 2, self.screen.get_height() - 50)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    waiting = False

    def run(self):
        """The main application loop."""
        while True:
            choice = self._main_menu()

            if choice == "Balloon Pop":
                self._run_game(BalloonPopGame, "BalloonPop")
            elif choice == "Finger Painter":
                self._run_game(FingerPainterGame, "FingerPainter")
            elif choice == "Maze Game":
                self._run_game(MazeGame, "MazeGame")
            elif choice == "Dashboard":
                self._show_dashboard()
            elif choice == "Quit":
                self.cap.release()
                pygame.quit()
                sys.exit()

if __name__ == '__main__':
    app = MainApp()
    app.run()


