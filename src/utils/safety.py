class SafetyChecker:
    """Detect emergency symptoms and safety concerns"""
    
    def __init__(self):
        # Emergency keywords that require immediate 911 call
        self.emergency_keywords = [
            # Cardiac emergencies
            "chest pain", "heart attack", "severe chest pressure",
            "crushing chest pain", "chest discomfort radiating",
            
            # Respiratory emergencies
            "can't breathe", "difficulty breathing", "choking",
            "severe shortness of breath", "gasping for air",
            "blue lips", "blue face",
            
            # Neurological emergencies
            "stroke", "stroke symptoms", "loss of consciousness",
            "passed out", "fainted", "unresponsive",
            "severe head injury", "head trauma", "seizure",
            "sudden confusion", "can't speak", "slurred speech",
            "face drooping", "arm weakness", "sudden numbness",
            
            # Severe bleeding/trauma
            "severe bleeding", "bleeding won't stop", "heavy bleeding",
            "major injury", "severe trauma", "broken neck",
            "spinal injury",
            
            # Allergic reactions
            "severe allergic reaction", "anaphylaxis", "anaphylactic shock",
            "throat swelling", "throat closing", "can't swallow",
            
            # Mental health emergencies
            "suicidal", "want to die", "kill myself", "end my life",
            "suicide plan", "going to kill",
            
            # Other emergencies
            "severe pain", "unbearable pain", "excruciating pain",
            "poisoning", "overdose", "took too many pills",
            "severe burn", "third degree burn",
            "compound fracture", "bone through skin"
        ]
        
        # Urgent care keywords (within 24 hours)
        self.urgent_keywords = [
            "high fever", "fever over 103", "fever won't go down",
            "persistent vomiting", "can't keep anything down",
            "severe dehydration", "dizzy and weak",
            "signs of infection", "wound infection", "red streaks",
            "pregnancy complications", "bleeding during pregnancy",
            "severe pain that won't go away",
            "broken bone", "think i broke", "deep cut",
            "eye injury", "something in eye",
            "severe headache", "worst headache of life",
            "stiff neck with fever"
        ]
    
    def check_query(self, query: str) -> dict:
        """
        Check query for safety concerns
        
        Returns:
            dict with 'level', 'message', and 'keyword_triggered'
        """
        query_lower = query.lower()
        
        # Check for emergencies
        for keyword in self.emergency_keywords:
            if keyword in query_lower:
                return {
                    'level': 'EMERGENCY',
                    'message': self._get_emergency_message(),
                    'keyword_triggered': keyword
                }
        
        # Check for urgent care needs
        for keyword in self.urgent_keywords:
            if keyword in query_lower:
                return {
                    'level': 'URGENT',
                    'message': self._get_urgent_message(),
                    'keyword_triggered': keyword
                }
        
        # No safety concerns
        return {
            'level': 'INFO',
            'message': None,
            'keyword_triggered': None
        }
    
    def _get_emergency_message(self) -> str:
        """Emergency response message"""
        return """🚨 MEDICAL EMERGENCY - CALL 911 IMMEDIATELY 🚨

The symptoms you described may be a life-threatening emergency.

⚠️ DO NOT WAIT - CALL 911 OR GO TO EMERGENCY ROOM NOW

Call 911 if you're experiencing:
- Chest pain or severe pressure
- Difficulty breathing or can't breathe
- Signs of stroke (face drooping, arm weakness, speech difficulty, time to call 911)
- Severe bleeding that won't stop
- Loss of consciousness or unresponsiveness
- Seizures
- Severe allergic reaction (throat swelling, difficulty breathing)
- Thoughts of suicide or harming yourself
- Severe trauma or injury

📞 CALL 911 NOW - Do not drive yourself
📞 If you're having suicidal thoughts, call 988 (Suicide & Crisis Lifeline)

This is a medical emergency. Online information cannot help in emergencies.
SEEK IMMEDIATE PROFESSIONAL HELP."""
    
    def _get_urgent_message(self) -> str:
        """Urgent care message"""
        return """⚠️ URGENT MEDICAL ATTENTION RECOMMENDED

The symptoms you described may require prompt medical care.

Please take these steps:
1. Contact your doctor or healthcare provider within 24 hours
2. Visit an urgent care clinic if your doctor is unavailable
3. Go to the emergency room if symptoms worsen
4. Call 911 if you develop emergency symptoms

Do not rely solely on online information for urgent medical concerns.
Healthcare professionals can properly evaluate your specific situation.

If symptoms worsen or you develop emergency symptoms, call 911 immediately."""

# Test the safety checker
if __name__ == "__main__":
    checker = SafetyChecker()
    
    print("Testing Safety Checker\n")
    print("="*60)
    
    test_cases = [
        ("I have a headache", "INFO"),
        ("Severe chest pain and shortness of breath", "EMERGENCY"),
        ("High fever that won't go down", "URGENT"),
        ("What causes diabetes?", "INFO"),
        ("I want to kill myself", "EMERGENCY"),
        ("Deep cut that won't stop bleeding", "URGENT"),
    ]
    
    for query, expected in test_cases:
        result = checker.check_query(query)
        status = "✅" if result['level'] == expected else "❌"
        
        print(f"\n{status} Query: {query}")
        print(f"   Level: {result['level']} (Expected: {expected})")
        if result['keyword_triggered']:
            print(f"   Triggered by: {result['keyword_triggered']}")
        if result['message']:
            print(f"   Message: {result['message'][:100]}...")
    
    print("\n" + "="*60)