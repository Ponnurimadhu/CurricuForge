import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiHelper:
    def __init__(self):
        """Initialize Gemini AI with API key"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Please set GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, prompt, max_tokens=2048):
        """Generate response from Gemini AI"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_curriculum(self, subject, level, duration, learning_objectives):
        """Generate curriculum based on parameters"""
        prompt = f"""
        Create a comprehensive curriculum for:
        Subject: {subject}
        Level: {level}
        Duration: {duration} weeks
        Learning Objectives: {learning_objectives}
        
        Please include:
        1. Course overview and description
        2. Learning outcomes
        3. Weekly breakdown of topics
        4. Assessment methods
        5. Required resources
        6. Prerequisites
        
        Format in a clear, organized structure.
        """
        return self.generate_response(prompt)
    
    def generate_lesson_plan(self, topic, duration, objectives, activities):
        """Generate detailed lesson plan"""
        prompt = f"""
        Create a detailed lesson plan for:
        Topic: {topic}
        Duration: {duration} minutes
        Learning Objectives: {objectives}
        Activities/Exercises: {activities}
        
        Include:
        1. Lesson objectives
        2. Materials needed
        3. Step-by-step procedure
        4. Assessment strategies
        5. Differentiation ideas
        6. Homework/Extension activities
        """
        return self.generate_response(prompt)
    
    def generate_assessment(self, topic, assessment_type, difficulty):
        """Generate assessment questions"""
        prompt = f"""
        Create {assessment_type} assessment for topic: {topic}
        Difficulty level: {difficulty}
        
        Include:
        1. 5 multiple choice questions with answers
        2. 3 short answer questions
        3. 1 essay/long answer question
        4. Rubric for grading
        """
        return self.generate_response(prompt)