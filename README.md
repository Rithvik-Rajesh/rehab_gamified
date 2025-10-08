# Rehab Gamified

> A gamified rehabilitation platform leveraging real-time hand tracking and
> interactive games to make hand therapy engaging, measurable, and fun.

---

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vishwavinayak/rehab_gamified.git
   cd Rehab-Gamified
   ```

2. **(Recommended) Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r rehab_gamification/requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```
   _(Run from the project root directory)_

---

## 🗂️ Project Structure

```
rehab_gamification/
├── assets/                # Images, sounds, and game assets
│   └── dino_game/         # Assets for Dino Game
├── data/                  # Session data (auto-generated)
├── ExampleGames/          # Example game scripts and templates
├── games/                 # Game implementations (Balloon Pop, Maze, etc.)
│   ├── base_game.py       # Base class for all games
│   └── ...
├── hand_tracking/         # Hand tracking module (MediaPipe)
│   └── hand_tracker.py
├── Progress/              # Progress reports, analytics, dashboards
├── calibration.py         # Calibration utilities
├── dashboard_analytics.py # Analytics and dashboard logic
├── dashboard_launcher.py  # Dashboard launcher script
├── data_manager.py        # Handles session data I/O
├── dummy_data_generator.py# Generates sample data
├── enhanced_dashboard.py  # Enhanced dashboard features
├── requirements.txt       # Python dependencies
└── main.py                # Main application entry point
```

---

## 🎮 Games Included

- **Balloon Pop**: Pop balloons with a pinching gesture (thumb & index finger).
  Features colorful visuals, score tracking, and real-time feedback.
- **Maze Game**: Navigate a maze using hand gestures. Includes challenging
  layouts, timing, and scoring.
- **(More games can be added easily! See below.)**

---

## 📊 Progress Tracking & Analytics

- All session data is stored as JSON in `rehab_gamification/data/`.
- Progress dashboards, analytics, and detailed reports are generated in
  `rehab_gamification/Progress/`.
- Data includes: game type, score, session timestamp, and game-specific metrics
  (e.g., pinch counts, angles achieved).

---

## 🛠️ Customization & Extensibility

### Adding a New Game

1. Create a new Python file in `rehab_gamification/games/`.
2. Inherit from `BaseGame` and implement required methods (e.g., `run`).
3. Register your game in the main menu (`main.py`).

### Adjusting Hand Tracking

- Modify parameters in `hand_tracking/hand_tracker.py` to change:
  - Number of hands tracked
  - Detection/tracking confidence

---

## ✅ What's Done

- Modular, extensible codebase for gamified rehab
- Real-time hand tracking (MediaPipe)
- Multiple interactive games
- Progress tracking and analytics dashboards
- Data storage and management
- Easy game addition and customization
- Clean, organized project structure

---

## 📢 Notes

- **Run `main.py` from the project root** (not inside the `rehab_gamification`
  folder).
- All dependencies are listed in `rehab_gamification/requirements.txt`.
- For best results, use a webcam and ensure good lighting for hand tracking.

---

## 🙏 Acknowledgments

- [MediaPipe](https://google.github.io/mediapipe/) — Hand tracking technology
- [PyGame](https://www.pygame.org/) — Game framework
- Project contributors
