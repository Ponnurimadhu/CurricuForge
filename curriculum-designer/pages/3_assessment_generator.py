import streamlit as st
from utils.openai_helper import generate_content, format_assessment
from utils.prompts import ASSESSMENT_PROMPTS
import re
from datetime import datetime

st.set_page_config(page_title="Assessment Generator", page_icon="📊")

# Custom CSS for this page
st.markdown("""
<style>
    .assessment-header {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 2rem;
        border-radius: 20px;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(255, 154, 158, 0.3);
    }
    
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #ff9a9e;
        transition: transform 0.3s ease;
    }
    
    .question-card:hover {
        transform: translateX(10px);
    }
    
    .difficulty-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .easy { background: #d4edda; color: #155724; }
    .medium { background: #fff3cd; color: #856404; }
    .hard { background: #f8d7da; color: #721c24; }
    
    .rubric-table {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .rubric-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        text-align: left;
    }
    
    .rubric-table td {
        padding: 1rem;
        border-bottom: 1px solid #e0e0e0;
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
    
    .stats-card {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #667eea30;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown("""
<div class="assessment-header">
    <h1>📊 Assessment Generator</h1>
    <p>Create comprehensive assessments with automatic answer keys and rubrics</p>
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
with st.form("assessment_form"):
    st.markdown("### 📝 Assessment Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        assessment_type = st.selectbox(
            "Assessment Type*",
            ["Quiz", "Test", "Exam", "Assignment", "Project", "Worksheet"],
            format_func=lambda x: f"📌 {x}"
        )
        topic = st.text_input("Topic/Subject*", placeholder="e.g., Quadratic Equations")
        grade_level = st.text_input("Grade Level*", placeholder="e.g., 10th Grade, College")
        
    with col2:
        num_questions = st.number_input("Number of Questions*", min_value=1, max_value=50, value=10)
        difficulty = st.select_slider(
            "Difficulty Level*",
            options=["Very Easy", "Easy", "Medium", "Hard", "Very Hard"],
            value="Medium"
        )
        time_limit = st.number_input("Time Limit (minutes)", min_value=5, max_value=180, value=60, step=5)
    
    objectives = st.text_area(
        "Learning Objectives Tested*",
        placeholder="What specific knowledge or skills should this assessment measure?",
        height=100
    )
    
    requirements = st.text_area(
        "Additional Requirements",
        placeholder="e.g., Include real-world problems, require written explanations, etc.",
        height=80
    )
    
    # Assessment purpose
    st.markdown("### 🎯 Assessment Purpose")
    assessment_style = st.radio(
        "Select the main purpose",
        options=list(ASSESSMENT_PROMPTS.keys()),
        format_func=lambda x: x.title(),
        horizontal=True
    )
    
    # Question types with visual icons
    st.markdown("### 📋 Question Types")
    q_col1, q_col2, q_col3 = st.columns(3)
    
    with q_col1:
        multiple_choice = st.checkbox("🔘 Multiple Choice", value=True)
        true_false = st.checkbox("✅ True/False")
        
    with q_col2:
        short_answer = st.checkbox("📝 Short Answer", value=True)
        essay = st.checkbox("📄 Essay")
        
    with q_col3:
        matching = st.checkbox("🔗 Matching")
        fill_blank = st.checkbox("✏️ Fill in the Blank", value=True)
        diagram = st.checkbox("📊 Diagram/Label")
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            use_streaming = st.checkbox("Enable streaming output", value=True,
                                       help="See content as it's being generated")
            include_answer_key = st.checkbox("Include answer key", value=True)
            include_rubric = st.checkbox("Include grading rubric", value=True)
        with col2:
            temperature_override = st.slider(
                "Temperature override",
                min_value=0.0,
                max_value=1.0,
                value=temperature,
                step=0.1,
                help="Override default temperature for more/less creative questions"
            )
            include_blooms = st.checkbox("Include Bloom's Taxonomy levels", value=False)
    
    submitted = st.form_submit_button("🚀 Generate Assessment", type="primary", use_container_width=True)

if submitted:
    if not all([topic, grade_level, objectives]):
        st.error("❌ Please fill in all required fields (*)")
    else:
        # Compile question types
        question_types = []
        if multiple_choice: question_types.append("multiple choice")
        if true_false: question_types.append("true/false")
        if short_answer: question_types.append("short answer")
        if essay: question_types.append("essay")
        if matching: question_types.append("matching")
        if fill_blank: question_types.append("fill in the blank")
        if diagram: question_types.append("diagram labeling")
        
        assessment_data = {
            'type': assessment_type,
            'topic': topic,
            'grade_level': grade_level,
            'num_questions': num_questions,
            'difficulty': difficulty,
            'time_limit': time_limit,
            'objectives': objectives,
            'requirements': f"{requirements}\nQuestion types to include: {', '.join(question_types)}",
            'include_blooms': include_blooms if 'include_blooms' in locals() else False
        }
        
        base_prompt = format_assessment(assessment_data)
        style_prompt = ASSESSMENT_PROMPTS[assessment_style]
        full_prompt = f"{base_prompt}\n\n{style_prompt}"
        
        if use_streaming:
            # Streaming generation for main assessment
            st.markdown("### 📝 Generating your assessment...")
            assessment_container = st.empty()
            full_response = ""
            
            with st.spinner("Creating assessment questions..."):
                for chunk in generate_content(
                    full_prompt, 
                    model=model, 
                    temperature=temperature_override,
                    
                ):
                    if chunk:
                        full_response += chunk
                        assessment_container.markdown(f"""
                        <div class="outline-container">
                            <h2 style="color: #ff9a9e;">{topic} - {assessment_type}</h2>
                            <p><strong>Grade Level:</strong> {grade_level} | <strong>Time:</strong> {time_limit} min</p>
                            <p><strong>Difficulty:</strong> 
                                <span class="difficulty-badge {'easy' if difficulty in ['Very Easy', 'Easy'] else 'medium' if difficulty == 'Medium' else 'hard'}">
                                    {difficulty}
                                </span>
                            </p>
                            <p><small>Generating with {model}...</small></p>
                            <hr>
                            {full_response}
                        </div>
                        """, unsafe_allow_html=True)
            
            assessment = full_response
        else:
            # Regular generation
            with st.spinner("📝 Generating your assessment..."):
                assessment = generate_content(
                    full_prompt, 
                    model=model, 
                    temperature=temperature_override
                )
        
        if assessment:
            st.success("✅ Assessment generated successfully!")
            
            # Display assessment in styled tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Assessment", "🔑 Answer Key", "📊 Rubric", "📈 Analysis", "💾 Export"])
            
            with tab1:
                st.markdown(f"""
                <div class="outline-container">
                    <h2 style="color: #ff9a9e;">{topic} - {assessment_type}</h2>
                    <p><strong>Grade Level:</strong> {grade_level} | <strong>Time Limit:</strong> {time_limit} minutes</p>
                    <p><strong>Difficulty:</strong> 
                        <span class="difficulty-badge {'easy' if difficulty in ['Very Easy', 'Easy'] else 'medium' if difficulty == 'Medium' else 'hard'}">
                            {difficulty}
                        </span>
                    </p>
                    <p><small>Generated with: {model} | Temperature: {temperature_override}</small></p>
                    <hr>
                    {assessment}
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                if include_answer_key:
                    with st.spinner("🔑 Generating answer key..."):
                        answer_key_prompt = f"""Create a detailed answer key for this {assessment_type} on {topic}:

{assessment}

Format the answer key with:
1. Correct answers for multiple choice, true/false, matching
2. Model answers/sample responses for short answer and essay questions
3. Point values for each question
4. Explanations for correct answers where helpful"""
                        
                        if use_streaming:
                            answer_container = st.empty()
                            answer_full = ""
                            for chunk in generate_content(answer_key_prompt, model=model, temperature=0.3):
                                if chunk:
                                    answer_full += chunk
                                    answer_container.markdown(f"""
                                    <div class="outline-container">
                                        <h3 style="color: #ff9a9e;">Answer Key</h3>
                                        {answer_full}
                                    </div>
                                    """, unsafe_allow_html=True)
                            answer_key = answer_full
                        else:
                            answer_key = generate_content(answer_key_prompt, model=model, temperature=0.3)
                            
                        if answer_key:
                            st.markdown(f"""
                            <div class="outline-container">
                                <h3 style="color: #ff9a9e;">Answer Key</h3>
                                {answer_key}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Answer key generation was disabled. Enable it in Advanced Options to include.")
            
            with tab3:
                if include_rubric:
                    with st.spinner("📊 Generating scoring rubric..."):
                        rubric_prompt = f"""Create a detailed scoring rubric for this {assessment_type} on {topic}:

{assessment}

Include:
1. Grading criteria for each question type
2. Point distribution
3. Performance levels (Excellent, Good, Satisfactory, Needs Improvement)
4. Specific descriptors for each level
5. Total points calculation"""
                        
                        if use_streaming:
                            rubric_container = st.empty()
                            rubric_full = ""
                            for chunk in generate_content(rubric_prompt, model=model, temperature=0.3):
                                if chunk:
                                    rubric_full += chunk
                                    rubric_container.markdown(f"""
                                    <div class="rubric-table">
                                        <h3 style="padding: 1rem; color: #ff9a9e;">Scoring Rubric</h3>
                                        {rubric_full}
                                    </div>
                                    """, unsafe_allow_html=True)
                            rubric = rubric_full
                        else:
                            rubric = generate_content(rubric_prompt, model=model, temperature=0.3)
                            
                        if rubric:
                            st.markdown(f"""
                            <div class="rubric-table">
                                <h3 style="padding: 1rem; color: #ff9a9e;">Scoring Rubric</h3>
                                {rubric}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Rubric generation was disabled. Enable it in Advanced Options to include.")
            
            with tab4:
                st.markdown("### 📈 Assessment Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Difficulty Distribution")
                    
                    # Parse or estimate difficulty distribution
                    difficulty_map = {
                        "Very Easy": 20,
                        "Easy": 20,
                        "Medium": 30,
                        "Hard": 20,
                        "Very Hard": 10
                    }
                    
                    for level, percentage in difficulty_map.items():
                        st.markdown(f"**{level}**")
                        st.progress(percentage / 100, text=f"{percentage}%")
                
                with col2:
                    st.markdown("#### Question Type Distribution")
                    
                    # Calculate percentages
                    num_types = len(question_types)
                    if num_types > 0:
                        base_percentage = 100 // num_types
                        remainder = 100 - (base_percentage * num_types)
                        
                        for i, q_type in enumerate(question_types):
                            percentage = base_percentage + (remainder if i == 0 else 0)
                            st.markdown(f"• {q_type.title()} ({percentage}%)")
                    
                    st.markdown(f"**Total Questions:** {num_questions}")
                    st.markdown(f"**Estimated Time:** {time_limit} minutes")
                    st.markdown(f"**Questions per minute:** {num_questions/time_limit:.1f}")
                
                # Bloom's Taxonomy analysis if requested
                if include_blooms:
                    st.markdown("#### 🧠 Bloom's Taxonomy Distribution")
                    blooms_levels = {
                        "Remember": 15,
                        "Understand": 25,
                        "Apply": 30,
                        "Analyze": 15,
                        "Evaluate": 10,
                        "Create": 5
                    }
                    
                    for level, percentage in blooms_levels.items():
                        st.markdown(f"**{level}**")
                        st.progress(percentage / 100, text=f"{percentage}%")
            
            with tab5:
                st.markdown("### 💾 Export Options")
                
                # Prepare comprehensive markdown content
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                markdown_content = f"""# {topic} - {assessment_type}

## Assessment Overview
- **Grade Level:** {grade_level}
- **Time Limit:** {time_limit} minutes
- **Total Questions:** {num_questions}
- **Difficulty:** {difficulty}
- **Question Types:** {', '.join(question_types)}

## Learning Objectives
{objectives}

## Additional Requirements
{requirements if requirements else 'None specified'}

---

{assessment}

"""
                
                if include_answer_key and 'answer_key' in locals():
                    markdown_content += f"\n## Answer Key\n\n{answer_key}\n"
                
                if include_rubric and 'rubric' in locals():
                    markdown_content += f"\n## Grading Rubric\n\n{rubric}\n"
                
                markdown_content += f"""
---
*Generated with OpenAI {model} on {timestamp}*
*Temperature: {temperature_override}*
"""
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📥 Download Markdown",
                        data=markdown_content,
                        file_name=f"{topic.lower().replace(' ', '_')}_{assessment_type.lower()}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col2:
                    # Plain text version
                    plain_text = re.sub(r'[#*`]', '', markdown_content)
                    st.download_button(
                        label="📄 Plain Text",
                        data=plain_text,
                        file_name=f"{topic.lower().replace(' ', '_')}_{assessment_type.lower()}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col3:
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.success("✅ Content copied to clipboard!")

# Question bank feature in sidebar
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                padding: 1rem; border-radius: 10px; color: #2c3e50;">
        <h3>📚 Question Bank</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Model info
    st.markdown("### 🤖 Current Configuration")
    st.info(f"""
    **Model:** {model}
    **Temperature:** {temperature}
    **Max Tokens:** 4000
    """)
    
    if 'question_bank' not in st.session_state:
        st.session_state.question_bank = []
    
    # Quick question generator
    with st.expander("➕ Add Custom Question", expanded=False):
        q_topic = st.text_input("Topic", key="q_topic", placeholder="e.g., Algebra")
        q_type = st.selectbox("Type", ["Multiple Choice", "Short Answer", "Essay", "Problem Solving", "True/False"])
        q_difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
        
        if st.button("Generate Question", use_container_width=True):
            if q_topic:
                with st.spinner("Generating..."):
                    q_prompt = f"""Generate one {q_difficulty} {q_type} question about {q_topic} for {grade_level if 'grade_level' in locals() else 'appropriate'} level.
                    
Include:
1. The question
2. If multiple choice, provide 4 options
3. Indicate the correct answer
"""
                    if use_streaming:
                        st.info("Question will appear below...")
                        question_container = st.empty()
                        question_full = ""
                        for chunk in generate_content(q_prompt, model=model, temperature=0.5):
                            if chunk:
                                question_full += chunk
                                question_container.markdown(question_full)
                        question = question_full
                    else:
                        question = generate_content(q_prompt, model=model, temperature=0.5)
                    
                    if question:
                        st.session_state.question_bank.append({
                            'question': question,
                            'topic': q_topic,
                            'type': q_type,
                            'difficulty': q_difficulty,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        st.success("✅ Question added to bank!")
                        st.rerun()
    
    # Display question bank
    if st.session_state.question_bank:
        st.markdown("### 📌 Saved Questions")
        for i, q in enumerate(reversed(st.session_state.question_bank[-5:])):
            with st.container():
                difficulty_class = q['difficulty'].lower()
                st.markdown(f"""
                <div class="question-card" style="padding: 1rem;">
                    <span class="difficulty-badge {difficulty_class}">{q['difficulty']}</span>
                    <span style="color: #666; font-size: 0.85rem;">{q['type']}</span>
                    <p style="margin-top: 0.5rem;"><strong>{q['topic']}</strong></p>
                    <p style="font-size: 0.85rem; color: #666;">{q['question'][:100]}...</p>
                    <p style="font-size: 0.75rem; color: #999;">{q.get('timestamp', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if len(st.session_state.question_bank) > 5:
            st.caption(f"... and {len(st.session_state.question_bank) - 5} more questions")
        
        if st.button("🗑️ Clear Question Bank", use_container_width=True):
            st.session_state.question_bank = []
            st.rerun()
    else:
        st.info("No questions saved yet. Generate questions above to build your bank.")

# Initialize timestamp if not exists
if 'timestamp' not in st.session_state:
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")