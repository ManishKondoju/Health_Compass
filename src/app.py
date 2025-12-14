import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import base64
import io

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag.rag_pipeline import HealthCompassRAG
from src.utils.symptom_tracker import SymptomTracker
from src.utils.healthcare_assistant import HealthcareAssistant
from src.utils.document_analyzer_enhanced import EnhancedDocumentAnalyzer
from src.utils.specialist_matcher import SpecialistMatcher
from src.utils.user_profile import UserProfile

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = UserProfile()

# Check if onboarding is needed - FIXED LOGIC
if 'show_onboarding' not in st.session_state:
    # On Streamlit Cloud (deployed), always show onboarding for new sessions
    # Check if profile has meaningful data (not just defaults)
    profile_data = st.session_state.user_profile.get_basic_info()
    
    # Profile is complete if name AND age are set
    has_valid_profile = (
        profile_data.get('name') and 
        profile_data.get('name') != '' and
        profile_data.get('age') and
        profile_data.get('age') > 0
    )
    
    st.session_state.show_onboarding = not has_valid_profile

# Add a URL parameter to force onboarding (useful for testing)
query_params = st.query_params
if query_params.get("reset") == "true":
    st.session_state.user_profile.reset_profile()
    st.session_state.show_onboarding = True
    st.query_params.clear()
    st.rerun()

# Initialize other session state
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load RAG
@st.cache_resource(show_spinner=False)
def load_rag():
    try:
        return HealthCompassRAG()
    except:
        return None

# ==================== ONBOARDING FLOW ====================
if st.session_state.show_onboarding:
    st.set_page_config(
        page_title="Welcome to Health Compass",
        page_icon="🏥",
        layout="wide"
    )
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #F0F4F8 0%, #E2E8F0 100%);
        }
        
        .onboarding-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
        }
        .onboarding-header h1 {
            color: white !important;
            font-size: 3rem;
            margin: 0;
        }
        .onboarding-header p {
            color: rgba(255,255,255,0.9) !important;
            font-size: 1.2rem;
        }
        .step-card {
            background: white;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        h1, h2, h3, h4, p, label, span, div {
            color: #1E293B !important;
        }
        
        /* Fix all inputs */
        .stTextInput input, .stNumberInput input, .stSelectbox select,
        .stTextArea textarea {
            background: white !important;
            color: #1E293B !important;
            border: 2px solid #E2E8F0 !important;
        }
        
        /* Fix dropdown specifically */
        .stSelectbox > div > div {
            background: white !important;
            color: #1E293B !important;
        }
        
        [data-baseweb="select"] {
            background: white !important;
        }
        
        [data-baseweb="select"] > div {
            background: white !important;
            color: #1E293B !important;
        }
        
        #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='onboarding-header'>
        <h1>👋 Welcome to Health Compass!</h1>
        <p>Let's set up your personalized health profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Multi-step form
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1
    
    profile = st.session_state.user_profile
    
    # Progress bar
    progress = st.session_state.onboarding_step / 4
    st.progress(progress)
    st.caption(f"Step {st.session_state.onboarding_step} of 4")
    
    # STEP 1: Basic Information
    if st.session_state.onboarding_step == 1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 📋 Step 1: Basic Information")
        st.write("Help us personalize your experience")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            age = st.number_input("Age *", min_value=1, max_value=120, value=30)
        
        with col2:
            gender = st.selectbox("Gender *", ["Select...", "Male", "Female", "Other", "Prefer not to say"])
            dob = st.date_input("Date of Birth", value=None)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True, type="primary"):
            if name and age and gender != "Select...":
                profile.update_basic_info(
                    name=name,
                    age=age,
                    gender=gender if gender != "Prefer not to say" else None,
                    dob=dob.isoformat() if dob else None
                )
                st.session_state.onboarding_step = 2
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")
    
    # STEP 2: Health Information
    elif st.session_state.onboarding_step == 2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 🏥 Step 2: Health Information")
        st.write("This helps us provide accurate health insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
            weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70)
        
        with col2:
            blood_type = st.selectbox("Blood Type", 
                ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        st.markdown("**Allergies** (optional)")
        allergies_input = st.text_area(
            "List any allergies (one per line)",
            placeholder="Penicillin\nPeanuts\nLatex",
            height=100
        )
        
        st.markdown("**Chronic Conditions** (optional)")
        conditions_input = st.text_area(
            "List any chronic conditions (one per line)",
            placeholder="Diabetes\nHypertension\nAsthma",
            height=100
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col_b2:
            if st.button("Continue →", use_container_width=True, type="primary"):
                profile.update_health_info(
                    height=height,
                    weight=weight,
                    blood_type=blood_type if blood_type != "Unknown" else None
                )
                
                if allergies_input:
                    for allergy in allergies_input.strip().split('\n'):
                        if allergy.strip():
                            profile.add_allergy(allergy.strip())
                
                if conditions_input:
                    for condition in conditions_input.strip().split('\n'):
                        if condition.strip():
                            profile.add_condition(condition.strip())
                
                st.session_state.onboarding_step = 3
                st.rerun()
    
    # STEP 3: Lifestyle
    elif st.session_state.onboarding_step == 3:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 🏃 Step 3: Lifestyle")
        st.write("Understanding your lifestyle helps provide better recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            smoking = st.selectbox("Smoking Status", 
                ["Never", "Former smoker", "Current smoker"])
            
            alcohol = st.selectbox("Alcohol Consumption",
                ["None", "Occasional (1-2 drinks/week)", "Moderate (3-7 drinks/week)", "Heavy (8+ drinks/week)"])
        
        with col2:
            exercise = st.selectbox("Exercise Level",
                ["Sedentary (little/no exercise)", 
                 "Light (1-2 days/week)",
                 "Moderate (3-5 days/week)",
                 "Active (6-7 days/week)"])
            
            diet = st.selectbox("Dietary Preference",
                ["Balanced/Regular", "Vegetarian", "Vegan", "Other"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col_b2:
            if st.button("Continue →", use_container_width=True, type="primary"):
                smoking_map = {"Never": "never", "Former smoker": "former", "Current smoker": "current"}
                alcohol_map = {"None": "none", "Occasional (1-2 drinks/week)": "occasional", 
                              "Moderate (3-7 drinks/week)": "moderate", "Heavy (8+ drinks/week)": "heavy"}
                exercise_map = {"Sedentary (little/no exercise)": "sedentary", "Light (1-2 days/week)": "light",
                               "Moderate (3-5 days/week)": "moderate", "Active (6-7 days/week)": "active"}
                diet_map = {"Balanced/Regular": "balanced", "Vegetarian": "vegetarian", "Vegan": "vegan", "Other": "other"}
                
                profile.update_lifestyle(
                    smoking=smoking_map[smoking],
                    alcohol=alcohol_map[alcohol],
                    exercise=exercise_map[exercise],
                    diet=diet_map[diet]
                )
                
                st.session_state.onboarding_step = 4
                st.rerun()
    
    # STEP 4: Preferences & Complete
    elif st.session_state.onboarding_step == 4:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## ⚙️ Step 4: Preferences")
        st.write("Final step - customize your experience")
        
        location = st.text_input("Location (City, State)", 
            placeholder="Boston, MA",
            help="Used to find nearby healthcare facilities")
        
        language = st.selectbox("Preferred Language",
            ["English", "Spanish", "Chinese", "French"])
        
        st.markdown("---")
        st.info("💡 You can update your profile anytime from the Dashboard")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()
        with col_b2:
            if st.button("🎉 Complete Setup", use_container_width=True, type="primary"):
                profile.update_preferences(language=language, location=location)
                profile.mark_setup_complete()
                st.session_state.show_onboarding = False
                st.session_state.language = language
                st.balloons()
                st.success("✅ Profile setup complete! Welcome to Health Compass!")
                import time
                time.sleep(1)
                st.rerun()

# ==================== MAIN APP ====================
else:
    st.set_page_config(
        page_title="Health Compass | AI Medical Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # FIXED CSS - ALL CONTRAST ISSUES RESOLVED
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #F0F4F8 0%, #E2E8F0 100%);
        }
        
        .main .block-container {
            padding: 1.5rem 2.5rem;
            max-width: 1600px;
        }
        
        /* Fix all text */
        h1, h2, h3, h4, h5, h6, p, span, div, label {
            color: #1E293B !important;
        }
        
        /* CRITICAL FIX: Dropdown/Select visibility */
        .stSelectbox > div > div {
            background: white !important;
            color: #1E293B !important;
        }
        
        [data-baseweb="select"] {
            background: white !important;
        }
        
        [data-baseweb="select"] > div {
            background: white !important;
            color: #1E293B !important;
        }
        
        [data-baseweb="select"] span {
            color: #1E293B !important;
        }
        
        /* Dropdown menu items */
        [role="listbox"] {
            background: white !important;
        }
        
        [role="option"] {
            background: white !important;
            color: #1E293B !important;
        }
        
        [role="option"]:hover {
            background: #F1F5F9 !important;
            color: #3B82F6 !important;
        }
        
        /* Header */
        .app-header {
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
            padding: 2rem 2.5rem;
            margin: -1.5rem -2.5rem 2.5rem -2.5rem;
            border-radius: 0 0 24px 24px;
            box-shadow: 0 10px 30px rgba(30, 64, 175, 0.2);
        }
        
        .app-header h1 {
            color: white !important;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
        }
        
        .app-header p {
            color: rgba(255, 255, 255, 0.95) !important;
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 20px;
            padding: 2.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #E2E8F0;
        }
        
        .card h3, .card h4 {
            color: #1E293B !important;
            font-weight: 700 !important;
        }
        
        /* Inputs */
        .stTextArea textarea, .stTextInput input, .stNumberInput input {
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            background: white !important;
            color: #1E293B !important;
        }
        
        .stTextArea textarea::placeholder, .stTextInput input::placeholder {
            color: #94A3B8 !important;
        }
        
        /* Labels */
        .stTextArea label, .stTextInput label, .stSelectbox label, 
        .stNumberInput label, .stFileUploader label, .stRadio label {
            color: #1E293B !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 0.8rem 2.5rem;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #475569 !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.8rem;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #F1F5F9;
            color: #3B82F6 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
            color: white !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E293B 0%, #334155 100%);
        }
        
        [data-testid="stSidebar"] * {
            color: rgba(255, 255, 255, 0.95) !important;
        }
        
        [data-testid="stSidebar"] h2 {
            color: white !important;
            font-weight: 700 !important;
        }
        
        /* Metrics */
        [data-testid="stMetric"] {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        [data-testid="stMetricValue"] {
            color: #3B82F6 !important;
            font-size: 2.5rem !important;
            font-weight: 800 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 600 !important;
        }
        
        /* Alerts */
        [data-baseweb="notification"] p {
            color: #1E293B !important;
            font-weight: 500 !important;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: white;
            border: 2px dashed #CBD5E1;
            border-radius: 12px;
            padding: 2rem;
        }
        
        [data-testid="stFileUploader"] label {
            color: #1E293B !important;
            font-weight: 600 !important;
        }
        
        /* Source cards */
        .source-card {
            background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
            border: 1px solid #BAE6FD;
            border-left: 4px solid #0EA5E9;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Language translations
    translations = {
        'English': {'header': 'Health Compass', 'tagline': 'AI-Powered Medical Assistant',
                   'search_placeholder': 'Ask any health question...', 'search_btn': 'Search',
                   'emergency': 'Emergency', 'call_911': 'Call 911'},
        'Spanish': {'header': 'Brújula de Salud', 'tagline': 'Asistente Médico con IA',
                   'search_placeholder': 'Haga cualquier pregunta...', 'search_btn': 'Buscar',
                   'emergency': 'Emergencia', 'call_911': 'Llamar al 911'},
        'Chinese': {'header': '健康指南针', 'tagline': 'AI医疗助手',
                   'search_placeholder': '提出任何健康问题...', 'search_btn': '搜索',
                   'emergency': '紧急情况', 'call_911': '拨打911'},
        'French': {'header': 'Boussole Santé', 'tagline': 'Assistant Médical IA',
                  'search_placeholder': 'Posez une question...', 'search_btn': 'Rechercher',
                  'emergency': 'Urgence', 'call_911': 'Appeler le 911'}
    }
    
    t = translations[st.session_state.language]
    
    # Header
    st.markdown(f"""
    <div class='app-header'>
        <h1>🏥 {t['header']}</h1>
        <p>{t['tagline']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with Profile
    with st.sidebar:
        # Profile Summary
        profile = st.session_state.user_profile
        summary = profile.get_profile_summary()
        
        st.markdown("## 👤 Profile")
        st.write(f"**{summary['name']}**")
        st.caption(f"{summary['age']} years • {summary.get('gender', 'N/A')}")
        
        if summary['bmi']:
            st.caption(f"BMI: {summary['bmi']} ({summary['bmi_category']})")
        
        if summary['conditions_count'] > 0:
            st.caption(f"📋 {summary['conditions_count']} condition(s)")
        
        st.markdown("---")
        
        st.markdown("## 🌍 Language")
        lang = st.selectbox("", ["English", "Spanish", "Chinese", "French"], 
                           index=["English", "Spanish", "Chinese", "French"].index(st.session_state.language),
                           label_visibility="collapsed")
        
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        
        st.markdown("---")
        
        st.markdown(f"## 🚨 {t['emergency']}")
        st.error(f"**{t['call_911']}**")
        st.caption("☎️ Poison: 1-800-222-1222")
        st.caption("🧠 Crisis: 988")
        
        st.markdown("---")
        
        st.markdown("## 📊 System")
        rag = load_rag()
        if rag:
            try:
                stats = rag.vector_db.get_stats()
                st.success("✓ Online")
                st.caption(f"{stats['total_documents']} documents")
            except:
                st.warning("Limited")
        else:
            st.error("Offline")
    
    # Main tabs - Dashboard first
    tab_dash, tab_qa, tab_doc, tab_symptom, tab_ai = st.tabs([
        "🏠 Dashboard",
        "🔍 Q&A",
        "📄 Documents",
        "📊 Symptoms",
        "💬 AI Chat"
    ])
    
    # ==================== TAB: DASHBOARD ====================
# REPLACE the Dashboard tab section in app.py with this FIXED version
# This fixes: Lifestyle editor, adds Reset Profile button, better editing

with tab_dash:
    st.markdown("### 🏠 Your Health Dashboard")
    
    profile = st.session_state.user_profile
    summary = profile.get_profile_summary()
    basic = profile.get_basic_info()
    health = profile.get_health_info()
    lifestyle = profile.get_lifestyle()
    
    st.markdown(f"## Welcome back, {summary['name']}! 👋")
    st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y')}")
    
    st.markdown("---")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Age", f"{summary['age']} years" if summary['age'] else "Not set")
    
    with col2:
        if summary['bmi']:
            st.metric("BMI", summary['bmi'], delta=summary['bmi_category'], delta_color="off")
        else:
            st.metric("BMI", "Not calculated")
    
    with col3:
        st.metric("Active Conditions", summary['conditions_count'])
    
    with col4:
        risk_color = {'Low': '🟢', 'Moderate': '🟡', 'High': '🔴'}
        st.metric("Lifestyle Risk", f"{risk_color.get(summary['lifestyle_risk'], '⚪')} {summary['lifestyle_risk']}")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📊 Health Overview")
        
        with st.expander("🩺 Medical Information", expanded=True):
            col_a, col_b = st.columns(2)
            
            with col_a:
                if health.get('height') and health.get('weight'):
                    st.write(f"**Height:** {health['height']} cm")
                    st.write(f"**Weight:** {health['weight']} kg")
                else:
                    st.info("Add height/weight to calculate BMI")
                
                if health.get('blood_type'):
                    st.write(f"**Blood Type:** {health['blood_type']}")
            
            with col_b:
                allergies = health.get('allergies', [])
                if allergies:
                    st.write(f"**Allergies:** {len(allergies)}")
                    for allergy in allergies[:3]:
                        st.caption(f"• {allergy}")
                    if len(allergies) > 3:
                        st.caption(f"• +{len(allergies)-3} more")
                else:
                    st.info("No allergies recorded")
        
        with st.expander("🏥 Chronic Conditions"):
            conditions = health.get('chronic_conditions', [])
            if conditions:
                for condition in conditions:
                    st.write(f"• {condition}")
            else:
                st.info("No conditions recorded")
        
        with st.expander("💊 Current Medications"):
            medications = health.get('current_medications', [])
            if medications:
                for med in medications:
                    st.write(f"**{med.get('name')}**")
                    st.caption(f"{med.get('dosage', '')} - {med.get('frequency', '')}")
            else:
                st.info("No medications recorded")
    
    with col_right:
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("📝 Log Symptom", use_container_width=True):
            st.info("👉 Go to Symptoms tab")
        
        if st.button("📄 Analyze Document", use_container_width=True):
            st.info("👉 Go to Documents tab")
        
        if st.button("💬 Ask AI", use_container_width=True):
            st.info("👉 Go to AI Chat tab")
        
        st.markdown("---")
        
        st.markdown("### 🏃 Lifestyle")
        
        lifestyle_icons = {
            'smoking': {'never': '✅ Non-smoker', 'former': '⚠️ Former', 'current': '🚫 Smoker'},
            'exercise': {'sedentary': '😴 Sedentary', 'light': '🚶 Light', 
                        'moderate': '🏃 Moderate', 'active': '💪 Active'},
            'alcohol': {'none': '✅ None', 'occasional': '🍷 Occasional', 
                       'moderate': '⚠️ Moderate', 'heavy': '🚫 Heavy'}
        }
        
        st.write(lifestyle_icons['smoking'].get(lifestyle.get('smoking', 'never'), '✅ Non-smoker'))
        st.write(lifestyle_icons['exercise'].get(lifestyle.get('exercise', 'sedentary'), '😴 Sedentary'))
        st.write(lifestyle_icons['alcohol'].get(lifestyle.get('alcohol', 'none'), '✅ None'))
        
        st.markdown("---")
        
        # Profile management buttons
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            if st.button("⚙️ Edit Profile", use_container_width=True):
                st.session_state.show_profile_editor = True
                st.rerun()
        
        with col_edit2:
            if st.button("🔄 Reset Profile", use_container_width=True):
                st.session_state.user_profile.reset_profile()
                st.session_state.show_onboarding = True
                st.session_state.chat_history = []
                st.success("Profile reset! Reloading...")
                import time
                time.sleep(1)
                st.rerun()
    
    # FIXED: Profile Editor with working Lifestyle section
    if st.session_state.get('show_profile_editor', False):
        st.markdown("---")
        st.markdown("## ⚙️ Edit Profile")
        
        edit_tab = st.radio("What would you like to edit?", 
                           ["Basic Info", "Health Info", "Lifestyle", "Close Editor"], 
                           horizontal=True,
                           key="edit_tab_selector")
        
        if edit_tab == "Basic Info":
            st.markdown("### 📋 Basic Information")
            
            with st.form("edit_basic"):
                name = st.text_input("Full Name", value=basic.get('name', ''))
                age = st.number_input("Age", value=basic.get('age', 30), min_value=1, max_value=120)
                gender = st.selectbox("Gender", 
                                     ["Male", "Female", "Other", "Prefer not to say"],
                                     index=["Male", "Female", "Other", "Prefer not to say"].index(basic.get('gender', 'Male')) if basic.get('gender') in ["Male", "Female", "Other", "Prefer not to say"] else 0)
                
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    profile.update_basic_info(name=name, age=age, gender=gender)
                    st.success("✅ Profile updated!")
                    st.session_state.show_profile_editor = False
                    st.rerun()
        
        elif edit_tab == "Health Info":
            st.markdown("### 🏥 Health Information")
            
            with st.form("edit_health"):
                col_h1, col_h2 = st.columns(2)
                
                with col_h1:
                    height = st.number_input("Height (cm)", 
                                            value=health.get('height', 170), 
                                            min_value=50, 
                                            max_value=250)
                    weight = st.number_input("Weight (kg)", 
                                            value=health.get('weight', 70), 
                                            min_value=20, 
                                            max_value=300)
                
                with col_h2:
                    blood_type = st.selectbox("Blood Type", 
                                             ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                             index=["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(health.get('blood_type', 'Unknown')) if health.get('blood_type') in ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] else 0)
                
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    profile.update_health_info(
                        height=height, 
                        weight=weight,
                        blood_type=blood_type if blood_type != "Unknown" else None
                    )
                    st.success("✅ Profile updated!")
                    st.session_state.show_profile_editor = False
                    st.rerun()
        
        elif edit_tab == "Lifestyle":
            st.markdown("### 🏃 Lifestyle Information")
            
            with st.form("edit_lifestyle"):
                smoking = st.selectbox("Smoking Status", 
                                      ["Never", "Former smoker", "Current smoker"],
                                      index=["never", "former", "current"].index(lifestyle.get('smoking', 'never')))
                
                alcohol = st.selectbox("Alcohol Consumption",
                                      ["None", "Occasional", "Moderate", "Heavy"],
                                      index=["none", "occasional", "moderate", "heavy"].index(lifestyle.get('alcohol', 'none')))
                
                exercise = st.selectbox("Exercise Level",
                                       ["Sedentary", "Light", "Moderate", "Active"],
                                       index=["sedentary", "light", "moderate", "active"].index(lifestyle.get('exercise', 'sedentary')))
                
                diet = st.selectbox("Dietary Preference",
                                   ["Balanced", "Vegetarian", "Vegan", "Other"],
                                   index=["balanced", "vegetarian", "vegan", "other"].index(lifestyle.get('diet', 'balanced')))
                
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    # Map display values to internal values
                    smoking_map = {"Never": "never", "Former smoker": "former", "Current smoker": "current"}
                    alcohol_map = {"None": "none", "Occasional": "occasional", "Moderate": "moderate", "Heavy": "heavy"}
                    exercise_map = {"Sedentary": "sedentary", "Light": "light", "Moderate": "moderate", "Active": "active"}
                    diet_map = {"Balanced": "balanced", "Vegetarian": "vegetarian", "Vegan": "vegan", "Other": "other"}
                    
                    profile.update_lifestyle(
                        smoking=smoking_map.get(smoking, 'never'),
                        alcohol=alcohol_map.get(alcohol, 'none'),
                        exercise=exercise_map.get(exercise, 'sedentary'),
                        diet=diet_map.get(diet, 'balanced')
                    )
                    st.success("✅ Lifestyle updated!")
                    st.session_state.show_profile_editor = False
                    st.rerun()
        
        elif edit_tab == "Close Editor":
            st.session_state.show_profile_editor = False
            st.rerun()    

    # ==================== TAB: Q&A SEARCH ====================
    with tab_qa:
        st.markdown("### 🔍 Medical Information Search")
        st.warning("⚠️ Educational only. Not medical advice. Call 911 for emergencies.")
        
        query = st.text_area("Ask your health question:", height=120, 
                            placeholder=t['search_placeholder'], key="search_query")
        
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            search_btn = st.button(f"🔍 {t['search_btn']}", use_container_width=True, type="primary")
        with col_b2:
            if st.button("Clear", use_container_width=True):
                st.session_state.search_query = ''
                st.rerun()
        
        if search_btn and query:
            rag = load_rag()
            if rag:
                with st.spinner("Searching..."):
                    result = rag.query(query, n_results=5)
                
                if result.get('is_emergency'):
                    st.error("🚨 MEDICAL EMERGENCY - CALL 911 IMMEDIATELY")
                    st.stop()
                
                st.markdown("---")
                st.markdown("### 📋 Answer")
                st.write(result['answer'])
                
                if result.get('sources'):
                    st.markdown("### 📚 Sources")
                    for i, source in enumerate(result['sources'], 1):
                        st.markdown(f"""
                        <div class='source-card'>
                            <strong>{i}. {source.get('source', 'Unknown')}</strong><br>
                            {source.get('title', '')}<br>
                            <a href="{source.get('url', '#')}" target="_blank">View →</a>
                        </div>
                        """, unsafe_allow_html=True)
    
    # ==================== TAB: DOCUMENT ANALYZER ====================
    with tab_doc:
        st.markdown("### 📄 Medical Document Analyzer")
        
        rag_system = load_rag()
        analyzer_doc = EnhancedDocumentAnalyzer(rag_system=rag_system)
        
        col_up1, col_up2 = st.columns([2, 1])
        
        with col_up1:
            st.markdown("#### 📤 Upload Document")
            uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'png', 'jpg', 'jpeg', 'txt'])
        
        with col_up2:
            st.markdown("#### 👤 Gender")
            # Auto-fill from profile
            profile = st.session_state.user_profile
            profile_gender = profile.get_basic_info().get('gender')
            default_gender = profile_gender if profile_gender in ['Male', 'Female'] else 'Not specified'
            
            gender = st.selectbox("For reference ranges", 
                                 ["Not specified", "Male", "Female"],
                                 index=["Not specified", "Male", "Female"].index(default_gender) if default_gender in ["Not specified", "Male", "Female"] else 0)
            
            if profile_gender and gender != "Not specified":
                st.caption(f"✅ Using profile: {profile_gender}")
        
        if uploaded_file:
            st.success(f"✅ Uploaded: **{uploaded_file.name}**")
            
            analysis_type = st.radio("Analysis type:", 
                ["🔬 Lab Values Analysis", "📋 Plain English Explanation", 
                 "⚠️ Abnormal Values Only", "❓ Doctor Questions", "💊 Medication List"],
                horizontal=False)
            
            if st.button("🤖 Analyze Document", type="primary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    file_bytes = uploaded_file.getvalue()
                    gender_param = None if gender == "Not specified" else gender
                    
                    if "Lab Values" in analysis_type:
                        result = analyzer_doc.analyze_document(file_bytes, uploaded_file.type, gender_param)
                        
                        if 'error' not in result:
                            st.success("✅ Analysis complete!")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Tests", result['total_tests'])
                            with col2:
                                st.metric("Abnormal", result['abnormal_count'])
                            with col3:
                                st.metric("Normal", result['total_tests'] - result['abnormal_count'])
                            
                            st.markdown("---")
                            st.markdown(result['report'])
        else:
            st.info("👆 Upload a medical document to analyze")
    
    # ==================== TAB: SYMPTOM TRACKER ====================
    with tab_symptom:
        st.markdown("### 📊 Symptom Tracker")
        
        tracker = SymptomTracker()
        specialist_matcher = SpecialistMatcher(rag_system=load_rag())
        
        col1, col2 = st.columns([1.2, 1])
        
        with col1:
            st.markdown("#### 📝 Log Symptom")
            
            with st.form("symptom_form", clear_on_submit=True):
                symptom = st.text_input("Symptom:", placeholder="e.g., Headache")
                severity = st.slider("Severity:", 1, 10, 5)
                notes = st.text_area("Notes:", height=80, placeholder="Details...")
                
                if st.form_submit_button("💾 Log", use_container_width=True):
                    if symptom:
                        tracker.log_symptom(symptom, severity, notes)
                        st.success("✅ Logged!")
                        st.rerun()
        
        with col2:
            st.markdown("#### 📈 Stats")
            insights = tracker.get_ai_insights()
            
            if insights:
                st.metric("Entries", insights['total_entries'])
                st.metric("Avg Severity", f"{insights['average_severity']}/10")
            else:
                st.info("Log 3+ symptoms")
        
        # Specialist Finder
        entries = tracker.get_all_symptoms()
        if entries:
            st.markdown("---")
            st.markdown("## 👨‍⚕️ Which Specialist?")
            
            recent = [e['symptom'] for e in entries[-5:]]
            st.write(f"Based on: {', '.join(recent[:3])}")
            
            if st.button("🔍 Find Right Specialist", type="primary"):
                with st.spinner("Analyzing..."):
                    match_result = specialist_matcher.match_specialist(recent)
                    
                    if match_result['specialists']:
                        top = match_result['specialists'][0]
                        st.markdown(f"### {top['icon']} {top['name']}")
                        st.write(f"**Confidence:** {top['confidence']:.0f}%")
                        st.write(f"**Treats:** {top['treats']}")
                        
                        if match_result['urgency'] == 'urgent':
                            st.error("🚨 URGENT - Seek immediate care")
    
    # ==================== TAB: AI ASSISTANT ====================
    with tab_ai:
        st.markdown("### 💬 AI Healthcare Assistant")
        
        # Get profile for personalized responses
        profile = st.session_state.user_profile
        
        assistant = HealthcareAssistant()
        
        if not st.session_state.chat_history:
            st.session_state.chat_history = [{
                'role': 'assistant',
                'content': f"""Hello! I'm your AI assistant. I can help with medical questions, medications, and finding healthcare facilities. How can I help?"""
            }]
        
        # Display chat
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role'], avatar="🤖" if msg['role'] == 'assistant' else "👤"):
                st.write(msg['content'])
        
        # Chat input
        user_input = st.chat_input("Type your message...")
        
        if user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            rag = load_rag()
            if rag:
                with st.spinner("🤖 Thinking..."):
                    
                    # Get profile context
                    profile_context = profile.get_context_for_ai()
                    
                    # Query vector DB
                    rag_result = rag.query(user_input, n_results=3)
                    
                    # Build personalized prompt
                    prompt = f"""Patient Profile:
{profile_context}

Patient asks: {user_input}

Medical info:
{rag_result['answer'][:1200]}

Provide brief, personalized response (3-4 sentences):
- Consider their age, gender, conditions, medications
- Give practical advice
- Mention profile factors when relevant
- Skip legal disclaimers

Be helpful and conversational."""
                    
                    response = rag.llm.generate([
                        {"role": "system", "content": "Personalized healthcare assistant."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.4, max_tokens=500)
                    
                    response = response.replace('<s>', '').replace('</s>', '').strip()
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    
                    st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #64748B;'>
        <div style='font-size: 1.3rem; font-weight: 700; color: #1E40AF;'>
            🏥 Health Compass
        </div>
        <div style='font-size: 0.95rem;'>
            Educational Information Only • Not Medical Advice
        </div>
        <div style='font-size: 0.85rem; margin-top: 1rem; color: #94A3B8;'>
            INFO 7390 Final Project | Manish K | Northeastern University
        </div>
    </div>
    """, unsafe_allow_html=True)
