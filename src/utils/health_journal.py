import json
from pathlib import Path
from datetime import datetime
import pandas as pd

class HealthJournal:
    """Personal health journal with pattern analysis"""
    
    def __init__(self, journal_dir="data/journal"):
        self.journal_dir = Path(journal_dir)
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self.journal_file = self.journal_dir / "entries.json"
    
    def add_entry(self, symptoms, severity, notes):
        """Add a new journal entry"""
        entry = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "symptoms": symptoms,
            "severity": int(severity),
            "notes": notes
        }
        
        # Load existing entries
        entries = self.get_entries()
        entries.append(entry)
        
        # Save
        with open(self.journal_file, 'w') as f:
            json.dump(entries, f, indent=2)
        
        return entry
    
    def get_entries(self):
        """Get all journal entries"""
        try:
            with open(self.journal_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def delete_entry(self, entry_id):
        """Delete a journal entry"""
        entries = self.get_entries()
        entries = [e for e in entries if e['id'] != entry_id]
        
        with open(self.journal_file, 'w') as f:
            json.dump(entries, f, indent=2)
    
    def analyze_patterns(self):
        """Analyze health patterns"""
        entries = self.get_entries()
        
        if not entries:
            return None
        
        df = pd.DataFrame(entries)
        
        # Calculate patterns
        patterns = {
            "total_entries": len(entries),
            "most_common_symptom": df['symptoms'].value_counts().index[0] if len(df) > 0 else "N/A",
            "average_severity": round(df['severity'].mean(), 1) if len(df) > 0 else 0,
            "max_severity": int(df['severity'].max()) if len(df) > 0 else 0,
            "recent_trend": self._calculate_trend(df),
            "entries_by_symptom": df['symptoms'].value_counts().to_dict() if len(df) > 0 else {}
        }
        
        return patterns
    
    def _calculate_trend(self, df):
        """Calculate if symptoms are improving, stable, or worsening"""
        if len(df) < 2:
            return "Not enough data"
        
        # Get last 5 entries
        recent = df.tail(5)
        
        # Simple linear trend
        severities = recent['severity'].tolist()
        
        if len(severities) < 2:
            return "Stable"
        
        # Calculate if generally increasing or decreasing
        increasing = sum([severities[i] < severities[i+1] for i in range(len(severities)-1)])
        decreasing = sum([severities[i] > severities[i+1] for i in range(len(severities)-1)])
        
        if increasing > decreasing:
            return "Worsening ⚠️"
        elif decreasing > increasing:
            return "Improving ✅"
        else:
            return "Stable ➡️"
    
    def export_for_doctor(self):
        """Export entries in doctor-friendly format"""
        entries = self.get_entries()
        
        text = "HEALTH JOURNAL SUMMARY\n"
        text += "="*60 + "\n\n"
        
        for entry in entries:
            text += f"Date: {entry['date']}\n"
            text += f"Symptoms: {entry['symptoms']}\n"
            text += f"Severity: {entry['severity']}/10\n"
            text += f"Notes: {entry['notes']}\n"
            text += "-"*60 + "\n\n"
        
        patterns = self.analyze_patterns()
        if patterns:
            text += "\nPATTERN ANALYSIS\n"
            text += "="*60 + "\n"
            text += f"Total Entries: {patterns['total_entries']}\n"
            text += f"Most Common Symptom: {patterns['most_common_symptom']}\n"
            text += f"Average Severity: {patterns['average_severity']}/10\n"
            text += f"Trend: {patterns['recent_trend']}\n"
        
        return text