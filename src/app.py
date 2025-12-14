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

# Initialize user profile
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = UserProfile()

# Better onboarding detection - check for REAL data
if 'show_onboarding' not in st.session_state:
    profile_data = st.session_state.user_profile.get_basic_info()
    has_valid_profile = (
        profile_data.get('name') and 
        profile_data.get('name') != '' and
        profile_data.get('age') and
        profile_data.get('age') > 0
    )
    st.session_state.show_onboarding = not has_valid_profile

# Initialize session state
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
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: linear-gradient(135deg, #F0F4F8 0%, #E2E8F0 100%); }
        .onboarding-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;
        }
        .onboarding-header h1 { color: white !important; font-size: 3rem; margin: 0; }
        .onboarding-header p { color: rgba(255,255,255,0.9) !important; font-size: 1.2rem; }
        .step-card { background: white; padding: 2.5rem; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1rem 0; }
        h1, h2, h3, h4, p, label { color: #1E293B !important; }
        .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
            background: white !important; color: #1E293B !important; border: 2px solid #E2E8F0 !important;
        }
        .stSelectbox > div > div, [data-baseweb="select"] { background: white !important; color: #1E293B !important; }
        [role="option"] { background: white !important; color: #1E293B !important; }
        #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='onboarding-header'>
        <h1>👋 Welcome to Health Compass!</h1>
        <p>Let's set up your personalized health profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1
    
    profile = st.session_state.user_profile
    progress = st.session_state.onboarding_step / 4
    st.progress(progress)
    st.caption(f"Step {st.session_state.onboarding_step} of 4")
    
    # STEP 1
    if st.session_state.onboarding_step == 1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 📋 Step 1: Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            age = st.number_input("Age *", min_value=1, max_value=120, value=30)
        with col2:
            gender = st.selectbox("Gender *", ["Select...", "Male", "Female", "Other"])
            dob = st.date_input("Date of Birth", value=None)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True, type="primary"):
            if name and age and gender != "Select...":
                profile.update_basic_info(name=name, age=age, gender=gender, dob=dob.isoformat() if dob else None)
                st.session_state.onboarding_step = 2
                st.rerun()
            else:
                st.error("Please fill required fields")
    
    # STEP 2
    elif st.session_state.onboarding_step == 2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 🏥 Step 2: Health Information")
        
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
            weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70)
        with col2:
            blood_type = st.selectbox("Blood Type", ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        allergies_input = st.text_area("Allergies (one per line)", placeholder="Penicillin\nPeanuts", height=100)
        conditions_input = st.text_area("Chronic Conditions (one per line)", placeholder="Diabetes\nHypertension", height=100)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col_b2:
            if st.button("Continue →", use_container_width=True, type="primary"):
                profile.update_health_info(height=height, weight=weight, blood_type=blood_type if blood_type != "Unknown" else None)
                if allergies_input:
                    for a in allergies_input.strip().split('\n'):
                        if a.strip():
                            profile.add_allergy(a.strip())
                if conditions_input:
                    for c in conditions_input.strip().split('\n'):
                        if c.strip():
                            profile.add_condition(c.strip())
                st.session_state.onboarding_step = 3
                st.rerun()
    
    # STEP 3
    elif st.session_state.onboarding_step == 3:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 🏃 Step 3: Lifestyle")
        
        col1, col2 = st.columns(2)
        with col1:
            smoking = st.selectbox("Smoking", ["Never", "Former smoker", "Current smoker"])
            alcohol = st.selectbox("Alcohol", ["None", "Occasional", "Moderate", "Heavy"])
        with col2:
            exercise = st.selectbox("Exercise", ["Sedentary", "Light", "Moderate", "Active"])
            diet = st.selectbox("Diet", ["Balanced", "Vegetarian", "Vegan", "Other"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col_b2:
            if st.button("Continue →", use_container_width=True, type="primary"):
                profile.update_lifestyle(
                    smoking={"Never": "never", "Former smoker": "former", "Current smoker": "current"}[smoking],
                    alcohol={"None": "none", "Occasional": "occasional", "Moderate": "moderate", "Heavy": "heavy"}[alcohol],
                    exercise={"Sedentary": "sedentary", "Light": "light", "Moderate": "moderate", "Active": "active"}[exercise],
                    diet={"Balanced": "balanced", "Vegetarian": "vegetarian", "Vegan": "vegan", "Other": "other"}[diet]
                )
                st.session_state.onboarding_step = 4
                st.rerun()
    
    # STEP 4
    else:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## ⚙️ Step 4: Preferences")
        
        location = st.text_input("Location", placeholder="Boston, MA")
        language = st.selectbox("Language", ["English", "Spanish", "Chinese", "French"])
        
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
                st.success("✅ Welcome to Health Compass!")
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
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: linear-gradient(135deg, #F0F4F8 0%, #E2E8F0 100%); }
        h1, h2, h3, h4, h5, h6, p, span, div, label { color: #1E293B !important; }
        
        .app-header {
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
            padding: 2rem 2.5rem; margin: -1.5rem -2.5rem 2.5rem -2.5rem;
            border-radius: 0 0 24px 24px; box-shadow: 0 10px 30px rgba(30, 64, 175, 0.2);
        }
        .app-header h1 { color: white !important; font-size: 2.5rem; font-weight: 800; }
        .app-header p { color: rgba(255, 255, 255, 0.95) !important; font-size: 1.1rem; }
        
        .stSelectbox > div > div, [data-baseweb="select"], [data-baseweb="select"] > div {
            background: white !important; color: #1E293B !important;
        }
        [role="listbox"], [role="option"] { background: white !important; color: #1E293B !important; }
        [role="option"]:hover { background: #F1F5F9 !important; color: #3B82F6 !important; }
        
        .stTextArea textarea, .stTextInput input, .stNumberInput input {
            border: 2px solid #E2E8F0 !important; border-radius: 12px !important;
            background: white !important; color: #1E293B !important;
        }
        .stTextArea label, .stTextInput label, .stSelectbox label, .stNumberInput label {
            color: #1E293B !important; font-weight: 600 !important;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white !important; border: none; border-radius: 12px;
            padding: 0.8rem 2.5rem; font-weight: 600 !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            transform: translateY(-2px);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: white; padding: 1rem 1.5rem; border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            color: #475569 !important; font-weight: 600 !important;
            padding: 0.75rem 1.8rem; border-radius: 10px;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
            color: white !important;
        }
        
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #1E293B 0%, #334155 100%); }
        [data-testid="stSidebar"] * { color: rgba(255, 255, 255, 0.95) !important; }
        [data-testid="stSidebar"] h2 { color: white !important; font-weight: 700 !important; }
        
        [data-testid="stMetric"] { background: white; border-radius: 12px; padding: 1.5rem; }
        [data-testid="stMetricValue"] { color: #3B82F6 !important; font-size: 2.5rem !important; font-weight: 800 !important; }
        
        #MainMenu, footer {visibility: hidden;}
        .source-card {
            background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
            border: 1px solid #BAE6FD; border-left: 4px solid #0EA5E9;
            border-radius: 12px; padding: 1.5rem; margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    translations = {
        'English': {'header': 'Health Compass', 'tagline': 'AI-Powered Medical Assistant',
                   'search_placeholder': 'Ask any health question...', 'search_btn': 'Search',
                   'emergency': 'Emergency', 'call_911': 'Call 911'},
        'Spanish': {'header': 'Brújula de Salud', 'tagline': 'Asistente Médico con IA',
                   'search_placeholder': 'Pregunta de salud...', 'search_btn': 'Buscar',
                   'emergency': 'Emergencia', 'call_911': 'Llamar 911'},
        'Chinese': {'header': '健康指南针', 'tagline': 'AI医疗助手',
                   'search_placeholder': '健康问题...', 'search_btn': '搜索',
                   'emergency': '紧急', 'call_911': '911'},
        'French': {'header': 'Boussole Santé', 'tagline': 'Assistant Médical',
                  'search_placeholder': 'Question santé...', 'search_btn': 'Rechercher',
                  'emergency': 'Urgence', 'call_911': 'Appeler 911'}
    }
    t = translations[st.session_state.language]
    
    st.markdown(f"""
    <div class='app-header'>
        <h1>🏥 {t['header']}</h1>
        <p>{t['tagline']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        profile = st.session_state.user_profile
        summary = profile.get_profile_summary()
        
        st.markdown("## 👤 Profile")
        st.write(f"**{summary['name']}**")
        st.caption(f"{summary['age']} years • {summary.get('gender', 'N/A')}")
        if summary['bmi']:
            st.caption(f"BMI: {summary['bmi']}")
        if summary['conditions_count'] > 0:
            st.caption(f"📋 {summary['conditions_count']} condition(s)")
        
        if st.button("🔄 New Profile", use_container_width=True):
            st.session_state.user_profile.reset_profile()
            st.session_state.show_onboarding = True
            st.session_state.chat_history = []
            st.rerun()
        
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
                st.caption(f"{stats['total_documents']} docs")
            except:
                st.warning("Limited")
        else:
            st.error("Offline")
    
    # Main tabs
    tab_dash, tab_qa, tab_doc, tab_symptom, tab_ai = st.tabs([
        "🏠 Dashboard", "🔍 Q&A", "📄 Documents", "📊 Symptoms", "💬 AI Chat"
    ])
    
    # ==================== TAB: DASHBOARD ====================
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
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Age", f"{summary['age']} years" if summary['age'] else "Not set")
        with col2:
            if summary['bmi']:
                st.metric("BMI", summary['bmi'], delta=summary['bmi_category'], delta_color="off")
            else:
                st.metric("BMI", "Not calculated")
        with col3:
            st.metric("Conditions", summary['conditions_count'])
        with col4:
            risk_color = {'Low': '🟢', 'Moderate': '🟡', 'High': '🔴'}
            st.metric("Risk", f"{risk_color.get(summary['lifestyle_risk'], '⚪')} {summary['lifestyle_risk']}")
        
        st.markdown("---")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown("### 📊 Health Overview")
            
            with st.expander("🩺 Medical Info", expanded=True):
                if health.get('height') and health.get('weight'):
                    st.write(f"**Height:** {health['height']} cm • **Weight:** {health['weight']} kg")
                if health.get('blood_type'):
                    st.write(f"**Blood Type:** {health['blood_type']}")
                
                allergies = health.get('allergies', [])
                if allergies:
                    st.write(f"**Allergies:** {', '.join(allergies)}")
            
            with st.expander("🏥 Conditions"):
                conditions = health.get('chronic_conditions', [])
                if conditions:
                    for c in conditions:
                        st.write(f"• {c}")
                else:
                    st.info("None recorded")
        
        with col_right:
            st.markdown("### ⚡ Quick Actions")
            st.button("📝 Log Symptom", use_container_width=True)
            st.button("📄 Analyze Doc", use_container_width=True)
            st.button("💬 Ask AI", use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🏃 Lifestyle")
            
            icons = {
                'smoking': {'never': '✅ Non-smoker', 'former': '⚠️ Former', 'current': '🚫 Smoker'},
                'exercise': {'sedentary': '😴 Sedentary', 'light': '🚶 Light', 'moderate': '🏃 Moderate', 'active': '💪 Active'},
                'alcohol': {'none': '✅ None', 'occasional': '🍷 Occasional', 'moderate': '⚠️ Moderate', 'heavy': '🚫 Heavy'}
            }
            
            st.write(icons['smoking'].get(lifestyle.get('smoking', 'never'), ''))
            st.write(icons['exercise'].get(lifestyle.get('exercise', 'sedentary'), ''))
            st.write(icons['alcohol'].get(lifestyle.get('alcohol', 'none'), ''))
            
            st.markdown("---")
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                if st.button("⚙️ Edit", use_container_width=True):
                    st.session_state.show_profile_editor = True
                    st.rerun()
            with col_e2:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.user_profile.reset_profile()
                    st.session_state.show_onboarding = True
                    st.rerun()
        
        if st.session_state.get('show_profile_editor', False):
            st.markdown("---")
            st.markdown("## ⚙️ Edit Profile")
            
            edit_type = st.radio("Edit:", ["Basic", "Health", "Lifestyle", "Close"], horizontal=True)
            
            if edit_type == "Basic":
                with st.form("edit_basic"):
                    name = st.text_input("Name", value=basic.get('name', ''))
                    age = st.number_input("Age", value=basic.get('age', 30), min_value=1)
                    if st.form_submit_button("💾 Save"):
                        profile.update_basic_info(name=name, age=age)
                        st.success("✅ Updated!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
            
            elif edit_type == "Health":
                with st.form("edit_health"):
                    height = st.number_input("Height (cm)", value=health.get('height', 170))
                    weight = st.number_input("Weight (kg)", value=health.get('weight', 70))
                    if st.form_submit_button("💾 Save"):
                        profile.update_health_info(height=height, weight=weight)
                        st.success("✅ Updated!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
            
            elif edit_type == "Lifestyle":
                with st.form("edit_lifestyle"):
                    smoking = st.selectbox("Smoking", ["Never", "Former", "Current"],
                        index=["never", "former", "current"].index(lifestyle.get('smoking', 'never')))
                    alcohol = st.selectbox("Alcohol", ["None", "Occasional", "Moderate", "Heavy"],
                        index=["none", "occasional", "moderate", "heavy"].index(lifestyle.get('alcohol', 'none')))
                    exercise = st.selectbox("Exercise", ["Sedentary", "Light", "Moderate", "Active"],
                        index=["sedentary", "light", "moderate", "active"].index(lifestyle.get('exercise', 'sedentary')))
                    
                    if st.form_submit_button("💾 Save"):
                        maps = {
                            "Never": "never", "Former": "former", "Current": "current",
                            "None": "none", "Occasional": "occasional", "Moderate": "moderate", "Heavy": "heavy",
                            "Sedentary": "sedentary", "Light": "light", "Moderate": "moderate", "Active": "active"
                        }
                        profile.update_lifestyle(
                            smoking=maps[smoking],
                            alcohol=maps[alcohol],
                            exercise=maps[exercise]
                        )
                        st.success("✅ Lifestyle updated!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
            
            else:
                st.session_state.show_profile_editor = False
                st.rerun()
    
    # ==================== TAB: Q&A ====================
    with tab_qa:
        st.markdown("### 🔍 Medical Q&A")
        st.warning("⚠️ Educational only. Not medical advice.")
        
        query = st.text_area("Ask:", height=100, placeholder=t['search_placeholder'])
        
        if st.button(f"🔍 {t['search_btn']}", type="primary"):
            if query:
                rag = load_rag()
                if rag:
                    with st.spinner("Searching..."):
                        result = rag.query(query, n_results=5)
                    
                    if result.get('is_emergency'):
                        st.error("🚨 EMERGENCY - CALL 911")
                        st.stop()
                    
                    st.markdown("---")
                    st.markdown("### 📋 Answer")
                    st.write(result['answer'])
                    
                    if result.get('sources'):
                        st.markdown("### 📚 Sources")
                        for i, src in enumerate(result['sources'], 1):
                            st.markdown(f"""
                            <div class='source-card'>
                                <strong>{i}. {src.get('source', 'Unknown')}</strong><br>
                                {src.get('title', '')}<br>
                                <a href="{src.get('url', '#')}" target="_blank">View →</a>
                            </div>
                            """, unsafe_allow_html=True)
    
    # ==================== TAB: DOCUMENTS ====================
    with tab_doc:
        st.markdown("### 📄 Document Analyzer")
        
        rag_system = load_rag()
        analyzer = EnhancedDocumentAnalyzer(rag_system=rag_system)
        
        profile = st.session_state.user_profile
        profile_gender = profile.get_basic_info().get('gender')
        
        uploaded_file = st.file_uploader("Upload", type=['pdf', 'png', 'jpg', 'txt'])
        
        gender = st.selectbox("Gender", 
            ["Not specified", "Male", "Female"],
            index=0 if not profile_gender else (["Male", "Female"].index(profile_gender) + 1 if profile_gender in ["Male", "Female"] else 0))
        
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            
            analysis_type = st.radio("Analysis:", 
                ["🔬 Lab Values", "📋 Explain All", "⚠️ Abnormal Only", "❓ Questions", "💊 Medications"])
            
            if st.button("🤖 Analyze", type="primary"):
                with st.spinner("Analyzing..."):
                    file_bytes = uploaded_file.getvalue()
                    gender_param = None if gender == "Not specified" else gender
                    
                    if "Lab Values" in analysis_type:
                        result = analyzer.analyze_document(file_bytes, uploaded_file.type, gender_param)
                        if 'error' not in result:
                            st.success("✅ Done!")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total", result['total_tests'])
                            with col2:
                                st.metric("Abnormal", result['abnormal_count'])
                            with col3:
                                st.metric("Normal", result['total_tests'] - result['abnormal_count'])
                            st.markdown("---")
                            st.markdown(result['report'])
    
    # ==================== TAB: SYMPTOMS ====================
    with tab_symptom:
        st.markdown("### 📊 Symptom Tracker")
        
        tracker = SymptomTracker()
        specialist_matcher = SpecialistMatcher(rag_system=load_rag())
        
        with st.form("symptom_form", clear_on_submit=True):
            symptom = st.text_input("Symptom:", placeholder="Headache")
            severity = st.slider("Severity:", 1, 10, 5)
            notes = st.text_area("Notes:", height=60)
            
            if st.form_submit_button("💾 Log"):
                if symptom:
                    tracker.log_symptom(symptom, severity, notes)
                    st.success("✅ Logged!")
                    st.rerun()
        
        insights = tracker.get_ai_insights()
        if insights:
            st.metric("Entries", insights['total_entries'])
            st.metric("Avg Severity", f"{insights['average_severity']}/10")
        
        entries = tracker.get_all_symptoms()
        if entries:
            st.markdown("---")
            st.markdown("## 👨‍⚕️ Specialist Finder")
            
            recent = [e['symptom'] for e in entries[-5:]]
            st.write(f"Based on: {', '.join(recent[:3])}")
            
            if st.button("🔍 Find Specialist", type="primary"):
                with st.spinner("Analyzing..."):
                    match = specialist_matcher.match_specialist(recent)
                    if match['specialists']:
                        top = match['specialists'][0]
                        st.markdown(f"### {top['icon']} {top['name']}")
                        st.write(f"**Confidence:** {top['confidence']:.0f}%")
                        st.write(f"**Treats:** {top['treats']}")
                        if match['urgency'] == 'urgent':
                            st.error("🚨 URGENT - Seek immediate care")
    
    # ==================== TAB: AI ASSISTANT ====================
    with tab_ai:
        st.markdown("### 💬 AI Healthcare Assistant")
        
        profile = st.session_state.user_profile
        assistant = HealthcareAssistant()
        
        if not st.session_state.chat_history:
            st.session_state.chat_history = [{
                'role': 'assistant',
                'content': f"Hello! I'm your AI assistant. How can I help?"
            }]
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role'], avatar="🤖" if msg['role'] == 'assistant' else "👤"):
                st.write(msg['content'])
        
        user_input = st.chat_input("Type message...")
        
        if user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            rag = load_rag()
            if rag:
                with st.spinner("🤖 Thinking..."):
                    profile_context = profile.get_context_for_ai()
                    rag_result = rag.query(user_input, n_results=3)
                    
                    prompt = f"""Patient Profile:
{profile_context}

Patient asks: {user_input}

Medical info: {rag_result['answer'][:1200]}

Provide brief personalized response (3-4 sentences).
Consider their profile. Be helpful and conversational."""
                    
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
        <div style='font-size: 1.3rem; font-weight: 700; color: #1E40AF;'>🏥 Health Compass</div>
        <div style='font-size: 0.95rem;'>Educational Only • Not Medical Advice</div>
        <div style='font-size: 0.85rem; margin-top: 1rem; color: #94A3B8;'>
            INFO 7390 Final Project | Manish K | Northeastern University
        </div>
    </div>
    """, unsafe_allow_html=True)
