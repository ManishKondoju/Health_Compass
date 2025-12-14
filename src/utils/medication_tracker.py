import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

class MedicationTracker:
    """Complete medication management system with tracking and alerts"""
    
    def __init__(self, data_dir="data/medications"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.medications_file = self.data_dir / "medications.json"
        self.log_file = self.data_dir / "medication_log.json"
    
    def add_medication(self, name, dosage, frequency, times_per_day, 
                      specific_times=None, with_food=False, instructions="",
                      total_quantity=None, refill_date=None):
        """Add a new medication to tracker"""
        medications = self.get_medications(active_only=False)
        
        medication = {
            'id': datetime.now().strftime("%Y%m%d%H%M%S"),
            'name': name,
            'dosage': dosage,
            'frequency': frequency,
            'times_per_day': times_per_day,
            'specific_times': specific_times or [],
            'with_food': with_food,
            'instructions': instructions,
            'total_quantity': total_quantity,
            'quantity_remaining': total_quantity,
            'refill_date': refill_date,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'active': True,
            'side_effects_reported': [],
            'created_at': datetime.now().isoformat()
        }
        
        medications.append(medication)
        
        with open(self.medications_file, 'w') as f:
            json.dump(medications, f, indent=2)
        
        return medication
    
    def get_medications(self, active_only=True):
        """Get all medications"""
        try:
            with open(self.medications_file, 'r') as f:
                meds = json.load(f)
                if active_only:
                    return [m for m in meds if m.get('active', True)]
                return meds
        except:
            return []
    
    def log_dose_taken(self, medication_id, notes=""):
        """Log that a dose was taken"""
        log = self.get_log()
        
        entry = {
            'id': datetime.now().strftime("%Y%m%d%H%M%S"),
            'medication_id': medication_id,
            'taken_at': datetime.now().isoformat(),
            'taken_display': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'notes': notes,
            'missed': False
        }
        
        log.append(entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(log, f, indent=2)
        
        # Update quantity
        self._update_quantity(medication_id, -1)
        
        return entry
    
    def log_dose_missed(self, medication_id, reason=""):
        """Log a missed dose"""
        log = self.get_log()
        
        entry = {
            'id': datetime.now().strftime("%Y%m%d%H%M%S"),
            'medication_id': medication_id,
            'taken_at': datetime.now().isoformat(),
            'taken_display': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'notes': reason,
            'missed': True
        }
        
        log.append(entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(log, f, indent=2)
        
        return entry
    
    def get_log(self, days=30):
        """Get medication log for specified days"""
        try:
            with open(self.log_file, 'r') as f:
                log = json.load(f)
                
                # Filter by date range
                cutoff = datetime.now() - timedelta(days=days)
                filtered = [
                    entry for entry in log
                    if datetime.fromisoformat(entry['taken_at']) > cutoff
                ]
                
                return filtered
        except:
            return []
    
    def _update_quantity(self, medication_id, change):
        """Update remaining pill quantity"""
        medications = self.get_medications(active_only=False)
        
        for med in medications:
            if med['id'] == medication_id:
                if med.get('quantity_remaining') is not None:
                    med['quantity_remaining'] = max(0, med['quantity_remaining'] + change)
                    
                    # Set refill flag
                    if med['quantity_remaining'] <= 7:
                        med['needs_refill'] = True
                    else:
                        med['needs_refill'] = False
                break
        
        with open(self.medications_file, 'w') as f:
            json.dump(medications, f, indent=2)
    
    def get_todays_schedule(self):
        """Get today's medication schedule with status"""
        medications = self.get_medications()
        log = self.get_log(days=1)
        
        schedule = []
        
        for med in medications:
            if med.get('specific_times'):
                for time_str in med['specific_times']:
                    # Check if taken today at this time (within 1 hour window)
                    taken_today = False
                    
                    for entry in log:
                        if entry['medication_id'] == med['id'] and not entry.get('missed', False):
                            entry_time = datetime.fromisoformat(entry['taken_at'])
                            scheduled_time = datetime.combine(
                                datetime.now().date(),
                                datetime.strptime(time_str, "%H:%M").time()
                            )
                            
                            # Within 1 hour window of scheduled time
                            if abs((entry_time - scheduled_time).total_seconds()) < 3600:
                                taken_today = True
                                break
                    
                    # Check if overdue
                    scheduled_time = datetime.strptime(time_str, "%H:%M").time()
                    current_time = datetime.now().time()
                    overdue = current_time > scheduled_time and not taken_today
                    
                    schedule.append({
                        'medication': med,
                        'time': time_str,
                        'taken': taken_today,
                        'overdue': overdue
                    })
        
        # Sort by time
        schedule.sort(key=lambda x: x['time'])
        
        return schedule
    
    def get_adherence_rate(self, medication_id=None, days=30):
        """Calculate medication adherence percentage"""
        log = self.get_log(days=days)
        
        if medication_id:
            log = [entry for entry in log if entry['medication_id'] == medication_id]
        
        if not log:
            return None
        
        total_doses = len(log)
        taken_doses = len([entry for entry in log if not entry.get('missed', False)])
        
        adherence_pct = (taken_doses / total_doses) * 100 if total_doses > 0 else 0
        
        return {
            'adherence_percentage': round(adherence_pct, 1),
            'total_doses': total_doses,
            'taken': taken_doses,
            'missed': total_doses - taken_doses,
            'days_tracked': days
        }
    
    def get_refill_alerts(self):
        """Get medications needing refill"""
        medications = self.get_medications()
        alerts = []
        
        for med in medications:
            # Check remaining quantity
            if med.get('quantity_remaining') is not None:
                remaining = med['quantity_remaining']
                
                if remaining <= 7:
                    alerts.append({
                        'medication': med,
                        'type': 'quantity',
                        'message': f"Only {remaining} doses left - Refill needed!",
                        'urgency': 'high' if remaining <= 3 else 'medium',
                        'days_supply': remaining
                    })
            
            # Check refill date
            if med.get('refill_date'):
                try:
                    refill_date = datetime.strptime(med['refill_date'], "%Y-%m-%d")
                    days_until = (refill_date - datetime.now()).days
                    
                    if days_until <= 7 and days_until >= 0:
                        alerts.append({
                            'medication': med,
                            'type': 'refill_date',
                            'message': f"Refill due in {days_until} day{'s' if days_until != 1 else ''}",
                            'urgency': 'high' if days_until <= 3 else 'medium',
                            'days_until': days_until
                        })
                    elif days_until < 0:
                        alerts.append({
                            'medication': med,
                            'type': 'refill_overdue',
                            'message': f"Refill was due {abs(days_until)} days ago!",
                            'urgency': 'high',
                            'days_until': days_until
                        })
                except:
                    pass
        
        # Sort by urgency
        alerts.sort(key=lambda x: 0 if x['urgency'] == 'high' else 1)
        
        return alerts
    
    def deactivate_medication(self, medication_id):
        """Mark medication as inactive (stopped taking)"""
        medications = self.get_medications(active_only=False)
        
        for med in medications:
            if med['id'] == medication_id:
                med['active'] = False
                med['end_date'] = datetime.now().strftime("%Y-%m-%d")
                break
        
        with open(self.medications_file, 'w') as f:
            json.dump(medications, f, indent=2)
    
    def report_side_effect(self, medication_id, side_effect, severity):
        """Report a medication side effect"""
        medications = self.get_medications(active_only=False)
        
        for med in medications:
            if med['id'] == medication_id:
                if 'side_effects_reported' not in med:
                    med['side_effects_reported'] = []
                
                med['side_effects_reported'].append({
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'effect': side_effect,
                    'severity': severity,
                    'reported_at': datetime.now().isoformat()
                })
                break
        
        with open(self.medications_file, 'w') as f:
            json.dump(medications, f, indent=2)
    
    def get_medication_by_id(self, medication_id):
        """Get single medication details"""
        medications = self.get_medications(active_only=False)
        
        for med in medications:
            if med['id'] == medication_id:
                return med
        
        return None
    
    def export_medication_list(self):
        """Export medication list for doctor/pharmacy"""
        medications = self.get_medications()
        
        export = "CURRENT MEDICATIONS LIST\n"
        export += "="*70 + "\n"
        export += f"Patient Name: [Fill in your name]\n"
        export += f"Date: {datetime.now().strftime('%B %d, %Y')}\n"
        export += f"Total Active Medications: {len(medications)}\n\n"
        export += "="*70 + "\n\n"
        
        for i, med in enumerate(medications, 1):
            export += f"{i}. MEDICATION: {med['name']}\n"
            export += f"   Dosage: {med['dosage']}\n"
            export += f"   Frequency: {med['frequency']}\n"
            
            if med.get('specific_times'):
                times_display = ", ".join(med['specific_times'])
                export += f"   Schedule: {times_display}\n"
            
            if med.get('with_food'):
                export += f"   Special: Take with food\n"
            
            if med.get('instructions'):
                export += f"   Instructions: {med['instructions']}\n"
            
            export += f"   Start Date: {med['start_date']}\n"
            
            if med.get('side_effects_reported') and len(med['side_effects_reported']) > 0:
                export += f"   Side Effects: {len(med['side_effects_reported'])} reported\n"
                for se in med['side_effects_reported'][-3:]:  # Last 3
                    export += f"     - {se['date']}: {se['effect']} (Severity: {se['severity']}/10)\n"
            
            export += "\n" + "-"*70 + "\n\n"
        
        export += "="*70 + "\n"
        export += "IMPORTANT NOTES:\n"
        export += "• This list is current as of the date above\n"
        export += "• Allergies: [Fill in any drug allergies]\n"
        export += "• Over-the-counter supplements: [Add if any]\n\n"
        export += "Generated by Health Compass Medication Tracker\n"
        export += "="*70 + "\n"
        
        return export
    
    def check_interactions(self, medication_names_list):
        """Check for potential drug interactions"""
        # Educational note about interactions
        if len(medication_names_list) < 2:
            return {
                'has_interactions': False,
                'message': 'Need at least 2 medications to check interactions'
            }
        
        return {
            'has_interactions': True,
            'medications': medication_names_list,
            'count': len(medication_names_list),
            'recommendation': 'Always consult your pharmacist or doctor about potential drug interactions. They have access to comprehensive interaction databases.'
        }
    
    def get_medication_info_summary(self, medication_id):
        """Get comprehensive summary for a medication"""
        med = self.get_medication_by_id(medication_id)
        
        if not med:
            return None
        
        # Get adherence for this medication
        adherence = self.get_adherence_rate(medication_id=medication_id, days=30)
        
        # Calculate days on medication
        start = datetime.strptime(med['start_date'], "%Y-%m-%d")
        days_on_med = (datetime.now() - start).days
        
        summary = {
            'medication': med,
            'days_on_medication': days_on_med,
            'adherence': adherence,
            'needs_refill': med.get('needs_refill', False),
            'has_side_effects': len(med.get('side_effects_reported', [])) > 0,
            'total_side_effects': len(med.get('side_effects_reported', []))
        }
        
        return summary