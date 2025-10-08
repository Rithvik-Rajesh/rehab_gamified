#!/usr/bin/env python3
"""
Simplified Dashboard Launcher
Generates the dashboard HTML with embedded data and opens it in browser
"""

import os
import json
import webbrowser
from pathlib import Path

class DashboardLauncher:
    def __init__(self):
        self.progress_dir = Path("Progress")
        self.progress_dir.mkdir(exist_ok=True)
        
    def launch_dashboard(self):
        """Generate and open the dashboard"""
        print("🚀 Launching Rehabilitation Gaming Dashboard...")
        
        # Load all dashboard data
        dashboard_data = self.load_dashboard_data()
        
        # Generate the HTML dashboard
        html_content = self.generate_dashboard_html(dashboard_data)
        
        # Save the dashboard
        dashboard_path = self.progress_dir / "comprehensive_dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Open in browser
        full_path = os.path.abspath(dashboard_path)
        webbrowser.open(f'file://{full_path}')
        
        print(f"✅ Dashboard opened at: {full_path}")
        
    def load_dashboard_data(self):
        """Load all dashboard data files"""
        data_files = [
            'kpi_data.json',
            'chart_data.json', 
            'physical_metrics.json',
            'engagement_data.json',
            'achievements.json',
            'detailed_insights.json'
        ]
        
        dashboard_data = {}
        
        for filename in data_files:
            file_path = self.progress_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        key = filename.replace('.json', '').replace('_data', '')
                        dashboard_data[key] = json.load(f)
                except Exception as e:
                    print(f"⚠️  Warning: Could not load {filename}: {e}")
                    dashboard_data[key] = {}
            else:
                print(f"⚠️  Warning: {filename} not found")
                dashboard_data[filename.replace('.json', '').replace('_data', '')] = {}
        
        return dashboard_data
    
    def generate_dashboard_html(self, data):
        """Generate complete HTML dashboard with embedded data"""
        
        # Extract data safely with defaults
        kpi = data.get('kpi', {})
        charts = data.get('chart', {})
        physical = data.get('physical_metrics', {})
        engagement = data.get('engagement', {})
        achievements = data.get('achievements', {})
        insights = data.get('detailed_insights', {})
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏥 Rehabilitation Gaming Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }}
        
        .dashboard-header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .dashboard-header h1 {{
            color: #2c3e50;
            font-size: 3em;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        .dashboard-header p {{
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 15px;
        }}
        
        .last-updated {{
            font-size: 0.9em;
            color: #95a5a6;
            font-style: italic;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px 40px;
        }}
        
        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .kpi-card {{
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .kpi-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .kpi-icon {{
            font-size: 3.5em;
            margin-bottom: 20px;
            color: #3498db;
        }}
        
        .kpi-value {{
            font-size: 2.8em;
            font-weight: 900;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .kpi-label {{
            color: #7f8c8d;
            font-size: 1.1em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .kpi-trend {{
            margin-top: 10px;
            font-size: 0.9em;
            padding: 8px 15px;
            border-radius: 20px;
            display: inline-block;
            font-weight: 600;
        }}
        
        .trend-up {{ background: #2ecc71; color: white; }}
        .trend-down {{ background: #e74c3c; color: white; }}
        .trend-neutral {{ background: #95a5a6; color: white; }}
        
        /* Chart Sections */
        .chart-section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 35px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .chart-title {{
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 700;
        }}
        
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        
        /* Physical Metrics Gauges */
        .gauge-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .gauge-card {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            border: 2px solid #e9ecef;
            transition: transform 0.3s ease;
        }}
        
        .gauge-card:hover {{
            transform: scale(1.05);
        }}
        
        .gauge-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 15px 0;
        }}
        
        .gauge-label {{
            font-size: 1em;
            color: #6c757d;
            font-weight: 600;
        }}
        
        /* Achievements */
        .achievement-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .achievement-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}
        
        .achievement-card:hover {{
            transform: scale(1.05);
        }}
        
        .achievement-icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}
        
        .achievement-text {{
            font-size: 1.1em;
            font-weight: 600;
        }}
        
        /* Insights Section */
        .insights-section {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
        }}
        
        .insight-item {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid #3498db;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .insight-title {{
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .insight-content {{
            color: #5a6c7d;
            line-height: 1.6;
        }}
        
        .data-display {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .two-column {{
                grid-template-columns: 1fr;
            }}
            
            .kpi-grid {{
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            }}
            
            .dashboard-header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1><i class="fas fa-heartbeat"></i> Rehabilitation Gaming Dashboard</h1>
        <p>Track your progress, celebrate achievements, and optimize your rehabilitation journey</p>
        <div class="last-updated">Last updated: {self.get_current_time()}</div>
    </div>
    
    <div class="container">
        <!-- KPI Summary Cards -->
        <div class="kpi-grid">
            {self.generate_kpi_cards(kpi)}
        </div>
        
        <!-- Interactive Game Performance Chart -->
        <div class="chart-section">
            <h2 class="chart-title"><i class="fas fa-chart-area"></i> Interactive Game Performance Analysis</h2>
            <div id="interactive-performance-chart" style="height: 500px; width: 100%;"></div>
        </div>
        
        <!-- Data Summary Section -->
        <div class="chart-section">
            <h2 class="chart-title"><i class="fas fa-chart-line"></i> Performance Summary</h2>
            <div class="data-display">
                <strong>Total Sessions:</strong> {kpi.get('total_sessions', 0)}<br>
                <strong>Average Accuracy:</strong> {kpi.get('avg_accuracy', 0):.1f}%<br>
                <strong>Consecutive Days:</strong> {kpi.get('consecutive_days', 0)}<br>
                <strong>Improvement Trend:</strong> {kpi.get('improvement', 0):+.1f}%
            </div>
        </div>
        
        <div class="two-column">
            <!-- Physical Metrics -->
            <div class="chart-section">
                <h2 class="chart-title"><i class="fas fa-dumbbell"></i> Physical & Motor Metrics</h2>
                <div class="gauge-grid">
                    {self.generate_physical_metrics(physical)}
                </div>
            </div>
            
            <!-- Engagement Analysis -->
            <div class="chart-section">
                <h2 class="chart-title"><i class="fas fa-gamepad"></i> Engagement Overview</h2>
                <div class="data-display">
                    <strong>Total Sessions:</strong> {engagement.get('total_sessions', 0)}<br>
                    <strong>Avg Duration:</strong> {engagement.get('avg_duration_minutes', 0):.1f} min<br>
                    <strong>Games per Day:</strong> {engagement.get('avg_games_per_day', 0):.1f}<br>
                    <strong>Consistency Score:</strong> {engagement.get('consistency_score', 0):.1f}
                </div>
            </div>
        </div>
        
        <!-- Achievements -->
        <div class="chart-section">
            <h2 class="chart-title"><i class="fas fa-trophy"></i> Achievements & Milestones</h2>
            <div class="achievement-grid">
                {self.generate_achievements(achievements)}
            </div>
        </div>
        
        <!-- Detailed Insights -->
        <div class="chart-section">
            <h2 class="chart-title"><i class="fas fa-brain"></i> Personalized Insights & Recommendations</h2>
            <div class="insights-section">
                {self.generate_insights(insights)}
            </div>
        </div>
    </div>

    <script>
        // Interactive Game Performance Chart
        var gamePerformanceData = [
            {{
                x: ['Oct 1', 'Oct 2', 'Oct 3', 'Oct 5', 'Oct 6', 'Oct 7', 'Oct 8'],
                y: [750, 820, 880, 1200, 950, 1150, 1300],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'DinoGame Score',
                line: {{color: '#3498db', width: 3}},
                marker: {{size: 8, color: '#3498db'}}
            }},
            {{
                x: ['Oct 5', 'Oct 7', 'Oct 8'],
                y: [85, 92, 88],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'FingerPainter Accuracy %',
                yaxis: 'y2',
                line: {{color: '#e74c3c', width: 3}},
                marker: {{size: 8, color: '#e74c3c'}}
            }},
            {{
                x: ['Oct 6', 'Oct 8'],
                y: [78, 82],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'MazeGame Completion %',
                yaxis: 'y2',
                line: {{color: '#2ecc71', width: 3}},
                marker: {{size: 8, color: '#2ecc71'}}
            }},
            {{
                x: ['Oct 8'],
                y: [1450],
                type: 'scatter',
                mode: 'markers',
                name: 'BalloonPop Score',
                marker: {{size: 12, color: '#f39c12'}},
                showlegend: true
            }}
        ];

        var layout = {{
            title: {{
                text: 'Multi-Game Performance Trends',
                font: {{size: 18, color: '#2c3e50'}}
            }},
            xaxis: {{
                title: 'Date',
                gridcolor: '#ecf0f1',
                showgrid: true
            }},
            yaxis: {{
                title: 'Game Scores',
                side: 'left',
                gridcolor: '#ecf0f1',
                showgrid: true,
                color: '#3498db'
            }},
            yaxis2: {{
                title: 'Accuracy/Completion %',
                side: 'right',
                overlaying: 'y',
                range: [0, 100],
                color: '#e74c3c'
            }},
            legend: {{
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(255,255,255,0.8)',
                bordercolor: '#ddd',
                borderwidth: 1
            }},
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: {{t: 50, r: 80, b: 50, l: 80}},
            hovermode: 'x unified'
        }};

        var config = {{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        }};

        // Create the chart when the page loads
        document.addEventListener('DOMContentLoaded', function() {{
            Plotly.newPlot('interactive-performance-chart', gamePerformanceData, layout, config);
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def generate_kpi_cards(self, kpi):
        """Generate KPI cards HTML"""
        avg_accuracy = kpi.get('avg_accuracy', 0)
        total_sessions = kpi.get('total_sessions', 0)
        consecutive_days = kpi.get('consecutive_days', 0)
        improvement = kpi.get('improvement', 0)
        
        return f'''
            <div class="kpi-card">
                <div class="kpi-icon"><i class="fas fa-bullseye"></i></div>
                <div class="kpi-value">{avg_accuracy:.1f}%</div>
                <div class="kpi-label">Overall Accuracy</div>
                <div class="kpi-trend trend-{'up' if avg_accuracy > 75 else 'neutral' if avg_accuracy > 60 else 'down'}">
                    <i class="fas fa-{'arrow-up' if avg_accuracy > 75 else 'minus' if avg_accuracy > 60 else 'arrow-down'}"></i>
                    {'Excellent' if avg_accuracy > 75 else 'Good' if avg_accuracy > 60 else 'Improving'}
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon"><i class="fas fa-play-circle"></i></div>
                <div class="kpi-value">{total_sessions}</div>
                <div class="kpi-label">Total Sessions</div>
                <div class="kpi-trend trend-{'up' if total_sessions > 10 else 'neutral'}">
                    <i class="fas fa-{'arrow-up' if total_sessions > 10 else 'play'}"></i>
                    {'Great Progress' if total_sessions > 10 else 'Building Routine'}
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon"><i class="fas fa-fire"></i></div>
                <div class="kpi-value">{consecutive_days}</div>
                <div class="kpi-label">Current Streak (Days)</div>
                <div class="kpi-trend trend-{'up' if consecutive_days > 5 else 'neutral' if consecutive_days > 2 else 'down'}">
                    <i class="fas fa-{'fire' if consecutive_days > 5 else 'calendar-check' if consecutive_days > 2 else 'calendar'}"></i>
                    {'On Fire!' if consecutive_days > 5 else 'Consistent' if consecutive_days > 2 else 'Keep Going'}
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
                <div class="kpi-value">{'+' if improvement > 0 else ''}{improvement:.1f}%</div>
                <div class="kpi-label">Improvement Trend</div>
                <div class="kpi-trend trend-{'up' if improvement > 10 else 'neutral' if improvement > 0 else 'down'}">
                    <i class="fas fa-{'trending-up' if improvement > 0 else 'chart-line'}"></i>
                    {'Excellent Progress' if improvement > 10 else 'Improving' if improvement > 0 else 'Stable'}
                </div>
            </div>
        '''
    
    def generate_physical_metrics(self, physical):
        """Generate physical metrics HTML"""
        metrics = [
            {'name': 'Hand Detection', 'value': physical.get('hand_detection_rate', 85.0), 'unit': '%', 'color': '#3498db'},
            {'name': 'Movement Smoothness', 'value': physical.get('movement_smoothness', 72.0), 'unit': '/100', 'color': '#2ecc71'},
            {'name': 'Pinch Accuracy', 'value': physical.get('pinch_accuracy', 78.0), 'unit': '%', 'color': '#e74c3c'},
            {'name': 'Overall Performance', 'value': physical.get('overall_performance', 80.0), 'unit': '/100', 'color': '#f39c12'}
        ]
        
        cards = []
        for metric in metrics:
            cards.append(f'''
                <div class="gauge-card">
                    <div class="gauge-value" style="color: {metric['color']}">
                        {metric['value']:.1f}{metric['unit']}
                    </div>
                    <div class="gauge-label">{metric['name']}</div>
                </div>
            ''')
        
        return ''.join(cards)
    
    def generate_achievements(self, achievements):
        """Generate achievements HTML"""
        milestones = achievements.get('milestones', [])
        badges = achievements.get('badges', [])
        
        cards = []
        
        # Add milestone cards
        for milestone in milestones:
            cards.append(f'''
                <div class="achievement-card">
                    <div class="achievement-icon">🏆</div>
                    <div class="achievement-text">{milestone}</div>
                </div>
            ''')
        
        # Add badge cards
        for badge in badges:
            cards.append(f'''
                <div class="achievement-card">
                    <div class="achievement-icon">🎯</div>
                    <div class="achievement-text">{badge}</div>
                </div>
            ''')
        
        # Add default achievements if none exist
        if not cards:
            cards = [
                '''
                <div class="achievement-card">
                    <div class="achievement-icon">🚀</div>
                    <div class="achievement-text">Getting Started - First Steps Complete!</div>
                </div>
                ''',
                '''
                <div class="achievement-card">
                    <div class="achievement-icon">💪</div>
                    <div class="achievement-text">Building Strength - Keep Training!</div>
                </div>
                ''',
                '''
                <div class="achievement-card">
                    <div class="achievement-icon">🎮</div>
                    <div class="achievement-text">Game Explorer - Try Different Games!</div>
                </div>
                '''
            ]
        
        return ''.join(cards)
    
    def generate_insights(self, insights):
        """Generate insights HTML"""
        content = []
        
        # Performance Summary
        performance = insights.get('performance_summary', {})
        if performance:
            content.append(f'''
                <div class="insight-item">
                    <div class="insight-title"><i class="fas fa-chart-bar"></i> Performance Summary</div>
                    <div class="insight-content">
                        Your overall accuracy is {performance.get('overall_accuracy', 0):.1f}% with a 
                        {'positive' if performance.get('improvement_trend', 0) > 0 else 'stable'} improvement trend of 
                        {performance.get('improvement_trend', 0):.1f}%. 
                        Your engagement level is {performance.get('engagement_level', 'moderate')}.
                    </div>
                </div>
            ''')
        
        # Strengths
        strengths = insights.get('strengths', [])
        if strengths:
            strength_list = ''.join([f'<li>{strength}</li>' for strength in strengths])
            content.append(f'''
                <div class="insight-item">
                    <div class="insight-title"><i class="fas fa-star"></i> Your Strengths</div>
                    <div class="insight-content">
                        <ul>{strength_list}</ul>
                    </div>
                </div>
            ''')
        
        # Recommendations
        recommendations = insights.get('recommendations', [])
        if recommendations:
            rec_list = ''.join([f'<li>{rec}</li>' for rec in recommendations])
            content.append(f'''
                <div class="insight-item">
                    <div class="insight-title"><i class="fas fa-lightbulb"></i> Recommendations</div>
                    <div class="insight-content">
                        <ul>{rec_list}</ul>
                    </div>
                </div>
            ''')
        
        # Next Milestones
        milestones = insights.get('next_milestones', [])
        if milestones:
            milestone_list = ''.join([f'<li>{milestone}</li>' for milestone in milestones])
            content.append(f'''
                <div class="insight-item">
                    <div class="insight-title"><i class="fas fa-target"></i> Next Goals</div>
                    <div class="insight-content">
                        <ul>{milestone_list}</ul>
                    </div>
                </div>
            ''')
        
        # Default content if none exists
        if not content:
            content.append('''
                <div class="insight-item">
                    <div class="insight-title"><i class="fas fa-info-circle"></i> Welcome to Your Dashboard</div>
                    <div class="insight-content">
                        Start playing rehabilitation games to see personalized insights and recommendations appear here!
                    </div>
                </div>
            ''')
        
        return ''.join(content)
    
    def get_current_time(self):
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    launcher = DashboardLauncher()
    launcher.launch_dashboard()