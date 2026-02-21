import streamlit as st
from utils.openai_helper import generate_content, format_lesson_plan
from utils.prompts import LESSON_PLAN_PROMPTS

st.set_page_config(page_title="Lesson Planner", page_icon="📅")

# Custom CSS for this page
st.markdown("""
<style>
    .lesson-header {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 2rem;
        border-radius: 20px;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(132, 250, 176, 0.3);
    }
    
    .timeline-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .timeline-step {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .activity-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #84fab0;
        margin: 1rem 0;
    }
    
    .model-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        display: inline-block;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .engagement-tag {
        background: #e8f5e9;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.25rem;
        border-left: 3px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown("""
<div class="lesson-header">
    <h1>📅 AI Lesson Planner</h1>
    <p>Design engaging, interactive lessons that captivate your students</p>
</div>
""", unsafe_allow_html=True)

# Check if OpenAI client is initialized
if not st.session_state.get('client'):
    st.warning("⚠️ Please initialize OpenAI in the main page first.")
    st.stop()

# Get model configuration from session state
model = st.session_state.get('model', 'gpt-3.5-turbo')
temperature = st.session_state.get('temperature', 0.7)

# Display current model info
st.markdown(f"""
<div class="model-badge">
    🤖 Current Model: {model} | 🌡️ Temperature: {temperature}
</div>
""", unsafe_allow_html=True)

# Main form
with st.form("lesson_plan_form"):
    st.markdown("### 📝 Lesson Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Lesson Title*", placeholder="e.g., Introduction to Photosynthesis")
        course = st.text_input("Course Name*", placeholder="e.g., Biology 101")
        duration = st.slider("Lesson Duration (minutes)*", min_value=15, max_value=180, value=60, step=15)
        
    with col2:
        class_size = st.number_input("Class Size*", min_value=1, value=25, max_value=200)
        objectives = st.text_area(
            "Learning Objectives*",
            placeholder="What should students know or be able to do by the end of this lesson?",
            height=100
        )
    
    st.markdown("### 📚 Resources & Prerequisites")
    materials = st.text_input(
        "Materials Needed",
        placeholder="e.g., Textbook, worksheets, projector, lab equipment"
    )
    
    prerequisites = st.text_input(
        "Prior Knowledge Required",
        placeholder="What should students already know?"
    )
    
    # Teaching style selection with visual indicators
    st.markdown("### 🎯 Teaching Approach")
    teaching_style = st.selectbox(
        "Select teaching style",
        options=list(LESSON_PLAN_PROMPTS.keys()),
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # Engagement features
    st.markdown("### ✨ Engagement Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        group_work = st.checkbox("👥 Group Activities")
        technology = st.checkbox("💻 Technology Integration")
        brainstorming = st.checkbox("💡 Brainstorming")
    
    with col2:
        hands_on = st.checkbox("✋ Hands-on Exercises")
        discussion = st.checkbox("💬 Class Discussion")
        gamification = st.checkbox("🎮 Gamification")
    
    with col3:
        assessment = st.checkbox("📊 Formative Assessment")
        differentiation = st.checkbox("🎯 Differentiation")
        real_world = st.checkbox("🌍 Real-world Connections")
    
    # Advanced options expander
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            use_streaming = st.checkbox("Enable streaming output", value=True,
                                       help="See content as it's being generated")
            include_timings = st.checkbox("Include detailed timings", value=True)
        with col2:
            temperature_override = st.slider(
                "Temperature override",
                min_value=0.0,
                max_value=1.0,
                value=temperature,
                step=0.1,
                help="Override default temperature"
            )
            include_standards = st.checkbox("Include educational standards", value=False)
    
    submitted = st.form_submit_button("🚀 Generate Lesson Plan", type="primary", use_container_width=True)

if submitted:
    if not all([title, course, duration, objectives]):
        st.error("❌ Please fill in all required fields (*)")
    else:
        # Collect engagement features
        engagement_features = []
        if group_work: engagement_features.append("group activities with clear roles")
        if technology: engagement_features.append("technology integration (presentation tools, online resources)")
        if hands_on: engagement_features.append("hands-on exercises and manipulatives")
        if discussion: engagement_features.append("structured class discussions with guiding questions")
        if assessment: engagement_features.append("formative assessment strategies (exit tickets, quick checks)")
        if differentiation: engagement_features.append("differentiation strategies for diverse learners")
        if brainstorming: engagement_features.append("brainstorming sessions to activate prior knowledge")
        if gamification: engagement_features.append("gamification elements to increase engagement")
        if real_world: engagement_features.append("real-world connections and applications")
        
        lesson_data = {
            'title': title,
            'course': course,
            'duration': duration,
            'class_size': class_size,
            'objectives': objectives,
            'materials': materials,
            'prerequisites': prerequisites,
            'include_timings': include_timings if 'include_timings' in locals() else True,
            'include_standards': include_standards if 'include_standards' in locals() else False,
            'engagement_features': engagement_features
        }
        
        base_prompt = format_lesson_plan(lesson_data)
        style_prompt = LESSON_PLAN_PROMPTS[teaching_style]
        
        # Add engagement features to prompt
        if engagement_features:
            style_prompt += f"\n\n**ENGAGEMENT FEATURES TO INCLUDE:**\n"
            for feature in engagement_features:
                style_prompt += f"• {feature}\n"
        
        # Add standards if requested
        if include_standards:
            style_prompt += "\n\n**EDUCATIONAL STANDARDS:**\nAlign the lesson with Common Core or relevant educational standards and mention them explicitly."
        
        full_prompt = f"{base_prompt}\n\n{style_prompt}"
        
        if use_streaming:
            # Streaming generation
            st.markdown("### 🎨 Generating your lesson plan...")
            outline_container = st.empty()
            full_response = ""
            
            with st.spinner("Crafting your engaging lesson plan..."):
                for chunk in generate_content(
                    full_prompt, 
                    model=model, 
                    temperature=temperature_override,
                    
                ):
                    if chunk:
                        full_response += chunk
                        outline_container.markdown(f"""
                        <div class="outline-container">
                            <h2 style="color: #84fab0;">{title}</h2>
                            <p><strong>Course:</strong> {course} | <strong>Duration:</strong> {duration} minutes</p>
                            <p><strong>Class Size:</strong> {class_size} students</p>
                            <p><small>Generating with {model}...</small></p>
                            <hr>
                            {full_response}
                        </div>
                        """, unsafe_allow_html=True)
            
            lesson_plan = full_response
        else:
            # Regular generation
            with st.spinner("🎨 Crafting your engaging lesson plan..."):
                lesson_plan = generate_content(
                    full_prompt, 
                    model=model, 
                    temperature=temperature_override
                )
        
        if lesson_plan:
            st.success("✅ Lesson plan generated successfully!")
            
            # Display engagement tags
            if engagement_features:
                st.markdown("### ✨ Selected Engagement Features")
                tags_html = ""
                for feature in engagement_features:
                    tags_html += f'<span class="engagement-tag">{feature}</span> '
                st.markdown(f'<div>{tags_html}</div>', unsafe_allow_html=True)
            
            # Interactive timeline visualization
            st.markdown("### ⏱️ Lesson Timeline")
            
            cols = st.columns(4)
            timeline_segments = [
                ("🎯 Opening", "5-10 min", "Hook & Objectives"),
                ("📚 Instruction", "15-20 min", "Content Delivery"),
                ("✋ Practice", "15-20 min", "Guided & Independent"),
                ("🎉 Closing", "5-10 min", "Review & Assessment")
            ]
            
            for col, (title_seg, duration_seg, desc) in zip(cols, timeline_segments):
                with col:
                    st.markdown(f"""
                    <div class="timeline-step">
                        <h4>{title_seg}</h4>
                        <p style="font-size: 1.2rem; margin: 0.5rem 0;">{duration_seg}</p>
                        <p style="font-size: 0.9rem; opacity: 0.9;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Full Lesson Plan", "⏰ Timeline View", "📋 Activities", "💾 Export"])
            
            with tab1:
                st.markdown(f"""
                <div class="outline-container">
                    <h2 style="color: #84fab0;">{title}</h2>
                    <p><strong>Course:</strong> {course} | <strong>Duration:</strong> {duration} minutes</p>
                    <p><strong>Class Size:</strong> {class_size} students</p>
                    <p><small>Generated with: {model} | Temperature: {temperature_override}</small></p>
                    <hr>
                    {lesson_plan}
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("### ⏰ Detailed Timeline")
                
                # Try to extract timeline from lesson plan
                import re
                timeline_pattern = r'(\d+)[-–]\s*(\d+)?\s*minutes?[:\s]+([^\n]+)'
                timeline_items = re.findall(timeline_pattern, lesson_plan, re.IGNORECASE)
                
                if timeline_items:
                    for start, end, activity in timeline_items:
                        duration_text = f"{start}-{end}" if end else start
                        st.markdown(f"""
                        <div class="activity-card">
                            <strong>⏱️ {duration_text} minutes:</strong> {activity}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Timeline details will be extracted from the generated lesson plan")
            
            with tab3:
                st.markdown("### 📋 Activities Breakdown")
                
                # Parse activities
                activity_patterns = [
                    r'(?:Opening|Hook|Warm-up)[:\s]+([^\n]+)',
                    r'(?:Direct Instruction|Lecture)[:\s]+([^\n]+)',
                    r'(?:Guided Practice)[:\s]+([^\n]+)',
                    r'(?:Independent Practice)[:\s]+([^\n]+)',
                    r'(?:Closing|Exit Ticket)[:\s]+([^\n]+)'
                ]
                
                for pattern in activity_patterns:
                    matches = re.findall(pattern, lesson_plan, re.IGNORECASE)
                    for match in matches:
                        st.markdown(f"""
                        <div class="activity-card">
                            {match}
                        </div>
                        """, unsafe_allow_html=True)
            
            with tab4:
                st.markdown("### 💾 Export Options")
                
                # Prepare markdown content with metadata
                markdown_content = f"""# {title}

## Lesson Overview
- **Course:** {course}
- **Duration:** {duration} minutes
- **Class Size:** {class_size} students
- **Teaching Style:** {teaching_style.replace('_', ' ').title()}
- **Generated with:** {model} (Temperature: {temperature_override})

## Learning Objectives
{objectives}

## Materials Needed
{materials if materials else 'Standard classroom materials'}

## Prerequisites
{prerequisites if prerequisites else 'None specified'}

## Engagement Features
{chr(10).join(['- ' + f for f in engagement_features]) if engagement_features else '- Standard engagement techniques'}

---

{lesson_plan}

---
*Generated with OpenAI {model} on {st.session_state.get('timestamp', '')}*
"""
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📥 Download Markdown",
                        data=markdown_content,
                        file_name=f"{title.lower().replace(' ', '_')}_lesson_plan.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col2:
                    # Plain text version
                    plain_text = re.sub(r'[#*`]', '', markdown_content)
                    st.download_button(
                        label="📄 Plain Text",
                        data=plain_text,
                        file_name=f"{title.lower().replace(' ', '_')}_lesson_plan.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col3:
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.success("✅ Copied to clipboard!")

# Sidebar with differentiation strategies and tips
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
                padding: 1rem; border-radius: 10px; color: #2c3e50;">
        <h3>🎯 Differentiation Strategies</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Model info
    st.markdown("### 🤖 Current Configuration")
    st.info(f"""
    **Model:** {model}
    **Temperature:** {temperature}
    **Max Tokens:** 4000
    """)
    
    with st.expander("📚 For Different Learners"):
        st.markdown("""
        - **Visual learners**: Diagrams, charts, videos, concept maps
        - **Auditory learners**: Discussions, recordings, music integration
        - **Kinesthetic learners**: Hands-on activities, movement breaks
        - **Reading/Writing**: Text-based materials, written reflections
        """)
    
    with st.expander("⚡ For Quick Learners"):
        st.markdown("""
        - Extension activities with increasing complexity
        - Independent research projects
        - Peer tutoring opportunities
        - Advanced problem-solving tasks
        - Creative application challenges
        """)
    
    with st.expander("🆘 For Struggling Learners"):
        st.markdown("""
        - Scaffolded instructions with visual aids
        - Additional practice with immediate feedback
        - One-on-one support during activities
        - Modified assignments with clear steps
        - Peer buddies and cooperative learning
        """)
    
    with st.expander("📊 Assessment Ideas"):
        st.markdown("""
        - **Formative**: Exit tickets, thumbs up/down, quick writes
        - **Summative**: Quizzes, projects, presentations
        - **Peer Assessment**: Rubrics, feedback forms
        - **Self-Assessment**: Reflection journals, goal setting
        """)
    
    # Quick tips
    st.markdown("---")
    st.markdown("""
    ### 💡 Pro Tips
    - 🎯 Be specific with learning objectives
    - ⏱️ Include buffer time for transitions
    - 🔄 Plan for different pacing needs
    - 📝 Prepare backup activities
    - 🤔 Include think-pair-share moments
    """)

# Initialize timestamp if not exists
if 'timestamp' not in st.session_state:
    from datetime import datetime
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")