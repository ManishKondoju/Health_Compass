import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from collections import Counter

class SmartHealthJournal:
    """Intelligent health journal with AI-powered insights"""
    
    def __init__(self, journal_dir="data/journal"):
        self.journal_dir = Path(journal_dir)
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self.journal_file = self.journal_dir / "smart_entries.json"
    
    def add_entry(self, symptoms, severity, triggers=None, relievers=None, 
                  treatments=None, treatment_effectiveness=None, notes=""):
        """Add comprehensive health entry"""
        entries = self.get_entries()
        
        entry = {
            'id': datetime.now().strftime("%Y%m%d%H%M%S"),
            'date': datetime.now().isoformat(),
            'date_display': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'symptoms': symptoms,
            'severity': int(severity),
            'triggers': triggers or [],
            'relievers': relievers or [],
            'treatments': treatments or [],
            'treatment_effectiveness': treatment_effectiveness,
            'notes': notes,
            'day_of_week': datetime.now().strftime("%A"),
            'time_of_day': self._get_time_period()
        }
        
        entries.append(entry)
        
        with open(self.journal_file, 'w') as f:
            json.dump(entries, f, indent=2)
        
        # Auto-analyze if enough entries
        insights = None
        if len(entries) >= 5:
            insights = self.analyze_patterns()
        
        return entry, insights
    
    def _get_time_period(self):
        """Categorize time of day"""
        hour = datetime.now().hour
        if hour < 6:
            return "Night"
        elif hour < 12:
            return "Morning"
        elif hour < 18:
            return "Afternoon"
        else:
            return "Evening"
    
    def get_entries(self):
        """Get all journal entries"""
        try:
            with open(self.journal_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def analyze_patterns(self):
        """Comprehensive pattern analysis"""
        entries = self.get_entries()
        
        if not entries:
            return None
        
        df = pd.DataFrame(entries)
        
        patterns = {
            'total_entries': len(entries),
            'date_range': self._get_date_range(entries),
            'most_common_symptom': df['symptoms'].value_counts().index[0] if len(df) > 0 else "N/A",
            'average_severity': round(df['severity'].mean(), 1) if len(df) > 0 else 0,
            'max_severity': int(df['severity'].max()) if len(df) > 0 else 0,
            'trend': self._calculate_trend(df),
            'day_pattern': df['day_of_week'].value_counts().to_dict() if 'day_of_week' in df.columns else {},
            'time_pattern': df['time_of_day'].value_counts().to_dict() if 'time_of_day' in df.columns else {},
            'trigger_analysis': self._analyze_triggers(entries),
            'severity_distribution': df['severity'].value_counts().to_dict(),
            'concerning_episodes': len(df[df['severity'] >= 7]) if len(df) > 0 else 0
        }
        
        return patterns
    
    def _get_date_range(self, entries):
        """Get readable date range"""
        if not entries:
            return "No data"
        
        first = datetime.fromisoformat(entries[0]['date']).strftime("%b %d, %Y")
        last = datetime.fromisoformat(entries[-1]['date']).strftime("%b %d, %Y")
        
        return f"{first} to {last}"
    
    def _calculate_trend(self, df):
        """Calculate trend direction"""
        if len(df) < 3:
            return "Not enough data"
        
        recent_3 = df.tail(3)['severity'].mean()
        older_3 = df.head(3)['severity'].mean()
        
        diff = recent_3 - older_3
        
        if diff > 1.5:
            return "⚠️ Worsening"
        elif diff < -1.5:
            return "✅ Improving"
        else:
            return "➡️ Stable"
    
    def _analyze_triggers(self, entries):
        """Find common triggers"""
        all_triggers = []
        for entry in entries:
            if entry.get('triggers'):
                all_triggers.extend(entry['triggers'])
        
        if not all_triggers:
            return "No triggers recorded"
        
        trigger_counts = Counter(all_triggers)
        return dict(trigger_counts.most_common(5))
    
    def export_for_doctor(self):
        """Export for doctor visit"""
        entries = self.get_entries()
        
        text = "HEALTH JOURNAL SUMMARY\n"
        text += "="*60 + "\n\n"
        
        for entry in entries:
            text += f"Date: {entry['date_display']}\n"
            text += f"Symptoms: {entry['symptoms']}\n"
            text += f"Severity: {entry['severity']}/10\n"
            
            if entry.get('triggers'):
                text += f"Triggers: {', '.join(entry['triggers'])}\n"
            if entry.get('relievers'):
                text += f"What helped: {', '.join(entry['relievers'])}\n"
            if entry.get('treatments'):
                text += f"Treatments: {', '.join(entry['treatments'])}\n"
            if entry.get('treatment_effectiveness'):
                text += f"Effectiveness: {entry['treatment_effectiveness']}\n"
            if entry.get('notes'):
                text += f"Notes: {entry['notes']}\n"
            
            text += "-"*60 + "\n\n"
        
        patterns = self.analyze_patterns()
        if patterns:
            text += "\nPATTERN ANALYSIS\n"
            text += "="*60 + "\n"
            text += f"Total: {patterns['total_entries']}\n"
            text += f"Most common: {patterns['most_common_symptom']}\n"
            text += f"Avg severity: {patterns['average_severity']}/10\n"
            text += f"Trend: {patterns['trend']}\n"
        
        return text
    
    def get_risk_score(self):
        """Calculate health risk score"""
        entries = self.get_entries()
        
        if len(entries) < 3:
            return None
        
        df = pd.DataFrame(entries)
        
        recent_severity = df.tail(5)['severity'].mean()
        high_count = len(df[df['severity'] >= 7])
        
        if len(df) >= 5:
            recent = df.tail(3)['severity'].mean()
            older = df.head(3)['severity'].mean()
            worsening = recent > older + 1
        else:
            worsening = False
        
        score = 0
        factors = []
        
        if recent_severity >= 6:
            score += 3
            factors.append("High recent severity")
        
        if high_count >= 3:
            score += 2
            factors.append(f"{high_count} severe episodes")
        
        if worsening:
            score += 2
            factors.append("Worsening trend")
        
        if score >= 5:
            level, color, action = "HIGH", "🔴", "Medical consultation within 1 week"
        elif score >= 3:
            level, color, action = "MODERATE", "🟡", "Appointment within 2-4 weeks"
        else:
            level, color, action = "LOW", "🟢", "Continue monitoring"
        
        return {
            'score': score,
            'level': level,
            'color': color,
            'factors': factors,
            'action': action
        }
    
    def delete_entry(self, entry_id):
        """Delete entry by ID"""
        entries = self.get_entries()
        entries = [e for e in entries if e['id'] != entry_id]
        
        with open(self.journal_file, 'w') as f:
            json.dump(entries, f, indent=2)
    
    def generate_insights(self):
        """Alias for analyze_patterns"""
        return self.analyze_patterns()