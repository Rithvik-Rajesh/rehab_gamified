import json
import os
from datetime import datetime

class DataManager:
    """
    Manages saving and loading of game session data.
    """
    def __init__(self, data_folder='data'):
        """
        Initializes the DataManager.
        :param data_folder: The folder where session data is stored.
        """
        self.data_folder = data_folder
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def save_session(self, game_name, session_data):
        """
        Saves a game session's data to a JSON file.
        :param game_name: The name of the game.
        :param session_data: A dictionary containing the session's data.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_folder, f"session_{game_name}_{timestamp}.json")
        
        data_to_save = {
            "game_name": game_name,
            "timestamp": timestamp,
            "session_data": session_data
        }
        
        with open(filename, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Session saved to {filename}")

    def load_all_sessions(self):
        """
        Loads all session data from the data folder.
        :return: A list of all session data dictionaries.
        """
        all_sessions = []
        for filename in os.listdir(self.data_folder):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_folder, filename)
                with open(filepath, 'r') as f:
                    try:
                        all_sessions.append(json.load(f))
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from {filename}")
        return all_sessions

