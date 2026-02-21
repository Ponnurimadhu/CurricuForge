import google.generativeai as genai
import json
import streamlit as st
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class GeminiHelper:
    def __init__(self, api_key):
        """Initialize Gemini with free tier optimizations"""
        genai.configure(api_key=api_key)
        # Use the latest free-tier accessible models
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')  # Fast and free  # For complex tasks
        
        # Free tier rate limits (as of 2026) [citation:4]
        self.rate_limits = {
            'flash': {'rpm': 15, 'rpd': 1500},  # 15 requests per minute, 1500 per day
            'pro': {'rpm': 5, 'rpd': 50}        # 5 requests per minute, 50 per day
        }
        
        # Track requests for rate limiting
        self.request_timestamps = []
    
    def _check_rate_limit(self, model_type='flash'):
        """Check if we're within rate limits"""
        import time
        now = time.time()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        
        limit = self.rate_limits[model_type]['rpm']
        if len(self.request_timestamps) >= limit:
            wait_time = 60 - (now - self.request_timestamps[0])
            if wait_time > 0:
                st.warning(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
        
        self.request_timestamps.append(now)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def generate_curriculum(self, topic, duration, level, learning_objectives):
        """Generate a comprehensive curriculum with free tier optimization"""
        
        # Use flash model for faster responses (free tier optimized)
        self._check_rate_limit('flash')
        
        # Optimized prompt for shorter responses (saves tokens)
        prompt = f"""
        Create a concise curriculum for a {level} course on {topic} ({duration} weeks).
        
        Learning Objectives: {learning_objectives}
        
        Generate a structured curriculum with:
        1. Brief course overview
        2. 5 key learning outcomes
        3. Weekly topics (1 per week) with 3 subtopics each
        4. 3 prerequisites
        5. 3 assessment methods
        
        Format as JSON:
        {{
            "course_overview": {{
                "title": "string",
                "description": "string (max 100 words)",
                "duration": "{duration} weeks",
                "level": "{level}"
            }},
            "learning_outcomes": ["outcome1", "outcome2", "outcome3", "outcome4", "outcome5"],
            "weekly_breakdown": [
                {{
                    "week": integer,
                    "topic": "string",
                    "subtopics": ["subtopic1", "subtopic2", "subtopic3"],
                    "activities": ["activity1", "activity2"]
                }}
            ],
            "prerequisites": ["prereq1", "prereq2", "prereq3"],
            "assessment_methods": ["method1", "method2", "method3"],
            "resources": ["resource1", "resource2", "resource3"]
        }}
        
        Return only valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean response (remove markdown code blocks if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            curriculum = json.loads(response_text)
            return curriculum
            
        except Exception as e:
            st.error(f"Error generating curriculum: {str(e)}")
            return None
    
    def enhance_curriculum(self, existing_curriculum, enhancement_type):
        """Enhance curriculum with rate limit awareness"""
        
        self._check_rate_limit('flash')
        
        prompt = f"""
        Add more details to the {enhancement_type} section of this curriculum:
        
        {json.dumps(existing_curriculum, indent=2)}
        
        Return the complete enhanced curriculum in the same JSON format.
        Keep the response concise to save tokens.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            enhanced = json.loads(response_text)
            return enhanced
            
        except Exception as e:
            st.error(f"Error enhancing curriculum: {str(e)}")
            return None
    
    def generate_quiz_questions(self, topic, num_questions=3):
        """Generate quiz with fewer questions to save tokens"""
        
        self._check_rate_limit('flash')
        
        # Limit questions for free tier
        num_questions = min(num_questions, 3)  # Max 3 questions for free tier
        
        prompt = f"""
        Generate {num_questions} quiz questions about {topic}.
        Use multiple choice with 3 options each (saves tokens).
        
        Format as JSON:
        {{
            "questions": [
                {{
                    "question": "string (max 100 chars)",
                    "options": ["A", "B", "C"],
                    "correct_answer": "A",
                    "explanation": "string (max 50 chars)"
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            quiz = json.loads(response_text)
            return quiz
            
        except Exception as e:
            st.error(f"Error generating quiz: {str(e)}")
            return None
    
    def get_token_usage_estimate(self, text):
        """Estimate token usage for transparency"""
        # Rough estimate: ~4 characters per token
        return len(text) // 4

# Add a simple token counter utility
class TokenCounter:
    @staticmethod
    def count_tokens(text):
        """Simple token estimation"""
        return len(text.split()) * 1.3  # Rough estimate