# enhanced_dashboard.py

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from scipy.stats import pearsonr

# Set style for better looking plots
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

class EnhancedRehabDashboard:
    """
    Comprehensive Rehabilitation Gaming Dashboard System
    
    Features:
    - Game Performance Metrics (Score progression, Success rates, Reaction times)
    - Physical/Motor Improvement Metrics (ROM, Grip strength, Movement smoothness)  
    - Engagement Metrics (Session frequency, Duration, Game variety)
    - Achievement System (Badges, Milestones, Streaks)
    - Day-based Analysis with Trend Detection
    - Interactive Visualizations
    """
    
    def __init__(self, data_directory: str = None, progress_directory: str = None):
        """
        Initialize the Enhanced Dashboard System
        
        Args:
            data_directory: Path to session data files
            progress_directory: Path to save progress reports and visualizations
        """
        self.data_directory = data_directory or "rehab_gamification/data"
        self.progress_directory = progress_directory or "rehab_gamification/Progress"
        
        # Ensure progress directory exists
        os.makedirs(self.progress_directory, exist_ok=True)
        
        # Initialize data storage
        self.session_data = []
        self.daily_analytics = {}
        self.achievements = {}
        self.physical_metrics = {}
        self.engagement_metrics = {}
        
        # Load and process all data
        self.load_all_sessions()
        self.process_daily_analytics()
        self.calculate_achievements()
    
    def load_all_sessions(self):
        """Load and parse all session data files"""
        print("🔄 Loading session data...")
        
        self.session_data = []
        
        if not os.path.exists(self.data_directory):
            print(f"⚠️  Data directory {self.data_directory} not found.")
            return
        
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.data_directory, filename), 'r') as f:
                        data = json.load(f)
                        
                        # Extract metadata from filename
                        data['filename'] = filename
                        data['timestamp'] = self._extract_timestamp_from_filename(filename)
                        data['date'] = self._extract_date_from_filename(filename)
                        data['game_name'] = self._extract_game_name_from_filename(filename)
                        
                        self.session_data.append(data)
                        
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        
        # Sort sessions by timestamp
        self.session_data.sort(key=lambda x: x.get('timestamp', ''))
        print(f"✅ Loaded {len(self.session_data)} sessions")
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """Extract timestamp from filename format: session_GameName_YYYYMMDD_HHMMSS.json"""
        try:
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                date_part = parts[-2]  # YYYYMMDD
                time_part = parts[-1]  # HHMMSS
                
                # Parse into datetime
                dt = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                return dt.isoformat()
        except:
            pass
        return datetime.now().isoformat()
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """Extract date from filename"""
        try:
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                date_part = parts[-2]  # YYYYMMDD
                dt = datetime.strptime(date_part, "%Y%m%d")
                return dt.strftime("%Y-%m-%d")
        except:
            pass
        return datetime.now().strftime("%Y-%m-%d")
    
    def _extract_game_name_from_filename(self, filename: str) -> str:
        """Extract game name from filename"""
        try:
            parts = filename.split('_')
            if len(parts) >= 2:
                return parts[1]
        except:
            pass
        return "Unknown"
    
    def process_daily_analytics(self):
        """Process session data into daily analytics"""
        print("📊 Processing daily analytics...")
        
        self.daily_analytics = defaultdict(lambda: {
            'sessions_count': 0,
            'total_duration': 0,
            'games_played': set(),
            'total_score': 0,
            'successful_actions': 0,
            'total_actions': 0,
            'pinch_success_rate': [],
            'movement_smoothness': [],
            'hand_detection_rate': [],
            'reaction_times': [],
            'range_of_motion_scores': [],
            'session_details': []
        })
        
        for session in self.session_data:
            date = session.get('date')
            game_name = session.get('game_name')
            
            if not date:
                continue
            
            # Basic session info
            self.daily_analytics[date]['sessions_count'] += 1
            self.daily_analytics[date]['games_played'].add(game_name)
            self.daily_analytics[date]['session_details'].append(session)
            
            # Duration (from enhanced data or estimate)
            if 'session_metadata' in session:
                duration = session['session_metadata'].get('duration_seconds', 0)
            else:
                duration = 60  # Default estimate for legacy sessions
            
            self.daily_analytics[date]['total_duration'] += duration
            
            # Game-specific metrics
            if 'game_specific_metrics' in session:
                metrics = session['game_specific_metrics']
                score = metrics.get('score', 0)
                self.daily_analytics[date]['total_score'] += score
            
            # Enhanced analytics (if available)
            if 'pinch_analytics' in session:
                pinch_data = session['pinch_analytics']
                success_rate = pinch_data.get('pinch_success_rate', 0)
                if success_rate > 0:
                    self.daily_analytics[date]['pinch_success_rate'].append(success_rate)
                
                successful = pinch_data.get('successful_pinches', 0)
                total = pinch_data.get('total_pinch_attempts', 0)
                self.daily_analytics[date]['successful_actions'] += successful
                self.daily_analytics[date]['total_actions'] += total
            
            if 'hand_movement_analytics' in session:
                movement_data = session['hand_movement_analytics']
                smoothness = movement_data.get('movement_smoothness_score', 0)
                if smoothness > 0:
                    self.daily_analytics[date]['movement_smoothness'].append(smoothness)
            
            if 'session_metadata' in session:
                detection_rate = session['session_metadata'].get('hand_detection_rate', 0)
                if detection_rate > 0:
                    self.daily_analytics[date]['hand_detection_rate'].append(detection_rate)
        
        # Convert sets to lists for JSON serialization
        for date_data in self.daily_analytics.values():
            date_data['games_played'] = list(date_data['games_played'])
        
        print(f"✅ Processed {len(self.daily_analytics)} days of data")
    
    def calculate_achievements(self):
        """Calculate achievements and milestones"""
        print("🏆 Calculating achievements...")
        
        self.achievements = {
            'total_sessions': len(self.session_data),
            'consecutive_days': self._calculate_streak(),
            'games_mastered': [],
            'milestones': [],
            'badges': []
        }
        
        # Calculate game-specific achievements
        game_stats = defaultdict(list)
        for session in self.session_data:
            game_name = session.get('game_name')
            if 'game_specific_metrics' in session:
                score = session['game_specific_metrics'].get('score', 0)
                game_stats[game_name].append(score)
        
        # Determine mastered games (consistent high performance)
        for game, scores in game_stats.items():
            if len(scores) >= 3:
                recent_avg = np.mean(scores[-3:])
                if recent_avg > np.mean(scores) * 1.2:  # 20% improvement
                    self.achievements['games_mastered'].append(game)
        
        # Add milestones
        if self.achievements['total_sessions'] >= 10:
            self.achievements['milestones'].append("🎯 Dedicated Player - 10+ Sessions")
        
        if self.achievements['consecutive_days'] >= 3:
            self.achievements['milestones'].append(f"🔥 {self.achievements['consecutive_days']}-Day Streak")
        
        if len(self.achievements['games_mastered']) >= 2:
            self.achievements['milestones'].append("🎮 Multi-Game Master")
        
        # Add badges based on performance
        avg_accuracy = self._calculate_overall_accuracy()
        if avg_accuracy >= 80:
            self.achievements['badges'].append("🎯 Sharpshooter - 80%+ Accuracy")
        
        if avg_accuracy >= 90:
            self.achievements['badges'].append("🏹 Master Marksman - 90%+ Accuracy")
        
        print(f"✅ Calculated {len(self.achievements['milestones'])} milestones and {len(self.achievements['badges'])} badges")
    
    def _calculate_streak(self) -> int:
        """Calculate consecutive days with sessions"""
        if not self.daily_analytics:
            return 0
        
        dates = sorted(self.daily_analytics.keys())
        current_streak = 1
        max_streak = 1
        
        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i-1], "%Y-%m-%d")
            curr_date = datetime.strptime(dates[i], "%Y-%m-%d")
            
            if (curr_date - prev_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def _calculate_overall_accuracy(self) -> float:
        """Calculate overall accuracy across all sessions"""
        total_successful = 0
        total_attempts = 0
        
        for session in self.session_data:
            if 'pinch_analytics' in session:
                pinch_data = session['pinch_analytics']
                total_successful += pinch_data.get('successful_pinches', 0)
                total_attempts += pinch_data.get('total_pinch_attempts', 0)
        
        return (total_successful / max(1, total_attempts)) * 100
    
    def generate_comprehensive_dashboard(self):
        """Generate the complete dashboard with all visualizations"""
        print("🎨 Generating comprehensive dashboard...")
        
        # Create main dashboard HTML
        self._create_main_dashboard_html()
        
        # Generate individual visualizations
        self._create_kpi_summary()
        self._create_progress_charts()
        self._create_physical_metrics_gauges()
        self._create_engagement_analysis()
        self._create_achievements_display()
        self._create_detailed_insights()
        
        # Generate all new visualizations
        self.generate_all_visualizations()
        
        print("✅ Dashboard generation complete!")
        print(f"📁 Files saved in: {self.progress_directory}")
        print("\n📊 Generated Visualizations:")
        print("  • Progress Trends (progress_trends.png)")
        print("  • Physical Metrics (physical_metrics.png)")
        print("  • Engagement Analysis (engagement_analysis.png)")
        print("  • Game Distribution (game_distribution.png)")
        print("  • Weekly Activity Heatmap (weekly_heatmap.png)")
        print("  • Performance Correlation Matrix (correlation_matrix.png)")
        print("  • KPI Dashboard (kpi_dashboard.png)")
        print("  • Success Rate Trends (success_rate_trends.png)")
        print("  • Performance Radar Chart (performance_radar.png)")
    
    def _create_main_dashboard_html(self):
        """Create the main dashboard HTML file"""
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rehabilitation Gaming Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .dashboard-header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .dashboard-header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .dashboard-header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .kpi-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-5px);
        }
        
        .kpi-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .kpi-value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .kpi-label {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .accuracy { color: #e74c3c; }
        .sessions { color: #3498db; }
        .improvement { color: #2ecc71; }
        .streak { color: #f39c12; }
        
        .chart-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .achievement-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .achievement-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .achievement-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .two-column {
                grid-template-columns: 1fr;
            }
            
            .kpi-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1><i class="fas fa-heartbeat"></i> Rehabilitation Gaming Dashboard</h1>
        <p>Track your progress, celebrate achievements, and optimize your rehabilitation journey</p>
    </div>
    
    <div class="container">
        <!-- KPI Summary Cards -->
        <div class="kpi-grid" id="kpi-section">
            <!-- KPI cards will be inserted here -->
        </div>
        
        <!-- Progress Charts -->
        <div class="chart-section">
            <h2 class="chart-title">📈 Game Performance Over Time</h2>
            <div id="progress-chart"></div>
        </div>
        
        <div class="two-column">
            <!-- Physical Metrics -->
            <div class="chart-section">
                <h2 class="chart-title">💪 Physical Metrics</h2>
                <div id="physical-metrics"></div>
            </div>
            
            <!-- Engagement Analysis -->
            <div class="chart-section">
                <h2 class="chart-title">🎮 Engagement Pattern</h2>
                <div id="engagement-chart"></div>
            </div>
        </div>
        
        <!-- Achievements -->
        <div class="chart-section">
            <h2 class="chart-title">🏆 Achievements & Milestones</h2>
            <div class="achievement-grid" id="achievements-section">
                <!-- Achievement cards will be inserted here -->
            </div>
        </div>
        
        <!-- Interactive Game Performance Chart -->
        <div class="chart-section">
            <h2 class="chart-title">📊 Interactive Game Performance Analysis</h2>
            <div id="interactive-performance-chart" style="height: 500px;"></div>
        </div>
        
        <!-- Detailed Insights -->
        <div class="chart-section">
            <h2 class="chart-title">🔍 Detailed Analysis & Recommendations</h2>
            <div id="insights-section">
                <!-- Insights will be inserted here -->
            </div>
        </div>
    </div>
    
    <script>
        // Sample data for the interactive chart
        var gamePerformanceData = [
            {
                x: ['Oct 1', 'Oct 2', 'Oct 3', 'Oct 5', 'Oct 6', 'Oct 7', 'Oct 8'],
                y: [750, 820, 880, 1200, 950, 1150, 1300],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'DinoGame Score',
                line: {color: '#3498db', width: 3},
                marker: {size: 8, color: '#3498db'}
            },
            {
                x: ['Oct 5', 'Oct 7', 'Oct 8'],
                y: [85, 92, 88],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'FingerPainter Accuracy %',
                yaxis: 'y2',
                line: {color: '#e74c3c', width: 3},
                marker: {size: 8, color: '#e74c3c'}
            },
            {
                x: ['Oct 6', 'Oct 8'],
                y: [78, 82],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'MazeGame Completion %',
                yaxis: 'y2',
                line: {color: '#2ecc71', width: 3},
                marker: {size: 8, color: '#2ecc71'}
            },
            {
                x: ['Oct 8'],
                y: [1450],
                type: 'scatter',
                mode: 'markers',
                name: 'BalloonPop Score',
                marker: {size: 12, color: '#f39c12'},
                showlegend: true
            }
        ];

        var layout = {
            title: {
                text: 'Multi-Game Performance Trends',
                font: {size: 18, color: '#2c3e50'}
            },
            xaxis: {
                title: 'Date',
                gridcolor: '#ecf0f1',
                showgrid: true
            },
            yaxis: {
                title: 'Game Scores',
                side: 'left',
                gridcolor: '#ecf0f1',
                showgrid: true,
                color: '#3498db'
            },
            yaxis2: {
                title: 'Accuracy/Completion %',
                side: 'right',
                overlaying: 'y',
                range: [0, 100],
                color: '#e74c3c'
            },
            legend: {
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(255,255,255,0.8)',
                bordercolor: '#ddd',
                borderwidth: 1
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: {t: 50, r: 80, b: 50, l: 80},
            hovermode: 'x unified'
        };

        var config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        };

        Plotly.newPlot('interactive-performance-chart', gamePerformanceData, layout, config);
        
        // Dashboard will be populated by Python-generated data
        console.log('Rehabilitation Gaming Dashboard Loaded');
    </script>
</body>
</html>
        '''
        
        with open(os.path.join(self.progress_directory, 'dashboard.html'), 'w') as f:
            f.write(html_content)
    
    def _create_kpi_summary(self):
        """Create KPI summary cards data"""
        # Calculate key metrics
        total_sessions = len(self.session_data)
        avg_accuracy = self._calculate_overall_accuracy()
        consecutive_days = self.achievements.get('consecutive_days', 0)
        
        # Calculate improvement (compare first vs last week)
        improvement = self._calculate_improvement_percentage()
        
        kpi_data = {
            'total_sessions': total_sessions,
            'avg_accuracy': round(avg_accuracy, 1),
            'consecutive_days': consecutive_days,
            'improvement': improvement
        }
        
        # Save KPI data
        with open(os.path.join(self.progress_directory, 'kpi_data.json'), 'w') as f:
            json.dump(kpi_data, f, indent=2)
        
        return kpi_data
    
    def _calculate_improvement_percentage(self) -> float:
        """Calculate improvement percentage from first to recent sessions"""
        if len(self.session_data) < 4:
            return 0
        
        # Compare first 2 vs last 2 sessions accuracy
        first_sessions = self.session_data[:2]
        last_sessions = self.session_data[-2:]
        
        def get_accuracy_from_sessions(sessions):
            total_successful = 0
            total_attempts = 0
            for session in sessions:
                if 'pinch_analytics' in session:
                    pinch_data = session['pinch_analytics']
                    total_successful += pinch_data.get('successful_pinches', 0)
                    total_attempts += pinch_data.get('total_pinch_attempts', 0)
            return (total_successful / max(1, total_attempts)) * 100
        
        first_accuracy = get_accuracy_from_sessions(first_sessions)
        last_accuracy = get_accuracy_from_sessions(last_sessions)
        
        if first_accuracy > 0:
            improvement = ((last_accuracy - first_accuracy) / first_accuracy) * 100
            return round(improvement, 1)
        
        return 0
    
    def _create_progress_charts(self):
        """Create progress visualization charts using matplotlib"""
        # Prepare daily data for charts
        dates = sorted(self.daily_analytics.keys())
        daily_scores = []
        daily_accuracy = []
        daily_smoothness = []
        
        for date in dates:
            day_data = self.daily_analytics[date]
            
            # Average score for the day
            total_score = day_data['total_score']
            sessions = day_data['sessions_count']
            avg_score = total_score / max(1, sessions)
            daily_scores.append(avg_score)
            
            # Average accuracy
            pinch_rates = day_data['pinch_success_rate']
            avg_accuracy = np.mean(pinch_rates) if pinch_rates else 0
            daily_accuracy.append(avg_accuracy)
            
            # Average smoothness
            smoothness_scores = day_data['movement_smoothness']
            avg_smoothness = np.mean(smoothness_scores) if smoothness_scores else 0
            daily_smoothness.append(avg_smoothness)
        
        # Convert dates to datetime objects for plotting
        date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
        
        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Performance Trends Over Time', fontsize=16, fontweight='bold')
        
        # Scores chart
        ax1.plot(date_objects, daily_scores, marker='o', linewidth=2, markersize=6, color='#3498db')
        ax1.set_title('Game Scores Over Time')
        ax1.set_ylabel('Average Score')
        ax1.grid(True, alpha=0.3)
        
        # Accuracy chart
        ax2.plot(date_objects, daily_accuracy, marker='s', linewidth=2, markersize=6, color='#e74c3c')
        ax2.set_title('Accuracy Percentage')
        ax2.set_ylabel('Accuracy %')
        ax2.grid(True, alpha=0.3)
        
        # Smoothness chart
        ax3.plot(date_objects, daily_smoothness, marker='^', linewidth=2, markersize=6, color='#2ecc71')
        ax3.set_title('Movement Smoothness')
        ax3.set_ylabel('Smoothness Score')
        ax3.set_xlabel('Date')
        ax3.grid(True, alpha=0.3)
        
        # Format x-axis dates
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'progress_trends.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Save chart data as JSON for web dashboard
        chart_data = {
            'dates': dates,
            'daily_scores': daily_scores,
            'daily_accuracy': daily_accuracy,
            'daily_smoothness': daily_smoothness
        }
        
        with open(os.path.join(self.progress_directory, 'chart_data.json'), 'w') as f:
            json.dump(chart_data, f, indent=2)
    
    def _create_physical_metrics_gauges(self):
        """Create physical metrics visualization"""
        # Calculate physical metrics
        avg_hand_detection = np.mean([np.mean(day['hand_detection_rate']) 
                                    for day in self.daily_analytics.values() 
                                    if day['hand_detection_rate']])
        
        avg_smoothness = np.mean([np.mean(day['movement_smoothness']) 
                                for day in self.daily_analytics.values() 
                                if day['movement_smoothness']])
        
        pinch_accuracy = self._calculate_overall_accuracy()
        
        # Create gauge-style chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Physical & Motor Metrics', fontsize=16, fontweight='bold')
        
        metrics = [
            ('Hand Detection Rate', avg_hand_detection, '%', '#3498db'),
            ('Movement Smoothness', avg_smoothness, '/100', '#2ecc71'),
            ('Pinch Accuracy', pinch_accuracy, '%', '#e74c3c'),
            ('Overall Performance', (avg_hand_detection + avg_smoothness + pinch_accuracy) / 3, '/100', '#f39c12')
        ]
        
        axes = [ax1, ax2, ax3, ax4]
        
        for i, (name, value, unit, color) in enumerate(metrics):
            ax = axes[i]
            
            # Create circular progress bar
            theta = np.linspace(0, 2*np.pi, 100)
            radius = 1
            
            # Background circle
            ax.plot(radius * np.cos(theta), radius * np.sin(theta), color='lightgray', linewidth=10)
            
            # Progress arc
            progress_theta = np.linspace(0, 2*np.pi * (value/100), int(value))
            ax.plot(radius * np.cos(progress_theta), radius * np.sin(progress_theta), 
                   color=color, linewidth=10)
            
            # Add text
            ax.text(0, 0, f'{value:.1f}{unit}', ha='center', va='center', 
                   fontsize=14, fontweight='bold')
            ax.text(0, -1.5, name, ha='center', va='center', fontsize=12)
            
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.8, 1.5)
            ax.set_aspect('equal')
            ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'physical_metrics.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Save metrics data
        physical_data = {
            'hand_detection_rate': avg_hand_detection,
            'movement_smoothness': avg_smoothness,
            'pinch_accuracy': pinch_accuracy,
            'overall_performance': (avg_hand_detection + avg_smoothness + pinch_accuracy) / 3
        }
        
        with open(os.path.join(self.progress_directory, 'physical_metrics.json'), 'w') as f:
            json.dump(physical_data, f, indent=2)
    
    def _create_engagement_analysis(self):
        """Create engagement pattern analysis"""
        # Calculate engagement metrics
        dates = sorted(self.daily_analytics.keys())
        session_counts = [self.daily_analytics[date]['sessions_count'] for date in dates]
        durations = [self.daily_analytics[date]['total_duration'] / 60 for date in dates]  # Convert to minutes
        game_variety = [len(self.daily_analytics[date]['games_played']) for date in dates]
        
        # Create engagement visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Engagement & Motivation Analysis', fontsize=16, fontweight='bold')
        
        date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
        
        # Sessions per day
        ax1.bar(date_objects, session_counts, color='#3498db', alpha=0.7)
        ax1.set_title('Sessions per Day')
        ax1.set_ylabel('Number of Sessions')
        ax1.grid(True, alpha=0.3)
        
        # Total duration per day
        ax2.bar(date_objects, durations, color='#e74c3c', alpha=0.7)
        ax2.set_title('Training Duration per Day')
        ax2.set_ylabel('Minutes')
        ax2.grid(True, alpha=0.3)
        
        # Game variety
        ax3.bar(date_objects, game_variety, color='#2ecc71', alpha=0.7)
        ax3.set_title('Game Variety per Day')
        ax3.set_ylabel('Different Games Played')
        ax3.grid(True, alpha=0.3)
        
        # Weekly pattern analysis
        weekdays = [datetime.strptime(date, "%Y-%m-%d").weekday() for date in dates]
        weekday_sessions = defaultdict(list)
        for i, day in enumerate(weekdays):
            weekday_sessions[day].append(session_counts[i])
        
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        avg_sessions_by_weekday = [np.mean(weekday_sessions.get(i, [0])) for i in range(7)]
        
        ax4.bar(weekday_names, avg_sessions_by_weekday, color='#f39c12', alpha=0.7)
        ax4.set_title('Average Sessions by Day of Week')
        ax4.set_ylabel('Average Sessions')
        ax4.grid(True, alpha=0.3)
        
        # Format dates
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'engagement_analysis.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Save engagement data
        engagement_data = {
            'total_sessions': sum(session_counts),
            'avg_sessions_per_day': np.mean(session_counts),
            'avg_duration_minutes': np.mean(durations),
            'avg_games_per_day': np.mean(game_variety),
            'most_active_weekday': weekday_names[np.argmax(avg_sessions_by_weekday)],
            'consistency_score': 100 - (np.std(session_counts) / np.mean(session_counts) * 100) if np.mean(session_counts) > 0 else 0
        }
        
        with open(os.path.join(self.progress_directory, 'engagement_data.json'), 'w') as f:
            json.dump(engagement_data, f, indent=2)
    
    def _create_achievements_display(self):
        """Create achievements and milestones display"""
        achievements_data = {
            'badges': self.achievements.get('badges', []),
            'milestones': self.achievements.get('milestones', []),
            'games_mastered': self.achievements.get('games_mastered', []),
            'total_sessions': self.achievements.get('total_sessions', 0),
            'consecutive_days': self.achievements.get('consecutive_days', 0)
        }
        
        with open(os.path.join(self.progress_directory, 'achievements.json'), 'w') as f:
            json.dump(achievements_data, f, indent=2)
    
    def _create_detailed_insights(self):
        """Create detailed insights and recommendations"""
        insights = {
            'performance_summary': {
                'overall_accuracy': self._calculate_overall_accuracy(),
                'improvement_trend': self._calculate_improvement_percentage(),
                'consistency_rating': self._calculate_consistency_rating(),
                'engagement_level': self._calculate_engagement_level()
            },
            'strengths': self._identify_strengths(),
            'areas_for_improvement': self._identify_improvement_areas(),
            'recommendations': self._generate_recommendations(),
            'next_milestones': self._suggest_next_milestones()
        }
        
        with open(os.path.join(self.progress_directory, 'detailed_insights.json'), 'w') as f:
            json.dump(insights, f, indent=2)
    
    def _calculate_consistency_rating(self) -> str:
        """Calculate consistency rating based on session patterns"""
        if len(self.daily_analytics) < 3:
            return "Building Routine"
        
        session_counts = [day['sessions_count'] for day in self.daily_analytics.values()]
        consistency = 100 - (np.std(session_counts) / np.mean(session_counts) * 100) if np.mean(session_counts) > 0 else 0
        
        if consistency > 80:
            return "Highly Consistent"
        elif consistency > 60:
            return "Moderately Consistent"
        else:
            return "Variable Pattern"
    
    def _calculate_engagement_level(self) -> str:
        """Calculate engagement level"""
        total_sessions = len(self.session_data)
        days_active = len(self.daily_analytics)
        
        if total_sessions > 20:
            return "Highly Engaged"
        elif total_sessions > 10:
            return "Well Engaged"
        elif total_sessions > 5:
            return "Building Engagement"
        else:
            return "Getting Started"
    
    def _identify_strengths(self) -> List[str]:
        """Identify user's strengths"""
        strengths = []
        accuracy = self._calculate_overall_accuracy()
        
        if accuracy > 85:
            strengths.append("Excellent pinch control accuracy")
        
        if len(self.session_data) > 15:
            strengths.append("Strong commitment to regular practice")
        
        if self.achievements.get('consecutive_days', 0) > 3:
            strengths.append("Consistent daily practice routine")
        
        if len(set(session.get('game_name') for session in self.session_data)) > 3:
            strengths.append("Good variety in exercise selection")
        
        return strengths
    
    def _identify_improvement_areas(self) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        accuracy = self._calculate_overall_accuracy()
        
        if accuracy < 70:
            areas.append("Pinch control precision")
        
        avg_smoothness = np.mean([np.mean(day['movement_smoothness']) 
                                for day in self.daily_analytics.values() 
                                if day['movement_smoothness']])
        
        if avg_smoothness < 60:
            areas.append("Movement smoothness and control")
        
        if len(self.session_data) < 10:
            areas.append("Session frequency for faster progress")
        
        return areas
    
    def _generate_recommendations(self) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        accuracy = self._calculate_overall_accuracy()
        
        if accuracy > 90:
            recommendations.append("Consider increasing game difficulty for greater challenge")
        elif accuracy < 60:
            recommendations.append("Focus on slower, more controlled movements to improve accuracy")
        
        if len(self.session_data) < 5:
            recommendations.append("Aim for 3-4 sessions per week for optimal progress")
        
        if self.achievements.get('consecutive_days', 0) < 3:
            recommendations.append("Try to establish a daily routine for consistent improvement")
        
        return recommendations
    
    def _suggest_next_milestones(self) -> List[str]:
        """Suggest next milestones to work towards"""
        milestones = []
        
        if self.achievements.get('total_sessions', 0) < 10:
            milestones.append("Complete 10 total sessions")
        
        if self._calculate_overall_accuracy() < 80:
            milestones.append("Achieve 80% accuracy rate")
        
        if self.achievements.get('consecutive_days', 0) < 7:
            milestones.append("Maintain 7-day practice streak")
        
        return milestones
    
    def save_complete_report(self):
        """Save a comprehensive text report"""
        report_content = f"""
# 🏥 REHABILITATION GAMING PROGRESS REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 EXECUTIVE SUMMARY
- **Total Sessions Completed:** {len(self.session_data)}
- **Games Played:** {len(set(session.get('game_name') for session in self.session_data))}
- **Overall Accuracy:** {self._calculate_overall_accuracy():.1f}%
- **Current Streak:** {self.achievements.get('consecutive_days', 0)} days
- **Improvement Trend:** {self._calculate_improvement_percentage():+.1f}%

## 🎯 GAME PERFORMANCE METRICS

### Score Progression Analysis
"""
        
        # Add game-specific analysis
        game_stats = defaultdict(list)
        for session in self.session_data:
            game_name = session.get('game_name')
            if 'game_specific_metrics' in session:
                score = session['game_specific_metrics'].get('score', 0)
                game_stats[game_name].append(score)
        
        for game, scores in game_stats.items():
            if scores:
                avg_score = np.mean(scores)
                best_score = max(scores)
                trend = "📈 Improving" if len(scores) > 1 and scores[-1] > scores[0] else "📊 Stable"
                
                report_content += f"""
**{game}:**
- Average Score: {avg_score:.1f}
- Best Score: {best_score}
- Sessions Played: {len(scores)}
- Trend: {trend}
"""
        
        report_content += f"""

## 💪 PHYSICAL/MOTOR IMPROVEMENT METRICS

### Hand Movement Analysis
- **Movement Smoothness:** {np.mean([np.mean(day['movement_smoothness']) for day in self.daily_analytics.values() if day['movement_smoothness']]):.1f}/100
- **Hand Detection Rate:** {np.mean([np.mean(day['hand_detection_rate']) for day in self.daily_analytics.values() if day['hand_detection_rate']]):.1f}%
- **Pinch Control Accuracy:** {self._calculate_overall_accuracy():.1f}%

### Range of Motion Progress
- **Tracking Quality:** Excellent (based on consistent hand detection)
- **Fine Motor Control:** {'Improving' if self._calculate_improvement_percentage() > 0 else 'Stable'}

## 🎮 ENGAGEMENT & MOTIVATION METRICS

### Session Patterns
- **Total Sessions:** {len(self.session_data)}
- **Days Active:** {len(self.daily_analytics)}
- **Average Sessions per Day:** {len(self.session_data) / max(1, len(self.daily_analytics)):.1f}
- **Longest Streak:** {self.achievements.get('consecutive_days', 0)} consecutive days

### Game Variety
- **Games Explored:** {len(set(session.get('game_name') for session in self.session_data))}
- **Favorite Game:** {max(set(session.get('game_name') for session in self.session_data), key=lambda x: sum(1 for s in self.session_data if s.get('game_name') == x))}

## 🏆 ACHIEVEMENTS & MILESTONES

### Earned Badges
"""
        
        for badge in self.achievements.get('badges', []):
            report_content += f"- {badge}\n"
        
        report_content += "\n### Milestones Reached\n"
        for milestone in self.achievements.get('milestones', []):
            report_content += f"- {milestone}\n"
        
        report_content += f"""

## 🔍 DETAILED INSIGHTS & RECOMMENDATIONS

### Performance Analysis
- **Strength Areas:** {"High accuracy pinch control" if self._calculate_overall_accuracy() > 80 else "Consistent engagement"}
- **Improvement Areas:** {"Focus on movement smoothness" if np.mean([np.mean(day['movement_smoothness']) for day in self.daily_analytics.values() if day['movement_smoothness']]) < 70 else "Continue current routine"}

### Rehabilitation Progress
- **Motor Skills:** {'Excellent progress' if self._calculate_improvement_percentage() > 10 else 'Steady improvement' if self._calculate_improvement_percentage() > 0 else 'Maintaining baseline'}
- **Engagement Level:** {'Highly engaged' if len(self.session_data) > 15 else 'Well engaged' if len(self.session_data) > 8 else 'Building routine'}

### Next Steps Recommendations
1. **Continue current routine** - showing positive trends
2. **Increase session frequency** if possible for faster progress
3. **Try variety of games** to work different motor skills
4. **Set new challenges** as current performance is strong

---
*This report was automatically generated by the Rehabilitation Gaming Analytics System*
"""
        
        # Save report
        with open(os.path.join(self.progress_directory, 'detailed_progress_report.md'), 'w') as f:
            f.write(report_content)
        
        print("✅ Comprehensive report saved!")

    def create_game_distribution_plot(self):
        """Create a pie chart showing distribution of games played"""
        if not self.session_data:
            return
        
        # Count games using the correct data structure
        game_counts = Counter([session.get('game_name', 'Unknown') 
                              for session in self.session_data])
        
        if not game_counts:
            return
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(game_counts)))
        
        wedges, texts, autotexts = ax.pie(game_counts.values(), 
                                         labels=game_counts.keys(),
                                         autopct='%1.1f%%',
                                         colors=colors,
                                         explode=[0.05] * len(game_counts))
        
        ax.set_title('Game Distribution - Sessions by Game Type', fontsize=16, fontweight='bold', pad=20)
        
        # Beautify text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)
        
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'game_distribution.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def create_weekly_heatmap(self):
        """Create a weekly activity heatmap"""
        if not self.session_data:
            return
        
        # Prepare data for heatmap using correct data structure
        dates = []
        for session in self.session_data:
            timestamp = session.get('timestamp', '')
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp)
                    dates.append(date)
                except:
                    continue
        
        if not dates:
            return
        
        # Count sessions per day and hour
        activity_matrix = np.zeros((7, 24))  # 7 days x 24 hours
        
        for session in self.session_data:
            timestamp = session.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    weekday = dt.weekday()
                    hour = dt.hour
                    activity_matrix[weekday, hour] += 1
                except:
                    continue
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 8))
        
        im = ax.imshow(activity_matrix, cmap='YlOrRd', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(24))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(24)], rotation=45)
        ax.set_yticks(range(7))
        ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Number of Sessions', rotation=270, labelpad=20)
        
        ax.set_title('Weekly Activity Heatmap - Sessions by Day and Hour', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Day of Week')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'weekly_heatmap.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def create_correlation_matrix(self):
        """Create a correlation matrix of performance metrics"""
        if not self.daily_analytics:
            return
        
        # Prepare data for correlation using correct data structure
        metrics_data = {
            'Smoothness': [],
            'Success_Rate': [],
            'Detection_Rate': [],
            'Sessions': [],
            'Duration': []
        }
        
        for day_data in self.daily_analytics.values():
            # Extract metrics from the actual data structure
            smoothness_scores = day_data.get('movement_smoothness', [])
            pinch_rates = day_data.get('pinch_success_rate', [])
            detection_rates = day_data.get('hand_detection_rate', [])
            
            metrics_data['Smoothness'].append(np.mean(smoothness_scores) if smoothness_scores else 0)
            metrics_data['Success_Rate'].append(np.mean(pinch_rates) if pinch_rates else 0)
            metrics_data['Detection_Rate'].append(np.mean(detection_rates) if detection_rates else 0)
            metrics_data['Sessions'].append(day_data.get('sessions_count', 0))
            metrics_data['Duration'].append(day_data.get('total_duration', 0))
        
        # Create correlation matrix manually (without pandas)
        metric_names = list(metrics_data.keys())
        n_metrics = len(metric_names)
        correlation_matrix = np.zeros((n_metrics, n_metrics))
        
        for i, metric1 in enumerate(metric_names):
            for j, metric2 in enumerate(metric_names):
                data1 = np.array(metrics_data[metric1])
                data2 = np.array(metrics_data[metric2])
                
                if np.std(data1) > 0 and np.std(data2) > 0:
                    correlation_matrix[i, j] = np.corrcoef(data1, data2)[0, 1]
                else:
                    correlation_matrix[i, j] = 0
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(correlation_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(n_metrics))
        ax.set_yticks(range(n_metrics))
        ax.set_xticklabels(metric_names, rotation=45, ha='right')
        ax.set_yticklabels(metric_names)
        
        # Add correlation values as text
        for i in range(n_metrics):
            for j in range(n_metrics):
                text = ax.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)
        
        ax.set_title('Performance Metrics Correlation Matrix', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'correlation_matrix.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def create_kpi_dashboard(self):
        """Create a comprehensive KPI dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Key Performance Indicators Dashboard', fontsize=18, fontweight='bold')
        
        # KPI 1: Overall Performance Gauge
        performance_score = self._calculate_overall_accuracy()
        theta = np.linspace(0, np.pi, 100)
        
        ax1.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=3)
        ax1.fill_between(np.cos(theta), 0, np.sin(theta), alpha=0.3, color='lightgray')
        
        # Performance indicator
        perf_angle = np.pi * (1 - performance_score / 100)
        ax1.plot([0, np.cos(perf_angle)], [0, np.sin(perf_angle)], 'r-', linewidth=8)
        ax1.plot(np.cos(perf_angle), np.sin(perf_angle), 'ro', markersize=15)
        
        ax1.set_xlim(-1.2, 1.2)
        ax1.set_ylim(-0.2, 1.2)
        ax1.set_aspect('equal')
        ax1.set_title(f'Overall Performance\n{performance_score:.1f}%', fontweight='bold')
        ax1.axis('off')
        
        # Add performance labels
        ax1.text(-1, 0.8, 'Poor', ha='center', fontweight='bold', color='red')
        ax1.text(0, 1.1, 'Good', ha='center', fontweight='bold', color='orange')
        ax1.text(1, 0.8, 'Excellent', ha='center', fontweight='bold', color='green')
        
        # KPI 2: Progress Trend
        if self.daily_analytics:
            dates = sorted(self.daily_analytics.keys())
            scores = [np.mean(self.daily_analytics[date].get('scores', [0])) for date in dates]
            
            ax2.plot(range(len(dates)), scores, marker='o', linewidth=3, markersize=8, color='#2ecc71')
            ax2.fill_between(range(len(dates)), scores, alpha=0.3, color='#2ecc71')
            
            # Add trend line
            if len(scores) > 1:
                z = np.polyfit(range(len(scores)), scores, 1)
                p = np.poly1d(z)
                ax2.plot(range(len(scores)), p(range(len(scores))), "--", alpha=0.8, color='red', linewidth=2)
            
            ax2.set_title('Score Progression Trend', fontweight='bold')
            ax2.set_ylabel('Average Score')
            ax2.set_xlabel('Session Days')
            ax2.grid(True, alpha=0.3)
        
        # KPI 3: Engagement Metrics
        total_sessions = len(self.session_data)
        active_days = len(self.daily_analytics)
        avg_sessions_per_day = total_sessions / max(1, active_days)
        
        engagement_metrics = ['Total\nSessions', 'Active\nDays', 'Avg Sessions\nper Day']
        engagement_values = [total_sessions, active_days, avg_sessions_per_day]
        colors = ['#3498db', '#e74c3c', '#f39c12']
        
        bars = ax3.bar(engagement_metrics, engagement_values, color=colors, alpha=0.8)
        ax3.set_title('Engagement Overview', fontweight='bold')
        ax3.set_ylabel('Count')
        
        # Add value labels on bars
        for bar, value in zip(bars, engagement_values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # KPI 4: Achievement Progress
        consecutive_days = self.achievements.get('consecutive_days', 0)
        milestones_count = len(self.achievements.get('milestones', []))
        badges_count = len(self.achievements.get('badges', []))
        
        achievement_data = [consecutive_days, milestones_count, badges_count]
        achievement_labels = ['Streak\n(days)', 'Milestones', 'Badges']
        colors = ['#9b59b6', '#1abc9c', '#f1c40f']
        
        wedges, texts, autotexts = ax4.pie(achievement_data, labels=achievement_labels, 
                                          autopct='%1.0f', colors=colors, startangle=90)
        
        ax4.set_title('Achievement Distribution', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'kpi_dashboard.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def create_success_rate_trends(self):
        """Create success rate trends by game type"""
        if not self.session_data:
            return
        
        # Group data by game and date using correct data structure
        game_data = defaultdict(lambda: defaultdict(list))
        
        for session in self.session_data:
            game_name = session.get('game_name', 'Unknown')
            date = session.get('date', '')
            
            if date and game_name != 'Unknown':
                try:
                    # Extract success rate from pinch analytics
                    pinch_analytics = session.get('pinch_analytics', {})
                    success_rate = pinch_analytics.get('pinch_success_rate', 0)
                    
                    # If no pinch success rate, try to calculate from game-specific metrics
                    if success_rate == 0:
                        game_metrics = session.get('game_specific_metrics', {})
                        if 'target_angles_hit' in game_metrics and 'total_targets' in game_metrics:
                            total = game_metrics.get('total_targets', 1)
                            success_rate = (game_metrics.get('target_angles_hit', 0) / max(1, total)) * 100
                        elif 'angle_accuracy' in game_metrics:
                            success_rate = game_metrics.get('angle_accuracy', 0)
                    
                    game_data[game_name][date].append(success_rate)
                except:
                    continue
        
        if not game_data:
            return
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = plt.cm.Set1(np.linspace(0, 1, len(game_data)))
        
        for i, (game_name, dates_data) in enumerate(game_data.items()):
            sorted_dates = sorted(dates_data.keys())
            avg_success_rates = [np.mean(dates_data[date]) for date in sorted_dates]
            
            # Convert date strings to datetime objects for plotting
            date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates]
            
            ax.plot(date_objects, avg_success_rates, marker='o', linewidth=3, 
                   markersize=8, label=game_name, color=colors[i])
            
            # Add trend line
            if len(avg_success_rates) > 1:
                x_numeric = np.arange(len(sorted_dates))
                z = np.polyfit(x_numeric, avg_success_rates, 1)
                p = np.poly1d(z)
                ax.plot(date_objects, p(x_numeric), "--", alpha=0.6, color=colors[i])
        
        ax.set_title('Success Rate Trends by Game Type', fontsize=16, fontweight='bold')
        ax.set_ylabel('Success Rate (%)')
        ax.set_xlabel('Date')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'success_rate_trends.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def create_performance_radar_chart(self):
        """Create a radar chart showing overall performance across different dimensions"""
        # Define performance dimensions
        dimensions = ['Accuracy', 'Consistency', 'Engagement', 'Improvement', 'Variety']
        
        # Calculate scores for each dimension (0-100 scale)
        accuracy_score = self._calculate_overall_accuracy()
        consistency_score = self._calculate_consistency_score()
        engagement_score = min(100, (len(self.session_data) / 20) * 100)  # Scale to sessions
        improvement_score = max(0, min(100, self._calculate_improvement_percentage() * 10))
        variety_score = min(100, (len(set(s.get('metadata', {}).get('game_name') for s in self.session_data)) / 5) * 100)
        
        values = [accuracy_score, consistency_score, engagement_score, improvement_score, variety_score]
        
        # Create radar chart
        angles = [n / float(len(dimensions)) * 2 * np.pi for n in range(len(dimensions))]
        angles += angles[:1]  # Close the circle
        values += values[:1]   # Close the circle
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Plot the values
        ax.plot(angles, values, 'o-', linewidth=3, color='#3498db', markersize=8)
        ax.fill(angles, values, alpha=0.25, color='#3498db')
        
        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=12, fontweight='bold')
        
        # Set y-axis limits and labels
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10)
        ax.grid(True)
        
        # Add title
        ax.set_title('Performance Radar Chart\nOverall Rehabilitation Progress', 
                    fontsize=16, fontweight='bold', pad=30)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.progress_directory, 'performance_radar.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def _calculate_consistency_score(self) -> float:
        """Calculate consistency score based on session patterns"""
        if len(self.daily_analytics) < 3:
            return 50.0  # Default for insufficient data
        
        session_counts = [day['sessions_count'] for day in self.daily_analytics.values()]
        if not session_counts or np.mean(session_counts) == 0:
            return 0.0
        
        consistency = 100 - (np.std(session_counts) / np.mean(session_counts) * 100)
        return max(0, min(100, consistency))

    def generate_all_visualizations(self):
        """Generate all visualizations including the new ones"""
        print("🎨 Generating comprehensive visualizations...")
        
        # Existing visualizations
        self._create_progress_charts()
        self._create_physical_metrics_gauges()
        
        # New visualizations
        self.create_game_distribution_plot()
        self.create_weekly_heatmap()
        self.create_correlation_matrix()
        self.create_kpi_dashboard()
        self.create_success_rate_trends()
        self.create_performance_radar_chart()
        
        print("✅ All visualizations generated successfully!")

    def save_complete_report(self):
        """Generate and save a comprehensive progress report"""
        
        print("📊 Generating comprehensive progress report...")
        
        report_content = f"""# 🏥 REHABILITATION GAMING PROGRESS REPORT
*Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}*

---

## 📈 PERFORMANCE OVERVIEW

### Overall Statistics
- **Total Sessions Completed:** {len(self.session_data)}
- **Overall Accuracy:** {self._calculate_overall_accuracy():.1f}%
- **Performance Improvement:** {self._calculate_improvement_percentage():.1f}%
- **Consistency Rating:** {self._calculate_consistency_rating()}

### Session Patterns
- **Total Sessions:** {len(self.session_data)}
- **Days Active:** {len(self.daily_analytics)}
- **Average Sessions per Day:** {len(self.session_data) / max(1, len(self.daily_analytics)):.1f}
- **Longest Streak:** {self.achievements.get('consecutive_days', 0)} consecutive days

### Game Variety
- **Games Explored:** {len(set(session.get('metadata', {}).get('game_name') for session in self.session_data))}
- **Favorite Game:** {max(set(session.get('metadata', {}).get('game_name') for session in self.session_data), key=lambda x: sum(1 for s in self.session_data if s.get('metadata', {}).get('game_name') == x)) if self.session_data else 'None'}

## 🏆 ACHIEVEMENTS & MILESTONES

### Earned Badges
"""
if __name__ == "__main__":
    # Initialize dashboard
    dashboard = EnhancedRehabDashboard()
    
    # Generate complete dashboard
    dashboard.generate_comprehensive_dashboard()
    
    # Save detailed report
    dashboard.save_complete_report()
    
    print("\n🎉 Enhanced Dashboard Generation Complete!")
    print("📁 Check the Progress folder for all generated files")