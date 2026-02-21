import streamlit as st
from utils.openai_helper import generate_content, format_course_outline
from utils.prompts import COURSE_OUTLINE_PROMPTS

st.set_page_config(page_title="Course Outline Generator", page_icon="📝")

# Custom CSS for this page
st.markdown("""
<style>
    .page-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
    }
    
    .feature-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1rem;
        border-radius: 50px;
        display: inline-block;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    
    .outline-container {
        background: #0E1117;   /* Dark background */
        color: #ffffff;        /* White text */
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border-left: 5px solid #f093fb;
    }
            
      .module-card {
        background: #1C1F26;   /* Dark card */
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Model badge styling */
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
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown("""
<div class="page-header">
    <h1>📝 Course Outline Generator</h1>
    <p>Create comprehensive, well-structured course outlines with AI assistance</p>
    <div>
        <span class="feature-badge">🎯 Learning Objectives</span>
        <span class="feature-badge">📚 Module Breakdown</span>
        <span class="feature-badge">⏱️ Duration Planning</span>
        <span class="feature-badge">📊 Assessment Methods</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Check if OpenAI client is initialized
if not st.session_state.get('client'):
    st.warning("⚠️ Please initialize OpenAI in the main page first.")
    st.stop()

# Model selection from session state (set in main page)
model = st.session_state.get('model', 'gpt-3.5-turbo')
temperature = st.session_state.get('temperature', 0.7)

# Display current model info
st.markdown(f"""
<div class="model-badge">
    🤖 Current Model: {model} | 🌡️ Temperature: {temperature}
</div>
""", unsafe_allow_html=True)

# Main form with enhanced styling
with st.form("course_outline_form"):
    st.markdown("### 📋 Course Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Course Title*", placeholder="e.g., Introduction to Python Programming")
        subject = st.text_input("Subject Area*", placeholder="e.g., Computer Science")
        audience = st.text_input("Target Audience*", placeholder="e.g., College freshmen, professionals")
        
    with col2:
        duration = st.number_input("Course Duration*", min_value=1, value=8)
        duration_unit = st.selectbox("Duration Unit", ["weeks", "days", "months", "sessions"])
        level = st.selectbox(
            "Course Level*",
            ["Beginner", "Intermediate", "Advanced", "All Levels"]
        )
    
    st.markdown("### 🎯 Additional Specifications")
    additional_reqs = st.text_area(
        "Additional Requirements (optional)",
        placeholder="Any specific topics, teaching methods, or resources to include?",
        height=100
    )
    
    # Prompt style selection with visual cards
    st.markdown("### 🎨 Outline Style")
    prompt_style = st.radio(
        "Select the teaching approach",
        options=list(COURSE_OUTLINE_PROMPTS.keys()),
        format_func=lambda x: x.title(),
        horizontal=True
    )
    
    # Advanced options expander
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            use_streaming = st.checkbox("Enable streaming output", value=True, 
                                       help="See content as it's being generated")
        with col2:
            include_examples = st.checkbox("Include real-world examples", value=True)
        
        temperature_override = st.slider(
            "Temperature override (optional)",
            min_value=0.0,
            max_value=1.0,
            value=temperature,
            step=0.1,
            help="Override the default temperature for this generation"
        )
    
    # Submit button with icon
    submitted = st.form_submit_button("🚀 Generate Course Outline", type="primary", use_container_width=True)

if submitted:
    if not all([title, subject, audience, duration]):
        st.error("❌ Please fill in all required fields (*)")
    else:
        course_data = {
            'title': title,
            'subject': subject,
            'audience': audience,
            'duration': duration,
            'duration_unit': duration_unit,
            'level': level,
            'additional_reqs': additional_reqs,
            'include_examples': include_examples if 'include_examples' in locals() else True
        }
        
        # Combine base prompt with style prompt
        base_prompt = format_course_outline(course_data)
        style_prompt = COURSE_OUTLINE_PROMPTS[prompt_style]
        full_prompt = f"{base_prompt}\n\n{style_prompt}"
        
        if use_streaming:
            # Streaming generation
            st.markdown("### 🎨 Generating your course outline...")
            outline_container = st.empty()
            full_response = ""
            
            with st.spinner("Crafting your course outline..."):
                for chunk in generate_content(
                    full_prompt, 
                    model=model, 
                    temperature=temperature_override,
                    
                ):
                    if chunk:
                        full_response += chunk
                        outline_container.markdown(f"""
                        <div class="outline-container">
                            <h2 style="color: #f093fb;">{title}</h2>
                            <p><strong>Subject:</strong> {subject} | <strong>Level:</strong> {level}</p>
                            <p><strong>Audience:</strong> {audience} | <strong>Duration:</strong> {duration} {duration_unit}</p>
                            <hr>
                            {full_response}
                        </div>
                        """, unsafe_allow_html=True)
            
            outline = full_response
        else:
            # Regular generation
            with st.spinner("🎨 Crafting your course outline..."):
                outline = generate_content(
                    full_prompt, 
                    model=model, 
                    temperature=temperature_override
                )
        
        if outline:
            st.success("✅ Course outline generated successfully!")
            
            # Display outline in styled tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Outline", "📊 Structure", "📋 Module Details", "💾 Export"])
            
            with tab1:
                st.markdown(f"""
                <div class="outline-container">
                    <h2 style="color: #f093fb;">{title}</h2>
                    <p><strong>Subject:</strong> {subject} | <strong>Level:</strong> {level}</p>
                    <p><strong>Audience:</strong> {audience} | <strong>Duration:</strong> {duration} {duration_unit}</p>
                    <p><small>Generated with: {model} | Temperature: {temperature_override}</small></p>
                    <hr>
                    {outline}
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("### 📊 Course Structure Overview")
                
                # Extract modules from outline (simplified parsing)
                import re
                modules = re.findall(r'(?:Module|Week)\s+\d+[:\s]+([^\n]+)', outline)
                
                if modules:
                    st.markdown("#### Module Distribution")
                    for i, module in enumerate(modules[:5], 1):
                        with st.container():
                            st.markdown(f"""
                            <div class="module-card">
                                <strong>Module {i}:</strong> {module}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Visual progress
                    st.markdown("#### Time Allocation")
                    progress_data = {
                        "Foundations": 25,
                        "Core Concepts": 35,
                        "Applications": 25,
                        "Assessment": 15
                    }
                    
                    for phase, percentage in progress_data.items():
                        st.markdown(f"**{phase}**")
                        st.progress(percentage / 100, text=f"{percentage}%")
                else:
                    st.info("Module breakdown will appear here after generation")
            
            with tab3:
                st.markdown("### 📋 Detailed Module Breakdown")
                
                # Parse modules for detailed view
                module_pattern = r'(?:Module|Week)\s+(\d+)[:\s]+([^\n]+)(.*?)(?=(?:Module|Week)\s+\d+|$)'
                modules_detailed = re.findall(module_pattern, outline, re.DOTALL)
                
                if modules_detailed:
                    for module_num, module_title, module_content in modules_detailed:
                        with st.expander(f"Module {module_num}: {module_title}", expanded=False):
                            st.markdown(module_content if module_content else "No detailed content available")
                            
                            # Add interactive elements
                            col1, col2 = st.columns(2)
                            with col1:
                                st.button(f"📝 Edit Module {module_num}", key=f"edit_{module_num}")
                            with col2:
                                st.button(f"📊 Add Assessment {module_num}", key=f"assess_{module_num}")
                else:
                    st.info("Detailed module breakdown will appear here")
            
            with tab4:
                st.markdown("### 💾 Export Options")
                
                # Prepare different formats
                markdown_content = f"""# {title}

## Course Overview
- **Subject:** {subject}
- **Level:** {level}
- **Audience:** {audience}
- **Duration:** {duration} {duration_unit}

{outline}

---
*Generated with OpenAI {model} on {st.session_state.get('timestamp', '')}*
"""
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.download_button(
                        label="📥 Markdown",
                        data=markdown_content,
                        file_name=f"{title.lower().replace(' ', '_')}_outline.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col2:
                    # Convert markdown to plain text
                    plain_text = re.sub(r'[#*`]', '', markdown_content)
                    st.download_button(
                        label="📄 Plain Text",
                        data=plain_text,
                        file_name=f"{title.lower().replace(' ', '_')}_outline.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col3:
                    st.button("📋 Copy to Clipboard", 
                             use_container_width=True,
                             on_click=lambda: st.write("📋 Copied!"))
                
                with col4:
                    st.button("📧 Email Outline", use_container_width=True)

# Sidebar with enhanced tips
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
        <h3 style="color: white;">💡 Pro Tips</h3>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin: 0.5rem 0;">🎯 Be specific about learning outcomes</li>
            <li style="margin: 0.5rem 0;">📚 Mention required prerequisites</li>
            <li style="margin: 0.5rem 0;">💻 Specify technology requirements</li>
            <li style="margin: 0.5rem 0;">👥 Include target audience details</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Model info section
    st.markdown("### 🤖 Current Configuration")
    st.info(f"""
    **Model:** {model}
    **Temperature:** {temperature}
    **Max Tokens:** 4000
    """)
    
    st.markdown("### 📚 Example Courses")
    
    example_courses = {
        "Computer Science": ["Data Structures", "Web Development", "Machine Learning"],
        "Business": ["Project Management", "Digital Marketing", "Financial Accounting"],
        "Languages": ["Spanish Basics", "Business English", "Academic Writing"]
    }
    
    for category, courses in example_courses.items():
        with st.expander(category):
            for course in courses:
                if st.button(f"📘 {course}", key=f"example_{course}", use_container_width=True):
                    # Auto-fill form with example
                    st.session_state['example_title'] = course
                    st.rerun()

# Auto-fill from example if selected
if 'example_title' in st.session_state:
    title = st.session_state.example_title
    # Clear after use
    del st.session_state.example_title