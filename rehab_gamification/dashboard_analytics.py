# dashboard_analytics.py

import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt

class DashboardAnalytics:
    """
    A comprehensive analytics class for rehabilitation gaming dashboard.
    Processes enhanced session data to provide meaningful insights.
    """
    
    def __init__(self, data_directory: str = None):
        """
        Initialize the dashboard analytics.
        :param data_directory: Path to directory containing session data files
        """
        self.data_directory = data_directory or "rehab_gamification/data"
        self.session_data = []
        self.load_all_sessions()
    
    def load_all_sessions(self):
        """Load all session data from the data directory."""
        self.session_data = []
        
        if not os.path.exists(self.data_directory):
            print(f"Data directory {self.data_directory} not found.")
            return
        
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.data_directory, filename), 'r') as f:
                        data = json.load(f)
                        # Add filename for reference
                        data['filename'] = filename
                        self.session_data.append(data)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def get_overall_performance_summary(self) -> Dict[str, Any]:
        """
        Generate an overall performance summary across all games and sessions.
        """
        if not self.session_data:
            return {"error": "No session data available"}
        
        # Separate enhanced data sessions from legacy sessions
        enhanced_sessions = [s for s in self.session_data if 'hand_movement_analytics' in s]
        legacy_sessions = [s for s in self.session_data if 'hand_movement_analytics' not in s]
        
        summary = {
            "overall_stats": {
                "total_sessions": len(self.session_data),
                "enhanced_sessions": len(enhanced_sessions),
                "legacy_sessions": len(legacy_sessions),
                "games_played": list(set([self._extract_game_name(s) for s in self.session_data]))
            },
            "hand_movement_performance": self._analyze_hand_movements(enhanced_sessions),
            "pinch_performance": self._analyze_pinch_data(enhanced_sessions),
            "game_specific_performance": self._analyze_game_performance(),
            "progress_trends": self._analyze_progress_trends(),
            "rehabilitation_insights": self._generate_rehab_insights()
        }
        
        return summary
    
    def _extract_game_name(self, session: Dict) -> str:
        """Extract game name from session data."""
        if 'game_name' in session:
            return session['game_name']
        elif 'filename' in session:
            # Extract from filename pattern: session_GameName_timestamp.json
            parts = session['filename'].split('_')
            if len(parts) >= 2:
                return parts[1]
        return "Unknown"
    
    def _analyze_hand_movements(self, enhanced_sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze hand movement data across enhanced sessions."""
        if not enhanced_sessions:
            return {"message": "No enhanced session data available"}
        
        movement_data = []
        for session in enhanced_sessions:
            if 'hand_movement_analytics' in session:
                movement_data.append(session['hand_movement_analytics'])
        
        if not movement_data:
            return {"message": "No hand movement data found"}
        
        # Calculate aggregated metrics
        total_movements = sum([d.get('total_movements', 0) for d in movement_data])
        successful_interactions = sum([d.get('successful_interactions', 0) for d in movement_data])
        avg_speeds = [d.get('avg_movement_speed', 0) for d in movement_data if d.get('avg_movement_speed', 0) > 0]
        smoothness_scores = [d.get('movement_smoothness_score', 0) for d in movement_data if d.get('movement_smoothness_score', 0) > 0]
        
        return {
            "total_hand_movements": total_movements,
            "successful_interactions": successful_interactions,
            "overall_interaction_success_rate": round((successful_interactions / max(1, total_movements)) * 100, 2),
            "average_movement_speed": round(np.mean(avg_speeds) if avg_speeds else 0, 2),
            "movement_speed_consistency": round(100 - (np.std(avg_speeds) / np.mean(avg_speeds) * 100) if avg_speeds and np.mean(avg_speeds) > 0 else 0, 2),
            "average_movement_smoothness": round(np.mean(smoothness_scores) if smoothness_scores else 0, 2),
            "hand_tracking_quality": {
                "avg_detection_rate": round(np.mean([s.get('session_metadata', {}).get('hand_detection_rate', 0) for s in enhanced_sessions]), 2),
                "total_tracking_losses": sum([d.get('tracking_lost_count', 0) for d in movement_data])
            }
        }
    
    def _analyze_pinch_data(self, enhanced_sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze pinch gesture data across enhanced sessions."""
        if not enhanced_sessions:
            return {"message": "No enhanced session data available"}
        
        pinch_data = []
        for session in enhanced_sessions:
            if 'pinch_analytics' in session:
                pinch_data.append(session['pinch_analytics'])
        
        if not pinch_data:
            return {"message": "No pinch data found"}
        
        # Calculate aggregated pinch metrics
        total_attempts = sum([d.get('total_pinch_attempts', 0) for d in pinch_data])
        successful_pinches = sum([d.get('successful_pinches', 0) for d in pinch_data])
        avg_distances = [d.get('avg_pinch_distance', 0) for d in pinch_data if d.get('avg_pinch_distance', 0) > 0]
        avg_durations = [d.get('avg_pinch_duration', 0) for d in pinch_data if d.get('avg_pinch_duration', 0) > 0]
        consistency_scores = [d.get('pinch_consistency', 0) for d in pinch_data if d.get('pinch_consistency', 0) > 0]
        
        return {
            "total_pinch_attempts": total_attempts,
            "successful_pinches": successful_pinches,
            "overall_pinch_success_rate": round((successful_pinches / max(1, total_attempts)) * 100, 2),
            "average_pinch_distance": round(np.mean(avg_distances) if avg_distances else 0, 2),
            "pinch_distance_consistency": round(100 - (np.std(avg_distances) / np.mean(avg_distances) * 100) if avg_distances and np.mean(avg_distances) > 0 else 0, 2),
            "average_pinch_duration": round(np.mean(avg_durations) if avg_durations else 0, 3),
            "pinch_control_consistency": round(np.mean(consistency_scores) if consistency_scores else 0, 2),
            "pinch_timing_analysis": {
                "avg_time_between_pinches": round(np.mean([d.get('avg_time_between_pinches', 0) for d in pinch_data if d.get('avg_time_between_pinches', 0) > 0]), 2)
            }
        }
    
    def _analyze_game_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics for each game type."""
        game_performance = {}
        
        # Group sessions by game
        games = {}
        for session in self.session_data:
            game_name = self._extract_game_name(session)
            if game_name not in games:
                games[game_name] = []
            games[game_name].append(session)
        
        for game_name, sessions in games.items():
            game_performance[game_name] = self._analyze_single_game_performance(game_name, sessions)
        
        return game_performance
    
    def _analyze_single_game_performance(self, game_name: str, sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze performance for a specific game."""
        performance = {
            "sessions_played": len(sessions),
            "game_specific_metrics": {}
        }
        
        if game_name == "BalloonPop":
            scores = []
            for session in sessions:
                if 'game_specific_metrics' in session:
                    scores.append(session['game_specific_metrics'].get('score', 0))
                elif 'score' in session:
                    scores.append(session['score'])
            
            if scores:
                performance["game_specific_metrics"] = {
                    "average_score": round(np.mean(scores), 2),
                    "best_score": max(scores),
                    "score_improvement": round(scores[-1] - scores[0] if len(scores) > 1 else 0, 2),
                    "balloons_popped_total": sum(scores)
                }
        
        elif game_name == "MazeGame":
            completion_times = []
            wall_touches = []
            completed_count = 0
            
            for session in sessions:
                if 'game_specific_metrics' in session:
                    metrics = session['game_specific_metrics']
                    if metrics.get('completed', False):
                        completion_times.append(metrics.get('time_taken', 0))
                        completed_count += 1
                    wall_touches.append(metrics.get('wall_touches', 0))
                elif 'time_taken' in session:
                    if session.get('completed', False):
                        completion_times.append(session['time_taken'])
                        completed_count += 1
                    wall_touches.append(session.get('wall_touches', 0))
            
            performance["game_specific_metrics"] = {
                "completion_rate": round((completed_count / len(sessions)) * 100, 2),
                "average_completion_time": round(np.mean(completion_times) if completion_times else 0, 2),
                "best_completion_time": round(min(completion_times) if completion_times else 0, 2),
                "average_wall_touches": round(np.mean(wall_touches) if wall_touches else 0, 2),
                "navigation_improvement": round(wall_touches[0] - wall_touches[-1] if len(wall_touches) > 1 else 0, 2)
            }
        
        return performance
    
    def _analyze_progress_trends(self) -> Dict[str, Any]:
        """Analyze progress trends over time."""
        if len(self.session_data) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Sort sessions by timestamp (extracted from filename)
        sorted_sessions = sorted(self.session_data, key=lambda x: self._extract_timestamp(x.get('filename', '')))
        
        trends = {
            "session_count_over_time": len(sorted_sessions),
            "performance_trends": {}
        }
        
        # Analyze trends for enhanced sessions
        enhanced_sessions = [s for s in sorted_sessions if 'hand_movement_analytics' in s]
        if len(enhanced_sessions) >= 2:
            early_sessions = enhanced_sessions[:len(enhanced_sessions)//2]
            recent_sessions = enhanced_sessions[len(enhanced_sessions)//2:]
            
            early_success_rate = np.mean([s.get('hand_movement_analytics', {}).get('interaction_effectiveness', 0) for s in early_sessions])
            recent_success_rate = np.mean([s.get('hand_movement_analytics', {}).get('interaction_effectiveness', 0) for s in recent_sessions])
            
            early_smoothness = np.mean([s.get('hand_movement_analytics', {}).get('movement_smoothness_score', 0) for s in early_sessions])
            recent_smoothness = np.mean([s.get('hand_movement_analytics', {}).get('movement_smoothness_score', 0) for s in recent_sessions])
            
            trends["performance_trends"] = {
                "interaction_effectiveness_improvement": round(recent_success_rate - early_success_rate, 2),
                "movement_smoothness_improvement": round(recent_smoothness - early_smoothness, 2),
                "trend_direction": "improving" if recent_success_rate > early_success_rate else "stable" if recent_success_rate == early_success_rate else "declining"
            }
        
        return trends
    
    def _extract_timestamp(self, filename: str) -> str:
        """Extract timestamp from filename for sorting."""
        if not filename:
            return "00000000_000000"
        parts = filename.split('_')
        if len(parts) >= 3:
            return f"{parts[-2]}_{parts[-1].replace('.json', '')}"
        return "00000000_000000"
    
    def _generate_rehab_insights(self) -> Dict[str, Any]:
        """Generate rehabilitation-focused insights and recommendations."""
        enhanced_sessions = [s for s in self.session_data if 'hand_movement_analytics' in s]
        
        if not enhanced_sessions:
            return {"message": "No enhanced session data for rehabilitation insights"}
        
        # Calculate overall rehabilitation metrics
        avg_hand_detection = np.mean([s.get('session_metadata', {}).get('hand_detection_rate', 0) for s in enhanced_sessions])
        avg_interaction_effectiveness = np.mean([s.get('hand_movement_analytics', {}).get('interaction_effectiveness', 0) for s in enhanced_sessions])
        avg_movement_smoothness = np.mean([s.get('hand_movement_analytics', {}).get('movement_smoothness_score', 0) for s in enhanced_sessions])
        avg_pinch_success = np.mean([s.get('pinch_analytics', {}).get('pinch_success_rate', 0) for s in enhanced_sessions])
        
        insights = {
            "overall_rehabilitation_score": round((avg_hand_detection + avg_interaction_effectiveness + avg_movement_smoothness + avg_pinch_success) / 4, 2),
            "key_metrics": {
                "hand_tracking_reliability": round(avg_hand_detection, 2),
                "motor_control_effectiveness": round(avg_interaction_effectiveness, 2),
                "movement_quality": round(avg_movement_smoothness, 2),
                "fine_motor_skills": round(avg_pinch_success, 2)
            },
            "recommendations": self._generate_recommendations(avg_hand_detection, avg_interaction_effectiveness, avg_movement_smoothness, avg_pinch_success)
        }
        
        return insights
    
    def _generate_recommendations(self, detection_rate: float, interaction_rate: float, smoothness: float, pinch_rate: float) -> List[str]:
        """Generate personalized recommendations based on performance metrics."""
        recommendations = []
        
        if detection_rate < 80:
            recommendations.append("Consider improving lighting conditions and camera positioning for better hand tracking.")
        
        if interaction_rate < 60:
            recommendations.append("Focus on games that improve hand-eye coordination and precise movements.")
        
        if smoothness < 50:
            recommendations.append("Practice slow, controlled movements to improve movement smoothness and reduce tremor.")
        
        if pinch_rate < 70:
            recommendations.append("Work on pinch exercises to strengthen fine motor control and finger coordination.")
        
        if detection_rate > 90 and interaction_rate > 80:
            recommendations.append("Excellent progress! Consider increasing game difficulty or trying more challenging tasks.")
        
        if not recommendations:
            recommendations.append("Great performance across all metrics! Continue with current rehabilitation routine.")
        
        return recommendations
    
    def save_dashboard_report(self, output_path: str = None):
        """Save a comprehensive dashboard report to a JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"rehabilitation_dashboard_report_{timestamp}.json"
        
        report = self.get_overall_performance_summary()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Dashboard report saved to: {output_path}")
        return output_path

# Example usage and testing
if __name__ == "__main__":
    # Initialize dashboard analytics
    dashboard = DashboardAnalytics()
    
    # Generate comprehensive report
    report = dashboard.get_overall_performance_summary()
    
    # Print summary
    print("=== REHABILITATION GAMING DASHBOARD ===")
    print(f"Total Sessions: {report.get('overall_stats', {}).get('total_sessions', 0)}")
    print(f"Games Played: {', '.join(report.get('overall_stats', {}).get('games_played', []))}")
    
    if 'hand_movement_performance' in report:
        hand_perf = report['hand_movement_performance']
        print(f"\\nHand Movement Success Rate: {hand_perf.get('overall_interaction_success_rate', 0)}%")
        print(f"Average Movement Smoothness: {hand_perf.get('average_movement_smoothness', 0)}")
    
    if 'pinch_performance' in report:
        pinch_perf = report['pinch_performance']
        print(f"\\nPinch Success Rate: {pinch_perf.get('overall_pinch_success_rate', 0)}%")
        print(f"Pinch Control Consistency: {pinch_perf.get('pinch_control_consistency', 0)}")
    
    # Save detailed report
    dashboard.save_dashboard_report()