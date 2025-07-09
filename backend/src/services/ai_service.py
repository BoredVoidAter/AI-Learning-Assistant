import google.generativeai as genai
import os
import json
from typing import List, Dict, Optional
from flask import current_app


class AIService:
    """Service for AI-powered content generation and analysis using Google Gemini"""

    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-pro")
        else:
            self.model = None

    def generate_learning_path(self, subject: str, difficulty: str, goals: List[str]) -> Dict:
        """Generate a personalized learning path using AI"""
        try:
            if not self.model:
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
            
            Respond only with valid JSON, no additional text.
            """

            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Clean up the response to ensure it's valid JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]

            return json.loads(content)

        except Exception as e:
            current_app.logger.error(f"AI learning path generation failed: {str(e)}")
            return self._fallback_learning_path(subject, difficulty)

    def generate_quiz_questions(self, topic: str, difficulty: str, count: int = 5) -> List[Dict]:
        """Generate quiz questions for a topic"""
        try:
            if not self.model:
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
            
            Respond only with valid JSON array, no additional text.
            """

            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Clean up the response to ensure it's valid JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]

            return json.loads(content)

        except Exception as e:
            current_app.logger.error(f"AI quiz generation failed: {str(e)}")
            return self._fallback_quiz_questions(topic, difficulty, count)

    def summarize_content(self, content: str, max_length: int = 200) -> str:
        """Summarize long content using AI"""
        try:
            if not self.model or len(content) < 100:
                return content[:max_length] + "..." if len(content) > max_length else content

            prompt = f"""
            Summarize the following content in approximately {max_length} characters.
            Focus on the key points and main ideas:
            
            {content}
            
            Provide only the summary, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            current_app.logger.error(f"AI summarization failed: {str(e)}")
            return content[:max_length] + "..." if len(content) > max_length else content

    def answer_question(self, question: str, context: str = "") -> str:
        """Answer a user question using AI"""
        try:
            if not self.model:
                return "I'm sorry, but AI question answering is not available at the moment. Please try again later."

            if context:
                prompt = (
                    f"Context: {context}nnQuestion: {question}nnProvide a clear, accurate, and educational answer."
                )
            else:
                prompt = f"Question: {question}nnProvide a clear, accurate, and educational answer."

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            current_app.logger.error(f"AI question answering failed: {str(e)}")
            return "I'm sorry, but I couldn't process your question at the moment. Please try again later."

    def generate_study_recommendations(self, user_progress: Dict, learning_style: str) -> List[Dict]:
        """Generate personalized study recommendations"""
        try:
            if not self.model:
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
            
            Respond only with valid JSON array, no additional text.
            """

            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Clean up the response to ensure it's valid JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]

            return json.loads(content)

        except Exception as e:
            current_app.logger.error(f"AI recommendations failed: {str(e)}")
            return self._fallback_recommendations(learning_style)

    def generate_article(self, topic: str, length: int = 500) -> str:
        """Generate an educational article on a topic"""
        try:
            if not self.model:
                return self._fallback_article(topic, length)

            prompt = f"""
            Write an educational article about: {topic}
            Target length: approximately {length} words
            
            The article should be:
            - Informative and well-structured
            - Suitable for learners
            - Include key concepts and practical examples
            - Written in clear, accessible language
            
            Provide only the article content, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            current_app.logger.error(f"AI article generation failed: {str(e)}")
            return self._fallback_article(topic, length)

    # Fallback methods for when AI is not available
    def _fallback_learning_path(self, subject: str, difficulty: str) -> Dict:
        """Fallback learning path when AI is not available"""
        return {
            "title": f"{subject} Learning Path ({difficulty})",
            "description": f"A structured learning path for {subject} at {difficulty} level. This is a basic template that can be customized.",
            "estimated_total_hours": 30,
            "topics": [
                {
                    "title": f"Introduction to {subject}",
                    "description": f"Get started with the fundamentals of {subject}. Learn basic concepts and terminology.",
                    "estimated_hours": 5,
                    "resources": [
                        {
                            "title": f"What is {subject}?",
                            "type": "article",
                            "description": f"An introductory article covering the basics of {subject}",
                            "estimated_minutes": 30,
                        },
                        {
                            "title": f"{subject} Fundamentals",
                            "type": "video",
                            "description": f"Video tutorial covering core concepts",
                            "estimated_minutes": 45,
                        },
                    ],
                },
                {
                    "title": f"Core Concepts in {subject}",
                    "description": f"Dive deeper into the essential concepts and principles of {subject}.",
                    "estimated_hours": 8,
                    "resources": [
                        {
                            "title": f"Key Principles of {subject}",
                            "type": "article",
                            "description": f"Detailed explanation of important principles",
                            "estimated_minutes": 60,
                        },
                        {
                            "title": f"Hands-on {subject} Practice",
                            "type": "exercise",
                            "description": f"Practical exercises to reinforce learning",
                            "estimated_minutes": 90,
                        },
                    ],
                },
                {
                    "title": f"Advanced {subject} Topics",
                    "description": f"Explore advanced concepts and real-world applications of {subject}.",
                    "estimated_hours": 10,
                    "resources": [
                        {
                            "title": f"Advanced {subject} Techniques",
                            "type": "article",
                            "description": f"In-depth coverage of advanced topics",
                            "estimated_minutes": 75,
                        },
                        {
                            "title": f"Real-world {subject} Applications",
                            "type": "video",
                            "description": f"Case studies and practical applications",
                            "estimated_minutes": 60,
                        },
                    ],
                },
                {
                    "title": f"Practice and Assessment",
                    "description": f"Test your knowledge and apply what you've learned about {subject}.",
                    "estimated_hours": 7,
                    "resources": [
                        {
                            "title": f"{subject} Practice Problems",
                            "type": "exercise",
                            "description": f"Comprehensive practice exercises",
                            "estimated_minutes": 120,
                        },
                        {
                            "title": f"{subject} Assessment Quiz",
                            "type": "exercise",
                            "description": f"Test your understanding with this quiz",
                            "estimated_minutes": 45,
                        },
                    ],
                },
            ],
        }

    def _fallback_quiz_questions(self, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Fallback quiz questions when AI is not available"""
        questions = []

        for i in range(count):
            if i % 3 == 0:  # Multiple choice
                questions.append(
                    {
                        "question_text": f"What is an important concept in {topic}?",
                        "question_type": "multiple_choice",
                        "correct_answer": f"Key concept of {topic}",
                        "options": [
                            f"Key concept of {topic}",
                            f"Unrelated concept A",
                            f"Unrelated concept B",
                            f"Unrelated concept C",
                        ],
                        "explanation": f"This is a fundamental concept in {topic} that students should understand.",
                    }
                )
            elif i % 3 == 1:  # True/False
                questions.append(
                    {
                        "question_text": f"{topic} is an important subject to study.",
                        "question_type": "true_false",
                        "correct_answer": "True",
                        "options": ["True", "False"],
                        "explanation": f"Yes, {topic} is indeed an important subject with many practical applications.",
                    }
                )
            else:  # Short answer
                questions.append(
                    {
                        "question_text": f"Explain one key benefit of studying {topic}.",
                        "question_type": "short_answer",
                        "correct_answer": f"Studying {topic} provides valuable knowledge and skills",
                        "options": [],
                        "explanation": f"There are many benefits to studying {topic}, including practical applications and career opportunities.",
                    }
                )

        return questions

    def _fallback_recommendations(self, learning_style: str) -> List[Dict]:
        """Fallback recommendations when AI is not available"""
        return [
            {
                "title": "Set a Regular Study Schedule",
                "description": "Establish a consistent daily study routine to build good learning habits and maintain momentum.",
                "priority": "high",
                "estimated_time": "15 minutes to plan",
                "category": "time_management",
            },
            {
                "title": "Use Active Learning Techniques",
                "description": f"Based on your {learning_style} learning style, try techniques like summarizing, teaching others, or creating mind maps.",
                "priority": "high",
                "estimated_time": "Ongoing",
                "category": "study_technique",
            },
            {
                "title": "Take Regular Breaks",
                "description": "Use the Pomodoro Technique: study for 25 minutes, then take a 5-minute break to maintain focus and prevent burnout.",
                "priority": "medium",
                "estimated_time": "Built into study sessions",
                "category": "time_management",
            },
            {
                "title": "Review Previous Material",
                "description": "Spend 10-15 minutes each day reviewing previously learned material to strengthen long-term retention.",
                "priority": "medium",
                "estimated_time": "10-15 minutes daily",
                "category": "content_review",
            },
            {
                "title": "Set Learning Goals",
                "description": "Define specific, measurable learning objectives for each study session to stay motivated and track progress.",
                "priority": "medium",
                "estimated_time": "5 minutes before each session",
                "category": "motivation",
            },
        ]

    def _fallback_article(self, topic: str, length: int) -> str:
        """Fallback article when AI is not available"""
        return f"""# Introduction to {topic}

{topic} is an important subject that offers valuable knowledge and skills for learners. Understanding the fundamentals of {topic} can provide numerous benefits and open up new opportunities for personal and professional growth.

## Key Concepts

When studying {topic}, it's essential to focus on the core concepts that form the foundation of the subject. These fundamental principles serve as building blocks for more advanced topics and practical applications.

## Learning Approach

To effectively learn {topic}, consider using a structured approach that combines theoretical understanding with practical application. This balanced method helps reinforce learning and makes the subject more engaging and memorable.

## Practical Applications

{topic} has many real-world applications that make it relevant and useful in various contexts. Understanding these applications can help motivate learning and provide context for theoretical concepts.

## Conclusion

Studying {topic} is a worthwhile investment in your education and personal development. With consistent effort and the right learning strategies, you can master this subject and apply your knowledge effectively.

*Note: This is a basic template article. For more detailed and personalized content, consider setting up the Gemini API for AI-powered content generation.*"""
