import pygame
import sys
from datetime import datetime
from rehab_gamification.games.balloon_pop import BalloonPopGame
from rehab_gamification.games.game_2 import FingerPainterGame
from rehab_gamification.games.maze_game import MazeGame
from rehab_gamification.games.dino_game import DinoGame
from rehab_gamification.data_manager import DataManager
from rehab_gamification.calibration import CalibrationScreen
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
        self.menu_options = ["Balloon Pop", "Finger Painter", "Maze Game","Dino Game", "Dashboard", "Quit"]
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
        """Runs a game with calibration, and saves the session data."""
        # Run calibration first
        calibration = CalibrationScreen(self.screen, self.hand_tracker, self.cap)
        calibration_data = calibration.run()
        
        # Apply calibration to hand tracker
        self.hand_tracker.set_calibration(calibration_data)
        
        # Run the game with calibration data
        game = game_class(self.screen, self.hand_tracker, self.cap, calibration_data)
        session_data = game.run()
        self.data_manager.save_session(game_name, session_data)

    def _show_dashboard(self):
        """Displays the dashboard with data from past sessions and allows per-game progress viewing."""
        sessions = self.data_manager.load_all_sessions()
        self.screen.fill(self.white)
        self._draw_text('Dashboard', self.font, self.black, self.screen, self.screen.get_width() / 2, 50)

        # --- Group sessions by game ---
        game_sessions = {}
        for session in sessions:
            game_name = session.get('metadata', {}).get('game_name', 'Unknown')
            if game_name not in game_sessions:
                game_sessions[game_name] = []
            game_sessions[game_name].append(session)

        # --- Game selection menu ---
        games = list(game_sessions.keys())
        button_rects = []
        y_pos = 120
        for game in games:
            rect = pygame.Rect(self.screen.get_width() // 2 - 200, y_pos, 400, 50)
            button_rects.append((rect, game))
            pygame.draw.rect(self.screen, self.gray, rect)
            self._draw_text(game, self.small_font, self.black, self.screen, self.screen.get_width() // 2, y_pos + 25)
            y_pos += 70

        self._draw_text("Click a game to view progress", self.small_font, self.gray, self.screen, self.screen.get_width() // 2, y_pos + 20)
        pygame.display.flip()

        # --- Wait for game selection ---
        selected_game = None
        while selected_game is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, game in button_rects:
                        if rect.collidepoint(event.pos):
                            selected_game = game
            pygame.time.wait(10)

        # --- Show progress chart for selected game ---
        self._show_game_progress_chart(game_sessions[selected_game], selected_game)

    def _show_game_progress_chart(self, sessions, game_name):
        """Displays a progress chart for a specific game with hover tooltips."""
        # --- Prepare data ---
        from collections import defaultdict
        import datetime

        date_sessions = defaultdict(list)
        for session in sessions:
            ts = session.get('metadata', {}).get('session_start_time', None)
            if ts:
                try:
                    date = datetime.datetime.fromisoformat(ts).date()
                except Exception:
                    date = "Unknown"
            else:
                date = "Unknown"
            date_sessions[date].append(session)

        # For each date, get max score, min/max pinch distance, max speed, etc.
        chart_data = []
        for date in sorted(date_sessions.keys()):
            day_sessions = date_sessions[date]
            max_score = max([s.get('metrics', {}).get('score', 0) for s in day_sessions])
            
            # Get min and max pinch distances
            all_min_pinch = [s.get('metrics', {}).get('min_pinch_distance', 0) for s in day_sessions]
            all_max_pinch = [s.get('metrics', {}).get('max_pinch_distance', 0) for s in day_sessions]
            min_pinch_distance = min([d for d in all_min_pinch if d > 0]) if any(d > 0 for d in all_min_pinch) else 0
            max_pinch_distance = max(all_max_pinch) if all_max_pinch else 0
            
            # Get max speed
            max_speed = max([s.get('metrics', {}).get('max_speed', 0) for s in day_sessions])
            
            chart_data.append({
                "date": date,
                "score": max_score,
                "min_pinch_distance": round(min_pinch_distance, 2),
                "max_pinch_distance": round(max_pinch_distance, 2),
                "max_speed": round(max_speed, 2),
                "sessions": day_sessions
            })

        # --- Draw chart ---
        running = True
        hover_index = None
        while running:
            self.screen.fill(self.white)
            self._draw_text(f"{game_name} Progress", self.font, self.black, self.screen, self.screen.get_width() // 2, 50)
            
            # Back button
            self._draw_text("Back", self.small_font, self.red, self.screen, 80, 40)
            back_rect = pygame.Rect(30, 20, 100, 40)
            
            # Clear Data button
            self._draw_text("Clear Data", self.small_font, self.red, self.screen, self.screen.get_width() - 100, 40)
            clear_rect = pygame.Rect(self.screen.get_width() - 170, 20, 150, 40)

            # Chart area
            chart_x = 120
            chart_y = 120
            chart_w = self.screen.get_width() - 200
            chart_h = 350

            # Draw axes
            pygame.draw.line(self.screen, self.black, (chart_x, chart_y), (chart_x, chart_y + chart_h), 2)
            pygame.draw.line(self.screen, self.black, (chart_x, chart_y + chart_h), (chart_x + chart_w, chart_y + chart_h), 2)

            # Draw bars for scores
            if chart_data:
                max_score = max([d["score"] for d in chart_data]) or 1
                bar_w = max(30, min(60, chart_w // max(1, len(chart_data))))
                spacing = bar_w + 10
                for i, d in enumerate(chart_data):
                    bar_height = int((d["score"] / max_score) * (chart_h - 40))
                    bar_rect = pygame.Rect(chart_x + i * spacing, chart_y + chart_h - bar_height, bar_w, bar_height)
                    color = (100, 180, 255) if i != hover_index else (255, 180, 100)
                    pygame.draw.rect(self.screen, color, bar_rect)
                    # Date label
                    date_str = str(d["date"])[5:] if d["date"] != "Unknown" else "?"
                    date_label = self.small_font.render(date_str, True, self.black)
                    self.screen.blit(date_label, (bar_rect.centerx - date_label.get_width() // 2, chart_y + chart_h + 5))
                    # Hover detection
                    mouse_pos = pygame.mouse.get_pos()
                    if bar_rect.collidepoint(mouse_pos):
                        hover_index = i
                    elif hover_index == i and not bar_rect.collidepoint(mouse_pos):
                        hover_index = None

            # --- Hover tooltip ---
            if hover_index is not None and hover_index < len(chart_data):
                d = chart_data[hover_index]
                tooltip_lines = [
                    f"Date: {d['date']}",
                    f"Score: {d['score']}",
                    f"Min Pinch: {d['min_pinch_distance']}px",
                    f"Max Pinch: {d['max_pinch_distance']}px",
                    f"Max Speed: {d['max_speed']}"
                ]
                tooltip_w = max(self.small_font.size(line)[0] for line in tooltip_lines) + 20
                tooltip_h = 25 * len(tooltip_lines) + 10
                mx, my = pygame.mouse.get_pos()
                tooltip_rect = pygame.Rect(mx + 10, my - tooltip_h, tooltip_w, tooltip_h)
                pygame.draw.rect(self.screen, (240, 240, 200), tooltip_rect)
                pygame.draw.rect(self.screen, self.black, tooltip_rect, 2)
                for idx, line in enumerate(tooltip_lines):
                    text = self.small_font.render(line, True, self.black)
                    self.screen.blit(text, (tooltip_rect.x + 10, tooltip_rect.y + 5 + idx * 25))

            pygame.display.flip()

            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos):
                        running = False
                    elif clear_rect.collidepoint(event.pos):
                        # Confirm and clear data
                        if self._confirm_clear_data(game_name):
                            self.data_manager.clear_game_data(game_name)
                            running = False

            pygame.time.wait(20)

    def _confirm_clear_data(self, game_name):
        """Shows a confirmation dialog for clearing data."""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        confirm_text = self.font.render(f"Clear all data for {game_name}?", True, self.white)
        yes_text = self.small_font.render("Yes", True, self.white)
        no_text = self.small_font.render("No", True, self.white)
        
        self.screen.blit(confirm_text, (self.screen.get_width() // 2 - confirm_text.get_width() // 2, 250))
        
        yes_rect = pygame.Rect(self.screen.get_width() // 2 - 120, 350, 100, 50)
        no_rect = pygame.Rect(self.screen.get_width() // 2 + 20, 350, 100, 50)
        
        pygame.draw.rect(self.screen, self.red, yes_rect)
        pygame.draw.rect(self.screen, self.gray, no_rect)
        
        self.screen.blit(yes_text, (yes_rect.centerx - yes_text.get_width() // 2, yes_rect.centery - yes_text.get_height() // 2))
        self.screen.blit(no_text, (no_rect.centerx - no_text.get_width() // 2, no_rect.centery - no_text.get_height() // 2))
        
        pygame.display.flip()
        
        waiting = True
        result = False
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_rect.collidepoint(event.pos):
                        result = True
                        waiting = False
                    elif no_rect.collidepoint(event.pos):
                        result = False
                        waiting = False
        
        return result

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
            elif choice == "Dino Game":
                self._run_game(DinoGame, "DinoGame")
            elif choice == "Dashboard":
                self._show_dashboard()
            elif choice == "Quit":
                self.cap.release()
                pygame.quit()
                sys.exit()

if __name__ == '__main__':
    app = MainApp()
    app.run()


