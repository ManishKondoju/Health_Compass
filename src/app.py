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

# Page config
st.set_page_config(
    page_title="Health Compass | AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Replace the st.markdown CSS section (lines 29-244) with this:

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
    
    /* Fix all text contrast issues */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #1E293B !important;
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
        letter-spacing: -0.5px;
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
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .card:hover {
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        transform: translateY(-4px);
    }
    
    .card h3 {
        color: #1E293B !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .card h4 {
        color: #334155 !important;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
    }
    
    /* Markdown headings - CRITICAL FIX */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    
    .main h3 {
        font-size: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Labels and captions - CRITICAL FIX */
    .stTextArea label, .stTextInput label, .stSelectbox label, 
    .stFileUploader label, .stRadio label, .stSlider label {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stMarkdown p, .stMarkdown div {
        color: #334155 !important;
    }
    
    [data-testid="stMarkdownContainer"] p {
        color: #475569 !important;
        font-size: 0.95rem;
    }
    
    /* Caption text */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #64748B !important;
        font-size: 0.875rem !important;
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
        transition: all 0.3s ease;
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
        font-size: 0.95rem !important;
        padding: 0.75rem 1.8rem;
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #F1F5F9;
        color: #3B82F6 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
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
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.1);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    [data-testid="stSidebar"] .stCaption {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        color: #1E293B !important;
        background: white;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
    }
    
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: #94A3B8 !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stChatMessage p {
        color: #334155 !important;
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
    
    /* Info/Warning/Success/Error boxes */
    .stAlert {
        border-radius: 12px;
        padding: 1rem 1.5rem;
    }
    
    .stAlert p, .stAlert div {
        color: #1E293B !important;
        font-weight: 500 !important;
    }
    
    /* Warning box specific */
    [data-baseweb="notification"][kind="warning"] {
        background: #FEF3C7 !important;
        border-left: 4px solid #F59E0B !important;
    }
    
    [data-baseweb="notification"][kind="warning"] p {
        color: #92400E !important;
        font-weight: 600 !important;
    }
    
    /* Info box */
    [data-baseweb="notification"][kind="info"] {
        background: #DBEAFE !important;
        border-left: 4px solid #3B82F6 !important;
    }
    
    [data-baseweb="notification"][kind="info"] p {
        color: #1E3A8A !important;
        font-weight: 500 !important;
    }
    
    /* Success box */
    [data-baseweb="notification"][kind="success"] {
        background: #D1FAE5 !important;
        border-left: 4px solid #10B981 !important;
    }
    
    [data-baseweb="notification"][kind="success"] p {
        color: #065F46 !important;
        font-weight: 600 !important;
    }
    
    /* Error box */
    [data-baseweb="notification"][kind="error"] {
        background: #FEE2E2 !important;
        border-left: 4px solid #EF4444 !important;
    }
    
    [data-baseweb="notification"][kind="error"] p {
        color: #991B1B !important;
        font-weight: 600 !important;
    }
    
    /* Clean up */
    #MainMenu, footer {visibility: hidden;}
    
    /* Emergency */
    .emergency-box {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        border: 3px solid #EF4444;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .emergency-box h2 {
        color: #DC2626 !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
    }
    
    .emergency-box h3 {
        color: #DC2626 !important;
    }
    
    .emergency-box p {
        color: #4A5568 !important;
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
    
    .source-card:hover {
        box-shadow: 0 8px 16px rgba(14, 165, 233, 0.2);
    }
    
    .source-card strong {
        color: #0C4A6E !important;
    }
    
    .source-card a {
        color: #0EA5E9 !important;
        font-weight: 600 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* Radio buttons */
    .stRadio label {
        color: #334155 !important;
    }
    
    /* Slider */
    .stSlider label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* Form */
    [data-testid="stForm"] {
        background: transparent;
        border: none;
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
    
    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
    }
    
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state
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

# Language translations (simple implementation)
translations = {
    'English': {
        'header': 'Health Compass',
        'tagline': 'AI-Powered Medical Assistant',
        'search_placeholder': 'Ask any health question...',
        'search_btn': 'Search',
        'emergency': 'Emergency',
        'call_911': 'Call 911'
    },
    'Spanish': {
        'header': 'Brújula de Salud',
        'tagline': 'Asistente Médico con IA',
        'search_placeholder': 'Haga cualquier pregunta de salud...',
        'search_btn': 'Buscar',
        'emergency': 'Emergencia',
        'call_911': 'Llamar al 911'
    },
    'Chinese': {
        'header': '健康指南针',
        'tagline': 'AI医疗助手',
        'search_placeholder': '提出任何健康问题...',
        'search_btn': '搜索',
        'emergency': '紧急情况',
        'call_911': '拨打911'
    },
    'French': {
        'header': 'Boussole Santé',
        'tagline': 'Assistant Médical IA',
        'search_placeholder': 'Posez une question santé...',
        'search_btn': 'Rechercher',
        'emergency': 'Urgence',
        'call_911': 'Appeler le 911'
    }
}

t = translations[st.session_state.language]

# Header
st.markdown(f"""
<div class='app-header'>
    <h1>🏥 {t['header']}</h1>
    <p>{t['tagline']}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
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
    
    st.markdown("---")
    
    # Quick medication tracker in sidebar
    assistant = HealthcareAssistant()
    meds = assistant.get_tracked_medications()
    
    if meds:
        st.markdown("## 💊 Tracked Meds")
        for med in meds[-3:]:
            st.caption(f"• {med['name']}")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Q&A Search",
    "📄 Document Analyzer",
    "📊 Symptom Tracker",
    "💬 AI Assistant"
])

# ==================== TAB 1: Q&A SEARCH ====================
with tab1:
    st.markdown("### 🔍 Medical Information Search")
    st.caption("Ask questions and get evidence-based answers from trusted medical sources")
    
    st.warning("⚠️ Educational purposes only. Not medical advice. Call 911 for emergencies.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        query = st.text_area(
            "Ask your health question:",
            height=120,
            placeholder=t['search_placeholder'],
            key="search_query"
        )
        
        col_b1, col_b2 = st.columns([2, 1])
        
        with col_b1:
            search_btn = st.button(f"🔍 {t['search_btn']}", use_container_width=True, type="primary")
        
        with col_b2:
            if st.button("Clear", use_container_width=True):
                st.session_state.search_query = ''
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💡 Tips")
        st.info("""
**Ask about:**
• Symptoms
• Conditions  
• Treatments
• Prevention
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if search_btn and query:
        rag = load_rag()
        
        if rag:
            # Translate query if not English
            if st.session_state.language != 'English':
                with st.spinner("Translating..."):
                    translate_prompt = f"Translate this to English: {query}"
                    query_en = rag.llm.generate([{"role": "user", "content": translate_prompt}], max_tokens=200)
                    st.caption(f"🌍 Translated: {query_en}")
            else:
                query_en = query
            
            with st.spinner("Searching..."):
                result = rag.query(query_en, n_results=5)
            
            # Check emergency
            if result['is_emergency']:
                st.markdown(f"""
                <div class='emergency-box'>
                    <h2>🚨 MEDICAL EMERGENCY</h2>
                    <h3 style="color: #DC2626;">{t['call_911'].upper()}</h3>
                    <p style="color: #4A5568;">Do not delay. Seek emergency care immediately.</p>
                </div>
                """, unsafe_allow_html=True)
                st.stop()
            
            # Display answer
            st.markdown("---")
            
            answer_text = result['answer']
            
            # Translate answer if needed
            if st.session_state.language != 'English':
                with st.spinner("Translating answer..."):
                    translate_answer_prompt = f"Translate this medical information to {st.session_state.language}. Keep it clear and accurate:\n\n{answer_text}"
                    answer_text = rag.llm.generate([{"role": "user", "content": translate_answer_prompt}], max_tokens=2000)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📋 Answer")
            st.write(answer_text)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sources
            if result['sources']:
                st.markdown("### 📚 Sources")
                
                for i, source in enumerate(result['sources'], 1):
                    st.markdown(f"""
                    <div class='source-card'>
                        <strong>{i}. {source.get('source', 'Unknown')}</strong> ✓<br>
                        {source.get('title', 'Untitled')}<br>
                        <a href="{source.get('url', '#')}" target="_blank">View source →</a>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Download
            st.download_button(
                "📥 Download Answer",
                f"{query}\n\n{answer_text}",
                f"answer_{datetime.now().strftime('%Y%m%d')}.txt",
                use_container_width=True
            )

# ==================== TAB 2: DOCUMENT ANALYZER ====================
with tab2:
    st.markdown("### 📄 Medical Document Analyzer")
    st.caption("Upload lab results, prescriptions, or discharge papers - AI explains in plain language")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Upload Your Medical Document")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
        help="Upload lab results, prescriptions, discharge summaries, etc."
    )
    
    if uploaded_file:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Display file
        if uploaded_file.type.startswith('image'):
            image = Image.open(uploaded_file)
            st.image(image, caption="Your document", width=600)
        
        st.markdown("---")
        
        # Analysis options
        analysis_type = st.radio("What would you like to know?", [
            "📋 Explain everything in simple terms",
            "🔬 Highlight abnormal values",
            "❓ Generate questions for my doctor",
            "📝 Summarize key findings",
            "💊 List medications mentioned"
        ])
        
        if st.button("🤖 Analyze Document", use_container_width=True, type="primary"):
            rag = load_rag()
            
            if rag:
                with st.spinner("🤖 AI is analyzing your document..."):
                    
                    # Read file content
                    if uploaded_file.type == 'text/plain':
                        content = uploaded_file.read().decode('utf-8')
                    elif uploaded_file.type == 'application/pdf':
                        # For PDF, would use PyPDF2 or similar
                        st.info("📄 For this educational version, please copy text from PDF and paste below")
                        content = st.text_area("Paste PDF text here:", height=200)
                    elif uploaded_file.type.startswith('image'):
                        # For images, would use OCR (pytesseract)
                        st.info("📷 For this educational version, please type the text from the image below")
                        content = st.text_area("Type text from image:", height=200)
                    else:
                        content = ""
                    
                    if content:
                        # Create analysis prompt based on selection
                        if "Explain everything" in analysis_type:
                            prompt = f"""Analyze this medical document and explain in simple, plain language:

{content[:3000]}

Provide:
1. What type of document is this?
2. Key information explained simply
3. Important medical terms defined
4. What the numbers/results mean
5. Any concerning findings to discuss with doctor

Use simple language a non-medical person can understand."""

                        elif "abnormal values" in analysis_type:
                            prompt = f"""Analyze this medical document and identify abnormal values:

{content[:3000]}

For each test/value:
1. Name of test
2. Your value
3. Normal range
4. Is it abnormal? (High/Low/Normal)
5. What it might mean (educational, not diagnosis)

Highlight anything that needs doctor's attention."""

                        elif "questions for doctor" in analysis_type:
                            prompt = f"""Based on this medical document:

{content[:3000]}

Generate 10 specific questions the patient should ask their doctor about these results.
Make them practical and focused on understanding the results and next steps."""

                        elif "Summarize" in analysis_type:
                            prompt = f"""Summarize this medical document in simple terms:

{content[:3000]}

Provide:
1. Document type
2. Main findings (3-5 key points)
3. Bottom line: What does this mean?
4. Recommended next steps

Keep it brief and clear."""

                        else:  # List medications
                            prompt = f"""List all medications mentioned in this document:

{content[:3000]}

For each medication:
1. Name
2. Dosage
3. Frequency/instructions
4. What it's used for (brief)

Format as a clear list."""

                        # Get AI analysis
                        analysis = rag.llm.generate([
                            {"role": "system", "content": "You are a medical education assistant helping patients understand medical documents."},
                            {"role": "user", "content": prompt}
                        ], temperature=0.2, max_tokens=2000)
                        
                        # Translate if needed
                        if st.session_state.language != 'English':
                            translate_prompt = f"Translate to {st.session_state.language}:\n\n{analysis}"
                            analysis = rag.llm.generate([{"role": "user", "content": translate_prompt}], max_tokens=2500)
                        
                        st.markdown("---")
                        st.markdown("### 🤖 AI Analysis")
                        st.write(analysis)
                        
                        st.caption("⚠️ This is educational analysis. Always discuss results with your healthcare provider.")
                        
                        # Download analysis
                        st.markdown("---")
                        
                        download_content = f"""MEDICAL DOCUMENT ANALYSIS
{'='*70}

Document: {uploaded_file.name}
Analyzed: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
Analysis Type: {analysis_type}

{'='*70}

AI ANALYSIS:

{analysis}

{'='*70}

ORIGINAL CONTENT:

{content[:2000]}

{'='*70}
Generated by Health Compass Document Analyzer
For educational purposes - Discuss with healthcare provider
{'='*70}
"""
                        
                        st.download_button(
                            "📥 Download Complete Analysis",
                            download_content,
                            f"analysis_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d')}.txt",
                            use_container_width=True
                        )
                    else:
                        st.warning("Please provide document text for analysis")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: SYMPTOM TRACKER ====================
with tab3:
    st.markdown("### 📊 Symptom Tracker with AI Insights")
    st.caption("Log symptoms and let AI discover patterns you might miss")
    
    tracker = SymptomTracker()
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📝 Log Symptom")
        
        with st.form("symptom_form", clear_on_submit=True):
            symptom_desc = st.text_input("What are you experiencing?",
                                        placeholder="e.g., Headache, Stomach pain, Fatigue")
            
            severity = st.slider("How severe? (1=Mild, 10=Severe)", 1, 10, 5)
            
            notes = st.text_area("Additional details (optional)", height=80,
                                placeholder="What were you doing? What makes it better/worse?")
            
            if st.form_submit_button("💾 Log Symptom", use_container_width=True):
                if symptom_desc:
                    tracker.log_symptom(symptom_desc, severity, notes)
                    st.success("✅ Symptom logged!")
                    st.rerun()
                else:
                    st.error("Please describe your symptom")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📈 Quick Stats")
        
        insights = tracker.get_ai_insights()
        
        if insights:
            st.metric("Entries", insights['total_entries'])
            st.metric("Avg Severity", f"{insights['average_severity']}/10")
            st.metric("Trend", insights['trend'].capitalize())
        else:
            st.info("Log 3+ symptoms to see stats")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Insights (3+ entries)
    if insights:
        st.markdown("---")
        st.markdown("## 🤖 AI Pattern Analysis")
        
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 📅 When do they occur?")
            
            day_df = pd.DataFrame(list(insights['day_pattern'].items()), columns=['Day', 'Count'])
            
            fig = px.bar(day_df, x='Day', y='Count', title="By Day of Week",
                        color='Count', color_continuous_scale='Blues')
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"💡 Most symptoms on **{insights['most_common_day']}s**")
            
            if insights['weekday_vs_weekend']['pattern'] == 'weekday-dominant':
                st.warning("⚠️ **Pattern:** Symptoms mostly on weekdays - could be stress-related")
            elif insights['weekday_vs_weekend']['pattern'] == 'weekend-dominant':
                st.info("💡 **Pattern:** Symptoms mostly on weekends")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_i2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 🕐 What time of day?")
            
            time_df = pd.DataFrame(list(insights['time_pattern'].items()), columns=['Period', 'Count'])
            
            fig = px.pie(time_df, values='Count', names='Period', title="By Time of Day")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"💡 Most symptoms in the **{insights['most_common_time']}**")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Get AI interpretation
        st.markdown("---")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🤖 AI Interpretation of Your Patterns")
        
        if st.button("Generate AI Insights", use_container_width=True):
            rag = load_rag()
            
            if rag:
                with st.spinner("AI is analyzing your symptom patterns..."):
                    
                    insight_data = tracker.generate_insight_text()
                    
                    prompt = f"""As a medical education assistant, analyze these symptom tracking patterns:

{insight_data}

Provide helpful insights:
1. What patterns are notable? (timing, frequency, trends)
2. Possible correlations or triggers to consider
3. What should the patient monitor or track additionally?
4. Should they see a doctor? When and why?
5. Questions to ask their doctor about these patterns

Be specific and actionable. Remind this is educational, not diagnosis."""
                    
                    ai_insights = rag.llm.generate([
                        {"role": "system", "content": "You are a medical education assistant."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.3, max_tokens=1500)
                    
                    # Translate if needed
                    if st.session_state.language != 'English':
                        translate_prompt = f"Translate to {st.session_state.language}:\n\n{ai_insights}"
                        ai_insights = rag.llm.generate([{"role": "user", "content": translate_prompt}], max_tokens=2000)
                    
                    st.write(ai_insights)
                    
                    st.caption("💡 Share these insights with your doctor at your next visit")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # View entries
    entries = tracker.get_all_symptoms()
    
    if entries:
        st.markdown("---")
        st.markdown("### 📜 Your Symptom History")
        
        for entry in reversed(entries[-10:]):
            with st.expander(f"📅 {entry['date_display']} • {entry['symptom']} ({entry['severity']}/10)"):
                st.write(f"**Severity:** {entry['severity']}/10")
                st.write(f"**Day:** {entry['day_of_week']} • **Time:** {entry['time_of_day']}")
                if entry.get('notes'):
                    st.write(f"**Notes:** {entry['notes']}")
                
                if st.button("Delete", key=f"del_{entry['id']}", use_container_width=True):
                    tracker.delete_entry(entry['id'])
                    st.success("Deleted")
                    st.rerun()
        
        st.markdown("---")
        
        # Export
        export_text = f"""SYMPTOM TRACKER LOG
{'='*70}

Total Entries: {len(entries)}
Period: {entries[0]['date_display']} to {entries[-1]['date_display']}

SYMPTOM LOG:

"""
        for entry in entries:
            export_text += f"""
Date: {entry['date_display']} ({entry['day_of_week']}, {entry['time_of_day']})
Symptom: {entry['symptom']}
Severity: {entry['severity']}/10
Notes: {entry.get('notes', 'None')}
{'─'*70}
"""
        
        if insights:
            export_text += f"""

PATTERN ANALYSIS:
Most common: {insights['most_common_symptom']}
Average severity: {insights['average_severity']}/10
Trend: {insights['trend']}
Most common day: {insights['most_common_day']}
Most common time: {insights['most_common_time']}

{'='*70}
Generated by Health Compass Symptom Tracker
"""
        
        st.download_button(
            "📥 Export Symptom Log",
            export_text,
            f"symptoms_{datetime.now().strftime('%Y%m%d')}.txt",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 4: AI ASSISTANT CHATBOT ====================
with tab4:
    st.markdown("### 💬 Healthcare Assistant")
    st.caption("Chat with your AI medical assistant - Ask questions, track medications, find hospitals")
    
    assistant = HealthcareAssistant()
    
    # Initialize chat if empty
    if not st.session_state.chat_history:
        st.session_state.chat_history = assistant.get_conversation_history()
        
        if not st.session_state.chat_history:
            # Welcome message
            welcome = {
                'role': 'assistant',
                'content': f"""Hello! I'm your AI Healthcare Assistant. I can help you with:

• **Medical questions** - Ask anything about health conditions, symptoms, treatments
• **Medication tracking** - Tell me what medications you're taking
• **Hospital finder** - Ask "What hospitals are near me?" (provide your location)
• **Health guidance** - Get educational information and advice

How can I help you today?""",
                'timestamp': datetime.now().isoformat()
            }
            
            assistant.add_message('assistant', welcome['content'])
            st.session_state.chat_history = [welcome]
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'assistant':
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message['content'])
                if message.get('display_time'):
                    st.caption(message['display_time'])
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(message['content'])
                if message.get('display_time'):
                    st.caption(message['display_time'])
    
    # Chat input
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        # Add user message
        assistant.add_message('user', user_input)
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'display_time': datetime.now().strftime("%I:%M %p")
        })
        
        # Get RAG system
        rag = load_rag()
        
        if rag:
            with st.spinner("🤖 Assistant is thinking..."):
                
                # Check for special commands
                user_lower = user_input.lower()
                
                # Hospital finder
                if any(keyword in user_lower for keyword in ['hospital', 'clinic', 'doctor near', 'where can i']):
                    # Extract location if provided
                    profile = assistant.get_user_profile()
                    location = profile.get('location', 'your area')
                    
                    # Check if location in message
                    if 'in ' in user_lower or 'near ' in user_lower:
                        # Try to extract location
                        words = user_input.split()
                        for i, word in enumerate(words):
                            if word.lower() in ['in', 'near'] and i + 1 < len(words):
                                location = ' '.join(words[i+1:])
                                assistant.update_user_profile(location=location)
                                break
                    
                    hospitals = assistant.get_hospital_suggestions(location)
                    
                    response = f"""I can help you find medical care near {location}. Here are some options:

"""
                    for i, hosp in enumerate(hospitals, 1):
                        if hosp.get('name'):
                            response += f"""
**{i}. {hosp['name']}**
"""
                            if hosp.get('specialty'):
                                response += f"Specialties: {hosp['specialty']}\n"
                            if hosp.get('address'):
                                response += f"📍 {hosp['address']}\n"
                            if hosp.get('phone'):
                                response += f"📞 {hosp['phone']}\n"
                            if hosp.get('rating'):
                                response += f"⭐ Rating: {hosp['rating']}\n"
                            response += "\n"
                    
                    response += "\n💡 Would you like more information about any of these facilities?"
                
                # Medication tracking
                elif any(keyword in user_lower for keyword in ['medication', 'medicine', 'pill', 'drug', 'taking', 'prescribed']):
                    # Check tracked medications
                    tracked_meds = assistant.get_tracked_medications()
                    
                    # Get AI response about medications
                    context = assistant.get_conversation_context()
                    
                    prompt = f"""{context}

Patient just said: {user_input}

Respond helpfully about their medications:
1. If they mentioned a medication, provide information about it (uses, dosage, side effects)
2. If asking about interactions, explain potential concerns
3. If asking when to take it, provide guidance
4. Remind to follow doctor's instructions

If they mentioned medication names, I'll track those for them.

Be helpful and informative."""
                    
                    response = rag.llm.generate([
                        {"role": "system", "content": "You are a helpful medical education assistant."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.3, max_tokens=1000)
                    
                    if tracked_meds:
                        response += f"\n\n💊 **I'm tracking these medications for you:** {', '.join([m['name'] for m in tracked_meds])}"
                
                # General health question
                else:
                    # Use RAG for medical information
                    rag_result = rag.query(user_input, n_results=3)
                    
                    # Build context-aware response
                    context = assistant.get_conversation_context(last_n=4)
                    
                    prompt = f"""{context}

Patient asks: {user_input}

Medical information from trusted sources:
{rag_result['answer']}

Respond conversationally and helpfully:
1. Answer their question using the medical information
2. Reference conversation context if relevant
3. Ask if they need more details
4. Suggest related topics if helpful

Keep it conversational and supportive."""
                    
                    response = rag.llm.generate([
                        {"role": "system", "content": "You are a friendly healthcare education assistant in an ongoing conversation."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.4, max_tokens=1200)
                
                # Translate if needed
                if st.session_state.language != 'English':
                    translate_prompt = f"Translate to {st.session_state.language}:\n\n{response}"
                    response = rag.llm.generate([{"role": "user", "content": translate_prompt}], max_tokens=1500)
                
                # Add assistant response
                assistant.add_message('assistant', response)
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'display_time': datetime.now().strftime("%I:%M %p")
                })
                
                st.rerun()
    
    # Sidebar features for chat
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 💬 Chat Actions")
        
        tracked_meds = assistant.get_tracked_medications()
        
        if tracked_meds:
            st.success(f"💊 Tracking {len(tracked_meds)} medications")
            
            with st.expander("View tracked meds"):
                for med in tracked_meds:
                    st.write(f"• {med['name']}")
                    st.caption(f"Added: {med['display_time']}")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            assistant.clear_conversation()
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        
        # Download chat
        if st.session_state.chat_history:
            chat_export = f"""HEALTHCARE ASSISTANT CONVERSATION
{'='*70}

Date: {datetime.now().strftime("%B %d, %Y")}

CONVERSATION:

"""
            for msg in st.session_state.chat_history:
                role = "You" if msg['role'] == 'user' else "AI Assistant"
                chat_export += f"{role}: {msg['content']}\n\n"
            
            chat_export += "="*70 + "\nGenerated by Health Compass\n"
            
            st.download_button(
                "📥 Download Chat",
                chat_export,
                f"chat_{datetime.now().strftime('%Y%m%d')}.txt",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #64748B;'>
    <div style='font-size: 1.3rem; font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;'>
        🏥 Health Compass
    </div>
    <div style='font-size: 0.95rem;'>
        Educational Information Only • Not Medical Advice • Always Consult Healthcare Professionals
    </div>
    <div style='font-size: 0.85rem; margin-top: 1rem; color: #94A3B8;'>
        INFO 7390 Final Project | Manish K | Northeastern University
    </div>
</div>
""", unsafe_allow_html=True)