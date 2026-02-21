import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import os
import json
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.gemini_helper import GeminiHelper
from utils.mermaid_generator import (
    generate_curriculum_mermaid, 
    generate_learning_path_mermaid
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CurriculumForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: slideDown 0.5s ease-out;
    }
    
    /* Card styling */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        font-size: 2rem;
        margin: 0;
        font-weight: 700;
    }
    
    .metric-card p {
        margin: 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: white;
        padding: 0.5rem;
        border-radius: 50px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 50px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        font-weight: 600;
        border-left: 4px solid #667eea;
    }
    
    /* Animations */
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Success message styling */
    .element-container:has(.stAlert) {
        animation: slideDown 0.3s ease-out;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Divider styling */
    hr {
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        height: 2px;
        border: none;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'curriculum' not in st.session_state:
    st.session_state.curriculum = None
if 'gemini_helper' not in st.session_state:
    st.session_state.gemini_helper = None
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = datetime.now()
if 'daily_requests' not in st.session_state:
    st.session_state.daily_requests = 0
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = datetime.now().date()
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'favorite_topics' not in st.session_state:
    st.session_state.favorite_topics = []

# Free tier limits
FREE_TIER_LIMITS = {
    'requests_per_minute': 15,
    'requests_per_day': 1500,
    'tokens_per_minute': 1000000
}

# Sidebar
with st.sidebar:
    # Logo and branding
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='font-size: 2rem; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            ⚡ CurriculumForge
        </h1>
        <p style='color: #666; font-size: 0.9rem;'>AI-Powered Curriculum Design</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dark mode toggle (simulated)
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.divider()
    
    # API Key section with modern design
    st.markdown("### 🔑 API Connection")
    
    if not st.session_state.gemini_helper:
        api_key = st.text_input("Enter your Gemini API Key:", type="password", 
                                placeholder="Paste your API key here",
                                help="Get your free API key from Google AI Studio")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", use_container_width=True):
                if api_key:
                    with st.spinner("Connecting..."):
                        try:
                            st.session_state.gemini_helper = GeminiHelper(api_key)
                            st.session_state.api_key_valid = True
                            st.success("✅ Connected!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Connection failed")
                else:
                    st.warning("Please enter an API key")
        
        with col2:
            st.link_button("Get Free Key", "https://aistudio.google.com/app/apikey", 
                          use_container_width=True)
    else:
        st.success("✅ Connected to Gemini Free Tier")
        
        if st.button("Disconnect", use_container_width=True, type="secondary"):
            st.session_state.gemini_helper = None
            st.session_state.api_key_valid = False
            st.rerun()
    
    st.divider()
    
    # Usage monitor with modern design
    st.markdown("### 📊 Usage Monitor")
    
    # Reset daily counter if new day
    today = datetime.now().date()
    if st.session_state.last_reset_date != today:
        st.session_state.daily_requests = 0
        st.session_state.last_reset_date = today
    
    # Calculate rate limit status
    minutes_remaining = max(0, 60 - (datetime.now() - st.session_state.last_request_time).seconds)
    requests_this_minute = st.session_state.request_count
    
    # Modern metric cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
            <h3>{requests_this_minute}/{FREE_TIER_LIMITS['requests_per_minute']}</h3>
            <p>Requests/Minute</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);'>
            <h3>{st.session_state.daily_requests}/{FREE_TIER_LIMITS['requests_per_day']}</h3>
            <p>Requests/Day</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bars with animation
    minute_progress = min(requests_this_minute / FREE_TIER_LIMITS['requests_per_minute'], 1.0)
    st.progress(minute_progress, text="Minute Limit")
    
    day_progress = min(st.session_state.daily_requests / FREE_TIER_LIMITS['requests_per_day'], 1.0)
    st.progress(day_progress, text="Daily Limit")
    
    # Warning messages
    if minute_progress > 0.8:
        st.warning("⚠️ Approaching minute limit")
    if day_progress > 0.8:
        st.warning("⚠️ Approaching daily limit")
    
    st.divider()
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("📋 New Curriculum", use_container_width=True):
        st.session_state.curriculum = None
        st.rerun()
    
    if st.button("⭐ Save to Favorites", use_container_width=True):
        if st.session_state.curriculum:
            topic = st.session_state.curriculum['course_overview']['title']
            if topic not in st.session_state.favorite_topics:
                st.session_state.favorite_topics.append(topic)
                st.success(f"✅ '{topic}' saved to favorites!")
    
    # Favorite topics
    if st.session_state.favorite_topics:
        st.markdown("### ⭐ Favorites")
        for topic in st.session_state.favorite_topics[-5:]:  # Show last 5
            st.markdown(f"• {topic}")

# Main content
if not st.session_state.gemini_helper:
    # Welcome screen with modern design
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class='main-header'>
            <h1>⚡ CurriculumForge AI</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>Design professional curricula with Google's Gemini AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='custom-card fade-in'>
            <h2 style='color: #667eea;'>✨ Features</h2>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;'>
                <div>
                    <h4>🤖 AI-Powered</h4>
                    <p style='color: #666;'>Generate comprehensive curricula in seconds</p>
                </div>
                <div>
                    <h4>📊 Visual Diagrams</h4>
                    <p style='color: #666;'>See your curriculum structure visually</p>
                </div>
                <div>
                    <h4>📝 Quiz Generator</h4>
                    <p style='color: #666;'>Create quizzes for each topic</p>
                </div>
                <div>
                    <h4>📥 Export Options</h4>
                    <p style='color: #666;'>Save as JSON or Markdown</p>
                </div>
            </div>
        </div>
        
        <div class='custom-card fade-in' style='margin-top: 1rem;'>
            <h2 style='color: #667eea;'>🎯 How It Works</h2>
            <ol style='color: #666; line-height: 1.8;'>
                <li>Enter your free Gemini API key in the sidebar</li>
                <li>Fill in your course details</li>
                <li>Click Generate to create your curriculum</li>
                <li>View, edit, and export your curriculum</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='custom-card fade-in' style='text-align: center;'>
            <h2 style='color: #667eea;'>🚀 Get Started</h2>
            <div style='margin: 2rem 0;'>
                <span style='font-size: 4rem;'>🔑</span>
            </div>
            <p style='color: #666; margin-bottom: 2rem;'>
                Connect your free Gemini API key to start designing
            </p>
        </div>
        
        <div class='custom-card fade-in' style='margin-top: 1rem;'>
            <h2 style='color: #667eea;'>📈 Free Tier Benefits</h2>
            <ul style='color: #666; line-height: 1.8;'>
                <li>✅ 15 requests per minute</li>
                <li>✅ 1500 requests per day</li>
                <li>✅ 1M tokens per minute</li>
                <li>✅ No credit card required</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Testimonials
    st.markdown("""
    <div style='margin-top: 2rem;'>
        <h2 style='text-align: center; color: #667eea;'>❤️ Loved by Educators</h2>
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;'>
            <div class='custom-card'>
                <p style='font-style: italic;'>"Saved me hours of curriculum planning!"</p>
                <p style='color: #667eea; font-weight: 600;'>- Dr. Smith</p>
            </div>
            <div class='custom-card'>
                <p style='font-style: italic;'>"The visual diagrams are incredibly helpful"</p>
                <p style='color: #667eea; font-weight: 600;'>- Prof. Johnson</p>
            </div>
            <div class='custom-card'>
                <p style='font-style: italic;'>"Best free curriculum tool available"</p>
                <p style='color: #667eea; font-weight: 600;'>- Ms. Davis</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Navigation with modern styling
    selected = option_menu(
        menu_title=None,
        options=["Curriculum Designer", "Learning Path", "Quiz Generator", "Export", "Analytics"],
        icons=["pencil-square", "diagram-3", "question-circle", "download", "graph-up"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "white", "border-radius": "50px", "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"},
            "icon": {"color": "#667eea", "font-size": "1rem"},
            "nav-link": {"font-size": "0.9rem", "text-align": "center", "margin": "0px", "color": "#666"},
            "nav-link-selected": {"background-color": "#667eea", "color": "white"},
        }
    )
    
    if selected == "Curriculum Designer":
        st.markdown("""
        <div class='main-header fade-in'>
            <h1>📚 Curriculum Designer</h1>
            <p style='font-size: 1.1rem; opacity: 0.9;'>Create comprehensive curricula with AI assistance</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class='custom-card fade-in'>
                <h3 style='color: #667eea; margin-bottom: 1.5rem;'>📋 Course Details</h3>
            </div>
            """, unsafe_allow_html=True)
            
            topic = st.text_input("Course Topic", placeholder="e.g., Machine Learning Fundamentals")
            duration = st.slider("Duration (weeks)", min_value=4, max_value=16, value=8)
            level = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
            
            # Subject area selection
            subject = st.selectbox(
                "Subject Area",
                ["Computer Science", "Business", "Arts", "Science", "Engineering", "Humanities", "Other"]
            )
            
            learning_objectives = st.text_area(
                "Learning Objectives",
                placeholder="What should students learn? (keep it concise)",
                height=100
            )
            
            # Additional options
            with st.expander("⚙️ Advanced Options"):
                include_quizzes = st.checkbox("Include quiz questions", value=True)
                include_resources = st.checkbox("Include learning resources", value=True)
                diagram_style = st.selectbox("Diagram Style", ["Modern", "Classic", "Minimal"])
            
            if st.button("🚀 Generate Curriculum", type="primary", use_container_width=True):
                if topic and learning_objectives:
                    with st.spinner("✨ Generating your curriculum..."):
                        # Simulate loading with progress
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        curriculum = st.session_state.gemini_helper.generate_curriculum(
                            topic, duration, level, learning_objectives
                        )
                        if curriculum:
                            st.session_state.curriculum = curriculum
                            st.balloons()
                            st.success("✅ Curriculum generated successfully!")
        
        with col2:
            if st.session_state.curriculum:
                curriculum = st.session_state.curriculum
                
                st.markdown("""
                <div class='custom-card fade-in'>
                    <h3 style='color: #667eea; margin-bottom: 1rem;'>📊 Curriculum Overview</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Modern metric cards
                col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
                
                with col_metrics1:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>{len(curriculum['weekly_breakdown'])}</h3>
                        <p>Weeks</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_metrics2:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>{len(curriculum['learning_outcomes'])}</h3>
                        <p>Outcomes</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_metrics3:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>{len(curriculum.get('prerequisites', []))}</h3>
                        <p>Prerequisites</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_metrics4:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>{len(curriculum.get('resources', []))}</h3>
                        <p>Resources</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Course info
                st.markdown(f"""
                <div class='custom-card' style='margin-top: 1rem;'>
                    <h4>{curriculum['course_overview']['title']}</h4>
                    <p style='color: #666;'>{curriculum['course_overview']['description']}</p>
                    <p><strong>Level:</strong> {curriculum['course_overview']['level']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Display full curriculum
        if st.session_state.curriculum:
            st.divider()
            
            tab1, tab2, tab3 = st.tabs(["📋 Detailed Curriculum", "📊 Visual Diagrams", "📝 Learning Outcomes"])
            
            with tab1:
                curriculum = st.session_state.curriculum
                
                # Weekly breakdown with modern design
                st.markdown("<h3 style='color: #667eea;'>Weekly Breakdown</h3>", unsafe_allow_html=True)
                
                for week in curriculum['weekly_breakdown']:
                    with st.expander(f"📅 Week {week['week']}: {week['topic']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📚 Subtopics:**")
                            for subtopic in week['subtopics']:
                                st.markdown(f"• {subtopic}")
                        
                        with col2:
                            if 'activities' in week and week['activities']:
                                st.markdown("**🎯 Activities:**")
                                for activity in week['activities']:
                                    st.markdown(f"• {activity}")
                
                # Prerequisites
                if curriculum.get('prerequisites'):
                    st.markdown("<h3 style='color: #667eea; margin-top: 2rem;'>📋 Prerequisites</h3>", unsafe_allow_html=True)
                    for prereq in curriculum['prerequisites']:
                        st.markdown(f"• {prereq}")
            
            with tab2:
                st.markdown("<h3 style='color: #667eea;'>Curriculum Flow Diagram</h3>", unsafe_allow_html=True)
                
                diagram_type = st.radio(
                    "Select Diagram Type",
                    ["Curriculum Structure", "Learning Path"],
                    horizontal=True
                )
                
                if diagram_type == "Curriculum Structure":
                    mermaid_code = generate_curriculum_mermaid(st.session_state.curriculum)
                else:
                    mermaid_code = generate_learning_path_mermaid(st.session_state.curriculum)
                
                # Modern diagram container
                st.markdown(f"""
                <div class='custom-card' style='padding: 2rem;'>
                    <div class='mermaid'>
                        {mermaid_code}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with tab3:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h3 style='color: #667eea;'>🎯 Learning Outcomes</h3>", unsafe_allow_html=True)
                    for outcome in st.session_state.curriculum['learning_outcomes']:
                        st.markdown(f"""
                        <div class='custom-card' style='padding: 1rem; margin-bottom: 0.5rem;'>
                            ✅ {outcome}
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<h3 style='color: #667eea;'>📝 Assessment Methods</h3>", unsafe_allow_html=True)
                    for assessment in st.session_state.curriculum['assessment_methods']:
                        st.markdown(f"""
                        <div class='custom-card' style='padding: 1rem; margin-bottom: 0.5rem;'>
                            📌 {assessment}
                        </div>
                        """, unsafe_allow_html=True)
    
    elif selected == "Quiz Generator":
        st.markdown("""
        <div class='main-header fade-in'>
            <h1>📝 Quiz Generator</h1>
            <p style='font-size: 1.1rem; opacity: 0.9;'>Create interactive quizzes for your curriculum</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.curriculum:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                <div class='custom-card'>
                    <h3 style='color: #667eea;'>⚙️ Quiz Settings</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Select week/topic
                week_options = [f"Week {w['week']}: {w['topic']}" for w in st.session_state.curriculum['weekly_breakdown']]
                selected_week = st.selectbox("Select Week", week_options)
                
                num_questions = st.slider("Number of Questions", min_value=1, max_value=3, value=2)
                difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
                
                if st.button("🎯 Generate Quiz", type="primary", use_container_width=True):
                    topic = selected_week.split(": ")[1]
                    with st.spinner("Generating quiz questions..."):
                        quiz = st.session_state.gemini_helper.generate_quiz_questions(topic, num_questions)
                        if quiz:
                            st.session_state.quiz = quiz
                            st.success("✅ Quiz generated!")
            
            with col2:
                if 'quiz' in st.session_state and st.session_state.quiz:
                    st.markdown("""
                    <div class='custom-card'>
                        <h3 style='color: #667eea;'>📋 Quiz Questions</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, q in enumerate(st.session_state.quiz['questions']):
                        st.markdown(f"""
                        <div class='custom-card' style='margin-top: 1rem;'>
                            <h4>Question {i+1}</h4>
                            <p style='font-size: 1.1rem;'>{q['question']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display options
                        user_answer = st.radio(
                            "Select answer:",
                            q['options'],
                            key=f"q_{i}",
                            index=None,
                            horizontal=True
                        )
                        
                        if user_answer:
                            if user_answer == q['correct_answer']:
                                st.success("✅ Correct!")
                            else:
                                st.error(f"❌ Incorrect. Correct answer: {q['correct_answer']}")
                                if 'explanation' in q:
                                    st.info(f"💡 {q['explanation']}")
                        
                        st.divider()
        else:
            st.warning("⚠️ Please generate a curriculum first in the Curriculum Designer tab")
    
    elif selected == "Export":
        st.markdown("""
        <div class='main-header fade-in'>
            <h1>📥 Export Curriculum</h1>
            <p style='font-size: 1.1rem; opacity: 0.9;'>Save and share your curriculum</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.curriculum:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class='custom-card'>
                    <h3 style='color: #667eea;'>📤 Export Options</h3>
                </div>
                """, unsafe_allow_html=True)
                
                export_format = st.selectbox(
                    "Select Format",
                    ["JSON", "Markdown", "HTML", "PDF (Preview)"]
                )
                
                if export_format == "JSON":
                    curriculum_json = json.dumps(st.session_state.curriculum, indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=curriculum_json,
                        file_name="curriculum.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                elif export_format == "Markdown":
                    # Generate markdown
                    md_content = f"# {st.session_state.curriculum['course_overview']['title']}\n\n"
                    md_content += f"**Duration:** {st.session_state.curriculum['course_overview']['duration']}\n"
                    md_content += f"**Level:** {st.session_state.curriculum['course_overview']['level']}\n\n"
                    md_content += "## Course Description\n"
                    md_content += f"{st.session_state.curriculum['course_overview']['description']}\n\n"
                    
                    md_content += "## Weekly Breakdown\n"
                    for week in st.session_state.curriculum['weekly_breakdown']:
                        md_content += f"### Week {week['week']}: {week['topic']}\n"
                        md_content += "**Subtopics:**\n"
                        for subtopic in week['subtopics']:
                            md_content += f"- {subtopic}\n"
                        md_content += "\n"
                    
                    st.download_button(
                        label="📥 Download Markdown",
                        data=md_content,
                        file_name="curriculum.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                elif export_format == "HTML":
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>{st.session_state.curriculum['course_overview']['title']}</title>
                        <style>
                            body {{ font-family: 'Inter', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                            h1 {{ color: #667eea; }}
                            .week {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 10px; }}
                        </style>
                    </head>
                    <body>
                        <h1>{st.session_state.curriculum['course_overview']['title']}</h1>
                        <p>{st.session_state.curriculum['course_overview']['description']}</p>
                        <h2>Weekly Breakdown</h2>
                    """
                    
                    for week in st.session_state.curriculum['weekly_breakdown']:
                        html_content += f"""
                        <div class='week'>
                            <h3>Week {week['week']}: {week['topic']}</h3>
                            <ul>
                                {''.join([f'<li>{subtopic}</li>' for subtopic in week['subtopics']])}
                            </ul>
                        </div>
                        """
                    
                    html_content += "</body></html>"
                    
                    st.download_button(
                        label="📥 Download HTML",
                        data=html_content,
                        file_name="curriculum.html",
                        mime="text/html",
                        use_container_width=True
                    )
            
            with col2:
                st.markdown("""
                <div class='custom-card'>
                    <h3 style='color: #667eea;'>📋 Export Preview</h3>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Preview JSON"):
                    st.json(st.session_state.curriculum)
                
                st.markdown("""
                <div class='custom-card' style='margin-top: 1rem;'>
                    <h4>Share Options</h4>
                    <p>Copy the link below to share:</p>
                    <code>https://curriculumforge.ai/share/abc123</code>
                    <div style='margin-top: 1rem;'>
                        <button style='background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px;'>📋 Copy Link</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No curriculum to export. Generate one first!")
    
    elif selected == "Analytics":
        st.markdown("""
        <div class='main-header fade-in'>
            <h1>📊 Analytics Dashboard</h1>
            <p style='font-size: 1.1rem; opacity: 0.9;'>Track your curriculum metrics</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.curriculum:
            curriculum = st.session_state.curriculum
            
            # Create sample analytics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class='metric-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
                    <h3>{}</h3>
                    <p>Total Weeks</p>
                </div>
                """.format(len(curriculum['weekly_breakdown'])), unsafe_allow_html=True)
            
            with col2:
                total_subtopics = sum(len(week['subtopics']) for week in curriculum['weekly_breakdown'])
                st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);'>
                    <h3>{total_subtopics}</h3>
                    <p>Total Subtopics</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_per_week = total_subtopics / len(curriculum['weekly_breakdown'])
                st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
                    <h3>{avg_per_week:.1f}</h3>
                    <p>Avg Subtopics/Week</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Create a bar chart of topics per week
            weeks = [f"Week {w['week']}" for w in curriculum['weekly_breakdown']]
            subtopics_count = [len(w['subtopics']) for w in curriculum['weekly_breakdown']]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=weeks,
                    y=subtopics_count,
                    marker_color='rgba(102, 126, 234, 0.7)',
                    marker_line_color='rgba(102, 126, 234, 1)',
                    marker_line_width=1.5
                )
            ])
            
            fig.update_layout(
                title="Subtopics per Week",
                xaxis_title="Week",
                yaxis_title="Number of Subtopics",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Learning progress visualization
            st.markdown("""
            <div class='custom-card'>
                <h3 style='color: #667eea;'>📈 Learning Progress Timeline</h3>
            </div>
            """, unsafe_allow_html=True)
            
            progress_data = pd.DataFrame({
                'Week': weeks,
                'Topics Covered': subtopics_count,
                'Cumulative Progress': [sum(subtopics_count[:i+1]) for i in range(len(subtopics_count))]
            })
            
            fig2 = px.line(
                progress_data,
                x='Week',
                y='Cumulative Progress',
                title="Cumulative Learning Progress",
                markers=True
            )
            
            fig2.update_traces(line_color='#667eea', marker_color='#764ba2')
            fig2.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=12)
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("📊 Generate a curriculum first to see analytics")

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;'>
    <p style='font-size: 1.1rem;'>Built with ❤️ using Streamlit and Google's Gemini AI</p>
    <p style='opacity: 0.8; font-size: 0.9rem;'>© 2026 CurriculumForge - Free AI Curriculum Designer</p>
</div>
""", unsafe_allow_html=True)

# Add Mermaid.js script
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        flowchart: {
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
        }
    });
</script>
""", unsafe_allow_html=True)