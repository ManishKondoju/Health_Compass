from datetime import datetime

class HealthTools:
    """Collection of health calculators and assessment tools"""
    
    @staticmethod
    def calculate_bmi(weight_lbs, height_inches):
        """Calculate Body Mass Index"""
        bmi = (weight_lbs / (height_inches ** 2)) * 703
        
        if bmi < 18.5:
            category = "Underweight"
            color = "blue"
            advice = "May need to gain weight. Consult doctor or nutritionist."
        elif bmi < 25:
            category = "Normal weight"
            color = "green"
            advice = "Maintain healthy habits!"
        elif bmi < 30:
            category = "Overweight"
            color = "orange"
            advice = "Consider lifestyle changes. Discuss with doctor."
        else:
            category = "Obese"
            color = "red"
            advice = "Health risks increase. Consult doctor about weight management."
        
        return {
            'bmi': round(bmi, 1),
            'category': category,
            'color': color,
            'advice': advice
        }
    
    @staticmethod
    def calculate_hydration(weight_lbs, activity_level):
        """Calculate daily water intake needs"""
        base_oz = weight_lbs / 2
        
        multipliers = {
            "Sedentary": 1.0,
            "Lightly Active": 1.1,
            "Moderately Active": 1.2,
            "Very Active": 1.4
        }
        
        multiplier = multipliers.get(activity_level, 1.0)
        daily_oz = base_oz * multiplier
        daily_liters = daily_oz * 0.0295735
        glasses_8oz = daily_oz / 8
        
        return {
            'ounces': round(daily_oz, 0),
            'liters': round(daily_liters, 1),
            'glasses': round(glasses_8oz, 0),
            'activity_adjustment': f"{int((multiplier - 1) * 100)}% more due to {activity_level.lower()} lifestyle"
        }
    
    @staticmethod
    def blood_pressure_assessment(systolic, diastolic):
        """Assess blood pressure reading"""
        
        if systolic >= 180 or diastolic >= 120:
            return {
                'category': 'Hypertensive Crisis',
                'action': '🚨 SEEK EMERGENCY CARE IMMEDIATELY',
                'color': 'red',
                'advice': 'Call 911 or go to ER. This is a medical emergency.',
                'risk': 'HIGH - Immediate risk of organ damage'
            }
        
        elif systolic >= 140 or diastolic >= 90:
            return {
                'category': 'High Blood Pressure (Stage 2 Hypertension)',
                'action': '⚠️ Consult your doctor soon',
                'color': 'orange',
                'advice': 'Schedule appointment to discuss medication and lifestyle changes.',
                'risk': 'ELEVATED - Increased risk of heart disease and stroke'
            }
        
        elif systolic >= 130 or diastolic >= 80:
            return {
                'category': 'High Blood Pressure (Stage 1 Hypertension)',
                'action': '💡 Lifestyle changes recommended',
                'color': 'yellow',
                'advice': 'Monitor regularly. Discuss with doctor. Diet, exercise, stress reduction.',
                'risk': 'MODERATE - Lifestyle changes may prevent progression'
            }
        
        elif systolic >= 120:
            return {
                'category': 'Elevated Blood Pressure',
                'action': '💡 Watch your numbers',
                'color': 'yellow',
                'advice': 'Adopt healthier lifestyle to prevent high blood pressure.',
                'risk': 'LOW - Early intervention recommended'
            }
        
        else:
            return {
                'category': 'Normal Blood Pressure',
                'action': '✅ Keep up the good work!',
                'color': 'green',
                'advice': 'Maintain healthy habits: diet, exercise, limit salt and alcohol.',
                'risk': 'NORMAL - Excellent cardiovascular health'
            }
    
    @staticmethod
    def get_screening_schedule(age, sex):
        """Get recommended health screenings based on age and sex"""
        screenings = []
        
        # Universal screenings
        if age >= 18:
            screenings.append({
                'test': 'Blood Pressure',
                'frequency': 'At least once every 2 years (annually if elevated)',
                'why': 'Detect hypertension early to prevent heart disease and stroke',
                'category': 'Cardiovascular'
            })
        
        if age >= 20:
            screenings.append({
                'test': 'Cholesterol Screening',
                'frequency': 'Every 5 years (more often if high risk)',
                'why': 'Assess heart disease risk',
                'category': 'Cardiovascular'
            })
        
        if age >= 35:
            screenings.append({
                'test': 'Diabetes Screening (Fasting Blood Glucose or A1C)',
                'frequency': 'Every 3 years (annually if prediabetic or high risk)',
                'why': 'Detect prediabetes and diabetes early',
                'category': 'Metabolic'
            })
        
        if age >= 45:
            screenings.append({
                'test': 'Colorectal Cancer Screening',
                'frequency': 'Every 10 years (colonoscopy) or annually (stool test)',
                'why': 'Detect colon cancer early when most treatable',
                'category': 'Cancer'
            })
        
        if age >= 65:
            screenings.append({
                'test': 'Bone Density Scan (DEXA)',
                'frequency': 'At age 65, then as recommended',
                'why': 'Screen for osteoporosis',
                'category': 'Bone Health'
            })
        
        # Female-specific screenings
        if sex == "Female":
            if age >= 21:
                screenings.append({
                    'test': 'Pap Smear',
                    'frequency': 'Every 3 years (ages 21-65)',
                    'why': 'Cervical cancer screening',
                    'category': 'Cancer - Women\'s Health'
                })
            
            if age >= 25 and age <= 65:
                screenings.append({
                    'test': 'HPV Test',
                    'frequency': 'Every 5 years (or with Pap smear every 3 years)',
                    'why': 'Detect HPV that can cause cervical cancer',
                    'category': 'Cancer - Women\'s Health'
                })
            
            if age >= 40:
                screenings.append({
                    'test': 'Mammogram',
                    'frequency': 'Every 1-2 years (ages 40-74), annually after 50',
                    'why': 'Breast cancer screening',
                    'category': 'Cancer - Women\'s Health'
                })
        
        # Male-specific screenings
        if sex == "Male":
            if age >= 50:
                screenings.append({
                    'test': 'Prostate Cancer Screening (PSA test)',
                    'frequency': 'Discuss with doctor - individualized decision',
                    'why': 'Prostate cancer detection (discuss risks/benefits with doctor)',
                    'category': 'Cancer - Men\'s Health'
                })
        
        # Additional screenings for older adults
        if age >= 50:
            screenings.append({
                'test': 'Lung Cancer Screening (Low-dose CT)',
                'frequency': 'Annually if high risk (heavy smoker or former smoker)',
                'why': 'Detect lung cancer early in high-risk individuals',
                'category': 'Cancer'
            })
        
        return screenings
    
    def get_care_locations(self, location, care_type):
        """Get care facility locations - educational examples"""
        
        # NOTE: In production, this would integrate with:
        # - Google Maps API
        # - Hospital finder APIs
        # - Insurance provider directories
        
        # For educational purposes, showing Boston area examples
        
        if care_type == 'emergency':
            return {
                'type': 'Emergency Room',
                'locations': [
                    {
                        'name': 'Massachusetts General Hospital Emergency Department',
                        'address': '55 Fruit Street, Boston, MA 02114',
                        'phone': '(617) 726-2000',
                        'distance': 'Call 911 for ambulance',
                        'wait_time': 'Variable - depends on severity',
                        'level': 'Level 1 Trauma Center',
                        'note': '24/7 Emergency care for all conditions'
                    },
                    {
                        'name': 'Brigham and Women\'s Hospital Emergency',
                        'address': '75 Francis Street, Boston, MA 02115',
                        'phone': '(617) 732-5500',
                        'distance': 'Call 911 for ambulance',
                        'wait_time': 'Variable',
                        'level': 'Level 1 Trauma Center',
                        'note': '24/7 Comprehensive emergency services'
                    },
                    {
                        'name': 'Beth Israel Deaconess Medical Center Emergency',
                        'address': '330 Brookline Avenue, Boston, MA 02215',
                        'phone': '(617) 667-7000',
                        'distance': 'Call 911 for ambulance',
                        'wait_time': 'Variable',
                        'level': 'Level 1 Trauma Center',
                        'note': '24/7 Full-service emergency department'
                    }
                ],
                'note': '🚨 FOR LIFE-THREATENING EMERGENCIES: CALL 911 IMMEDIATELY',
                'tips': [
                    'Call 911 - don\'t drive yourself if serious',
                    'Have someone drive you if non-life-threatening',
                    'Bring ID, insurance card, medication list',
                    'Be prepared for wait times based on severity'
                ]
            }
        
        elif care_type == 'urgent':
            return {
                'type': 'Urgent Care Center',
                'locations': [
                    {
                        'name': 'CareWell Urgent Care - Fenway',
                        'address': '1330 Boylston Street, Boston, MA',
                        'phone': '(617) 383-1900',
                        'hours': 'Mon-Fri: 8 AM - 8 PM, Sat-Sun: 8 AM - 8 PM',
                        'distance': 'Check Google Maps',
                        'services': 'X-rays, lab tests, minor procedures',
                        'wait_time': 'Usually 15-45 minutes'
                    },
                    {
                        'name': 'AFC Urgent Care',
                        'address': 'Multiple Boston locations',
                        'phone': 'Check website for nearest location',
                        'hours': 'Typically 8 AM - 8 PM',
                        'distance': 'Various locations',
                        'services': 'Illness, injuries, testing',
                        'wait_time': 'Call ahead'
                    },
                    {
                        'name': 'CVS MinuteClinic',
                        'address': 'Many locations throughout Boston',
                        'phone': 'Check local CVS',
                        'hours': 'Varies by location',
                        'distance': 'Find nearest CVS',
                        'services': 'Minor illnesses, vaccines, screenings',
                        'wait_time': 'Often can schedule online'
                    }
                ],
                'note': '💡 Urgent care is for non-life-threatening conditions that need care today',
                'tips': [
                    'Call ahead to check wait times',
                    'Verify your insurance is accepted',
                    'Bring ID, insurance card, medication list',
                    'Some offer online check-in'
                ]
            }
        
        else:  # primary care
            return {
                'type': 'Primary Care Options',
                'locations': [
                    {
                        'name': 'Your Primary Care Physician (PCP)',
                        'info': 'Check your insurance card for your assigned doctor',
                        'action': 'Call office to schedule appointment',
                        'timeframe': 'Usually within 1-2 weeks',
                        'note': 'Best for ongoing care and non-urgent issues'
                    },
                    {
                        'name': 'Walk-in Clinics',
                        'info': 'CVS MinuteClinic, Walgreens Healthcare Clinic',
                        'action': 'Walk in or schedule online',
                        'timeframe': 'Same day or next day',
                        'note': 'Good for minor illnesses and vaccines'
                    },
                    {
                        'name': 'Telehealth Services',
                        'info': 'Virtual doctor visits',
                        'action': 'Download app: Teladoc, MDLive, Amwell',
                        'timeframe': 'Often same day',
                        'note': 'Convenient for consultations from home'
                    },
                    {
                        'name': 'Community Health Centers',
                        'info': 'Federally Qualified Health Centers (FQHCs)',
                        'action': 'Search: findahealthcenter.hrsa.gov',
                        'timeframe': 'Varies',
                        'note': 'Sliding scale fees based on income'
                    }
                ],
                'note': '💡 Check your insurance provider directory for in-network doctors',
                'tips': [
                    'Ask for earliest available appointment',
                    'Request cancellation list for sooner openings',
                    'Prepare questions before visit',
                    'Bring current medication list'
                ]
            }