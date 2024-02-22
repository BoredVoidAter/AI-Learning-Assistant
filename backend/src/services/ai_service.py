import openai
import os
import requests
import json
from typing import List, Dict, Optional
from flask import current_app

class AIService:
    """Service for AI-powered content generation and analysis"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_learning_path(self, subject: str, difficulty: str, goals: List[str]) -> Dict:
        """Generate a personalized learning path using AI"""
        try:
            if not self.openai_api_key:
                return self._fallback_learning_path(subject, difficulty)
            
            prompt = f"""
            Create a comprehensive learning path for the subject: {subject}
            Difficulty level: {difficulty}
            Learning goals: {', '.join(goals)}
            
            Please provide a structured learning path with:
            1. 5-8 main topics in logical order
            2. For each topic, include:
               - Title
               - Description (2-3 sentences)
               - Estimated study time in hours
               - 3-5 key learning resources (mix of videos, articles, exercises)
            
            Format the response as JSON with this structure:
            {{
                "title": "Learning Path Title",
                "description": "Overall description",
                "estimated_total_hours": 40,
                "topics": [
                    {{
                        "title": "Topic Title",
                        "description": "Topic description",
                        "estimated_hours": 5,
                        "resources": [
                            {{
                                "title": "Resource Title",
                                "type": "video|article|exercise|book",
                                "description": "Resource description",
                                "estimated_minutes": 30
                            }}
                        ]
                    }}
                ]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Provide structured, practical learning paths."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            current_app.logger.error(f"AI learning path generation failed: {str(e)}")
            return self._fallback_learning_path(subject, difficulty)
    
    def generate_quiz_questions(self, topic: str, difficulty: str, count: int = 5) -> List[Dict]:
        """Generate quiz questions for a topic"""
        try:
            if not self.openai_api_key:
                return self._fallback_quiz_questions(topic, difficulty, count)
            
            prompt = f"""
            Generate {count} quiz questions about: {topic}
            Difficulty level: {difficulty}
            
            Create a mix of question types:
            - Multiple choice (60%)
            - True/False (20%)
            - Short answer (20%)
            
            For each question, provide:
            - Question text
            - Question type
            - Correct answer
            - For multiple choice: 4 options including the correct one
            - Brief explanation of the correct answer
            
            Format as JSON array:
            [
                {{
                    "question_text": "Question here?",
                    "question_type": "multiple_choice|true_false|short_answer",
                    "correct_answer": "Correct answer",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "explanation": "Why this is correct"
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating assessment questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            current_app.logger.error(f"AI quiz generation failed: {str(e)}")
            return self._fallback_quiz_questions(topic, difficulty, count)
    
    def summarize_content(self, content: str, max_length: int = 200) -> str:
        """Summarize long content using AI"""
        try:
            if not self.openai_api_key or len(content) < 100:
                return content[:max_length] + "..." if len(content) > max_length else content
            
            prompt = f"""
            Summarize the following content in approximately {max_length} characters.
            Focus on the key points and main ideas:
            
            {content}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a skilled content summarizer. Create concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            current_app.logger.error(f"AI summarization failed: {str(e)}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def answer_question(self, question: str, context: str = "") -> str:
        """Answer a user question using AI"""
        try:
            if not self.openai_api_key:
                return "I'm sorry, but AI question answering is not available at the moment. Please try again later."
            
            system_prompt = "You are a helpful learning assistant. Provide clear, accurate, and educational answers."
            
            if context:
                user_prompt = f"Context: {context}\n\nQuestion: {question}"
            else:
                user_prompt = question
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            current_app.logger.error(f"AI question answering failed: {str(e)}")
            return "I'm sorry, but I couldn't process your question at the moment. Please try again later."
    
    def generate_study_recommendations(self, user_progress: Dict, learning_style: str) -> List[Dict]:
        """Generate personalized study recommendations"""
        try:
            if not self.openai_api_key:
                return self._fallback_recommendations(learning_style)
            
            prompt = f"""
            Based on the following user learning data, provide 5 personalized study recommendations:
            
            Learning style: {learning_style}
            Progress data: {json.dumps(user_progress)}
            
            Consider:
            - Areas where the user is struggling
            - Learning style preferences
            - Time management
            - Motivation techniques
            
            Format as JSON array:
            [
                {{
                    "title": "Recommendation title",
                    "description": "Detailed recommendation",
                    "priority": "high|medium|low",
                    "estimated_time": "Time needed",
                    "category": "study_technique|time_management|content_review|motivation"
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert learning coach providing personalized study advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            current_app.logger.error(f"AI recommendations failed: {str(e)}")
            return self._fallback_recommendations(learning_style)
    
    def generate_study_recommendations(self, user_progress: Dict, learning_style: str) -> List[Dict]:
        """Generate personalized study recommendations"""
        try:
            if not self.openai_api_key:
                return self._fallback_recommendations(learning_style)
            
            prompt = f"""
            Based on the following user learning data, provide 5 personalized study recommendations:
            
            Learning style: {learning_style}
            Progress data: {json.dumps(user_progress)}
            
            Consider:
            - Areas where the user is struggling
            - Learning style preferences
            - Time management
            - Motivation techniques
            
            Format as JSON array:
            [
                {{
                    "title": "Recommendation title",
                    "description": "Detailed recommendation",
                    "priority": "high|medium|low",
                    "estimated_time": "Time needed",
                    "category": "study_technique|time_management|content_review|motivation"
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert learning coach providing personalized study advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            current_app.logger.error(f"AI recommendations failed: {str(e)}")
            return self._fallback_recommendations(learning_style)

    def generate_article(self, topic: str, length: int = 500) -> str: