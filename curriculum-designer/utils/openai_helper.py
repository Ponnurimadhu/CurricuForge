import streamlit as st
from openai import OpenAI
import time
from datetime import datetime

def generate_content(prompt, model="gpt-3.5-turbo", temperature=0.7, max_retries=3):
    """Generate content using OpenAI with retry logic"""
    
    if not st.session_state.client:
        st.error("OpenAI client not initialized. Please check your API key.")
        return None
    
    for attempt in range(max_retries):
        try:
            with st.spinner(f"Generating content... (Attempt {attempt + 1}/{max_retries})"):
                response = st.session_state.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert curriculum designer and educator. Create detailed, professional, and pedagogically sound educational content."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=4000
                )
                
                if response and response.choices[0].message.content:
                    content = response.choices[0].message.content
                    
                    # Save to session state
                    content_id = f"Content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    st.session_state.generated_content[content_id] = {
                        'content': content,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
                        'model': model,
                        'temperature': temperature
                    }
                    return content
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                st.error(f"Failed to generate content after {max_retries} attempts: {str(e)}")
                return None
    
    return None

def generate_content_streaming(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """Generate content using OpenAI with streaming response"""
    
    if not st.session_state.client:
        st.error("OpenAI client not initialized. Please check your API key.")
        return None
    
    try:
        stream = st.session_state.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert curriculum designer and educator. Create detailed, professional, and pedagogically sound educational content."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=4000,
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content
        
        # Save to session state after complete response
        if full_response:
            content_id = f"Content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.generated_content[content_id] = {
                'content': full_response,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
                'model': model,
                'temperature': temperature
            }
            
    except Exception as e:
        st.error(f"Error in streaming generation: {str(e)}")
        return None

def format_course_outline(course_data):
    """Format course outline data for prompt"""
    return f"""
    Create a comprehensive course outline with the following specifications:
    
    Course Title: {course_data['title']}
    Subject Area: {course_data['subject']}
    Target Audience: {course_data['audience']}
    Duration: {course_data['duration']} {course_data['duration_unit']}
    Level: {course_data['level']}
    
    Additional Requirements:
    - {course_data.get('additional_reqs', 'None specified')}
    
    Please structure the response with clear headings and formatting:
    
    1. COURSE DESCRIPTION
    Write a compelling overview of the course (2-3 paragraphs)
    
    2. LEARNING OBJECTIVES
    List 5-7 specific, measurable learning objectives
    
    3. PREREQUISITES
    List any required prior knowledge or skills
    
    4. COURSE OUTLINE
    For each module/week, include:
    - Module title
    - Key topics covered (bullet points)
    - Learning activities
    - Estimated time commitment
    
    5. ASSESSMENT METHODS
    Describe how student learning will be evaluated:
    - Formative assessments
    - Summative assessments
    - Grading criteria
    
    6. REQUIRED MATERIALS
    List textbooks, software, or other resources needed
    
    7. COURSE POLICIES
    Include attendance, late work, academic integrity policies
    """

def format_lesson_plan(lesson_data):
    """Format lesson plan data for prompt"""
    return f"""
    Create a detailed lesson plan with the following specifications:
    
    Lesson Title: {lesson_data['title']}
    Course: {lesson_data['course']}
    Duration: {lesson_data['duration']} minutes
    Class Size: {lesson_data['class_size']} students
    
    Learning Objectives:
    {lesson_data['objectives']}
    
    Materials Needed:
    {lesson_data.get('materials', 'Standard classroom materials')}
    
    Prior Knowledge Required:
    {lesson_data.get('prerequisites', 'None specified')}
    
    Teaching Strategies:
    {lesson_data.get('teaching_strategies', 'Mix of direct instruction and active learning')}
    
    Please structure the lesson plan with detailed timing and activities:
    
    1. LESSON OVERVIEW
    Brief summary of the lesson (2-3 sentences)
    
    2. LEARNING OBJECTIVES
    Restate the specific objectives for this lesson
    
    3. LESSON PROCEDURE (with timestamps)
    
    A. Opening (5-10 minutes)
    - Hook/Attention grabber
    - Review of prior learning
    - Lesson objectives introduction
    
    B. Direct Instruction (15-20 minutes)
    - Key concepts presentation
    - Visual aids/Examples
    - Check for understanding questions
    
    C. Guided Practice (15-20 minutes)
    - Step-by-step activities
    - Teacher scaffolding
    - Group/Partner work instructions
    
    D. Independent Practice (10-15 minutes)
    - Individual student work
    - Application of learning
    - Teacher monitoring strategies
    
    E. Closing (5-10 minutes)
    - Summary of key points
    - Exit ticket/Formative assessment
    - Preview of next lesson
    
    4. DIFFERENTIATION STRATEGIES
    - For struggling learners
    - For English language learners
    - For advanced students
    
    5. ASSESSMENT
    - Formative checks throughout
    - Success criteria
    - Feedback methods
    
    6. EXTENSION ACTIVITIES
    Ideas for early finishers or homework
    
    7. TEACHER REFLECTION
    Space for notes on lesson effectiveness
    """

def format_assessment(assessment_data):
    """Format assessment data for prompt"""
    return f"""
    Create a comprehensive assessment with the following specifications:
    
    Assessment Type: {assessment_data['type']}
    Subject/Topic: {assessment_data['topic']}
    Grade Level: {assessment_data['grade_level']}
    Number of Questions: {assessment_data['num_questions']}
    Difficulty Level: {assessment_data['difficulty']}
    
    Learning Objectives Tested:
    {assessment_data['objectives']}
    
    Question Types to Include:
    {assessment_data.get('question_types', 'Multiple choice, short answer, and essay')}
    
    Additional Requirements:
    - {assessment_data.get('requirements', 'Include a variety of question types and clear instructions')}
    
    Please structure the assessment professionally:
    
    1. ASSESSMENT TITLE AND HEADER
    - Assessment name
    - Total points possible
    - Time allowed
    - Instructions for students
    
    2. SECTION 1: MULTIPLE CHOICE assessment_data.get('num_mcq', assessment_data.get('num_questions', 9)//3)
    For each question:
    - Clear question stem
    - 4 options (A-D)
    - Indicate correct answer in key
    
    3. SECTION 2: SHORT ANSWER assessment_data.get('num_mcq', assessment_data.get('num_questions', 9)//3)
    For each question:
    - Clear prompt
    - Expected response length
    - Key points to include
    
    4. SECTION 3: ESSAY/EXTENDED RESPONSE ({assessment_data.get('num_essay', 1)} questions)
    For each prompt:
    - Detailed question
    - Rubric/Grading criteria
    - Expected length
    
    5. ANSWER KEY
    - Correct answers for multiple choice
    - Sample answers/model responses
    - Grading rubric with point values
    
    6. ASSESSMENT ANALYSIS
    - Skills assessed
    - Difficulty distribution
    - Recommendations for remediation
    """

def format_project_based_learning(pbl_data):
    """Format project-based learning activity data for prompt"""
    return f"""
    Create a detailed project-based learning activity with the following specifications:
    
    Project Title: {pbl_data['title']}
    Subject Area: {pbl_data['subject']}
    Grade Level: {pbl_data['grade_level']}
    Duration: {pbl_data['duration']} {pbl_data['duration_unit']}
    Group Size: {pbl_data['group_size']}
    
    Driving Question:
    {pbl_data['driving_question']}
    
    Learning Objectives:
    {pbl_data['objectives']}
    
    21st Century Skills Focus:
    {pbl_data.get('skills', 'Critical thinking, collaboration, communication, creativity')}
    
    Please structure the PBL activity with:
    
    1. PROJECT OVERVIEW
    - Real-world context
    - Authentic audience
    - Final product description
    
    2. ENTRY EVENT
    - Hook to launch the project
    - Initial questions to explore
    
    3. SCAFFOLDED ACTIVITIES
    Week-by-week breakdown of:
    - Research activities
    - Skill-building lessons
    - Checkpoints and milestones
    
    4. RESOURCES
    - Materials needed
    - Expert contacts/Community partners
    - Digital tools and resources
    
    5. STUDENT SUPPORT
    - Differentiation strategies
    - Scaffolding for diverse learners
    - Extension challenges
    
    6. ASSESSMENT
    - Formative checkpoints
    - Rubric for final product
    - Peer and self-assessment forms
    
    7. PRESENTATION
    - Presentation format
    - Audience engagement strategies
    - Reflection prompts
    """

def initialize_openai_client(api_key):
    """Initialize OpenAI client with error handling"""
    try:
        client = OpenAI(api_key=api_key)
        # Test the connection with a simple completion
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return client
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")
        return None