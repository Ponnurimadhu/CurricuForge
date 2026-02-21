import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure page with custom theme
st.set_page_config(
    page_title="AI Curriculum Designer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ULTRA-PREMIUM CSS DESIGN SYSTEM (keeping your existing CSS - it's the same)
st.markdown("""
<style>
    /* ===== PREMIUM FONTS & VARIABLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #4158D0;
        --primary-dark: #2c3e9e;
        --primary-light: #6b7fe0;
        --secondary: #C850C0;
        --tertiary: #FFCC70;
        --gradient-1: linear-gradient(135deg, #4158D0 0%, #C850C0 46%, #FFCC70 100%);
        --gradient-2: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-3: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-4: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        --gradient-5: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        --glass-bg: rgba(255, 255, 255, 0.25);
        --glass-border: rgba(255, 255, 255, 0.18);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --neumorph-shadow: 20px 20px 60px #d1d1d1, -20px -20px 60px #ffffff;
        --dark-bg: #1a1a2e;
        --dark-card: #16213e;
        --dark-text: #e0e0e0;
    }

    /* ===== GLOBAL STYLES ===== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ===== PREMIUM TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* ===== SIDEBAR STYLING ===== */
    .css-1d391kg, .css-1wrcr25 {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid var(--glass-border);
        box-shadow: 10px 0 30px -10px rgba(0,0,0,0.1);
    }

    .sidebar-content {
        padding: 2rem 1.5rem;
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(5px);
        border-radius: 20px;
        margin: 1rem;
    }

    /* ===== GLASSMORPHISM CARDS ===== */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        padding: 2rem;
        transition: all 0.3s ease;
        animation: floatIn 0.6s ease-out;
    }

    .glass-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 45px 0 rgba(31, 38, 135, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* ===== NEUMORPHISM CARDS ===== */
    .neumorph-card {
        background: #e0e0e0;
        border-radius: 50px;
        box-shadow: 20px 20px 60px #bebebe, -20px -20px 60px #ffffff;
        padding: 2rem;
        transition: all 0.3s ease;
    }

    .neumorph-card:hover {
        box-shadow: 10px 10px 30px #bebebe, -10px -10px 30px #ffffff;
    }

    /* ===== GRADIENT CARDS ===== */
    .gradient-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .gradient-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 70%
        );
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }

    /* ===== MAIN HEADER ===== */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 30px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        animation: gradientShift 10s ease infinite;
        background-size: 200% 200%;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .main-header h1 {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        animation: slideInDown 0.8s ease;
    }

    .main-header p {
        font-size: 1.3rem;
        opacity: 0.95;
        max-width: 600px;
        margin: 0 auto;
        animation: slideInUp 0.8s ease;
    }

    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        color: white;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }

    .metric-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .metric-card:hover::after {
        width: 300px;
        height: 300px;
    }

    .metric-card h3 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }

    .metric-card p {
        font-size: 1.1rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }

    /* ===== BUTTON STYLES ===== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
        z-index: -1;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    /* ===== INPUT FIELD STYLES ===== */
    .stTextInput > div > div > input {
        border-radius: 50px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.8rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: rgba(255,255,255,0.9) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-2px);
    }

    /* ===== SELECT BOX STYLES ===== */
    .stSelectbox > div > div {
        border-radius: 50px !important;
        border: 2px solid #e0e0e0 !important;
        transition: all 0.3s ease !important;
    }

    .stSelectbox > div > div:hover {
        border-color: #667eea !important;
        transform: translateY(-2px);
    }

    /* ===== ANIMATED INFO BOX ===== */
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        animation: pulseGlow 2s infinite;
        position: relative;
        overflow: hidden;
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(245, 87, 108, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(245, 87, 108, 0); }
        100% { box-shadow: 0 0 0 0 rgba(245, 87, 108, 0); }
    }

    /* ===== SUCCESS MESSAGE ===== */
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 15px;
        font-weight: 600;
        animation: slideInRight 0.5s ease;
        border-left: 5px solid #2ecc71;
    }

    /* ===== TAB STYLING ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(10px);
        padding: 0.5rem;
        border-radius: 60px;
        border: 1px solid rgba(255,255,255,0.18);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 60px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* ===== EXPANDER STYLING ===== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }

    /* ===== GENERATED CONTENT ANIMATION ===== */
    .generated-content {
        animation: fadeInScale 0.6s ease-out;
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }

    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.95) translateY(20px);
        }
        to {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }

    /* ===== LOADING SPINNER ===== */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent !important;
        border-width: 4px !important;
        animation: spin 1s linear infinite !important;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea) !important;
        background-size: 200% 100% !important;
        animation: progressShimmer 2s linear infinite !important;
        border-radius: 10px !important;
    }

    @keyframes progressShimmer {
        0% { background-position: 100% 0; }
        100% { background-position: -100% 0; }
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 30px 30px 0 0;
        margin-top: 3rem;
        position: relative;
        overflow: hidden;
    }

    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, white, transparent);
        animation: scan 2s linear infinite;
    }

    @keyframes scan {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* ===== CUSTOM SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    /* ===== PARTICLE BACKGROUND ===== */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        overflow: hidden;
    }

    .particle {
        position: absolute;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        opacity: 0.3;
        animation: float 20s infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-100px) rotate(180deg); }
    }

    /* ===== ENHANCED ANIMATIONS ===== */
    @keyframes slideInDown {
        from {
            transform: translateY(-100px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    @keyframes slideInUp {
        from {
            transform: translateY(100px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    @keyframes slideInRight {
        from {
            transform: translateX(100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideInLeft {
        from {
            transform: translateX(-100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    /* ===== RESPONSIVE DESIGN ===== */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .metric-card {
            margin-bottom: 1rem;
        }
        
        .glass-card, .neumorph-card, .gradient-card {
            padding: 1.5rem;
        }
    }

    /* ===== DARK MODE SUPPORT ===== */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: var(--dark-bg);
        }
        
        .glass-card {
            background: rgba(22, 33, 62, 0.7);
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .neumorph-card {
            background: var(--dark-card);
            box-shadow: 10px 10px 20px #0f0f1f, -10px -10px 20px #1d1d3d;
        }
    }

    /* ===== 3D TILT EFFECT ===== */
    .tilt-card {
        transform-style: preserve-3d;
        transform: perspective(1000px);
        transition: transform 0.1s ease;
    }

    .tilt-card:hover {
        transform: perspective(1000px) rotateX(5deg) rotateY(5deg);
    }

    /* ===== GLOWING BORDER ===== */
    .glow-border {
        position: relative;
        border-radius: 20px;
        overflow: hidden;
    }

    .glow-border::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #ff6b6b, #4ecdc4);
        border-radius: 22px;
        z-index: -1;
        animation: rotate 4s linear infinite;
    }

    @keyframes rotate {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }

    /* ===== TYPEWRITER EFFECT ===== */
    .typewriter {
        overflow: hidden;
        border-right: .15em solid #667eea;
        white-space: nowrap;
        margin: 0 auto;
        animation: 
            typing 3.5s steps(40, end),
            blink-caret .75s step-end infinite;
    }

    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }

    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: #667eea }
    }

    /* ===== CONFETTI ANIMATION ===== */
    .confetti {
        position: absolute;
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        opacity: 0;
        animation: confettiFall 3s ease-in infinite;
    }

    @keyframes confettiFall {
        0% {
            transform: translateY(-100px) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }
</style>

<!-- Particle Background -->
<div class="particles">
    <div class="particle" style="width: 100px; height: 100px; top: 10%; left: 10%; animation-delay: 0s;"></div>
    <div class="particle" style="width: 150px; height: 150px; top: 50%; right: 10%; animation-delay: 2s;"></div>
    <div class="particle" style="width: 80px; height: 80px; bottom: 20%; left: 20%; animation-delay: 4s;"></div>
    <div class="particle" style="width: 200px; height: 200px; bottom: 10%; right: 30%; animation-delay: 6s;"></div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")
if 'client' not in st.session_state:
    st.session_state.client = None
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def initialize_openai():
    """Initialize OpenAI client"""
    try:
        if st.session_state.api_key:
            st.session_state.client = OpenAI(api_key=st.session_state.api_key)
            # Test the connection with a simple completion
            test_response = st.session_state.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
    except Exception as e:
        st.error(f"Error initializing OpenAI: {str(e)}")
        return False
    return False

def generate_openai_response(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """Generate response using OpenAI"""
    try:
        response = st.session_state.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert curriculum designer and educator. Create detailed, professional educational content."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content glass-card">
        <h2 style="color: #4158D0; text-align: center; margin-bottom: 2rem; font-size: 2rem;">
            🎓 Curriculum Designer
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key input with icon
    st.markdown("### 🔑 API Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state.api_key,
        type="password",
        help="Enter your OpenAI API key",
        placeholder="sk-..."
    )
    
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        st.session_state.client = None
    
    # Model selection
    st.markdown("### 🤖 Model Selection")
    model = st.selectbox(
        "Choose OpenAI Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        index=0,
        help="Select the OpenAI model to use"
    )
    
    # Temperature slider
    temperature = st.slider(
        "🌡️ Creativity Level",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more creative, lower values more focused"
    )
    
    # Initialize button with animation
    if st.button("🚀 Initialize OpenAI", type="primary", use_container_width=True):
        if initialize_openai():
            st.markdown("""
            <div class="success-message">
                ✅ OpenAI initialized successfully!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Failed to initialize OpenAI")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Go to",
        ["🏠 Home", "📝 Course Outline", "📅 Lesson Planner", "📊 Assessment"],
        index=0
    )
    
    st.markdown("---")
    
    # Theme selector
    st.markdown("### 🎨 Customization")
    theme = st.selectbox("Theme", ["Light", "Dark", "System"], index=0)
    
    st.markdown("---")
    
    # App info with styled card
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #4158D0; margin-bottom: 1rem;">📚 About</h3>
        <p style="color: #666;">This AI-powered curriculum designer helps educators create:</p>
        <ul style="color: #666; list-style-type: none; padding-left: 0;">
            <li style="margin: 0.5rem 0;">📝 <strong>Course outlines</strong></li>
            <li style="margin: 0.5rem 0;">📅 <strong>Lesson plans</strong></li>
            <li style="margin: 0.5rem 0;">📊 <strong>Assessments</strong></li>
            <li style="margin: 0.5rem 0;">🎯 <strong>Learning objectives</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎓 AI Curriculum Designer</h1>
    <p>Empowering educators with intelligent content creation</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.markdown("""
    <div class="info-box">
        <h3>👋 Welcome to AI Curriculum Designer!</h3>
        <p>Please enter your OpenAI API key in the sidebar to get started.</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">Don't have an API key? 
        <a href="https://platform.openai.com/api-keys" target="_blank" style="color: white; text-decoration: underline;">
        Get one from OpenAI</a></p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Welcome message and metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📝</h3>
            <h3>Course Outlines</h3>
            <p>Create comprehensive structures</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📅</h3>
            <h3>Lesson Plans</h3>
            <p>Design engaging lessons</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊</h3>
            <h3>Assessments</h3>
            <p>Generate quizzes & tests</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Welcome section with animation
    st.markdown("""
    <div class="generated-content">
        <h2 style="color: #4158D0; margin-bottom: 1rem;">✨ Welcome to the Future of Education</h2>
        <p style="color: #666; font-size: 1.1rem; line-height: 1.6;">
        Navigate through our intelligent tools to create professional educational content in minutes. 
        Each tool is powered by OpenAI to ensure high-quality, engaging, and effective learning materials.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #4158D0;">📝 Course Outline</h3>
            <p style="color: #666;">Create structured course outlines with learning objectives and modules</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="neumorph-card" style="text-align: center;">
            <h3 style="color: #4158D0;">📅 Lesson Planner</h3>
            <p style="color: #666;">Design detailed lesson plans with timing and activities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="gradient-card" style="text-align: center;">
            <h3 style="color: white;">📊 Assessment</h3>
            <p style="color: rgba(255,255,255,0.9);">Generate quizzes, tests, and assignments with rubrics</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide with styled expander
    with st.expander("📖 Quick Start Guide", expanded=False):
        st.markdown("""
        <div style="padding: 1rem;">
            <h4 style="color: #4158D0;">Follow these steps to create your first curriculum:</h4>
            <ol style="color: #666; font-size: 1.1rem; line-height: 2;">
                <li>🔑 <strong>Enter your API Key</strong> in the sidebar</li>
                <li>🚀 <strong>Initialize OpenAI</strong> by clicking the button</li>
                <li>📋 <strong>Navigate</strong> to the desired tool using the sidebar menu</li>
                <li>✏️ <strong>Fill in the parameters</strong> for your curriculum element</li>
                <li>⚡ <strong>Generate</strong> and refine your content</li>
            </ol>
            
            <h4 style="color: #4158D0; margin-top: 2rem;">💡 Pro Tips:</h4>
            <ul style="color: #666; font-size: 1.1rem; line-height: 2;">
                <li>🎯 Be specific about learning objectives for better results</li>
                <li>👥 Include target audience details to tailor the content</li>
                <li>⏱️ Specify duration and format requirements</li>
                <li>🔄 You can regenerate content with modified parameters</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent generations gallery
    if st.session_state.generated_content:
        st.markdown("### 📋 Recent Creations")
        recent_items = list(st.session_state.generated_content.items())[-3:]
        
        cols = st.columns(len(recent_items))
        for idx, (key, value) in enumerate(recent_items):
            with cols[idx]:
                st.markdown(f"""
                <div class="glass-card tilt-card">
                    <h4 style="color: #4158D0; margin-bottom: 0.5rem;">📄 {key}</h4>
                    <p style="color: #666; font-size: 0.9rem;">🕒 {value['timestamp']}</p>
                    <p style="color: #666; font-size: 0.9rem;">📝 {value['prompt']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"👁️ View", key=f"view_{idx}"):
                    st.session_state[f"view_{key}"] = value['content']

# Footer
st.markdown("""
<div class="footer">
    <p style="margin: 0; font-size: 1rem;">Powered by OpenAI | Built with Streamlit</p>
    <p style="margin: 0.5rem 0 0; font-size: 0.9rem; opacity: 0.9;">© 2024 AI Curriculum Designer</p>
</div>
""", unsafe_allow_html=True)

# Conditional content based on navigation
if page == "📝 Course Outline":
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h1>📝 Course Outline Generator</h1>
        <p>Create comprehensive course outlines</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('client'):
        st.warning("⚠️ Please initialize OpenAI in the sidebar first.")
    else:
        with st.form("course_outline_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Course Title*", placeholder="e.g., Introduction to Python")
                subject = st.text_input("Subject Area*", placeholder="e.g., Computer Science")
                
            with col2:
                audience = st.text_input("Target Audience*", placeholder="e.g., College students")
                level = st.selectbox("Course Level", ["Beginner", "Intermediate", "Advanced"])
            
            duration = st.slider("Course Duration (weeks)", 1, 52, 8)
            additional = st.text_area("Additional Requirements", placeholder="Any specific topics to include?")
            
            if st.form_submit_button("🚀 Generate Outline", type="primary", use_container_width=True):
                if all([title, subject, audience]):
                    with st.spinner("Creating outline..."):
                        prompt = f"Create a detailed {level} level course outline for {title} in {subject} for {audience} over {duration} weeks. Additional requirements: {additional}"
                        response = generate_openai_response(prompt, model=model, temperature=temperature)
                        
                        if response:
                            st.success("✅ Outline generated!")
                            # Save to session state
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.session_state.generated_content[f"Outline: {title}"] = {
                                'content': response,
                                'timestamp': timestamp,
                                'prompt': prompt[:50] + "..."
                            }
                            
                            st.markdown(f"""
                            <div class="generated-content">
                                <h2 style="color: #f093fb;">{title}</h2>
                                {response}
                            </div>
                            """, unsafe_allow_html=True)

elif page == "📅 Lesson Planner":
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);">
        <h1>📅 Lesson Planner</h1>
        <p>Design detailed lesson plans</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('client'):
        st.warning("⚠️ Please initialize OpenAI in the sidebar first.")
    else:
        with st.form("lesson_plan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                lesson_title = st.text_input("Lesson Title*", placeholder="e.g., Introduction to Variables")
                course = st.text_input("Course Name*", placeholder="e.g., Python Programming 101")
                
            with col2:
                duration = st.number_input("Duration (minutes)*", min_value=15, value=60, step=15)
                objectives = st.text_area("Learning Objectives*", placeholder="What should students learn?", height=100)
            
            materials = st.text_input("Materials Needed", placeholder="e.g., Textbook, worksheets")
            
            if st.form_submit_button("🚀 Generate Lesson Plan", type="primary", use_container_width=True):
                if all([lesson_title, course, objectives]):
                    with st.spinner("Creating lesson plan..."):
                        prompt = f"Create a detailed {duration} minute lesson plan for {lesson_title} in {course}. Learning objectives: {objectives}. Materials: {materials}"
                        response = generate_openai_response(prompt, model=model, temperature=temperature)
                        
                        if response:
                            st.success("✅ Lesson plan generated!")
                            # Save to session state
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.session_state.generated_content[f"Lesson: {lesson_title}"] = {
                                'content': response,
                                'timestamp': timestamp,
                                'prompt': prompt[:50] + "..."
                            }
                            
                            st.markdown(f"""
                            <div class="generated-content">
                                <h2 style="color: #84fab0;">{lesson_title}</h2>
                                {response}
                            </div>
                            """, unsafe_allow_html=True)

elif page == "📊 Assessment":
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h1>📊 Assessment Generator</h1>
        <p>Create quizzes, tests, and assignments</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('client'):
        st.warning("⚠️ Please initialize OpenAI in the sidebar first.")
    else:
        with st.form("assessment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                topic = st.text_input("Topic/Subject*", placeholder="e.g., Quadratic Equations")
                grade = st.text_input("Grade Level*", placeholder="e.g., 10th Grade")
                
            with col2:
                num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=10)
                difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
            
            assessment_type = st.selectbox("Assessment Type", ["Quiz", "Test", "Assignment", "Project"])
            objectives = st.text_area("Learning Objectives Tested*", placeholder="What should this assessment measure?")
            
            if st.form_submit_button("🚀 Generate Assessment", type="primary", use_container_width=True):
                if all([topic, grade, objectives]):
                    with st.spinner("Creating assessment..."):
                        prompt = f"Create a {difficulty} level {assessment_type} for {topic} for {grade} with {num_questions} questions. Learning objectives: {objectives}. Include a mix of question types and an answer key."
                        response = generate_openai_response(prompt, model=model, temperature=temperature)
                        
                        if response:
                            st.success("✅ Assessment generated!")
                            # Save to session state
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.session_state.generated_content[f"Assessment: {topic}"] = {
                                'content': response,
                                'timestamp': timestamp,
                                'prompt': prompt[:50] + "..."
                            }
                            
                            st.markdown(f"""
                            <div class="generated-content">
                                <h2 style="color: #667eea;">{topic} {assessment_type}</h2>
                                {response}
                            </div>
                            """, unsafe_allow_html=True)