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
        Saves a game session's data to a JSON file with a more detailed structure.
        :param game_name: The name of the game.
        :param session_data: A dictionary containing the session's data.
        """
        timestamp = datetime.now()
        filename = os.path.join(self.data_folder, f"session_{game_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json")
        
        # Enhance the data structure
        data_to_save = {
            "metadata": {
                "game_name": game_name,
                "session_start_time": timestamp.isoformat(),
                "version": "1.0"
            },
            "metrics": session_data
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
        for filename in sorted(os.listdir(self.data_folder), reverse=True):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_folder, filename)
                with open(filepath, 'r') as f:
                    try:
                        data = json.load(f)
                        # Add filename for reference, can be useful for deletion or updates
                        data['metadata']['filename'] = filename
                        all_sessions.append(data)
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Warning: Could not decode or parse JSON from {filename}. Error: {e}")
        return all_sessions

    def clear_game_data(self, game_name):
        """
        Clears all session data for a specific game.
        :param game_name: The name of the game whose data should be cleared.
        """
        if not os.path.exists(self.data_folder):
            return
        
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        for filename in files:
            filepath = os.path.join(self.data_folder, filename)
            try:
                with open(filepath, 'r') as f:
                    session = json.load(f)
                if session.get('metadata', {}).get('game_name') == game_name:
                    os.remove(filepath)
            except Exception as e:
                print(f"Error clearing {filename}: {e}")


