# src/utils/user_profile.py
"""
User Profile Management System
- Stores user health information
- Provides context for all features
- Manages profile persistence
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class UserProfile:
    """Manages user health profile and preferences"""
    
    def __init__(self, profile_dir: str = "data/user_profile"):
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.profile_file = self.profile_dir / "profile.json"
        self.profile_data = self._load_profile()
    
    def _load_profile(self) -> Dict:
        """Load existing profile or create default"""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default empty profile
        return {
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_setup_complete': False,
            'basic_info': {
                'name': '',
                'age': None,
                'gender': None,
                'date_of_birth': None
            },
            'contact': {
                'email': '',
                'phone': '',
                'emergency_contact': '',
                'emergency_phone': ''
            },
            'health_info': {
                'height': None,  # in cm
                'weight': None,  # in kg
                'blood_type': None,
                'allergies': [],
                'chronic_conditions': [],
                'family_history': [],
                'current_medications': [],
                'past_surgeries': [],
                'immunizations': []
            },
            'lifestyle': {
                'smoking': 'never',  # never, former, current
                'alcohol': 'none',   # none, occasional, moderate, heavy
                'exercise': 'sedentary',  # sedentary, light, moderate, active
                'diet': 'balanced'  # balanced, vegetarian, vegan, other
            },
            'preferences': {
                'language': 'English',
                'units': 'metric',  # metric or imperial
                'notifications': True,
                'location': ''
            },
            'medical_history': {
                'last_checkup': None,
                'primary_care_doctor': '',
                'insurance_provider': '',
                'insurance_id': ''
            }
        }
    
    def _save_profile(self):
        """Save profile to disk"""
        self.profile_data['updated_at'] = datetime.now().isoformat()
        with open(self.profile_file, 'w') as f:
            json.dump(self.profile_data, f, indent=2)
    
    def is_setup_complete(self) -> bool:
        """Check if user has completed profile setup"""
        return self.profile_data.get('is_setup_complete', False)
    
    def mark_setup_complete(self):
        """Mark profile setup as complete"""
        self.profile_data['is_setup_complete'] = True
        self._save_profile()
    
    def update_basic_info(self, name: str = None, age: int = None, 
                         gender: str = None, dob: str = None):
        """Update basic information"""
        if name:
            self.profile_data['basic_info']['name'] = name
        if age:
            self.profile_data['basic_info']['age'] = age
        if gender:
            self.profile_data['basic_info']['gender'] = gender
        if dob:
            self.profile_data['basic_info']['date_of_birth'] = dob
        self._save_profile()
    
    def update_contact(self, email: str = None, phone: str = None,
                      emergency_contact: str = None, emergency_phone: str = None):
        """Update contact information"""
        if email:
            self.profile_data['contact']['email'] = email
        if phone:
            self.profile_data['contact']['phone'] = phone
        if emergency_contact:
            self.profile_data['contact']['emergency_contact'] = emergency_contact
        if emergency_phone:
            self.profile_data['contact']['emergency_phone'] = emergency_phone
        self._save_profile()
    
    def update_health_info(self, height: float = None, weight: float = None,
                          blood_type: str = None):
        """Update health measurements"""
        if height:
            self.profile_data['health_info']['height'] = height
        if weight:
            self.profile_data['health_info']['weight'] = weight
        if blood_type:
            self.profile_data['health_info']['blood_type'] = blood_type
        self._save_profile()
    
    def add_allergy(self, allergy: str):
        """Add an allergy"""
        if allergy and allergy not in self.profile_data['health_info']['allergies']:
            self.profile_data['health_info']['allergies'].append(allergy)
            self._save_profile()
    
    def remove_allergy(self, allergy: str):
        """Remove an allergy"""
        if allergy in self.profile_data['health_info']['allergies']:
            self.profile_data['health_info']['allergies'].remove(allergy)
            self._save_profile()
    
    def add_condition(self, condition: str):
        """Add a chronic condition"""
        if condition and condition not in self.profile_data['health_info']['chronic_conditions']:
            self.profile_data['health_info']['chronic_conditions'].append(condition)
            self._save_profile()
    
    def remove_condition(self, condition: str):
        """Remove a chronic condition"""
        if condition in self.profile_data['health_info']['chronic_conditions']:
            self.profile_data['health_info']['chronic_conditions'].remove(condition)
            self._save_profile()
    
    def add_medication(self, medication: Dict):
        """Add current medication"""
        self.profile_data['health_info']['current_medications'].append(medication)
        self._save_profile()
    
    def remove_medication(self, medication_name: str):
        """Remove a medication"""
        self.profile_data['health_info']['current_medications'] = [
            m for m in self.profile_data['health_info']['current_medications']
            if m.get('name') != medication_name
        ]
        self._save_profile()
    
    def update_lifestyle(self, smoking: str = None, alcohol: str = None,
                        exercise: str = None, diet: str = None):
        """Update lifestyle information"""
        if smoking:
            self.profile_data['lifestyle']['smoking'] = smoking
        if alcohol:
            self.profile_data['lifestyle']['alcohol'] = alcohol
        if exercise:
            self.profile_data['lifestyle']['exercise'] = exercise
        if diet:
            self.profile_data['lifestyle']['diet'] = diet
        self._save_profile()
    
    def update_preferences(self, language: str = None, location: str = None):
        """Update user preferences"""
        if language:
            self.profile_data['preferences']['language'] = language
        if location:
            self.profile_data['preferences']['location'] = location
        self._save_profile()
    
    def get_profile_summary(self) -> Dict:
        """Get formatted profile summary"""
        basic = self.profile_data['basic_info']
        health = self.profile_data['health_info']
        lifestyle = self.profile_data['lifestyle']
        
        # Calculate BMI if height and weight available
        bmi = None
        bmi_category = None
        if health.get('height') and health.get('weight'):
            height_m = health['height'] / 100
            bmi = health['weight'] / (height_m ** 2)
            
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif bmi < 25:
                bmi_category = "Normal"
            elif bmi < 30:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obese"
        
        return {
            'name': basic.get('name', 'User'),
            'age': basic.get('age'),
            'gender': basic.get('gender'),
            'bmi': round(bmi, 1) if bmi else None,
            'bmi_category': bmi_category,
            'allergies_count': len(health.get('allergies', [])),
            'conditions_count': len(health.get('chronic_conditions', [])),
            'medications_count': len(health.get('current_medications', [])),
            'lifestyle_risk': self._calculate_lifestyle_risk(lifestyle)
        }
    
    def _calculate_lifestyle_risk(self, lifestyle: Dict) -> str:
        """Calculate lifestyle risk level"""
        risk_score = 0
        
        if lifestyle.get('smoking') == 'current':
            risk_score += 3
        elif lifestyle.get('smoking') == 'former':
            risk_score += 1
        
        if lifestyle.get('alcohol') in ['moderate', 'heavy']:
            risk_score += 2
        
        if lifestyle.get('exercise') == 'sedentary':
            risk_score += 2
        
        if risk_score >= 5:
            return "High"
        elif risk_score >= 3:
            return "Moderate"
        else:
            return "Low"
    
    def get_context_for_ai(self) -> str:
        """Generate context string for AI assistant"""
        basic = self.profile_data['basic_info']
        health = self.profile_data['health_info']
        lifestyle = self.profile_data['lifestyle']
        
        context = f"Patient Profile:\n"
        
        if basic.get('name'):
            context += f"- Name: {basic['name']}\n"
        if basic.get('age'):
            context += f"- Age: {basic['age']} years old\n"
        if basic.get('gender'):
            context += f"- Gender: {basic['gender']}\n"
        
        if health.get('allergies'):
            context += f"- Allergies: {', '.join(health['allergies'])}\n"
        
        if health.get('chronic_conditions'):
            context += f"- Chronic Conditions: {', '.join(health['chronic_conditions'])}\n"
        
        if health.get('current_medications'):
            meds = [m.get('name', '') for m in health['current_medications']]
            context += f"- Current Medications: {', '.join(meds)}\n"
        
        context += f"- Smoking: {lifestyle.get('smoking', 'unknown')}\n"
        context += f"- Exercise: {lifestyle.get('exercise', 'unknown')}\n"
        
        return context
    
    def get_full_profile(self) -> Dict:
        """Get complete profile data"""
        return self.profile_data.copy()
    
    def get_basic_info(self) -> Dict:
        """Get basic info section"""
        return self.profile_data['basic_info'].copy()
    
    def get_health_info(self) -> Dict:
        """Get health info section"""
        return self.profile_data['health_info'].copy()
    
    def get_lifestyle(self) -> Dict:
        """Get lifestyle section"""
        return self.profile_data['lifestyle'].copy()
    
    def get_preferences(self) -> Dict:
        """Get preferences section"""
        return self.profile_data['preferences'].copy()
    
    def reset_profile(self):
        """Reset profile to default (for testing)"""
        if self.profile_file.exists():
            self.profile_file.unlink()
        self.profile_data = self._load_profile()


# Example usage
if __name__ == "__main__":
    # Create profile
    profile = UserProfile()
    
    # Setup profile
    profile.update_basic_info(
        name="John Doe",
        age=45,
        gender="Male"
    )
    
    profile.update_health_info(
        height=175,  # cm
        weight=80,   # kg
        blood_type="O+"
    )
    
    profile.add_allergy("Penicillin")
    profile.add_condition("Hypertension")
    
    profile.add_medication({
        'name': 'Lisinopril',
        'dosage': '10mg',
        'frequency': 'Once daily'
    })
    
    profile.update_lifestyle(
        smoking='never',
        exercise='moderate',
        alcohol='occasional'
    )
    
    profile.mark_setup_complete()
    
    # Get summary
    summary = profile.get_profile_summary()
    print("Profile Summary:")
    print(json.dumps(summary, indent=2))
    
    # Get AI context
    context = profile.get_context_for_ai()
    print("\nAI Context:")
    print(context)