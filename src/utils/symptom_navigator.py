from datetime import datetime

class SymptomNavigator:
    """Emergency symptom navigation and care pathway system"""
    
    def __init__(self):
        # Emergency symptoms by category
        self.emergency_keywords = {
            "chest": [
                "Pain radiating to arm, jaw, neck, or back",
                "Severe pressure or squeezing sensation",
                "Shortness of breath with chest discomfort",
                "Cold sweats or nausea with chest pain",
                "Pain lasting more than 5 minutes"
            ],
            "head": [
                "Sudden severe headache (worst headache ever)",
                "Headache with fever and stiff neck",
                "Confusion or trouble speaking",
                "Vision changes or sudden vision loss",
                "Weakness, numbness, or inability to move limbs"
            ],
            "breath": [
                "Severe difficulty breathing or gasping",
                "Cannot speak full sentences",
                "Blue lips, tongue, or face",
                "Wheezing with difficulty breathing",
                "Chest tightness with severe breathing difficulty"
            ],
            "abdominal": [
                "Severe, worsening abdominal pain",
                "Rigid, board-like abdomen",
                "Bloody vomit or blood in stool",
                "Unable to stand upright due to pain",
                "Severe pain with fever over 101°F"
            ],
            "mental": [
                "Thoughts of harming yourself or others",
                "Severe confusion or disorientation",
                "Hallucinations or delusions",
                "Uncontrollable behavior",
                "Loss of consciousness or fainting"
            ],
            "general": [
                "Difficulty breathing or severe shortness of breath",
                "Severe pain rated 8 or higher",
                "Loss of consciousness",
                "Severe bleeding that won't stop",
                "Sudden weakness or inability to move"
            ]
        }
    
    def get_emergency_symptoms(self, primary_symptom):
        """Get relevant emergency symptoms based on primary complaint"""
        symptom_lower = primary_symptom.lower()
        
        # Match keywords to get relevant emergency symptoms
        for keyword, symptoms in self.emergency_keywords.items():
            if keyword in symptom_lower:
                return symptoms
        
        # Default to general emergency symptoms
        return self.emergency_keywords["general"]
    
    def assess_urgency(self, severity, duration, worsening, emergency_symptoms_present):
        """Determine care urgency level"""
        
        if emergency_symptoms_present or severity >= 9:
            return {
                'level': 'EMERGENCY',
                'action': 'CALL 911 IMMEDIATELY',
                'color': 'red',
                'timeframe': 'NOW - Do not drive yourself',
                'care_type': 'Emergency Room'
            }
        
        if severity >= 7 or worsening or any(x in duration.lower() for x in ["hour", "< 1"]):
            return {
                'level': 'URGENT',
                'action': 'Seek medical care within 24 hours',
                'color': 'orange',
                'timeframe': 'Today or tomorrow',
                'care_type': 'Urgent Care or Doctor'
            }
        
        if severity >= 5 or "day" in duration.lower():
            return {
                'level': 'SOON',
                'action': 'Schedule doctor appointment',
                'color': 'yellow',
                'timeframe': 'Within a week',
                'care_type': 'Primary Care Doctor'
            }
        
        return {
            'level': 'MONITOR',
            'action': 'Self-care and monitoring',
            'color': 'green',
            'timeframe': 'Contact doctor if worsens or persists',
            'care_type': 'Home Care'
        }
    
    def get_care_locations(self, location, care_type):
        """Get care facility information by type"""
        
        # Educational examples - in production would use Google Maps API
        
        if care_type == 'emergency':
            return {
                'type': 'Emergency Room',
                'locations': [
                    {
                        'name': 'Massachusetts General Hospital Emergency',
                        'address': '55 Fruit Street, Boston, MA 02114',
                        'phone': '(617) 726-2000',
                        'distance': '~2 miles from downtown',
                        'wait_time': 'Variable - Call 911 for ambulance'
                    },
                    {
                        'name': 'Brigham and Women\'s Hospital Emergency',
                        'address': '75 Francis Street, Boston, MA 02115',
                        'phone': '(617) 732-5500',
                        'distance': '~3 miles from downtown',
                        'wait_time': 'Variable - Call 911 for ambulance'
                    },
                    {
                        'name': 'Beth Israel Deaconess Emergency',
                        'address': '330 Brookline Avenue, Boston, MA 02215',
                        'phone': '(617) 667-7000',
                        'distance': '~3 miles from downtown',
                        'wait_time': 'Variable - Call 911 for ambulance'
                    }
                ],
                'note': '🚨 For life-threatening emergencies, CALL 911 immediately. Do not drive yourself.'
            }
        
        elif care_type == 'urgent':
            return {
                'type': 'Urgent Care Center',
                'locations': [
                    {
                        'name': 'CareWell Urgent Care - Fenway',
                        'address': '1330 Boylston Street, Boston, MA 02215',
                        'phone': '(617) 383-1900',
                        'hours': '8:00 AM - 8:00 PM Daily',
                        'distance': '~1.5 miles'
                    },
                    {
                        'name': 'AFC Urgent Care Boston',
                        'address': 'Multiple Boston locations',
                        'phone': '(617) 522-7777',
                        'hours': '8:00 AM - 8:00 PM Weekdays, 9 AM - 5 PM Weekends',
                        'distance': 'Check website for nearest'
                    },
                    {
                        'name': 'Tufts Medical Center Urgent Care',
                        'address': '800 Washington Street, Boston, MA',
                        'phone': '(617) 636-5000',
                        'hours': '9:00 AM - 9:00 PM Daily',
                        'distance': '~2 miles'
                    }
                ],
                'note': '💡 TIP: Call ahead to check wait times and ensure they can treat your condition.'
            }
        
        elif care_type == 'primary':
            return {
                'type': 'Primary Care Options',
                'locations': [
                    {
                        'name': 'Your Primary Care Doctor',
                        'info': 'Check your insurance card for your assigned PCP',
                        'action': 'Call to schedule appointment',
                        'note': 'Usually can schedule within 1-2 weeks'
                    },
                    {
                        'name': 'Walk-in Clinics',
                        'info': 'CVS MinuteClinic, Walgreens Healthcare Clinic, Patient First',
                        'action': 'No appointment needed for minor issues',
                        'note': 'Convenient for vaccinations, minor illnesses'
                    },
                    {
                        'name': 'Telehealth',
                        'info': 'Virtual doctor visits via video call',
                        'action': 'Check if your insurance covers: Teladoc, MDLive, Doctor On Demand',
                        'note': 'Great for non-emergency consultations'
                    }
                ],
                'note': '💡 Check your insurance provider directory for in-network options'
            }
        
        return {
            'type': 'Medical Care',
            'locations': [],
            'note': 'Enter your location to find nearby facilities'
        }