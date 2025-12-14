import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import io

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag.rag_pipeline import HealthCompassRAG
from src.utils.symptom_tracker import SymptomTracker
from src.utils.healthcare_assistant import HealthcareAssistant
from src.utils.document_analyzer_enhanced import EnhancedDocumentAnalyzer
from src.utils.specialist_matcher import SpecialistMatcher
from src.utils.user_profile import UserProfile

# Initialize
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = UserProfile()
if 'show_onboarding' not in st.session_state:
    profile_data = st.session_state.user_profile.get_basic_info()
    has_valid = profile_data.get('name') and profile_data.get('age', 0) > 0
    st.session_state.show_onboarding = not has_valid
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

@st.cache_resource(show_spinner=False)
def load_rag():
    try:
        return HealthCompassRAG()
    except:
        return None

# ==================== ONBOARDING ====================
if st.session_state.show_onboarding:
    st.set_page_config(page_title="Welcome to Health Compass", page_icon="🏥", layout="wide")
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        * { font-family: 'Inter', sans-serif !important; }
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); }
        .onboarding-card {
            background: white; border-radius: 24px; padding: 3rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 800px; margin: 2rem auto;
        }
        .onboarding-title {
            text-align: center; color: #667eea; font-size: 3rem;
            font-weight: 800; margin-bottom: 0.5rem;
        }
        .onboarding-subtitle {
            text-align: center; color: #64748B; font-size: 1.2rem; margin-bottom: 2rem;
        }
        h2, h3, h4, label { color: #1E293B !important; }
        .stProgress > div > div { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important; }
        .stSelectbox > div > div, [data-baseweb="select"] { background: white !important; color: #1E293B !important; }
        [role="option"] { background: white !important; color: #1E293B !important; }
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            border: 2px solid #E2E8F0 !important; border-radius: 12px !important;
            background: #F8FAFC !important; color: #1E293B !important; padding: 0.75rem !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
            border-color: #667eea !important; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='onboarding-card'>", unsafe_allow_html=True)
    st.markdown("<div class='onboarding-title'>🏥 Health Compass</div>", unsafe_allow_html=True)
    st.markdown("<div class='onboarding-subtitle'>Let's personalize your health journey</div>", unsafe_allow_html=True)
    
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1
    
    profile = st.session_state.user_profile
    st.progress(st.session_state.onboarding_step / 4)
    st.caption(f"Step {st.session_state.onboarding_step} of 4")
    st.markdown("---")
    
    if st.session_state.onboarding_step == 1:
        st.markdown("## 📋 Tell us about yourself")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            age = st.number_input("Age *", min_value=1, max_value=120, value=30)
        with col2:
            gender = st.selectbox("Gender *", ["Select...", "Male", "Female", "Other"])
            dob = st.date_input("Date of Birth (optional)")
        
        if st.button("Continue →", use_container_width=True, type="primary"):
            if name and age and gender != "Select...":
                profile.update_basic_info(name=name, age=age, gender=gender, dob=dob.isoformat() if dob else None)
                st.session_state.onboarding_step = 2
                st.rerun()
            else:
                st.error("Please complete all required fields (*)")
    
    elif st.session_state.onboarding_step == 2:
        st.markdown("## 🏥 Your health information")
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (cm)", value=170, min_value=50, max_value=250)
            weight = st.number_input("Weight (kg)", value=70, min_value=20, max_value=300)
        with col2:
            blood_type = st.selectbox("Blood Type", ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        allergies = st.text_area("Allergies (one per line, optional)", placeholder="Penicillin\nPeanuts", height=80)
        conditions = st.text_area("Chronic Conditions (one per line, optional)", placeholder="Diabetes\nHypertension", height=80)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            if st.button("Continue →", use_container_width=True, type="primary"):
                profile.update_health_info(height=height, weight=weight, blood_type=blood_type if blood_type != "Unknown" else None)
                if allergies:
                    for a in allergies.strip().split('\n'):
                        if a.strip():
                            profile.add_allergy(a.strip())
                if conditions:
                    for c in conditions.strip().split('\n'):
                        if c.strip():
                            profile.add_condition(c.strip())
                st.session_state.onboarding_step = 3
                st.rerun()
    
    elif st.session_state.onboarding_step == 3:
        st.markdown("## 🏃 Lifestyle habits")
        col1, col2 = st.columns(2)
        with col1:
            smoking = st.selectbox("Smoking Status", ["Never", "Former smoker", "Current smoker"])
            alcohol = st.selectbox("Alcohol", ["None", "Occasional", "Moderate", "Heavy"])
        with col2:
            exercise = st.selectbox("Exercise Level", ["Sedentary", "Light", "Moderate", "Active"])
            diet = st.selectbox("Diet Type", ["Balanced", "Vegetarian", "Vegan", "Other"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col2:
            if st.button("Continue →", use_container_width=True, type="primary"):
                profile.update_lifestyle(
                    smoking=smoking.lower().replace(" smoker", ""),
                    alcohol=alcohol.lower(),
                    exercise=exercise.lower(),
                    diet=diet.lower()
                )
                st.session_state.onboarding_step = 4
                st.rerun()
    
    else:
        st.markdown("## ⚙️ Final touches")
        location = st.text_input("Location (City, State)", placeholder="Boston, MA", 
                                help="Used to find nearby healthcare facilities")
        language = st.selectbox("Preferred Language", ["English", "Spanish", "Chinese", "French"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()
        with col2:
            if st.button("🎉 Complete Setup", use_container_width=True, type="primary"):
                profile.update_preferences(location=location, language=language)
                profile.mark_setup_complete()
                st.session_state.show_onboarding = False
                st.session_state.language = language
                st.balloons()
                st.success("✅ Welcome to Health Compass!")
                import time
                time.sleep(1)
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== MAIN APP ====================
else:
    st.set_page_config(page_title="Health Compass", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")
    
    # BEAUTIFUL MODERN UI
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
        
        .stApp {
            background: linear-gradient(135deg, #E0E7FF 0%, #DBEAFE 50%, #E0F2FE 100%);
        }
        
        /* All text readable */
        h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
            color: #0F172A !important;
        }
        
        /* Header gradient */
        .app-header {
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 50%, #06B6D4 100%);
            padding: 2.5rem 3rem;
            margin: -1.5rem -2.5rem 3rem -2.5rem;
            border-radius: 0 0 32px 32px;
            box-shadow: 0 20px 60px rgba(30, 64, 175, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .app-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            border-radius: 50%;
        }
        
        .app-header h1 {
            color: white !important;
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: -1px;
            margin: 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .app-header p {
            color: rgba(255, 255, 255, 0.95) !important;
            font-size: 1.25rem;
            margin: 0.5rem 0 0 0;
            font-weight: 500;
        }
        
        /* Beautiful Cards */
        .feature-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(226, 232, 240, 0.6);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .feature-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(59, 130, 246, 0.15);
            border-color: rgba(59, 130, 246, 0.3);
        }
        
        /* Info boxes with icons */
        .info-box {
            background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
            border-left: 5px solid #3B82F6;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .warning-box {
            background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
            border-left: 5px solid #F59E0B;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .success-box {
            background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
            border-left: 5px solid #10B981;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        /* Dropdown fix */
        .stSelectbox > div > div {
            background: white !important;
            color: #1E293B !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
        }
        
        [data-baseweb="select"] {
            background: white !important;
        }
        
        [role="listbox"] {
            background: white !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15) !important;
        }
        
        [role="option"] {
            background: white !important;
            color: #1E293B !important;
            padding: 0.75rem 1rem !important;
        }
        
        [role="option"]:hover {
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
            color: #1E40AF !important;
        }
        
        /* Better inputs */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
            background: white !important;
            color: #1E293B !important;
            padding: 0.875rem !important;
            font-size: 1rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
        }
        
        /* Labels */
        .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
            color: #1E293B !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Beautiful buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.875rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.5) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Download button */
        .stDownloadButton button {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4) !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.75rem;
            background: white;
            padding: 1.25rem 2rem;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin-bottom: 2.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #64748B !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding: 0.875rem 2rem;
            border-radius: 12px;
            transition: all 0.2s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #F1F5F9;
            color: #3B82F6 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
            color: white !important;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        }
        
        [data-testid="stSidebar"] * {
            color: rgba(255, 255, 255, 0.95) !important;
        }
        
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: white !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(59, 130, 246, 0.2) !important;
            border: 2px solid rgba(59, 130, 246, 0.3) !important;
            color: white !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(59, 130, 246, 0.3) !important;
            border-color: rgba(59, 130, 246, 0.5) !important;
        }
        
        /* Metrics */
        [data-testid="stMetric"] {
            background: white;
            border-radius: 16px;
            padding: 1.75rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(226, 232, 240, 0.6);
        }
        
        [data-testid="stMetricValue"] {
            color: #3B82F6 !important;
            font-size: 2.25rem !important;
            font-weight: 800 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Alerts with better styling */
        [data-baseweb="notification"] {
            border-radius: 12px !important;
            padding: 1.25rem 1.5rem !important;
        }
        
        [data-baseweb="notification"][kind="info"] {
            background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%) !important;
            border-left: 5px solid #3B82F6 !important;
        }
        
        [data-baseweb="notification"][kind="warning"] {
            background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%) !important;
            border-left: 5px solid #F59E0B !important;
        }
        
        [data-baseweb="notification"][kind="success"] {
            background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%) !important;
            border-left: 5px solid #10B981 !important;
        }
        
        [data-baseweb="notification"][kind="error"] {
            background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%) !important;
            border-left: 5px solid #EF4444 !important;
        }
        
        [data-baseweb="notification"] p {
            color: #1E293B !important;
            font-weight: 500 !important;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: white;
            border: 3px dashed #CBD5E1;
            border-radius: 16px;
            padding: 2.5rem;
            transition: all 0.3s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #3B82F6;
            background: #F8FAFC;
        }
        
        /* Chat messages */
        .stChatMessage {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: white !important;
            border-radius: 12px !important;
            color: #1E293B !important;
            font-weight: 600 !important;
            padding: 1rem !important;
        }
        
        .streamlit-expanderHeader:hover {
            background: #F8FAFC !important;
        }
        
        /* Source cards */
        .source-card {
            background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
            border: 1px solid #BAE6FD;
            border-left: 5px solid #0EA5E9;
            border-radius: 14px;
            padding: 1.75rem;
            margin: 1.25rem 0;
            transition: all 0.3s ease;
        }
        
        .source-card:hover {
            box-shadow: 0 8px 24px rgba(14, 165, 233, 0.2);
            transform: translateX(4px);
        }
        
        .source-card strong {
            color: #0C4A6E !important;
            font-size: 1.05rem;
        }
        
        .source-card a {
            color: #0EA5E9 !important;
            font-weight: 600 !important;
            text-decoration: none;
        }
        
        /* Hide Streamlit branding */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Captions */
        .stCaption {
            color: #64748B !important;
            font-size: 0.875rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='app-header'>
        <h1>🏥 Health Compass</h1>
        <p>AI-Powered Medical Assistant • Evidence-Based Healthcare Information</p>
    </div>
    """, unsafe_allow_html=True)
    
    # SIDEBAR
    with st.sidebar:
        profile = st.session_state.user_profile
        summary = profile.get_profile_summary()
        
        st.markdown("## 👤 Your Profile")
        st.markdown(f"### {summary['name']}")
        st.caption(f"🎂 {summary['age']} years • {summary.get('gender', 'N/A')}")
        
        if summary['bmi']:
            bmi_emoji = "✅" if 18.5 <= summary['bmi'] < 25 else "⚠️"
            st.caption(f"{bmi_emoji} BMI: {summary['bmi']} ({summary['bmi_category']})")
        
        if summary['conditions_count'] > 0:
            st.caption(f"📋 {summary['conditions_count']} condition(s)")
        
        if st.button("🔄 Start New Profile", use_container_width=True):
            st.session_state.user_profile.reset_profile()
            st.session_state.show_onboarding = True
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("## 🚨 Emergency Contacts")
        st.error("**🚑 Call 911**")
        st.caption("☎️ Poison: 1-800-222-1222")
        st.caption("🧠 Crisis: 988")
        st.caption("🩺 Suicide Prevention: 1-800-273-8255")
        
        st.markdown("---")
        
        st.markdown("## 📊 System Status")
        rag = load_rag()
        if rag:
            try:
                stats = rag.vector_db.get_stats()
                st.success(f"✅ Online")
                st.caption(f"📚 {stats['total_documents']} medical documents")
                st.caption("🔍 Semantic search ready")
            except:
                st.warning("⚠️ Limited mode")
        else:
            st.error("❌ Offline")
    
    # MAIN TABS
    tabs = st.tabs(["🏠 Dashboard", "🔍 Q&A Search", "📄 Document Analyzer", "📊 Symptom Tracker", "💬 AI Assistant"])
    
    # ==================== DASHBOARD ====================
    with tabs[0]:
        profile = st.session_state.user_profile
        summary = profile.get_profile_summary()
        basic = profile.get_basic_info()
        health = profile.get_health_info()
        lifestyle = profile.get_lifestyle()
        
        st.markdown(f"# Welcome back, {summary['name']}! 👋")
        st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
        
        st.markdown("---")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👤 Age", f"{summary['age']} years")
        
        with col2:
            if summary['bmi']:
                bmi_color = "🟢" if 18.5 <= summary['bmi'] < 25 else ("🟡" if 25 <= summary['bmi'] < 30 else "🔴")
                st.metric("⚖️ BMI", f"{bmi_color} {summary['bmi']}", delta=summary['bmi_category'], delta_color="off")
            else:
                st.metric("⚖️ BMI", "Not set")
        
        with col3:
            st.metric("🏥 Conditions", summary['conditions_count'])
        
        with col4:
            risk_emoji = {'Low': '🟢', 'Moderate': '🟡', 'High': '🔴'}
            st.metric("⚡ Risk", f"{risk_emoji.get(summary['lifestyle_risk'], '⚪')} {summary['lifestyle_risk']}")
        
        st.markdown("---")
        
        col_main, col_side = st.columns([2.5, 1.5])
        
        with col_main:
            st.markdown("### 📊 Health Overview")
            
            with st.expander("🩺 Medical Information", expanded=True):
                if health.get('height') and health.get('weight'):
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        st.metric("📏 Height", f"{health['height']} cm")
                    with col_h2:
                        st.metric("⚖️ Weight", f"{health['weight']} kg")
                
                if health.get('blood_type'):
                    st.write(f"🩸 **Blood Type:** {health['blood_type']}")
                
                allergies = health.get('allergies', [])
                if allergies:
                    st.markdown("**🚫 Allergies:**")
                    for allergy in allergies:
                        st.markdown(f"- {allergy}")
            
            with st.expander("🏥 Chronic Conditions"):
                conditions = health.get('chronic_conditions', [])
                if conditions:
                    for condition in conditions:
                        st.markdown(f"• {condition}")
                else:
                    st.info("✅ No chronic conditions recorded")
            
            with st.expander("💊 Current Medications"):
                meds = health.get('current_medications', [])
                if meds:
                    for med in meds:
                        st.markdown(f"**{med.get('name')}**")
                        st.caption(f"{med.get('dosage', '')} - {med.get('frequency', '')}")
                else:
                    st.info("✅ No medications recorded")
        
        with col_side:
            st.markdown("### ⚡ Quick Actions")
            
            st.info("💡 Jump to any feature quickly")
            
            if st.button("📝 Log a Symptom", use_container_width=True):
                st.toast("👉 Navigate to Symptoms tab")
            
            if st.button("📄 Analyze Document", use_container_width=True):
                st.toast("👉 Navigate to Documents tab")
            
            if st.button("💬 Chat with AI", use_container_width=True):
                st.toast("👉 Navigate to AI Chat tab")
            
            st.markdown("---")
            
            st.markdown("### 🏃 Lifestyle Profile")
            
            lifestyle_map = {
                'smoking': {'never': '✅ Non-smoker', 'former': '⚠️ Former smoker', 'current': '🚫 Current smoker'},
                'exercise': {'sedentary': '😴 Sedentary', 'light': '🚶 Light activity', 'moderate': '🏃 Moderate', 'active': '💪 Very active'},
                'alcohol': {'none': '✅ No alcohol', 'occasional': '🍷 Occasional', 'moderate': '⚠️ Moderate', 'heavy': '🚫 Heavy use'}
            }
            
            st.write(lifestyle_map['smoking'].get(lifestyle.get('smoking', 'never'), ''))
            st.write(lifestyle_map['exercise'].get(lifestyle.get('exercise', 'sedentary'), ''))
            st.write(lifestyle_map['alcohol'].get(lifestyle.get('alcohol', 'none'), ''))
            
            st.markdown("---")
            
            if st.button("⚙️ Edit Profile", use_container_width=True):
                st.session_state.show_profile_editor = True
                st.rerun()
        
        # Profile Editor
        if st.session_state.get('show_profile_editor', False):
            st.markdown("---")
            st.markdown("## ⚙️ Edit Your Profile")
            
            edit_section = st.radio("Choose section to edit:", 
                                   ["📋 Basic", "🏥 Health", "🏃 Lifestyle", "✖️ Close"], 
                                   horizontal=True)
            
            if edit_section == "📋 Basic":
                with st.form("edit_basic_form"):
                    st.markdown("#### Basic Information")
                    name = st.text_input("Name", value=basic.get('name', ''))
                    age = st.number_input("Age", value=basic.get('age', 30), min_value=1)
                    
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        profile.update_basic_info(name=name, age=age)
                        st.success("✅ Profile updated!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
            
            elif edit_section == "🏥 Health":
                with st.form("edit_health_form"):
                    st.markdown("#### Health Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        height = st.number_input("Height (cm)", value=health.get('height', 170))
                    with col2:
                        weight = st.number_input("Weight (kg)", value=health.get('weight', 70))
                    
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        profile.update_health_info(height=height, weight=weight)
                        st.success("✅ Health info updated!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
            
            elif edit_section == "🏃 Lifestyle":
                with st.form("edit_lifestyle_form"):
                    st.markdown("#### Lifestyle Habits")
                    
                    smoking = st.selectbox("Smoking", ["Never", "Former", "Current"],
                        index=["never", "former", "current"].index(lifestyle.get('smoking', 'never')))
                    
                    alcohol = st.selectbox("Alcohol", ["None", "Occasional", "Moderate", "Heavy"],
                        index=["none", "occasional", "moderate", "heavy"].index(lifestyle.get('alcohol', 'none')))
                    
                    exercise = st.selectbox("Exercise", ["Sedentary", "Light", "Moderate", "Active"],
                        index=["sedentary", "light", "moderate", "active"].index(lifestyle.get('exercise', 'sedentary')))
                    
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        profile.update_lifestyle(
                            smoking=smoking.lower(),
                            alcohol=alcohol.lower(),
                            exercise=exercise.lower()
                        )
                        st.success("✅ Lifestyle updated!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
            
            else:
                st.session_state.show_profile_editor = False
                st.rerun()
    
    # ==================== Q&A SEARCH ====================
    with tabs[1]:
        st.markdown("## 🔍 Medical Information Search")
        st.caption("🎓 Get evidence-based answers from trusted medical sources")
        
        st.markdown("""
        <div class='warning-box'>
            <strong>⚠️ Important:</strong> This is for educational purposes only. Not medical advice. Call 911 for emergencies.
        </div>
        """, unsafe_allow_html=True)
        
        col_search, col_tips = st.columns([2.5, 1])
        
        with col_search:
            query = st.text_area(
                "💭 What would you like to know?",
                height=120,
                placeholder="e.g., What is Type 2 diabetes?\nWhat are symptoms of high blood pressure?\nHow does ibuprofen work?",
                help="Ask any health-related question"
            )
            
            col_btn1, col_btn2 = st.columns([2, 1])
            with col_btn1:
                search_btn = st.button("🔍 Search Medical Database", use_container_width=True, type="primary")
            with col_btn2:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.rerun()
        
        with col_tips:
            st.markdown("""
            <div class='info-box'>
                <strong>💡 Try asking about:</strong><br>
                • Medical conditions<br>
                • Symptoms & causes<br>
                • Medications & treatments<br>
                • Prevention strategies<br>
                • Lab tests explained
            </div>
            """, unsafe_allow_html=True)
        
        if search_btn and query:
            rag = load_rag()
            if rag:
                with st.spinner("🔍 Searching 700+ medical documents..."):
                    result = rag.query(query, n_results=5)
                
                if result.get('is_emergency'):
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%); 
                                border: 4px solid #EF4444; border-radius: 16px; padding: 2rem; text-align: center;'>
                        <h2 style='color: #DC2626 !important;'>🚨 MEDICAL EMERGENCY DETECTED</h2>
                        <h3 style='color: #DC2626 !important;'>CALL 911 IMMEDIATELY</h3>
                        <p style='color: #7F1D1D !important;'>Do not delay. Seek emergency medical care now.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.stop()
                
                st.markdown("---")
                st.markdown("## 📋 Answer")
                
                st.markdown(f"""
                <div class='feature-card'>
                    {result['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                if result.get('sources'):
                    st.markdown("---")
                    st.markdown("### 📚 Trusted Sources")
                    st.caption("All information verified from authoritative medical organizations")
                    
                    for i, source in enumerate(result['sources'], 1):
                        st.markdown(f"""
                        <div class='source-card'>
                            <strong>{i}. {source.get('source', 'Medical Source')}</strong> ✓<br>
                            📄 {source.get('title', 'Health Information')}<br>
                            <a href="{source.get('url', '#')}" target="_blank">🔗 View original source →</a>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.download_button(
                        "📥 Download Answer with Sources",
                        f"QUESTION:\n{query}\n\nANSWER:\n{result['answer']}\n\nSOURCES:\n" + 
                        '\n'.join([f"{i}. {s.get('source')} - {s.get('url', '')}" for i, s in enumerate(result['sources'], 1)]),
                        f"health_answer_{datetime.now().strftime('%Y%m%d')}.txt",
                        use_container_width=True
                    )
    
    # ==================== DOCUMENT ANALYZER ====================
    with tabs[2]:
        st.markdown("## 📄 Medical Document Analyzer")
        st.caption("📋 Upload lab results, prescriptions, or medical reports")
        
        rag_sys = load_rag()
        analyzer = EnhancedDocumentAnalyzer(rag_system=rag_sys)
        
        col_up, col_gender = st.columns([2, 1])
        
        with col_up:
            uploaded = st.file_uploader(
                "📤 Choose your medical document",
                type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
                help="Supports: Lab reports, prescriptions, discharge summaries"
            )
        
        with col_gender:
            prof_gender = profile.get_basic_info().get('gender')
            default_idx = 0
            if prof_gender in ["Male", "Female"]:
                default_idx = ["Not specified", "Male", "Female"].index(prof_gender)
            
            gender = st.selectbox(
                "👤 Gender (for lab ranges)",
                ["Not specified", "Male", "Female"],
                index=default_idx,
                help="Used for gender-specific reference ranges"
            )
            
            if prof_gender:
                st.caption(f"✅ From profile: {prof_gender}")
        
        if uploaded:
            st.markdown(f"""
            <div class='success-box'>
                <strong>✅ Uploaded:</strong> {uploaded.name} ({uploaded.size/1024:.1f} KB)
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("👁️ Preview Document"):
                if uploaded.type.startswith('image'):
                    st.image(Image.open(uploaded), use_column_width=True)
                elif uploaded.type == 'text/plain':
                    uploaded.seek(0)
                    preview = uploaded.read().decode('utf-8')[:500]
                    st.text(preview + "...")
                    uploaded.seek(0)
            
            st.markdown("---")
            st.markdown("### 🎯 Select Analysis Type")
            
            analysis_type = st.radio(
                "What would you like to know?",
                [
                    "📋 Explain everything in simple terms",
                    "🔬 Highlight abnormal values only",
                    "❓ Generate questions for my doctor",
                    "📝 Summarize key findings",
                    "💊 List all medications mentioned"
                ],
                label_visibility="collapsed"
            )
            
            if st.button("🤖 Analyze Document Now", use_container_width=True, type="primary"):
                with st.spinner("🔍 AI is analyzing your document... Please wait 10-30 seconds"):
                    file_bytes = uploaded.getvalue()
                    gender_param = None if gender == "Not specified" else gender
                    
                    try:
                        # Extract text
                        if uploaded.type == 'application/pdf':
                            text = analyzer.extract_text_from_pdf(file_bytes)
                        elif uploaded.type.startswith('image'):
                            try:
                                text = analyzer.extract_text_from_image(file_bytes)
                            except:
                                st.warning("⚠️ OCR not available in cloud. Please type text below:")
                                text = st.text_area("Enter document text:", height=200)
                        else:
                            text = file_bytes.decode('utf-8')
                        
                        if text and len(text) > 10 and not text.startswith("ERROR"):
                            st.success("✅ Document processed successfully!")
                            st.markdown("---")
                            
                            # EXPLAIN EVERYTHING
                            if "Explain everything" in analysis_type:
                                st.markdown("### 💡 Plain English Explanation")
                                
                                if rag_sys:
                                    prompt = f"""Analyze this medical document and explain it simply:

{text[:2500]}

Provide a clear explanation covering:
1. What type of document this is
2. The main information in simple terms
3. Important medical terms explained
4. What this means for the patient
5. Recommended next steps

Use everyday language, avoid medical jargon."""

                                    with st.spinner("Generating explanation..."):
                                        explanation = rag_sys.llm.generate([
                                            {"role": "system", "content": "You are a medical educator who explains complex information in simple, accessible language."},
                                            {"role": "user", "content": prompt}
                                        ], temperature=0.2, max_tokens=2000)
                                    
                                    st.markdown(f"""
                                    <div class='feature-card'>
                                        {explanation.replace('<s>', '').replace('</s>', '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    with st.expander("📄 View Original Text"):
                                        st.text_area("Document content:", text[:2000], height=300, disabled=True)
                            
                            # HIGHLIGHT ABNORMAL
                            elif "abnormal values" in analysis_type:
                                st.markdown("### ⚠️ Abnormal Value Analysis")
                                
                                result = analyzer.analyze_document(file_bytes, uploaded.type, gender_param)
                                
                                if 'error' not in result:
                                    abnormal_results = [r for r in result['lab_results'] if r['status'] in ['high', 'low']]
                                    
                                    if abnormal_results:
                                        st.markdown(f"""
                                        <div class='warning-box'>
                                            <strong>⚠️ Found {len(abnormal_results)} value(s) outside normal range</strong><br>
                                            These require your doctor's attention
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        for r in abnormal_results:
                                            status_color = "#EF4444" if r['status'] == 'high' else "#F59E0B"
                                            st.markdown(f"""
                                            <div style='background: white; border-left: 5px solid {status_color}; 
                                                        border-radius: 12px; padding: 1.5rem; margin: 1rem 0;'>
                                                <h4 style='color: {status_color} !important; margin: 0 0 0.5rem 0;'>
                                                    {'🔴' if r['status'] == 'high' else '🟡'} {r['test']}
                                                </h4>
                                                <p><strong>Your Value:</strong> {r['value']} {r['unit']}</p>
                                                <p><strong>Status:</strong> {r['status'].upper()}</p>
                                                <p><strong>What this means:</strong> {r['details']}</p>
                                                <p style='color: #64748B;'><em>{r['description']}</em></p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class='success-box'>
                                            <strong>✅ Great news!</strong><br>
                                            All analyzed values appear to be within normal ranges.
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.error(f"❌ {result['error']}")
                            
                            # DOCTOR QUESTIONS
                            elif "questions for" in analysis_type:
                                st.markdown("### ❓ Questions to Ask Your Doctor")
                                
                                if rag_sys:
                                    prompt = f"""Based on this medical document, generate 10 specific questions the patient should ask their doctor:

{text[:2000]}

Make questions:
- Specific to the findings
- Help understand results
- Address concerns
- Ask about treatment
- Easy to remember

Format as numbered list."""

                                    with st.spinner("Generating questions..."):
                                        questions = rag_sys.llm.generate([
                                            {"role": "system", "content": "Helping patients prepare for doctor visits."},
                                            {"role": "user", "content": prompt}
                                        ], temperature=0.3, max_tokens=1200)
                                    
                                    st.markdown(f"""
                                    <div class='feature-card'>
                                        {questions.replace('<s>', '').replace('</s>', '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.markdown("""
                                    <div class='info-box'>
                                        <strong>💡 Pro Tip:</strong> Print this list and bring it to your appointment. 
                                        Check off questions as they're answered.
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # SUMMARIZE
                            elif "Summarize" in analysis_type:
                                st.markdown("### 📝 Key Findings Summary")
                                
                                if rag_sys:
                                    prompt = f"""Summarize this medical document concisely:

{text[:2000]}

Provide:
1. Document type
2. Main findings (3-5 bullet points)
3. Bottom line: What does this mean?
4. Recommended next steps

Be brief and clear."""

                                    with st.spinner("Creating summary..."):
                                        summary_text = rag_sys.llm.generate([
                                            {"role": "system", "content": "Summarizing medical documents clearly and concisely."},
                                            {"role": "user", "content": prompt}
                                        ], temperature=0.2, max_tokens=1000)
                                    
                                    st.markdown(f"""
                                    <div class='feature-card'>
                                        {summary_text.replace('<s>', '').replace('</s>', '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # MEDICATIONS
                            else:
                                st.markdown("### 💊 Medication List")
                                
                                if rag_sys:
                                    prompt = f"""Extract ALL medications mentioned in this document:

{text[:2000]}

For each medication provide:
1. Medication name (generic + brand if available)
2. Dosage and strength
3. How often to take it
4. Brief description of what it's for

Format clearly."""

                                    with st.spinner("Extracting medications..."):
                                        meds = rag_sys.llm.generate([
                                            {"role": "system", "content": "Extracting medication information from medical documents."},
                                            {"role": "user", "content": prompt}
                                        ], temperature=0.1, max_tokens=1200)
                                    
                                    st.markdown(f"""
                                    <div class='feature-card'>
                                        {meds.replace('<s>', '').replace('</s>', '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Download option
                            st.markdown("---")
                            download_content = f"""HEALTH COMPASS - DOCUMENT ANALYSIS
{'='*70}

Document: {uploaded.name}
Analysis Type: {analysis_type}
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Gender: {gender}

{'='*70}

RESULTS:

{text[:3000]}

{'='*70}
Generated by Health Compass | Educational purposes only
Always discuss results with your healthcare provider
{'='*70}
"""
                            st.download_button(
                                "📥 Download Complete Analysis",
                                download_content,
                                f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                                use_container_width=True
                            )
                        
                        else:
                            st.error("❌ Could not extract text from document. Try a different file format.")
                    
                    except Exception as e:
                        st.error(f"❌ Analysis error: {str(e)}")
                        st.info("💡 Try uploading a different file or using a different analysis type.")
        
        else:
            # Instructions when no file
            st.markdown("""
            <div class='info-box'>
                <strong>👆 Upload a document above to get started</strong>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **✅ Supported Documents:**
                - Lab test results
                - Blood work reports
                - Cholesterol panels
                - Metabolic panels
                - Thyroid tests
                - Liver function
                """)
            
            with col2:
                st.markdown("""
                **📋 File Formats:**
                - PDF files (.pdf)
                - Images (.jpg, .png)
                - Text files (.txt)
                - Scanned documents
                """)
            
            with col3:
                st.markdown("""
                **🎯 Features:**
                - Normal range comparison
                - Plain English explanations
                - Abnormal value alerts
                - Doctor question generator
                - Medication extraction
                """)
    
    # ==================== SYMPTOM TRACKER ====================
    with tabs[3]:
        st.markdown("## 📊 Symptom Tracker & Insights")
        st.caption("📝 Track symptoms and discover patterns with AI")
        
        tracker = SymptomTracker()
        
        col_log, col_stats = st.columns([1.5, 1])
        
        with col_log:
            st.markdown("### 📝 Log New Symptom")
            
            with st.form("symptom_logger", clear_on_submit=True):
                symptom = st.text_input(
                    "What are you experiencing?",
                    placeholder="e.g., Headache, Nausea, Fatigue, Chest pain"
                )
                
                col_sev, col_notes = st.columns([1, 2])
                
                with col_sev:
                    severity = st.slider(
                        "Severity",
                        1, 10, 5,
                        help="1 = Mild, 10 = Severe"
                    )
                
                with col_notes:
                    notes = st.text_area(
                        "Additional details (optional)",
                        placeholder="What were you doing? When did it start? What makes it better/worse?",
                        height=100
                    )
                
                submitted = st.form_submit_button("💾 Log This Symptom", use_container_width=True, type="primary")
                
                if submitted:
                    if symptom:
                        tracker.log_symptom(symptom, severity, notes)
                        st.success("✅ Symptom logged successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ Please describe your symptom")
        
        with col_stats:
            st.markdown("### 📈 Quick Statistics")
            
            insights = tracker.get_ai_insights()
            
            if insights:
                st.metric("📊 Total Entries", insights['total_entries'])
                st.metric("📉 Average Severity", f"{insights['average_severity']}/10")
                
                trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}
                st.metric("📊 Trend", f"{trend_emoji.get(insights['trend'], '➡️')} {insights['trend'].title()}")
            else:
                st.markdown("""
                <div class='info-box'>
                    <strong>💡 Getting Started</strong><br>
                    Log 3+ symptoms to unlock:
                    <ul>
                        <li>Pattern analysis</li>
                        <li>AI insights</li>
                        <li>Trend charts</li>
                        <li>Specialist recommendations</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        # AI Insights & Charts
        if insights:
            st.markdown("---")
            st.markdown("## 🤖 AI-Powered Pattern Analysis")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("#### 📅 When do symptoms occur?")
                
                day_df = pd.DataFrame(list(insights['day_pattern'].items()), columns=['Day', 'Count'])
                fig = px.bar(
                    day_df, x='Day', y='Count',
                    title="Symptoms by Day of Week",
                    color='Count',
                    color_continuous_scale='Blues',
                    labels={'Count': 'Number of Symptoms'}
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12),
                    title_font_size=14,
                    showlegend=False,
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown(f"""
                <div class='info-box'>
                    <strong>💡 Pattern Detected:</strong><br>
                    Most symptoms occur on <strong>{insights['most_common_day']}s</strong>
                </div>
                """, unsafe_allow_html=True)
                
                if insights['weekday_vs_weekend']['pattern'] == 'weekday-dominant':
                    st.markdown("""
                    <div class='warning-box'>
                        <strong>⚠️ Weekday Pattern:</strong> Symptoms mostly on weekdays - could be work/stress-related
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_chart2:
                st.markdown("#### 🕐 What time of day?")
                
                time_df = pd.DataFrame(list(insights['time_pattern'].items()), columns=['Period', 'Count'])
                fig = px.pie(
                    time_df,
                    values='Count',
                    names='Period',
                    title="Symptoms by Time of Day",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig.update_layout(
                    font=dict(family="Inter", size=12),
                    title_font_size=14,
                    height=300
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown(f"""
                <div class='info-box'>
                    <strong>💡 Peak Time:</strong><br>
                    Most symptoms in the <strong>{insights['most_common_time']}</strong>
                </div>
                """, unsafe_allow_html=True)
            
            # AI Insights Generation
            st.markdown("---")
            
            if st.button("🤖 Generate AI Insights & Recommendations", use_container_width=True, type="primary"):
                rag = load_rag()
                if rag:
                    with st.spinner("🔮 AI is analyzing your symptom patterns... This may take 10-20 seconds"):
                        insight_text = tracker.generate_insight_text()
                        
                        prompt = f"""As a medical education assistant, analyze these detailed symptom tracking patterns:

{insight_text}

Provide comprehensive insights including:
1. Notable patterns in timing, frequency, and severity
2. Possible correlations or triggers to consider (stress, diet, activities, sleep)
3. What additional factors the patient should monitor
4. Assessment of when to see a doctor and urgency level
5. Specific questions to ask their doctor about these patterns

Be specific, actionable, and educational. Provide concrete recommendations."""
                        
                        ai_insights = rag.llm.generate([
                            {"role": "system", "content": "You are a medical education assistant analyzing symptom patterns to provide helpful insights."},
                            {"role": "user", "content": prompt}
                        ], temperature=0.3, max_tokens=1500)
                        
                        st.markdown("### 🤖 AI-Generated Insights")
                        st.markdown(f"""
                        <div class='feature-card'>
                            {ai_insights.replace('<s>', '').replace('</s>', '')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        <div class='info-box'>
                            <strong>💡 Next Steps:</strong> Share these insights with your doctor at your next visit
                        </div>
                        """, unsafe_allow_html=True)
        
        # Specialist Finder
        entries = tracker.get_all_symptoms()
        
        if entries and len(entries) >= 1:
            st.markdown("---")
            st.markdown("## 👨‍⚕️ Which Specialist Should I See?")
            
            recent_symptoms = [e['symptom'] for e in entries[-5:]]
            
            st.markdown(f"""
            <div class='info-box'>
                <strong>📋 Analyzing your recent symptoms:</strong><br>
                {', '.join(recent_symptoms[:3])}
            </div>
            """, unsafe_allow_html=True)
            
            col_spec1, col_spec2 = st.columns([2, 1])
            
            with col_spec1:
                if st.button("🔍 Find the Right Specialist for Me", use_container_width=True, type="primary"):
                    specialist_matcher = SpecialistMatcher(rag_system=rag)
                    
                    with st.spinner("🤖 Analyzing your symptoms and matching with specialists..."):
                        match_result = specialist_matcher.match_specialist(recent_symptoms)
                        
                        if match_result['specialists']:
                            top = match_result['specialists'][0]
                            
                            # Urgency warning
                            if match_result['urgency'] == 'urgent':
                                st.markdown("""
                                <div style='background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%); 
                                            border: 4px solid #EF4444; border-radius: 16px; padding: 2rem; text-align: center;'>
                                    <h3 style='color: #DC2626 !important;'>🚨 URGENT SYMPTOMS DETECTED</h3>
                                    <p style='color: #7F1D1D !important;'>These symptoms may require immediate medical attention</p>
                                </div>
                                """, unsafe_allow_html=True)
                                st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Specialist recommendation
                            st.markdown(f"""
                            <div class='feature-card' style='background: linear-gradient(135deg, #FFFFFF 0%, #F0F9FF 100%); 
                                                           border-left: 6px solid #3B82F6;'>
                                <h2 style='color: #1E40AF !important; margin-top: 0;'>
                                    {top['icon']} {top['name']}
                                </h2>
                                <p style='font-size: 1.1rem; color: #475569 !important;'>
                                    <strong>Specializes in:</strong> {top['treats']}
                                </p>
                                <p style='font-size: 1.05rem;'>
                                    <strong>Match Confidence:</strong> 
                                    <span style='color: #10B981; font-weight: 700; font-size: 1.3rem;'>{top['confidence']:.0f}%</span>
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Get AI explanation
                            enhanced_exp = specialist_matcher.get_rag_enhanced_recommendation(recent_symptoms)
                            
                            if enhanced_exp:
                                st.markdown("#### 💡 Why This Specialist?")
                                st.markdown(f"""
                                <div class='info-box'>
                                    {enhanced_exp.replace('<s>', '').replace('</s>', '')}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Other specialists
                            if len(match_result['specialists']) > 1:
                                st.markdown("#### 👥 Other Specialists to Consider")
                                for spec in match_result['specialists'][1:3]:
                                    st.markdown(f"- {spec['icon']} **{spec['name']}** ({spec['confidence']:.0f}% match)")
                            
                            # Next steps
                            st.markdown("---")
                            st.markdown("### 📞 Next Steps")
                            
                            if match_result['urgency'] == 'urgent':
                                st.markdown("""
                                1. 🚨 **Seek immediate medical attention** - Go to ER or call 911
                                2. 📞 Call the specialist's office for urgent appointment
                                3. 📋 Bring list of symptoms and medications
                                """)
                            else:
                                st.markdown("""
                                1. 📞 **Call to schedule** an appointment with the recommended specialist
                                2. 📋 **Prepare** a list of your symptoms and current medications
                                3. 💊 **Bring** any recent lab results or medical records
                                4. 🩺 **Consider starting** with your primary care doctor for referral
                                """)
            
            with col_spec2:
                st.markdown("""
                <div class='info-box'>
                    <strong>💡 When to see a specialist:</strong><br><br>
                    ✅ Symptoms persist >2 weeks<br>
                    ✅ Severe or worsening<br>
                    ✅ Not improving with primary care<br>
                    ✅ Need specialized testing<br><br>
                    <strong>Start with primary care if:</strong><br><br>
                    • First time symptom<br>
                    • Mild symptoms<br>
                    • General checkup needed
                </div>
                """, unsafe_allow_html=True)
        
        # Symptom History
        if entries:
            st.markdown("---")
            st.markdown("### 📜 Your Symptom History")
            
            for entry in reversed(entries[-10:]):
                severity_color = "#EF4444" if entry['severity'] >= 7 else ("#F59E0B" if entry['severity'] >= 4 else "#10B981")
                severity_label = "Severe" if entry['severity'] >= 7 else ("Moderate" if entry['severity'] >= 4 else "Mild")
                
                with st.expander(f"📅 {entry['date_display']} • {entry['symptom']} • {severity_label} ({entry['severity']}/10)"):
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.write(f"**Severity:** {entry['severity']}/10")
                        st.write(f"**Day:** {entry['day_of_week']}")
                    with col_d2:
                        st.write(f"**Time:** {entry['time_of_day']}")
                        if entry.get('notes'):
                            st.write(f"**Notes:** {entry['notes']}")
                    
                    if st.button("🗑️ Delete Entry", key=f"del_{entry['id']}"):
                        tracker.delete_entry(entry['id'])
                        st.success("Deleted")
                        st.rerun()
            
            # Export
            st.markdown("---")
            export_text = f"""SYMPTOM LOG - HEALTH COMPASS
{'='*70}

Total Entries: {len(entries)}
Period: {entries[0]['date_display']} to {entries[-1]['date_display']}

DETAILED LOG:

"""
            for e in entries:
                export_text += f"""
Date: {e['date_display']} ({e['day_of_week']}, {e['time_of_day']})
Symptom: {e['symptom']}
Severity: {e['severity']}/10
Notes: {e.get('notes', 'None')}
{'-'*70}
"""
            
            if insights:
                export_text += f"""

PATTERN ANALYSIS:
- Most common symptom: {insights['most_common_symptom']}
- Average severity: {insights['average_severity']}/10
- Trend: {insights['trend']}
- Most common day: {insights['most_common_day']}
- Most common time: {insights['most_common_time']}

{'='*70}
Generated by Health Compass | Bring this to your doctor
"""
            
            st.download_button(
                "📥 Download Complete Symptom Log",
                export_text,
                f"symptom_log_{datetime.now().strftime('%Y%m%d')}.txt",
                use_container_width=True
            )
    
    # ==================== AI ASSISTANT ====================
    with tabs[4]:
        st.markdown("## 💬 AI Healthcare Assistant")
        st.caption("🤖 Personalized medical guidance powered by your health profile")
        
        profile = st.session_state.user_profile
        assistant = HealthcareAssistant()
        
        # Initialize chat
        if not st.session_state.chat_history:
            welcome_msg = f"""Hello **{profile.get_profile_summary()['name']}**! 👋

I'm your AI Healthcare Assistant, and I have access to your health profile. I can help you with:

• 💊 **Medication information** - Uses, dosages, interactions
• 🩺 **Symptom guidance** - What symptoms might mean
• 🏥 **Hospital finder** - Medical facilities near you
• 📚 **Health education** - Conditions, treatments, prevention
• ❓ **General health questions** - Evidence-based answers

All my responses are personalized for you based on your age, gender, and health conditions.

**How can I help you today?**"""
            
            st.session_state.chat_history = [{'role': 'assistant', 'content': welcome_msg}]
        
        # Display chat
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role'], avatar="🤖" if msg['role'] == 'assistant' else "👤"):
                st.markdown(msg['content'])
                
                if msg.get('sources'):
                    with st.expander("📚 View Sources"):
                        for i, src in enumerate(msg['sources'], 1):
                            st.markdown(f"**{i}.** {src.get('source')} - {src.get('title', '')}")
        
        # Chat input
        user_input = st.chat_input("💬 Type your health question here...")
        
        if user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            rag = load_rag()
            if rag:
                with st.spinner("🤖 AI is thinking and searching medical database..."):
                    user_lower = user_input.lower()
                    
                    # Hospital/location query
                    if any(kw in user_lower for kw in ['hospital', 'clinic', 'doctor near', 'find hospital', 'medical center', 'emergency room', 'er near', 'urgent care']):
                        prof_data = assistant.get_user_profile()
                        location = prof_data.get('location', 'your area')
                        
                        # Extract location from message
                        if ' near ' in user_lower or ' in ' in user_lower:
                            words = user_input.split()
                            for i, w in enumerate(words):
                                if w.lower() in ['near', 'in'] and i + 1 < len(words):
                                    location = ' '.join(words[i+1:]).strip('.,!?')
                                    break
                        
                        hospitals = assistant.get_hospital_suggestions(location)
                        
                        response = f"### 🏥 Medical Facilities Near {location}\n\n"
                        response += "I found these healthcare facilities for you:\n\n"
                        
                        for i, h in enumerate(hospitals[:5], 1):
                            if h.get('name'):
                                response += f"**{i}. {h['name']}**\n"
                                if h.get('address'):
                                    response += f"📍 {h['address']}\n"
                                if h.get('phone'):
                                    response += f"📞 {h['phone']}\n"
                                if h.get('specialty'):
                                    response += f"🏥 Specialties: {h['specialty']}\n"
                                response += "\n"
                        
                        response += """---

💡 **Choosing the right facility:**
- 🚨 **Severe/urgent symptoms** → Emergency Room (ER)
- ⚠️ **Non-life-threatening urgent** → Urgent Care
- 📅 **Routine care** → Schedule with primary doctor
- 🩺 **Specialist needed** → Get referral first

Would you like more information about any specific facility?"""
                        
                        sources = []
                    
                    # Regular health question
                    else:
                        profile_context = profile.get_context_for_ai()
                        rag_result = rag.query(user_input, n_results=3)
                        
                        prompt = f"""You are a personalized healthcare assistant. Here's the patient's profile:

{profile_context}

Patient asks: {user_input}

Relevant medical information from trusted sources:
{rag_result['answer'][:1500]}

Provide a helpful, personalized response (4-5 sentences) that:
1. Directly answers their question using the medical information
2. Considers their specific age, gender, conditions, and medications
3. Mentions relevant profile factors naturally (e.g., "Given your hypertension...")
4. Gives practical, actionable advice
5. Encourages consulting healthcare provider for personalized care

Be conversational, supportive, and focus on what's most relevant to THIS patient.
DO NOT include legal disclaimers or boilerplate text."""
                        
                        response = rag.llm.generate([
                            {"role": "system", "content": "You are a personalized healthcare assistant with full patient context. Provide helpful, specific guidance."},
                            {"role": "user", "content": prompt}
                        ], temperature=0.4, max_tokens=600)
                        
                        response = response.replace('<s>', '').replace('</s>', '').strip()
                        
                        # Add source note
                        if rag_result.get('sources'):
                            response += "\n\n---\n*Information from: " + ", ".join(set([s.get('source', 'Medical Database') for s in rag_result['sources'][:3]])) + "*"
                        
                        sources = rag_result.get('sources', [])
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'sources': sources
                    })
                    
                    st.rerun()
        
        # Sidebar chat actions
        with st.sidebar:
            st.markdown("---")
            st.markdown("## 💬 Chat Actions")
            
            if len(st.session_state.chat_history) > 1:
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
                
                # Download chat
                chat_text = f"""HEALTH COMPASS CONVERSATION
{'='*70}

Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Patient: {profile.get_profile_summary()['name']}

{'='*70}

CONVERSATION:

"""
                for msg in st.session_state.chat_history:
                    role = "You" if msg['role'] == 'user' else "AI Assistant"
                    chat_text += f"\n{role}:\n{msg['content']}\n\n"
                
                st.download_button(
                    "📥 Download Conversation",
                    chat_text,
                    f"chat_{datetime.now().strftime('%Y%m%d')}.txt",
                    use_container_width=True
                )
    
    # FOOTER
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 3rem 1rem; color: #64748B;'>
        <div style='font-size: 1.5rem; font-weight: 800; color: #1E40AF; margin-bottom: 1rem;'>
            🏥 Health Compass
        </div>
        <div style='font-size: 1.05rem; margin-bottom: 0.75rem;'>
            <strong>Educational Information Only</strong> • Not Medical Advice • Always Consult Healthcare Professionals
        </div>
        <div style='font-size: 0.9rem; color: #94A3B8; margin-top: 1.5rem;'>
            INFO 7390 - Advanced Data Science & Architecture<br>
            Manish Kondoju | Northeastern University | Fall 2024
        </div>
        <div style='font-size: 0.85rem; color: #CBD5E1; margin-top: 1rem;'>
            Built with Streamlit • ChromaDB • Llama 3.2 • sentence-transformers
        </div>
    </div>
    """, unsafe_allow_html=True)