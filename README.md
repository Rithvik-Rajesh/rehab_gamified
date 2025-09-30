# Rehab Gamified

A gamification platform for rehabilitation exercises using hand tracking technology. This application uses computer vision to track hand movements and provides engaging games that help users with hand rehabilitation in a fun, interactive way.

## 📋 Features

- **Real-time hand tracking** using MediaPipe
- **Interactive games** designed for rehabilitation exercises
- **Progress tracking** across multiple sessions
- **Camera feed integration** so users can see their hands during gameplay
- **Dashboard** to view historical performance data

## 🎮 Available Games

### Balloon Pop

Pop balloons using a pinching gesture (bringing your thumb and index finger together). The game features:

- Colorful balloons floating upward
- Score tracking
- Visual feedback for pinch gestures

### Maze Game

Navigate through a maze using hand gestures. Features include:

- Challenging maze layouts
- Timing and scoring system
- Hand position tracking

### Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/Rehab-Gamified.git
   cd Rehab-Gamified
   ```

2. Create and activate a virtual environment (recommended):

   ```
   python -m venv .venv

   # On Windows
   .venv\Scripts\activate

   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

Navigate to the rehab_gamification directory and run the main script:

```
cd rehab_gamification
python main.py
```

This will launch the main menu where you can select a game to play or view your progress on the dashboard.

## 📊 Data Storage

Your session data is stored in JSON format in the `rehab_gamification/data` directory. This includes:

- Game type
- Score
- Session timestamp
- Game-specific metrics (e.g., pinch counts, angles achieved)

## 🧩 Project Structure

```
rehab_gamification/
├── hand_tracking/        # Hand tracking module using MediaPipe
├── games/               # Game implementations
├── data/                # Session data storage (created automatically)
├── assets/              # Images, sounds, and other assets
├── main.py              # Main application entry point
└── data_manager.py      # Handles saving and loading session data
```

## 🔧 Advanced Customization

### Adding New Games

To create a new game:

1. Create a new Python file in the `rehab_gamification/games` directory
2. Have your game class inherit from `BaseGame`
3. Implement the required methods (`run`, etc.)
4. Add your game to the menu options in `main.py`

### Changing Hand Tracking Parameters

Adjust the parameters in `HandTracker` initialization to customize:

- Maximum number of hands to track
- Detection confidence
- Tracking confidence

## 🙏 Acknowledgments

- [MediaPipe](https://google.github.io/mediapipe/) for hand tracking technology
- [PyGame](https://www.pygame.org/) for the game framework
- Contributors to the project
