import pygame
import sys
from rehab_gamification.games.pinch_runner import PinchRunnerGame
from rehab_gamification.games.angle_master import AngleMasterGame
from rehab_gamification.data_manager import DataManager

class MainApp:
    """
    The main application class that runs the game menu, games, and dashboard.
    """
    def __init__(self, width=800, height=600):
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
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)

        # Data Manager
        self.data_manager = DataManager(data_folder='rehab_gamification/data')

        # Menu options
        self.menu_options = ["Pinch Runner", "Angle Master", "Dashboard", "Quit"]
        self.buttons = []

    def _draw_text(self, text, font, color, surface, x, y):
        """Helper function to draw text on a surface."""
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect(center=(x, y))
        surface.blit(textobj, textrect)

    def _main_menu(self):
        """Displays the main menu and handles user input."""
        self.buttons.clear()
        self.screen.fill(self.white)
        self._draw_text('Main Menu', self.font, self.black, self.screen, 400, 100)

        y_pos = 200
        for option in self.menu_options:
            button_rect = pygame.Rect(250, y_pos, 300, 50)
            self.buttons.append(button_rect)
            pygame.draw.rect(self.screen, self.gray, button_rect)
            self._draw_text(option, self.small_font, self.black, self.screen, 400, y_pos + 25)
            y_pos += 70

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, button in enumerate(self.buttons):
                        if button.collidepoint(event.pos):
                            return self.menu_options[i]

    def _run_game(self, game_class, game_name):
        """Runs a game, and saves the session data."""
        game = game_class(self.screen)
        session_data = game.run()
        self.data_manager.save_session(game_name, session_data)

    def _show_dashboard(self):
        """Displays the dashboard with data from past sessions."""
        sessions = self.data_manager.load_all_sessions()
        self.screen.fill(self.white)
        self._draw_text('Dashboard', self.font, self.black, self.screen, 400, 50)

        if not sessions:
            self._draw_text("No data available yet.", self.small_font, self.black, self.screen, 400, 300)
        else:
            y_pos = 120
            for session in sorted(sessions, key=lambda x: x['timestamp'], reverse=True)[:10]: # Show last 10
                game_name = session.get('game_name', 'N/A')
                timestamp = session.get('timestamp', 'N/A').replace('_', ' ').split('.')[0]
                score = session.get('session_data', {}).get('score', 'N/A')
                
                display_text = f"{timestamp} - {game_name} - Score: {score}"
                self._draw_text(display_text, self.small_font, self.black, self.screen, 400, y_pos)
                y_pos += 40

        self._draw_text("Click anywhere to return to menu", self.small_font, self.gray, self.screen, 400, 550)
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

            if choice == "Pinch Runner":
                self._run_game(PinchRunnerGame, "PinchRunner")
            elif choice == "Angle Master":
                self._run_game(AngleMasterGame, "AngleMaster")
            elif choice == "Dashboard":
                self._show_dashboard()
            elif choice == "Quit":
                pygame.quit()
                sys.exit()

if __name__ == '__main__':
    app = MainApp()
    app.run()

