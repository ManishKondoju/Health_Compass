# src/utils/specialist_matcher.py
"""
Specialist Matcher - Matches symptoms to medical specialists
Integrates with: Symptom Tracker, AI Assistant, Document Analyzer
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

class SpecialistMatcher:
    """Matches symptoms/conditions to appropriate medical specialists"""
    
    def __init__(self, rag_system=None):
        self.rag = rag_system
        self.specialist_database = self._load_specialist_database()
    
    def _load_specialist_database(self) -> Dict:
        """Load specialist types and their common symptoms/conditions"""
        return {
            'cardiologist': {
                'name': 'Cardiologist (Heart Specialist)',
                'icon': '❤️',
                'treats': 'Heart and cardiovascular conditions',
                'keywords': [
                    'chest pain', 'heart palpitation', 'irregular heartbeat', 
                    'shortness of breath', 'high blood pressure', 'hypertension',
                    'heart attack', 'coronary', 'cardiac', 'arrhythmia',
                    'cholesterol', 'heart disease', 'angina', 'valve'
                ],
                'conditions': [
                    'High blood pressure', 'Heart disease', 'Irregular heartbeat',
                    'High cholesterol', 'Heart failure', 'Chest pain'
                ],
                'urgency_keywords': ['chest pain', 'heart attack', 'severe pain', 'crushing']
            },
            'dermatologist': {
                'name': 'Dermatologist (Skin Specialist)',
                'icon': '🩺',
                'treats': 'Skin, hair, and nail conditions',
                'keywords': [
                    'rash', 'acne', 'eczema', 'psoriasis', 'mole', 'skin cancer',
                    'dermatitis', 'hives', 'itching', 'skin lesion', 'wart',
                    'hair loss', 'nail', 'melanoma', 'sunburn', 'dry skin'
                ],
                'conditions': [
                    'Acne', 'Eczema', 'Psoriasis', 'Skin infections',
                    'Suspicious moles', 'Hair loss', 'Rashes'
                ]
            },
            'endocrinologist': {
                'name': 'Endocrinologist (Hormone Specialist)',
                'icon': '🔬',
                'treats': 'Hormone and metabolic disorders',
                'keywords': [
                    'diabetes', 'thyroid', 'hormone', 'glucose', 'insulin',
                    'metabolism', 'weight gain', 'weight loss', 'fatigue',
                    'hypothyroid', 'hyperthyroid', 'adrenal', 'pituitary'
                ],
                'conditions': [
                    'Diabetes', 'Thyroid disorders', 'Metabolic syndrome',
                    'Hormone imbalances', 'Osteoporosis', 'PCOS'
                ]
            },
            'gastroenterologist': {
                'name': 'Gastroenterologist (Digestive Specialist)',
                'icon': '🫃',
                'treats': 'Digestive system conditions',
                'keywords': [
                    'stomach pain', 'abdominal pain', 'diarrhea', 'constipation',
                    'nausea', 'vomiting', 'heartburn', 'acid reflux', 'ibs',
                    'crohn', 'colitis', 'ulcer', 'bloating', 'gas', 'indigestion'
                ],
                'conditions': [
                    'IBS', 'Acid reflux', 'Ulcers', "Crohn's disease",
                    'Colitis', 'Liver disease', 'Gallstones'
                ]
            },
            'neurologist': {
                'name': 'Neurologist (Brain & Nerve Specialist)',
                'icon': '🧠',
                'treats': 'Brain, spinal cord, and nerve conditions',
                'keywords': [
                    'headache', 'migraine', 'seizure', 'dizziness', 'vertigo',
                    'numbness', 'tingling', 'tremor', 'memory loss', 'stroke',
                    'multiple sclerosis', 'parkinson', 'epilepsy', 'neuropathy'
                ],
                'conditions': [
                    'Migraines', 'Seizures', 'Stroke', 'Multiple sclerosis',
                    'Parkinson\'s disease', 'Neuropathy', 'Memory disorders'
                ],
                'urgency_keywords': ['stroke', 'seizure', 'severe headache', 'paralysis']
            },
            'orthopedist': {
                'name': 'Orthopedist (Bone & Joint Specialist)',
                'icon': '🦴',
                'treats': 'Bones, joints, ligaments, and tendons',
                'keywords': [
                    'joint pain', 'back pain', 'knee pain', 'arthritis',
                    'fracture', 'broken bone', 'sprain', 'torn ligament',
                    'hip pain', 'shoulder pain', 'carpal tunnel', 'sciatica'
                ],
                'conditions': [
                    'Arthritis', 'Back pain', 'Joint injuries', 'Fractures',
                    'Sports injuries', 'Osteoporosis', 'Carpal tunnel'
                ]
            },
            'pulmonologist': {
                'name': 'Pulmonologist (Lung Specialist)',
                'icon': '🫁',
                'treats': 'Respiratory and lung conditions',
                'keywords': [
                    'breathing difficulty', 'asthma', 'copd', 'cough',
                    'wheezing', 'lung', 'pneumonia', 'bronchitis',
                    'shortness of breath', 'chest tightness', 'respiratory'
                ],
                'conditions': [
                    'Asthma', 'COPD', 'Pneumonia', 'Bronchitis',
                    'Sleep apnea', 'Lung disease', 'Chronic cough'
                ],
                'urgency_keywords': ['severe breathing', 'can\'t breathe', 'choking']
            },
            'rheumatologist': {
                'name': 'Rheumatologist (Autoimmune Specialist)',
                'icon': '🦠',
                'treats': 'Autoimmune and inflammatory conditions',
                'keywords': [
                    'rheumatoid arthritis', 'lupus', 'fibromyalgia',
                    'joint swelling', 'autoimmune', 'inflammation',
                    'chronic pain', 'stiffness', 'gout'
                ],
                'conditions': [
                    'Rheumatoid arthritis', 'Lupus', 'Fibromyalgia',
                    'Gout', 'Vasculitis', 'Scleroderma'
                ]
            },
            'psychiatrist': {
                'name': 'Psychiatrist (Mental Health MD)',
                'icon': '🧘',
                'treats': 'Mental health conditions (can prescribe)',
                'keywords': [
                    'depression', 'anxiety', 'panic attack', 'bipolar',
                    'schizophrenia', 'ptsd', 'ocd', 'mental health',
                    'suicidal', 'mood disorder', 'psychosis'
                ],
                'conditions': [
                    'Depression', 'Anxiety disorders', 'Bipolar disorder',
                    'PTSD', 'OCD', 'Schizophrenia', 'Eating disorders'
                ],
                'urgency_keywords': ['suicidal', 'self harm', 'crisis']
            },
            'urologist': {
                'name': 'Urologist (Urinary & Reproductive)',
                'icon': '🩺',
                'treats': 'Urinary tract and male reproductive issues',
                'keywords': [
                    'urinary', 'bladder', 'kidney stone', 'prostate',
                    'incontinence', 'uti', 'blood in urine', 'frequent urination',
                    'erectile dysfunction', 'testicular'
                ],
                'conditions': [
                    'Kidney stones', 'UTI', 'Prostate issues', 'Incontinence',
                    'Bladder problems', 'Male infertility'
                ]
            },
            'ent': {
                'name': 'ENT (Ear, Nose, Throat Specialist)',
                'icon': '👂',
                'treats': 'Ear, nose, throat, and sinus conditions',
                'keywords': [
                    'ear pain', 'hearing loss', 'tinnitus', 'sinus',
                    'nasal congestion', 'sore throat', 'tonsillitis',
                    'vertigo', 'smell loss', 'voice problems', 'sleep apnea'
                ],
                'conditions': [
                    'Ear infections', 'Sinusitis', 'Tonsillitis', 'Hearing loss',
                    'Sleep apnea', 'Voice disorders', 'Nasal polyps'
                ]
            },
            'ophthalmologist': {
                'name': 'Ophthalmologist (Eye MD)',
                'icon': '👁️',
                'treats': 'Eye diseases and surgery',
                'keywords': [
                    'vision', 'blurry vision', 'eye pain', 'cataracts',
                    'glaucoma', 'macular degeneration', 'double vision',
                    'eye infection', 'floaters', 'retina'
                ],
                'conditions': [
                    'Cataracts', 'Glaucoma', 'Macular degeneration',
                    'Diabetic retinopathy', 'Eye injuries', 'Vision problems'
                ]
            },
            'allergist': {
                'name': 'Allergist/Immunologist',
                'icon': '🤧',
                'treats': 'Allergies and immune system disorders',
                'keywords': [
                    'allergy', 'allergic reaction', 'hives', 'anaphylaxis',
                    'food allergy', 'seasonal allergies', 'asthma',
                    'hay fever', 'eczema', 'immune deficiency'
                ],
                'conditions': [
                    'Food allergies', 'Seasonal allergies', 'Asthma',
                    'Eczema', 'Hives', 'Immune deficiencies'
                ]
            },
            'primary_care': {
                'name': 'Primary Care Physician (General)',
                'icon': '👨‍⚕️',
                'treats': 'General health, preventive care, common conditions',
                'keywords': [
                    'checkup', 'physical exam', 'cold', 'flu', 'fever',
                    'general health', 'preventive', 'vaccination', 'routine'
                ],
                'conditions': [
                    'Routine checkups', 'Common illnesses', 'Preventive care',
                    'General health concerns', 'Referrals to specialists'
                ]
            }
        }
    
    def match_specialist(self, symptoms: List[str], context: str = "") -> Dict:
        """
        Match symptoms to appropriate specialist(s)
        
        Args:
            symptoms: List of symptom descriptions
            context: Additional context (age, gender, medical history)
        
        Returns:
            Dict with specialist recommendations, urgency, and reasoning
        """
        # Combine all symptoms into one text for analysis
        symptom_text = " ".join(symptoms).lower() + " " + context.lower()
        
        # Score each specialist
        specialist_scores = {}
        urgency = 'routine'
        urgency_reasons = []
        
        for spec_key, spec_data in self.specialist_database.items():
            score = 0
            matched_keywords = []
            
            # Check keyword matches
            for keyword in spec_data['keywords']:
                if keyword in symptom_text:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Check urgency keywords
            if 'urgency_keywords' in spec_data:
                for urgent_keyword in spec_data['urgency_keywords']:
                    if urgent_keyword in symptom_text:
                        urgency = 'urgent'
                        urgency_reasons.append(f"{urgent_keyword} detected")
            
            if score > 0:
                specialist_scores[spec_key] = {
                    'score': score,
                    'data': spec_data,
                    'matched_keywords': matched_keywords
                }
        
        # Sort by score
        sorted_specialists = sorted(
            specialist_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Prepare recommendations
        recommendations = []
        
        if sorted_specialists:
            for spec_key, spec_info in sorted_specialists[:3]:  # Top 3
                recommendations.append({
                    'type': spec_key,
                    'name': spec_info['data']['name'],
                    'icon': spec_info['data']['icon'],
                    'treats': spec_info['data']['treats'],
                    'conditions': spec_info['data']['conditions'],
                    'confidence': min(100, (spec_info['score'] / len(symptoms)) * 100) if symptoms else 50,
                    'matched_symptoms': spec_info['matched_keywords'][:3]
                })
        else:
            # Default to primary care
            pc = self.specialist_database['primary_care']
            recommendations.append({
                'type': 'primary_care',
                'name': pc['name'],
                'icon': pc['icon'],
                'treats': pc['treats'],
                'conditions': pc['conditions'],
                'confidence': 70,
                'matched_symptoms': []
            })
        
        return {
            'specialists': recommendations,
            'urgency': urgency,
            'urgency_reasons': urgency_reasons,
            'symptom_count': len(symptoms)
        }
    
    def get_rag_enhanced_recommendation(self, symptoms: List[str], context: str = "") -> str:
        """
        Use RAG system to provide detailed specialist recommendation
        """
        if not self.rag:
            return ""
        
        # Get basic match first
        match_result = self.match_specialist(symptoms, context)
        
        if not match_result['specialists']:
            return ""
        
        top_specialist = match_result['specialists'][0]
        
        # Query RAG for more context
        query = f"When should someone see a {top_specialist['name']} for {', '.join(symptoms[:3])}"
        
        try:
            rag_result = self.rag.query(query, n_results=2)
            
            prompt = f"""Based on these symptoms: {', '.join(symptoms)}

Recommended specialist: {top_specialist['name']}

Medical context:
{rag_result['answer'][:800]}

Provide a brief explanation (3-4 sentences) of:
1. Why this specialist is recommended
2. What to expect at the appointment
3. How they can help

Keep it practical and reassuring."""
            
            explanation = self.rag.llm.generate([
                {"role": "system", "content": "You are a helpful medical guide explaining specialist referrals."},
                {"role": "user", "content": prompt}
            ], temperature=0.3, max_tokens=400)
            
            return explanation.replace('<s>', '').replace('</s>', '').strip()
        
        except:
            return ""
    
    def format_recommendation_text(self, match_result: Dict, enhanced_explanation: str = "") -> str:
        """Format specialist recommendation as readable text"""
        
        specialists = match_result['specialists']
        urgency = match_result['urgency']
        
        if not specialists:
            return "Please consult your primary care physician for guidance."
        
        # Build response
        response = ""
        
        # Urgency warning
        if urgency == 'urgent':
            response += "🚨 **URGENT**: These symptoms may require immediate attention.\n\n"
        
        response += f"**Recommended Specialist{'s' if len(specialists) > 1 else ''}:**\n\n"
        
        # Top specialist
        top = specialists[0]
        response += f"### {top['icon']} {top['name']}\n"
        response += f"**Specializes in:** {top['treats']}\n"
        response += f"**Confidence:** {top['confidence']:.0f}%\n\n"
        
        if top['matched_symptoms']:
            response += f"**Matched symptoms:** {', '.join(top['matched_symptoms'][:3])}\n\n"
        
        if enhanced_explanation:
            response += f"**Why this specialist?**\n{enhanced_explanation}\n\n"
        
        # Other possible specialists
        if len(specialists) > 1:
            response += "**Other relevant specialists:**\n"
            for spec in specialists[1:]:
                response += f"- {spec['icon']} {spec['name']} ({spec['confidence']:.0f}% match)\n"
            response += "\n"
        
        # Next steps
        response += "**Next Steps:**\n"
        if urgency == 'urgent':
            response += "1. Seek immediate medical attention or go to ER\n"
            response += "2. Call the specialist's office for urgent appointment\n"
        else:
            response += "1. Schedule an appointment with the recommended specialist\n"
            response += "2. Start with your primary care doctor if unsure\n"
            response += "3. Bring a list of your symptoms and any medications\n"
        
        return response


# Example usage and testing
if __name__ == "__main__":
    matcher = SpecialistMatcher()
    
    # Test 1: Chest pain
    result = matcher.match_specialist(
        symptoms=["chest pain", "shortness of breath", "heart palpitations"],
        context="45 year old male, history of high blood pressure"
    )
    
    print("Test 1: Chest pain")
    print(matcher.format_recommendation_text(result))
    print("\n" + "="*70 + "\n")
    
    # Test 2: Skin rash
    result = matcher.match_specialist(
        symptoms=["itchy rash", "dry skin", "red patches"],
        context="30 year old female"
    )
    
    print("Test 2: Skin rash")
    print(matcher.format_recommendation_text(result))
    print("\n" + "="*70 + "\n")
    
    # Test 3: Headache
    result = matcher.match_specialist(
        symptoms=["severe headache", "dizziness", "nausea"],
        context="25 year old"
    )
    
    print("Test 3: Headache")
    print(matcher.format_recommendation_text(result))