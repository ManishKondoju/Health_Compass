import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter

class SymptomTracker:
    """Simple symptom tracker with AI-powered pattern insights"""
    
    def __init__(self, data_dir="data/symptoms"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.symptoms_file = self.data_dir / "symptom_log.json"
    
    def log_symptom(self, symptom_description, severity, notes=""):
        """Log a symptom entry"""
        symptoms = self.get_all_symptoms()
        
        now = datetime.now()
        
        entry = {
            'id': now.strftime("%Y%m%d%H%M%S"),
            'timestamp': now.isoformat(),
            'date_display': now.strftime("%Y-%m-%d %H:%M"),
            'symptom': symptom_description,
            'severity': int(severity),
            'notes': notes,
            'day_of_week': now.strftime("%A"),
            'time_of_day': self._get_time_period(now),
            'hour': now.hour
        }
        
        symptoms.append(entry)
        
        with open(self.symptoms_file, 'w') as f:
            json.dump(symptoms, f, indent=2)
        
        return entry
    
    def get_all_symptoms(self):
        """Get all symptom entries"""
        try:
            with open(self.symptoms_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _get_time_period(self, dt):
        """Categorize time of day"""
        hour = dt.hour
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"
    
    def get_ai_insights(self):
        """Generate AI-ready insights from symptom data"""
        symptoms = self.get_all_symptoms()
        
        if len(symptoms) < 3:
            return None
        
        df = pd.DataFrame(symptoms)
        
        # Day of week analysis
        day_pattern = df['day_of_week'].value_counts().to_dict()
        most_common_day = df['day_of_week'].value_counts().index[0]
        
        # Time of day analysis
        time_pattern = df['time_of_day'].value_counts().to_dict()
        most_common_time = df['time_of_day'].value_counts().index[0]
        
        # Severity analysis
        avg_severity = df['severity'].mean()
        max_severity = df['severity'].max()
        
        # Trend analysis
        recent_3 = df.tail(3)['severity'].mean()
        older_3 = df.head(3)['severity'].mean() if len(df) >= 6 else avg_severity
        
        if recent_3 > older_3 + 1.5:
            trend = "worsening"
        elif recent_3 < older_3 - 1.5:
            trend = "improving"
        else:
            trend = "stable"
        
        # Symptom frequency
        symptom_counts = df['symptom'].value_counts().to_dict()
        most_common_symptom = df['symptom'].value_counts().index[0]
        
        # Weekend vs weekday
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        weekday_count = len(df[df['day_of_week'].isin(weekdays)])
        weekend_count = len(df[~df['day_of_week'].isin(weekdays)])
        
        insights = {
            'total_entries': len(symptoms),
            'date_range': f"{symptoms[0]['date_display'].split()[0]} to {symptoms[-1]['date_display'].split()[0]}",
            'most_common_symptom': most_common_symptom,
            'symptom_frequency': symptom_counts,
            'average_severity': round(avg_severity, 1),
            'max_severity': int(max_severity),
            'trend': trend,
            'day_pattern': day_pattern,
            'most_common_day': most_common_day,
            'time_pattern': time_pattern,
            'most_common_time': most_common_time,
            'weekday_vs_weekend': {
                'weekday': weekday_count,
                'weekend': weekend_count,
                'pattern': 'weekday-dominant' if weekday_count > weekend_count * 1.5 else 'weekend-dominant' if weekend_count > weekday_count * 1.5 else 'no-pattern'
            }
        }
        
        return insights
    
    def generate_insight_text(self):
        """Generate human-readable insight text for AI"""
        insights = self.get_ai_insights()
        
        if not insights:
            return "Not enough data for insights (need at least 3 entries)"
        
        text = f"""Symptom Tracking Analysis:

Total entries: {insights['total_entries']}
Period: {insights['date_range']}
Most common symptom: {insights['most_common_symptom']}
Average severity: {insights['average_severity']}/10
Maximum severity: {insights['max_severity']}/10
Trend: {insights['trend']}

PATTERNS DETECTED:

Time Patterns:
- Most symptoms occur on {insights['most_common_day']}s
- Most symptoms occur in the {insights['most_common_time']}
- Weekday occurrences: {insights['weekday_vs_weekend']['weekday']}
- Weekend occurrences: {insights['weekday_vs_weekend']['weekend']}
- Pattern: {insights['weekday_vs_weekend']['pattern']}

Day-by-day breakdown:
"""
        
        for day, count in sorted(insights['day_pattern'].items(), key=lambda x: x[1], reverse=True):
            text += f"- {day}: {count} times\n"
        
        return text
    
    def delete_entry(self, entry_id):
        """Delete a symptom entry"""
        symptoms = self.get_all_symptoms()
        symptoms = [s for s in symptoms if s['id'] != entry_id]
        
        with open(self.symptoms_file, 'w') as f:
            json.dump(symptoms, f, indent=2)