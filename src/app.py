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

# Debug: Print to confirm app is loading
print("✅ App starting - imports successful")

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("✅ Path configuration complete")

from src.rag.rag_pipeline import HealthCompassRAG
from src.utils.symptom_tracker import SymptomTracker
from src.utils.healthcare_assistant import HealthcareAssistant
from src.utils.document_analyzer_enhanced import EnhancedDocumentAnalyzer
from src.utils.specialist_matcher import SpecialistMatcher
from src.utils.user_profile import UserProfile

print("✅ Custom modules imported")

# Initialize user profile
try:
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = UserProfile()
    
    # Better onboarding detection
    if 'show_onboarding' not in st.session_state:
        try:
            profile_data = st.session_state.user_profile.get_basic_info()
            has_valid_profile = (
                profile_data.get('name') and 
                profile_data.get('name') != '' and
                profile_data.get('age') and
                profile_data.get('age') > 0
            )
            st.session_state.show_onboarding = not has_valid_profile
        except Exception as e:
            # If profile check fails, show onboarding
            st.session_state.show_onboarding = True
except Exception as e:
    st.error(f"Error initializing profile: {e}")
    st.stop()

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

print("✅ Session state initialized")

# Load RAG
@st.cache_resource(show_spinner=False)
def load_rag():
    try:
        print("🔄 Loading RAG system...")
        return HealthCompassRAG()
    except Exception as e:
        print(f"❌ RAG loading failed: {e}")
        return None

print("✅ RAG loader defined")

# ==================== MODERN UI STYLES ====================
def inject_modern_styles():
    st.markdown("""
    <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Resets & Base */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }
        
        /* App Background with Pattern */
        .stApp {
            background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 50%, #f0f9ff 100%);
            background-attachment: fixed;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(6, 182, 212, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(20, 184, 166, 0.03) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* ==================== ONBOARDING STYLES ==================== */
        .onboarding-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        .onboarding-hero {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 50%, #0e7490 100%);
            padding: 4rem 3rem;
            border-radius: 32px;
            text-align: center;
            margin-bottom: 3rem;
            box-shadow: 
                0 20px 60px rgba(6, 182, 212, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
            position: relative;
            overflow: hidden;
        }
        
        .onboarding-hero::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .onboarding-hero h1 {
            color: white !important;
            font-size: 3.5rem !important;
            font-weight: 900 !important;
            margin: 0 0 1rem 0 !important;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            position: relative;
            z-index: 1;
        }
        
        .onboarding-hero p {
            color: rgba(255, 255, 255, 0.95) !important;
            font-size: 1.4rem !important;
            font-weight: 400 !important;
            margin: 0 !important;
            position: relative;
            z-index: 1;
        }
        
        .step-card {
            background: white;
            padding: 3rem;
            border-radius: 24px;
            box-shadow: 
                0 10px 40px rgba(0, 0, 0, 0.08),
                0 0 0 1px rgba(0, 0, 0, 0.03);
            margin: 2rem 0;
            border: 1px solid rgba(6, 182, 212, 0.1);
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .step-card h2 {
            color: #0e7490 !important;
            font-size: 2rem !important;
            margin-bottom: 2rem !important;
        }
        
        /* Progress Bar Enhancement */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #06b6d4 0%, #14b8a6 100%);
            border-radius: 10px;
            height: 8px;
        }
        
        /* ==================== MAIN APP STYLES ==================== */
        
        /* Header */
        .app-header {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 50%, #14b8a6 100%);
            padding: 3rem 3rem 4rem 3rem;
            margin: -4rem -4rem 3rem -4rem;
            border-radius: 0 0 40px 40px;
            box-shadow: 
                0 20px 60px rgba(6, 182, 212, 0.25),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
            position: relative;
            overflow: hidden;
        }
        
        .app-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.4;
        }
        
        .app-header h1 {
            color: white !important;
            font-size: 3rem !important;
            font-weight: 900 !important;
            margin: 0 0 0.5rem 0 !important;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            position: relative;
            z-index: 1;
        }
        
        .app-header p {
            color: rgba(255, 255, 255, 0.95) !important;
            font-size: 1.3rem !important;
            font-weight: 500 !important;
            margin: 0 !important;
            position: relative;
            z-index: 1;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
            border-right: 1px solid rgba(6, 182, 212, 0.2);
        }
        
        [data-testid="stSidebar"] * {
            color: rgba(255, 255, 255, 0.9) !important;
        }
        
        [data-testid="stSidebar"] h2 {
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.4rem !important;
            margin: 1.5rem 0 1rem 0 !important;
        }
        
        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.1) !important;
            margin: 1.5rem 0 !important;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(6, 182, 212, 0.15) !important;
            border: 1px solid rgba(6, 182, 212, 0.3) !important;
            color: white !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(6, 182, 212, 0.25) !important;
            border-color: rgba(6, 182, 212, 0.5) !important;
            transform: translateY(-2px);
        }
        
        /* Form Elements */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {
            background: white !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 16px !important;
            padding: 1rem !important;
            font-size: 1rem !important;
            color: #0f172a !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
            border-color: #06b6d4 !important;
            box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1) !important;
            transform: translateY(-2px);
        }
        
        .stTextInput label, .stTextArea label, .stNumberInput label, .stSelectbox label {
            color: #0f172a !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Select Boxes */
        .stSelectbox > div > div, [data-baseweb="select"], [data-baseweb="select"] > div {
            background: white !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 16px !important;
            color: #0f172a !important;
        }
        
        [data-baseweb="select"]:hover {
            border-color: #06b6d4 !important;
        }
        
        [role="listbox"] {
            background: white !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 16px !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15) !important;
        }
        
        [role="option"] {
            background: white !important;
            color: #0f172a !important;
            padding: 0.75rem 1rem !important;
            transition: all 0.2s ease !important;
        }
        
        [role="option"]:hover {
            background: linear-gradient(90deg, #ecfeff 0%, #f0fdfa 100%) !important;
            color: #0e7490 !important;
            transform: translateX(4px);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 0.9rem 2.5rem !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            box-shadow: 
                0 10px 30px rgba(6, 182, 212, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow: 
                0 15px 40px rgba(6, 182, 212, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.2) inset !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: white;
            padding: 0.8rem 1rem;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            margin-bottom: 2.5rem;
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #64748b !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding: 0.9rem 2rem !important;
            border-radius: 14px !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #f8fafc !important;
            color: #0891b2 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
        }
        
        /* Metrics */
        [data-testid="stMetric"] {
            background: white;
            border-radius: 20px;
            padding: 2rem 1.5rem;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.06),
                0 0 0 1px rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(6, 182, 212, 0.08);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 
                0 12px 40px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(6, 182, 212, 0.15);
        }
        
        [data-testid="stMetricLabel"] {
            color: #64748b !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        [data-testid="stMetricValue"] {
            color: #0891b2 !important;
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            font-family: 'Poppins', sans-serif !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background: white !important;
            border-radius: 16px !important;
            padding: 1.2rem 1.5rem !important;
            font-weight: 600 !important;
            color: #0f172a !important;
            border: 1px solid #e2e8f0 !important;
            transition: all 0.3s ease !important;
        }
        
        .streamlit-expanderHeader:hover {
            background: #f8fafc !important;
            border-color: #06b6d4 !important;
            transform: translateX(4px);
        }
        
        .streamlit-expanderContent {
            background: white !important;
            border: 1px solid #e2e8f0 !important;
            border-top: none !important;
            border-radius: 0 0 16px 16px !important;
            padding: 1.5rem !important;
        }
        
        /* Source Cards */
        .source-card {
            background: linear-gradient(135deg, #ecfeff 0%, #f0fdfa 100%);
            border: 1px solid #a5f3fc;
            border-left: 5px solid #06b6d4;
            border-radius: 16px;
            padding: 1.8rem;
            margin: 1.2rem 0;
            box-shadow: 0 4px 12px rgba(6, 182, 212, 0.1);
            transition: all 0.3s ease;
        }
        
        .source-card:hover {
            transform: translateX(8px);
            box-shadow: 0 8px 24px rgba(6, 182, 212, 0.2);
            border-left-width: 8px;
        }
        
        .source-card strong {
            color: #0e7490 !important;
            font-size: 1.1rem;
            display: block;
            margin-bottom: 0.5rem;
        }
        
        .source-card a {
            color: #06b6d4 !important;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        
        .source-card a:hover {
            color: #0891b2 !important;
            text-decoration: underline;
        }
        
        /* Chat Messages */
        .stChatMessage {
            background: white !important;
            border-radius: 20px !important;
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06) !important;
            border: 1px solid rgba(0, 0, 0, 0.03) !important;
        }
        
        /* File Uploader */
        [data-testid="stFileUploader"] {
            background: white;
            border: 2px dashed #cbd5e1;
            border-radius: 20px;
            padding: 2rem;
            transition: all 0.3s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #06b6d4;
            background: #f0fdfa;
        }
        
        /* Alerts */
        .stAlert {
            border-radius: 16px !important;
            border-left-width: 5px !important;
            padding: 1.2rem 1.5rem !important;
        }
        
        /* Radio Buttons */
        .stRadio > div {
            background: white;
            padding: 1rem;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
        }
        
        .stRadio label {
            color: #0f172a !important;
            font-weight: 500 !important;
        }
        
        /* Slider */
        .stSlider {
            padding: 1rem 0;
        }
        
        .stSlider [data-baseweb="slider"] {
            margin-top: 1rem;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #06b6d4 !important;
        }
        
        /* Custom Cards */
        .info-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(6, 182, 212, 0.1);
            margin: 1.5rem 0;
            transition: all 0.3s ease;
        }
        
        .info-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
        }
        
        .info-card h3 {
            color: #0891b2 !important;
            font-size: 1.5rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* Footer */
        .app-footer {
            text-align: center;
            padding: 3rem 2rem;
            margin-top: 4rem;
            background: white;
            border-radius: 24px;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
        }
        
        .app-footer h3 {
            color: #0891b2 !important;
            font-size: 1.8rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .app-footer p {
            color: #64748b !important;
            font-size: 1rem !important;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            border-radius: 10px;
            border: 2px solid #f1f5f9;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== ONBOARDING FLOW ====================
if st.session_state.show_onboarding:
    print("🎯 Starting ONBOARDING flow")
    st.set_page_config(
        page_title="Welcome to Health Compass",
        page_icon="🏥",
        layout="wide"
    )
    
    inject_modern_styles()
    
    st.markdown("""
    <div class='onboarding-container'>
        <div class='onboarding-hero'>
            <h1>👋 Welcome to Health Compass!</h1>
            <p>Let's set up your personalized health profile in just a few steps</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1
    
    profile = st.session_state.user_profile
    progress = st.session_state.onboarding_step / 4
    
    # Progress indicator
    col_prog1, col_prog2, col_prog3 = st.columns([1, 3, 1])
    with col_prog2:
        st.progress(progress)
        st.markdown(f"<p style='text-align: center; color: #0891b2; font-weight: 600; margin-top: 0.5rem;'>Step {st.session_state.onboarding_step} of 4</p>", unsafe_allow_html=True)
    
    # STEP 1
    if st.session_state.onboarding_step == 1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 📋 Basic Information")
        st.caption("Tell us a bit about yourself")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe", key="onb_name")
            age = st.number_input("Age *", min_value=1, max_value=120, value=30, key="onb_age")
        with col2:
            gender = st.selectbox("Gender *", ["Select...", "Male", "Female", "Other"], key="onb_gender")
            dob = st.date_input("Date of Birth", value=None, key="onb_dob")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
        with col_b2:
            if st.button("Continue →", use_container_width=True, type="primary"):
                if name and age and gender != "Select...":
                    profile.update_basic_info(name=name, age=age, gender=gender, dob=dob.isoformat() if dob else None)
                    st.session_state.onboarding_step = 2
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields")
    
    # STEP 2
    elif st.session_state.onboarding_step == 2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("## 🏥 Health Information")
        st.caption("Help us understand your health better")
        
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, key="onb_height")
            weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70, key="onb_weight")
        with col2:
            blood_type = st.selectbox("Blood Type", ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="onb_blood")
        
        st.markdown("---")
        allergies_input = st.text_area("Allergies (one per line)", placeholder="Penicillin\nPeanuts", height=100, key="onb_allergies")
        conditions_input = st.text_area("Chronic Conditions (one per line)", placeholder="Diabetes\nHypertension", height=100, key="onb_conditions")
        
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
        st.markdown("## 🏃 Lifestyle Habits")
        st.caption("These help us give you better recommendations")
        
        col1, col2 = st.columns(2)
        with col1:
            smoking = st.selectbox("Smoking Status", ["Never", "Former smoker", "Current smoker"], key="onb_smoking")
            alcohol = st.selectbox("Alcohol Consumption", ["None", "Occasional", "Moderate", "Heavy"], key="onb_alcohol")
        with col2:
            exercise = st.selectbox("Exercise Level", ["Sedentary", "Light", "Moderate", "Active"], key="onb_exercise")
            diet = st.selectbox("Diet Type", ["Balanced", "Vegetarian", "Vegan", "Other"], key="onb_diet")
        
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
        st.markdown("## ⚙️ Preferences")
        st.caption("Just a couple more things...")
        
        location = st.text_input("Location (Optional)", placeholder="Boston, MA", key="onb_location")
        language = st.selectbox("Preferred Language", ["English", "Spanish", "Chinese", "French"], key="onb_language")
        
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
                st.success("✅ Welcome to Health Compass! Your profile is ready.")
                import time
                time.sleep(1.5)
                st.rerun()

# ==================== MAIN APP ====================
else:
    print("🎯 Starting MAIN APP flow")
    st.set_page_config(
        page_title="Health Compass | AI Medical Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    inject_modern_styles()
    
    translations = {
        'English': {'header': 'Health Compass', 'tagline': 'Your AI-Powered Medical Assistant',
                   'search_placeholder': 'Ask any health question...', 'search_btn': 'Search',
                   'emergency': 'Emergency', 'call_911': 'Call 911 Immediately'},
        'Spanish': {'header': 'Brújula de Salud', 'tagline': 'Asistente Médico con IA',
                   'search_placeholder': 'Pregunta de salud...', 'search_btn': 'Buscar',
                   'emergency': 'Emergencia', 'call_911': 'Llamar 911'},
        'Chinese': {'header': '健康指南针', 'tagline': 'AI医疗助手',
                   'search_placeholder': '健康问题...', 'search_btn': '搜索',
                   'emergency': '紧急', 'call_911': '911'},
        'French': {'header': 'Boussole Santé', 'tagline': 'Assistant Médical IA',
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
        st.markdown(f"### {summary['name']}")
        st.caption(f"🎂 {summary['age']} years • {summary.get('gender', 'N/A')}")
        
        if summary['bmi']:
            st.caption(f"📊 BMI: {summary['bmi']} ({summary['bmi_category']})")
        if summary['conditions_count'] > 0:
            st.caption(f"📋 {summary['conditions_count']} condition(s) tracked")
        
        if st.button("🔄 Create New Profile", use_container_width=True):
            st.session_state.user_profile.reset_profile()
            st.session_state.show_onboarding = True
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("## 🌍 Language")
        lang = st.selectbox("Choose Language", ["English", "Spanish", "Chinese", "French"], 
                           index=["English", "Spanish", "Chinese", "French"].index(st.session_state.language),
                           label_visibility="collapsed", key="sidebar_lang")
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"## 🚨 {t['emergency']}")
        st.error(f"**☎️ {t['call_911']}**")
        st.caption("☠️ Poison Control: 1-800-222-1222")
        st.caption("🧠 Mental Health Crisis: 988")
        st.caption("🩺 Non-Emergency: 311")
        
        st.markdown("---")
        st.markdown("## 📊 System Status")
        rag = load_rag()
        if rag:
            try:
                stats = rag.vector_db.get_stats()
                st.success("✅ System Online")
                st.caption(f"📚 {stats['total_documents']} medical documents")
                st.caption(f"🔍 RAG System: Active")
            except:
                st.warning("⚠️ Limited Mode")
        else:
            st.error("❌ System Offline")
    
    # Track active tab using session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Main tabs with modern icons
    tab_dash, tab_qa, tab_doc, tab_symptom, tab_ai = st.tabs([
        "🏠 Dashboard", "🔍 Medical Q&A", "📄 Doc Analyzer", "📊 Symptom Tracker", "💬 AI Assistant"
    ])
    
    # ==================== TAB: DASHBOARD ====================
    with tab_dash:
        st.markdown("### 🏠 Your Personal Health Dashboard")
        
        profile = st.session_state.user_profile
        summary = profile.get_profile_summary()
        basic = profile.get_basic_info()
        health = profile.get_health_info()
        lifestyle = profile.get_lifestyle()
        
        st.markdown(f"## Welcome back, {summary['name']}! 👋")
        st.caption(f"📅 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        st.markdown("---")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👤 Age", f"{summary['age']}" if summary['age'] else "Not set", help="Your current age")
        with col2:
            if summary['bmi']:
                bmi_value = summary['bmi']
                bmi_cat = summary['bmi_category']
                st.metric("📊 BMI", bmi_value, delta=bmi_cat, delta_color="off", help="Body Mass Index")
            else:
                st.metric("📊 BMI", "Not calculated", help="Set height and weight to calculate")
        with col3:
            st.metric("🏥 Conditions", summary['conditions_count'], help="Tracked chronic conditions")
        with col4:
            risk_color = {'Low': '🟢', 'Moderate': '🟡', 'High': '🔴'}
            risk_icon = risk_color.get(summary['lifestyle_risk'], '⚪')
            st.metric("⚕️ Lifestyle Risk", f"{risk_icon} {summary['lifestyle_risk']}", 
                     help="Based on smoking, alcohol, and exercise habits")
        
        st.markdown("---")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown("### 📊 Health Overview")
            
            # Medical Information
            with st.expander("🩺 Medical Information", expanded=True):
                if health.get('height') and health.get('weight'):
                    col_h, col_w = st.columns(2)
                    with col_h:
                        st.metric("Height", f"{health['height']} cm")
                    with col_w:
                        st.metric("Weight", f"{health['weight']} kg")
                else:
                    st.info("💡 Add your height and weight to calculate BMI")
                
                if health.get('blood_type'):
                    st.write(f"🩸 **Blood Type:** {health['blood_type']}")
                
                allergies = health.get('allergies', [])
                if allergies:
                    st.write(f"⚠️ **Allergies:** {', '.join(allergies)}")
                else:
                    st.caption("No allergies recorded")
            
            # Chronic Conditions
            with st.expander("🏥 Chronic Conditions"):
                conditions = health.get('chronic_conditions', [])
                if conditions:
                    for idx, c in enumerate(conditions, 1):
                        st.write(f"{idx}. {c}")
                else:
                    st.info("✅ No chronic conditions recorded")
        
        with col_right:
            st.markdown("### ⚡ Quick Actions")
            if st.button("📝 Log New Symptom", use_container_width=True, key="qa_symptom"):
                st.info("Switch to the Symptom Tracker tab →")
            if st.button("📄 Analyze Document", use_container_width=True, key="qa_doc"):
                st.info("Switch to the Doc Analyzer tab →")
            if st.button("💬 Chat with AI", use_container_width=True, key="qa_chat"):
                st.info("Switch to the AI Assistant tab →")
            
            st.markdown("---")
            st.markdown("### 🏃 Lifestyle Factors")
            
            icons = {
                'smoking': {'never': '✅ Non-smoker', 'former': '⚠️ Former smoker', 'current': '🚫 Current smoker'},
                'exercise': {'sedentary': '😴 Sedentary', 'light': '🚶 Light activity', 'moderate': '🏃 Moderate activity', 'active': '💪 Very active'},
                'alcohol': {'none': '✅ No alcohol', 'occasional': '🍷 Occasional', 'moderate': '⚠️ Moderate', 'heavy': '🚫 Heavy use'}
            }
            
            st.write("🚭 " + icons['smoking'].get(lifestyle.get('smoking', 'never'), 'Not set'))
            st.write("🏃 " + icons['exercise'].get(lifestyle.get('exercise', 'sedentary'), 'Not set'))
            st.write("🍷 " + icons['alcohol'].get(lifestyle.get('alcohol', 'none'), 'Not set'))
            
            st.markdown("---")
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                if st.button("⚙️ Edit Profile", use_container_width=True):
                    st.session_state.show_profile_editor = True
                    st.rerun()
            with col_e2:
                if st.button("🔄 Reset All", use_container_width=True):
                    if st.session_state.get('confirm_reset'):
                        st.session_state.user_profile.reset_profile()
                        st.session_state.show_onboarding = True
                        st.session_state.confirm_reset = False
                        st.rerun()
                    else:
                        st.session_state.confirm_reset = True
                        st.warning("Click again to confirm reset")
        
        # Profile Editor
        if st.session_state.get('show_profile_editor', False):
            st.markdown("---")
            st.markdown("## ⚙️ Edit Your Profile")
            
            edit_type = st.radio("Select what to edit:", ["Basic Info", "Health Info", "Lifestyle", "✖️ Close"], 
                               horizontal=True, key="edit_radio")
            
            if edit_type == "Basic Info":
                with st.form("edit_basic"):
                    st.markdown("### 📋 Basic Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Name", value=basic.get('name', ''))
                        age = st.number_input("Age", value=basic.get('age', 30), min_value=1)
                    with col2:
                        gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                            index=["Male", "Female", "Other"].index(basic.get('gender', 'Male')) if basic.get('gender') in ["Male", "Female", "Other"] else 0)
                    
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        profile.update_basic_info(name=name, age=age, gender=gender)
                        st.success("✅ Profile updated successfully!")
                        st.session_state.show_profile_editor = False
                        import time
                        time.sleep(1)
                        st.rerun()
            
            elif edit_type == "Health Info":
                with st.form("edit_health"):
                    st.markdown("### 🏥 Health Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        height = st.number_input("Height (cm)", value=health.get('height', 170), min_value=50, max_value=250)
                        weight = st.number_input("Weight (kg)", value=health.get('weight', 70), min_value=20, max_value=300)
                    with col2:
                        blood_type = st.selectbox("Blood Type", 
                                                 ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                                 index=["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(health.get('blood_type', 'Unknown')) if health.get('blood_type') else 0)
                    
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        profile.update_health_info(height=height, weight=weight, 
                                                  blood_type=blood_type if blood_type != "Unknown" else None)
                        st.success("✅ Health information updated!")
                        st.session_state.show_profile_editor = False
                        import time
                        time.sleep(1)
                        st.rerun()
            
            elif edit_type == "Lifestyle":
                with st.form("edit_lifestyle"):
                    st.markdown("### 🏃 Lifestyle Factors")
                    col1, col2 = st.columns(2)
                    with col1:
                        smoking = st.selectbox("Smoking", ["Never", "Former", "Current"],
                            index=["never", "former", "current"].index(lifestyle.get('smoking', 'never')))
                        alcohol = st.selectbox("Alcohol", ["None", "Occasional", "Moderate", "Heavy"],
                            index=["none", "occasional", "moderate", "heavy"].index(lifestyle.get('alcohol', 'none')))
                    with col2:
                        exercise = st.selectbox("Exercise", ["Sedentary", "Light", "Moderate", "Active"],
                            index=["sedentary", "light", "moderate", "active"].index(lifestyle.get('exercise', 'sedentary')))
                        diet = st.selectbox("Diet", ["Balanced", "Vegetarian", "Vegan", "Other"],
                            index=["balanced", "vegetarian", "vegan", "other"].index(lifestyle.get('diet', 'balanced')) if lifestyle.get('diet') else 0)
                    
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        maps = {
                            "Never": "never", "Former": "former", "Current": "current",
                            "None": "none", "Occasional": "occasional", "Moderate": "moderate", "Heavy": "heavy",
                            "Sedentary": "sedentary", "Light": "light", "Moderate": "moderate", "Active": "active",
                            "Balanced": "balanced", "Vegetarian": "vegetarian", "Vegan": "vegan", "Other": "other"
                        }
                        profile.update_lifestyle(
                            smoking=maps[smoking],
                            alcohol=maps[alcohol],
                            exercise=maps[exercise],
                            diet=maps.get(diet, 'balanced')
                        )
                        st.success("✅ Lifestyle updated!")
                        st.session_state.show_profile_editor = False
                        import time
                        time.sleep(1)
                        st.rerun()
            
            else:
                st.session_state.show_profile_editor = False
                st.rerun()
    
    # ==================== TAB: MEDICAL Q&A ====================
    with tab_qa:
        st.markdown("### 🔍 Medical Questions & Answers")
        st.warning("⚠️ **Disclaimer:** This is for educational purposes only. Not a substitute for professional medical advice.")
        
        query = st.text_area("💭 What would you like to know?", height=120, 
                           placeholder=t['search_placeholder'], key="qa_input")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            search_btn = st.button(f"🔍 {t['search_btn']}", type="primary", use_container_width=True)
        
        if search_btn and query:
            rag = load_rag()
            if rag:
                with st.spinner("🔎 Searching medical databases..."):
                    result = rag.query(query, n_results=5)
                
                if result.get('is_emergency'):
                    st.error("🚨 **EMERGENCY DETECTED - CALL 911 IMMEDIATELY**")
                    st.error(result.get('emergency_message', ''))
                    st.stop()
                
                st.markdown("---")
                st.markdown("### 📋 Answer")
                st.markdown(f"""
                <div class='info-card'>
                    {result['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                if result.get('sources'):
                    st.markdown("### 📚 Trusted Medical Sources")
                    st.caption(f"Information verified from {len(result['sources'])} trusted sources")
                    
                    for i, src in enumerate(result['sources'], 1):
                        st.markdown(f"""
                        <div class='source-card'>
                            <strong>{i}. {src.get('source', 'Medical Source')}</strong><br>
                            <span style='color: #64748b;'>{src.get('title', 'Medical Information')}</span><br>
                            <a href="{src.get('url', '#')}" target="_blank">🔗 Read Full Article →</a>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("❌ System is currently offline. Please try again later.")
    
    # ==================== TAB: DOCUMENT ANALYZER ====================
    with tab_doc:
        st.markdown("### 📄 Medical Document Analyzer")
        st.caption("Upload lab results, medical reports, or prescriptions for AI analysis")
        
        rag_system = load_rag()
        analyzer = EnhancedDocumentAnalyzer(rag_system=rag_system)
        
        profile = st.session_state.user_profile
        profile_gender = profile.get_basic_info().get('gender')
        
        col_upload, col_settings = st.columns([2, 1])
        
        with col_upload:
            uploaded_file = st.file_uploader("📎 Upload Document", 
                                            type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
                                            help="Supported formats: PDF, PNG, JPG, TXT")
        
        with col_settings:
            gender = st.selectbox("👤 Patient Gender", 
                ["Not specified", "Male", "Female"],
                index=0 if not profile_gender else (["Male", "Female"].index(profile_gender) + 1 if profile_gender in ["Male", "Female"] else 0))
        
        if uploaded_file:
            st.success(f"✅ File uploaded: **{uploaded_file.name}**")
            
            st.markdown("---")
            st.markdown("### 🔬 Analysis Options")
            
            analysis_type = st.radio("Select analysis type:", 
                ["🔬 Comprehensive Lab Analysis", 
                 "📋 Explain All Results", 
                 "⚠️ Highlight Abnormal Values Only", 
                 "❓ Generate Questions for Doctor", 
                 "💊 Medication Review"],
                key="analysis_type_radio")
            
            col_analyze1, col_analyze2, col_analyze3 = st.columns([1, 2, 1])
            with col_analyze2:
                analyze_btn = st.button("🤖 Analyze Document", type="primary", use_container_width=True)
            
            if analyze_btn:
                with st.spinner("🧬 Analyzing your medical document..."):
                    file_bytes = uploaded_file.getvalue()
                    gender_param = None if gender == "Not specified" else gender
                    
                    if "Lab Analysis" in analysis_type or "Lab Values" in analysis_type:
                        result = analyzer.analyze_document(file_bytes, uploaded_file.type, gender_param)
                        
                        if 'error' not in result:
                            st.success("✅ Analysis complete!")
                            st.markdown("---")
                            
                            # Metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Total Tests", result['total_tests'])
                            with col2:
                                st.metric("⚠️ Abnormal", result['abnormal_count'], 
                                        delta=f"{result['abnormal_count']/result['total_tests']*100:.0f}%" if result['total_tests'] > 0 else "0%")
                            with col3:
                                st.metric("✅ Normal", result['total_tests'] - result['abnormal_count'])
                            
                            st.markdown("---")
                            st.markdown("### 📋 Detailed Report")
                            st.markdown(f"""
                            <div class='info-card'>
                                {result['report']}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Error: {result['error']}")
                    else:
                        st.info("💡 This analysis type is coming soon!")
        else:
            st.info("👆 Please upload a medical document to get started")
    
    # ==================== TAB: SYMPTOM TRACKER ====================
    with tab_symptom:
        st.markdown("### 📊 Symptom Tracker & Specialist Finder")
        st.caption("Track your symptoms and find the right medical specialist")
        
        tracker = SymptomTracker()
        specialist_matcher = SpecialistMatcher(rag_system=load_rag())
        
        col_form, col_insights = st.columns([2, 1])
        
        with col_form:
            st.markdown("#### 📝 Log New Symptom")
            with st.form("symptom_form", clear_on_submit=True):
                symptom = st.text_input("Symptom Description", 
                                       placeholder="e.g., Headache, Fatigue, Chest pain",
                                       key="symptom_input")
                
                col_sev, col_date = st.columns(2)
                with col_sev:
                    severity = st.slider("Severity Level", 1, 10, 5, 
                                       help="1 = Mild, 10 = Severe")
                with col_date:
                    symptom_date = st.date_input("Date", value=datetime.now())
                
                notes = st.text_area("Additional Notes (Optional)", 
                                   height=80,
                                   placeholder="Any relevant details...",
                                   key="symptom_notes")
                
                submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
                with submit_col2:
                    submitted = st.form_submit_button("💾 Log Symptom", 
                                                     type="primary", 
                                                     use_container_width=True)
                
                if submitted and symptom:
                    tracker.log_symptom(symptom, severity, notes)
                    st.success("✅ Symptom logged successfully!")
                    st.rerun()
        
        with col_insights:
            st.markdown("#### 📈 Quick Stats")
            insights = tracker.get_ai_insights()
            if insights and insights['total_entries'] > 0:
                st.metric("📝 Total Entries", insights['total_entries'])
                st.metric("📊 Avg Severity", f"{insights['average_severity']:.1f}/10")
                
                # Severity indicator
                avg_sev = insights['average_severity']
                if avg_sev < 4:
                    st.success("🟢 Generally mild symptoms")
                elif avg_sev < 7:
                    st.warning("🟡 Moderate symptoms")
                else:
                    st.error("🔴 Severe symptoms - consult doctor")
            else:
                st.info("No symptoms logged yet")
        
        # Symptom history
        entries = tracker.get_all_symptoms()
        if entries:
            st.markdown("---")
            st.markdown("### 📜 Symptom History")
            
            # Show recent entries
            recent_entries = entries[-10:][::-1]  # Last 10, reversed
            
            for idx, entry in enumerate(recent_entries, 1):
                severity_color = "🟢" if entry['severity'] < 4 else "🟡" if entry['severity'] < 7 else "🔴"
                
                with st.expander(f"{severity_color} {entry['symptom']} - Severity: {entry['severity']}/10"):
                    st.write(f"**Date:** {entry['timestamp']}")
                    if entry.get('notes'):
                        st.write(f"**Notes:** {entry['notes']}")
            
            st.markdown("---")
            st.markdown("### 👨‍⚕️ Find the Right Specialist")
            
            recent_symptoms = [e['symptom'] for e in entries[-5:]]
            st.write(f"**Based on recent symptoms:** {', '.join(recent_symptoms[:3])}")
            
            col_spec1, col_spec2, col_spec3 = st.columns([1, 2, 1])
            with col_spec2:
                if st.button("🔍 Find Specialist", type="primary", use_container_width=True):
                    with st.spinner("🔎 Analyzing symptoms and matching specialists..."):
                        match = specialist_matcher.match_specialist(recent_symptoms)
                        
                        if match['specialists']:
                            st.markdown("---")
                            st.markdown("### 🎯 Recommended Specialists")
                            
                            for spec in match['specialists'][:3]:  # Top 3
                                st.markdown(f"""
                                <div class='info-card'>
                                    <h3>{spec['icon']} {spec['name']}</h3>
                                    <p><strong>Confidence:</strong> {spec['confidence']:.0f}%</p>
                                    <p><strong>Specializes in:</strong> {spec['treats']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            if match['urgency'] == 'urgent':
                                st.error("🚨 **URGENT:** Your symptoms may require immediate medical attention. Please seek care promptly.")
                        else:
                            st.info("💡 Unable to match specialists. Consider consulting a general practitioner.")
        else:
            st.info("👆 Start tracking your symptoms to get specialist recommendations")
    
    # ==================== TAB: AI ASSISTANT ====================
    with tab_ai:
        st.markdown("### 💬 AI Healthcare Assistant")
        st.caption("Chat with your personalized AI health assistant")
        
        profile = st.session_state.user_profile
        assistant = HealthcareAssistant()
        
        # Initialize chat
        if not st.session_state.chat_history:
            st.session_state.chat_history = [{
                'role': 'assistant',
                'content': f"Hello, {profile.get_basic_info().get('name', 'there')}! 👋 I'm your AI healthcare assistant. I can help answer health questions, explain medical terms, or discuss your symptoms. How can I assist you today?"
            }]
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role'], avatar="🤖" if msg['role'] == 'assistant' else "👤"):
                st.markdown(msg['content'])
        
        # Chat input (using form since st.chat_input can't be in tabs)
        st.markdown("---")
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_btn = st.columns([4, 1])
            with col_input:
                user_input = st.text_area("Message", height=100, 
                                         placeholder="💭 Type your message here...",
                                         label_visibility="collapsed",
                                         key="chat_text_input")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                send_btn = st.form_submit_button("📤 Send", type="primary", use_container_width=True)
        
        if send_btn and user_input:
            # Add user message
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            # Generate response
            rag = load_rag()
            if rag:
                with st.spinner("🤖 Thinking..."):
                    profile_context = profile.get_context_for_ai()
                    rag_result = rag.query(user_input, n_results=3)
                    
                    prompt = f"""Patient Profile:
{profile_context}

Patient Question: {user_input}

Medical Context: {rag_result['answer'][:1200]}

As a caring healthcare AI assistant, provide a brief, personalized response (3-4 sentences).
Consider the patient's profile and be conversational yet professional."""
                    
                    response = rag.llm.generate([
                        {"role": "system", "content": "You are a knowledgeable and empathetic healthcare AI assistant."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.4, max_tokens=500)
                    
                    response = response.replace('<s>', '').replace('</s>', '').strip()
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    
                    st.rerun()
            else:
                st.error("❌ AI system is offline. Please try again later.")
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': "I apologize, but I'm currently offline. Please try again in a moment."
                })
                st.rerun()
    
    # ==================== FOOTER ====================
    st.markdown("---")
    st.markdown("""
    <div class='app-footer'>
        <h3>🏥 Health Compass</h3>
        <p style='font-size: 1.1rem; font-weight: 600; color: #0891b2;'>Your AI-Powered Medical Companion</p>
        <p style='margin-top: 1rem;'>📚 Educational Information Only • Not Medical Advice</p>
        <p style='color: #94a3b8; font-size: 0.9rem; margin-top: 1.5rem;'>
            INFO 7390 Advanced Data Science & Architecture<br>
            Final Project by <strong>Manish Kumar</strong><br>
            Northeastern University • Khoury College of Computer Sciences
        </p>
    </div>
    """, unsafe_allow_html=True)