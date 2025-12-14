import json
from pathlib import Path
from datetime import datetime

class HealthcareAssistant:
    """AI Healthcare Assistant with conversation memory and medication tracking"""
    
    def __init__(self, data_dir="data/chatbot"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_file = self.data_dir / "conversation_history.json"
        self.medications_mentioned_file = self.data_dir / "medications_mentioned.json"
        self.user_profile_file = self.data_dir / "user_profile.json"
    
    def get_conversation_history(self):
        """Get conversation history"""
        try:
            with open(self.conversation_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def add_message(self, role, content):
        """Add message to conversation"""
        history = self.get_conversation_history()
        
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'display_time': datetime.now().strftime("%I:%M %p")
        }
        
        history.append(message)
        
        # Keep last 50 messages
        if len(history) > 50:
            history = history[-50:]
        
        with open(self.conversation_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        # Extract medications if mentioned
        self._extract_medications(content)
        
        return message
    
    def _extract_medications(self, text):
        """Extract medication mentions from text"""
        # Common medication keywords
        med_keywords = [
            'aspirin', 'ibuprofen', 'acetaminophen', 'tylenol', 'advil',
            'metformin', 'lisinopril', 'atorvastatin', 'amlodipine',
            'levothyroxine', 'omeprazole', 'simvastatin', 'losartan',
            'gabapentin', 'hydrochlorothiazide', 'prednisone', 'amoxicillin'
        ]
        
        text_lower = text.lower()
        medications_found = []
        
        for med in med_keywords:
            if med in text_lower:
                medications_found.append(med.capitalize())
        
        if medications_found:
            self._save_medications(medications_found)
    
    def _save_medications(self, medications):
        """Save mentioned medications"""
        try:
            with open(self.medications_mentioned_file, 'r') as f:
                med_list = json.load(f)
        except:
            med_list = []
        
        for med in medications:
            # Check if already exists
            if not any(m['name'].lower() == med.lower() for m in med_list):
                med_list.append({
                    'name': med,
                    'mentioned_at': datetime.now().isoformat(),
                    'display_time': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        
        with open(self.medications_mentioned_file, 'w') as f:
            json.dump(med_list, f, indent=2)
    
    def get_tracked_medications(self):
        """Get medications mentioned in conversations"""
        try:
            with open(self.medications_mentioned_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def clear_conversation(self):
        """Clear conversation history"""
        with open(self.conversation_file, 'w') as f:
            json.dump([], f)
    
    def get_user_profile(self):
        """Get user profile information extracted from conversations"""
        try:
            with open(self.user_profile_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'location': None,
                'age': None,
                'conditions': [],
                'allergies': []
            }
    
    def update_user_profile(self, **kwargs):
        """Update user profile"""
        profile = self.get_user_profile()
        profile.update(kwargs)
        
        with open(self.user_profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
    
    def get_conversation_context(self, last_n=6):
        """Get recent conversation for context"""
        history = self.get_conversation_history()
        
        if not history:
            return ""
        
        recent = history[-last_n:]
        
        context = "Previous conversation:\n"
        for msg in recent:
            role = "Patient" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n\n"
        
        return context
    
    def get_hospital_suggestions(self, location, condition_type="general"):
        """Get hospital suggestions based on location and condition"""
        
        # Educational examples - in production would use Google Maps API
        hospitals = {
            'boston': [
                {
                    'name': 'Massachusetts General Hospital',
                    'specialty': 'Comprehensive care, all specialties',
                    'address': '55 Fruit Street, Boston, MA 02114',
                    'phone': '(617) 726-2000',
                    'rating': '4.5/5',
                    'services': ['Emergency', 'Primary Care', 'Specialists', 'Surgery']
                },
                {
                    'name': 'Brigham and Women\'s Hospital',
                    'specialty': 'Cardiovascular, Cancer, Women\'s Health',
                    'address': '75 Francis Street, Boston, MA 02115',
                    'phone': '(617) 732-5500',
                    'rating': '4.6/5',
                    'services': ['Emergency', 'Cardiology', 'Oncology', 'OB/GYN']
                },
                {
                    'name': 'Beth Israel Deaconess Medical Center',
                    'specialty': 'Internal Medicine, Research',
                    'address': '330 Brookline Avenue, Boston, MA 02215',
                    'phone': '(617) 667-7000',
                    'rating': '4.4/5',
                    'services': ['Emergency', 'Internal Medicine', 'Research Programs']
                }
            ],
            'default': [
                {
                    'name': 'Search nearby hospitals',
                    'info': f'Use Google Maps: Search "hospitals near {location}"',
                    'action': 'Find hospitals in your area'
                },
                {
                    'name': 'Your insurance provider',
                    'info': 'Check your insurance card or website',
                    'action': 'Find in-network hospitals'
                },
                {
                    'name': 'Call 911',
                    'info': 'For emergencies',
                    'action': 'Emergency services will direct you'
                }
            ]
        }
        
        location_lower = location.lower() if location else ''
        
        if 'boston' in location_lower:
            return hospitals['boston']
        else:
            return hospitals['default']