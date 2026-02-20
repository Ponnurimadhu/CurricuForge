import streamlit as st
import pandas as pd
from utils.gemini_helper import GeminiHelper
from utils.prompts import CURRICULUM_TEMPLATES, LESSON_STRUCTURE
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Curriculum Designer",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-message {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'gemini_helper' not in st.session_state:
    try:
        st.session_state.gemini_helper = GeminiHelper()
    except ValueError as e:
        st.error(str(e))
        st.stop()

if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}

# Header
st.markdown("""
    <div class="main-header">
        <h1>📚 AI-Powered Curriculum Designer</h1>
        <p>Create comprehensive educational materials with Gemini AI</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/764ba2/ffffff?text=Curriculum+AI", use_column_width=True)
    st.markdown("### 🎯 Navigation")
    
    menu_options = [
        "📋 Curriculum Generator",
        "📝 Lesson Plan Creator",
        "📊 Assessment Builder",
        "📈 Learning Path Designer",
        "💡 Teaching Resources"
    ]
    
    selected_menu = st.radio("Select Tool", menu_options)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    # Model settings
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max Response Length", 500, 4000, 2000, 100)
    
    # About section
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("This AI-powered tool helps educators design comprehensive curricula, lesson plans, and assessments using Google's Gemini AI.")

# Main content area
if selected_menu == "📋 Curriculum Generator":
    st.header("📋 Generate Complete Curriculum")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("Subject/Course Name", "Introduction to Python Programming")
        level = st.selectbox("Education Level", [
            "Elementary School",
            "Middle School", 
            "High School",
            "Undergraduate",
            "Graduate",
            "Professional Development"
        ])
        duration = st.number_input("Course Duration (weeks)", 4, 52, 12)
        
    with col2:
        curriculum_type = st.selectbox("Curriculum Focus", list(CURRICULUM_TEMPLATES.keys()))
        learning_objectives = st.text_area(
            "Learning Objectives (comma-separated)",
            "Understand basic programming concepts, Write Python scripts, Build simple applications"
        )
    
    prerequisites = st.text_area("Prerequisites (optional)", "Basic computer literacy")
    
    if st.button("🚀 Generate Curriculum", type="primary"):
        with st.spinner("Generating curriculum with Gemini AI..."):
            # Combine inputs
            full_objectives = f"{learning_objectives}\n\nCurriculum Focus: {CURRICULUM_TEMPLATES[curriculum_type]}"
            
            curriculum = st.session_state.gemini_helper.generate_curriculum(
                subject, level, duration, full_objectives
            )
            
            st.session_state.generated_content['curriculum'] = curriculum
            
            # Display in tabs
            tab1, tab2, tab3 = st.tabs(["📖 Generated Curriculum", "📊 Course Stats", "💾 Export"])
            
            with tab1:
                st.markdown(curriculum)
                
            with tab2:
                # Create some sample statistics
                weeks = list(range(1, duration + 1))
                topics_per_week = [3, 4, 3, 4, 4, 3, 4, 3, 4, 3, 4, 3][:duration]
                
                fig = px.line(
                    x=weeks, 
                    y=topics_per_week,
                    labels={'x': 'Week', 'y': 'Number of Topics'},
                    title='Topics Distribution per Week'
                )
                st.plotly_chart(fig)
                
            with tab3:
                st.download_button(
                    "📥 Download Curriculum",
                    curriculum,
                    file_name=f"{subject.lower().replace(' ', '_')}_curriculum.txt",
                    mime="text/plain"
                )

elif selected_menu == "📝 Lesson Plan Creator":
    st.header("📝 Create Detailed Lesson Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input("Lesson Topic", "Variables and Data Types")
        duration = st.number_input("Lesson Duration (minutes)", 30, 180, 60, 15)
        
    with col2:
        objectives = st.text_area(
            "Learning Objectives",
            "Understand variable types, Perform basic operations, Create simple programs"
        )
        activities = st.text_area(
            "Planned Activities",
            "Code-along exercises, Pair programming, Mini-quiz"
        )
    
    if st.button("🎯 Generate Lesson Plan", type="primary"):
        with st.spinner("Creating your lesson plan..."):
            lesson_plan = st.session_state.gemini_helper.generate_lesson_plan(
                topic, duration, objectives, activities
            )
            
            st.session_state.generated_content['lesson_plan'] = lesson_plan
            
            st.markdown("### 📋 Your Lesson Plan")
            st.markdown(lesson_plan)
            
            st.download_button(
                "📥 Download Lesson Plan",
                lesson_plan,
                file_name=f"{topic.lower().replace(' ', '_')}_lesson_plan.txt"
            )

elif selected_menu == "📊 Assessment Builder":
    st.header("📊 Build Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input("Assessment Topic", "Python Functions")
        assessment_type = st.selectbox(
            "Assessment Type",
            ["Quiz", "Test", "Exam", "Project", "Presentation"]
        )
        
    with col2:
        difficulty = st.select_slider(
            "Difficulty Level",
            options=["Beginner", "Intermediate", "Advanced", "Expert"]
        )
        num_questions = st.number_input("Number of Questions", 5, 50, 10)
    
    if st.button("📝 Generate Assessment", type="primary"):
        with st.spinner("Creating assessment..."):
            assessment = st.session_state.gemini_helper.generate_assessment(
                topic, assessment_type, difficulty
            )
            
            st.session_state.generated_content['assessment'] = assessment
            
            st.markdown("### 📝 Your Assessment")
            st.markdown(assessment)
            
            st.download_button(
                "📥 Download Assessment",
                assessment,
                file_name=f"{topic.lower().replace(' ', '_')}_{assessment_type.lower()}.txt"
            )

elif selected_menu == "📈 Learning Path Designer":
    st.header("📈 Design Personalized Learning Path")
    
    st.markdown("""
    <div class="feature-card">
        <h4>Create customized learning journeys for individual students or groups</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        student_level = st.selectbox("Student Level", [
            "Beginner", "Intermediate", "Advanced"
        ])
        learning_style = st.multiselect(
            "Learning Style Preferences",
            ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"]
        )
        
    with col2:
        time_available = st.number_input("Hours per week", 1, 20, 5)
        focus_areas = st.text_area("Focus Areas", "Problem-solving, Project work, Theory")
    
    if st.button("🎯 Generate Learning Path"):
        prompt = f"""
        Create a personalized learning path for:
        Current Level: {student_level}
        Learning Styles: {', '.join(learning_style)}
        Time Available: {time_available} hours/week
        Focus Areas: {focus_areas}
        
        Include:
        1. Weekly milestones
        2. Recommended resources
        3. Practice activities
        4. Assessment checkpoints
        5. Adaptive recommendations
        """
        
        with st.spinner("Designing learning path..."):
            response = st.session_state.gemini_helper.generate_response(prompt)
            st.markdown(response)

elif selected_menu == "💡 Teaching Resources":
    st.header("💡 Generate Teaching Resources")
    
    resource_type = st.selectbox(
        "Resource Type",
        ["Discussion Questions", "Group Activities", "Homework Assignments", 
         "Project Ideas", "Review Materials", "Extension Activities"]
    )
    
    topic = st.text_input("Topic", "Object-Oriented Programming")
    class_size = st.number_input("Class Size", 5, 100, 25)
    
    if st.button("✨ Generate Resources", type="primary"):
        prompt = f"""
        Create {resource_type} for topic: {topic}
        Class Size: {class_size} students
        
        Requirements:
        - Engaging and interactive
        - Suitable for diverse learners
        - Clear instructions
        - Time estimates
        - Materials needed
        - Differentiation suggestions
        """
        
        with st.spinner("Generating resources..."):
            resources = st.session_state.gemini_helper.generate_response(prompt)
            st.markdown(resources)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📚 Total Curricula Generated:** 0")
with col2:
    st.markdown("**📝 Lesson Plans Created:** 0")
with col3:
    st.markdown(f"**🕒 Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Save to history
if st.session_state.generated_content:
    with st.expander("📜 Generation History"):
        for key, value in st.session_state.generated_content.items():
            st.markdown(f"**{key}** generated at {datetime.now().strftime('%H:%M:%S')}")