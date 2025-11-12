"""
Feedback generation service.
Analyzes interview responses and generates comprehensive feedback.
"""
from typing import List
from ..models.schemas import InterviewAnswer, InterviewFeedback, FeedbackSection
from .gemini_service import GeminiService
from datetime import datetime
import json


class FeedbackService:
    """Service for generating interview feedback using Gemini"""
    
    def __init__(self, gemini_service: GeminiService):
        """
        Initialize feedback service with Gemini service.
        
        Args:
            gemini_service: Initialized GeminiService instance
        """
        self.gemini = gemini_service
    
    async def generate_feedback(
        self, 
        session_id: str, 
        answers: List[InterviewAnswer]
    ) -> InterviewFeedback:
        """
        Generate comprehensive feedback based on all interview answers.
        
        Args:
            session_id: ID of the interview session
            answers: List of all answers provided during interview
            
        Returns:
            InterviewFeedback object with complete analysis
        """
        # Prepare the interview transcript for analysis
        transcript = self._prepare_transcript(answers)
        
        # Generate comprehensive feedback using Gemini
        feedback_prompt = f"""You are an experienced interviewer providing constructive feedback to a vocational training student in India who just completed a mock interview.

INTERVIEW TRANSCRIPT:
{transcript}

Generate comprehensive, encouraging feedback following these guidelines:

1. OVERALL ASSESSMENT: A brief 2-3 sentence summary of their performance
2. STRENGTHS: Identify 3-4 specific positive aspects you observed
3. AREAS FOR IMPROVEMENT: Point out 2-3 areas where they can improve (be constructive and specific)
4. SPECIFIC SUGGESTIONS: Provide 3-4 actionable tips they can implement
5. ENCOURAGEMENT: End with 1-2 sentences of genuine encouragement

IMPORTANT:
- Be supportive and positive in tone
- Acknowledge their effort
- Make suggestions specific and actionable
- Consider the context of Indian vocational training students
- Focus on practical, implementable advice
- Keep language simple and clear

Respond in this exact JSON format:
{{
    "overall_assessment": "Your overall assessment here",
    "strengths": ["strength1", "strength2", "strength3"],
    "areas_for_improvement": ["area1", "area2", "area3"],
    "specific_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
    "encouragement": "Your encouraging message here"
}}
"""
        
        try:
            response = await self.gemini.generate_chat_response(
                system_prompt="You are a supportive interview coach.",
                user_message=feedback_prompt
            )
            
            # Parse the JSON response with cleaning
            import re
            
            # Clean the response - remove markdown code blocks if present
            clean_response = response.strip()
            clean_response = re.sub(r'^```(?:json)?\s*\n?', '', clean_response)
            clean_response = re.sub(r'\n?```\s*$', '', clean_response)
            clean_response = clean_response.strip()
            
            feedback_data = json.loads(clean_response)
            
            # Create category-specific feedback
            category_feedback = await self._generate_category_feedback(answers)
            
            # Build the feedback object
            feedback = InterviewFeedback(
                session_id=session_id,
                overall_assessment=feedback_data.get("overall_assessment", ""),
                strengths=feedback_data.get("strengths", []),
                areas_for_improvement=feedback_data.get("areas_for_improvement", []),
                specific_suggestions=feedback_data.get("specific_suggestions", []),
                encouragement=feedback_data.get("encouragement", ""),
                category_feedback=category_feedback,
                generated_at=datetime.now()
            )
            
            return feedback
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            print(f"Raw response: {response if 'response' in locals() else 'No response'}")
            # Return a basic fallback feedback
            return self._generate_fallback_feedback(session_id, answers)
    
    def _prepare_transcript(self, answers: List[InterviewAnswer]) -> str:
        """
        Format answers into a readable transcript for analysis.
        
        Args:
            answers: List of interview answers
            
        Returns:
            Formatted transcript string
        """
        transcript = ""
        for i, answer in enumerate(answers, 1):
            transcript += f"\nQ{i} ({answer.question_category.value.replace('_', ' ').title()}):\n"
            transcript += f"{answer.question_text}\n\n"
            transcript += f"Candidate's Answer:\n{answer.answer_text}\n"
            transcript += "-" * 80 + "\n"
        
        return transcript
    
    async def _generate_category_feedback(
        self, 
        answers: List[InterviewAnswer]
    ) -> List[FeedbackSection]:
        """
        Generate specific feedback for each question category.
        
        Args:
            answers: List of interview answers
            
        Returns:
            List of FeedbackSection objects
        """
        category_feedback = []
        
        for answer in answers:
            # Create a brief feedback for each category
            section = FeedbackSection(
                title=answer.question_category.value.replace('_', ' ').title(),
                content=f"You addressed this question with {'good detail' if len(answer.answer_text) > 100 else 'a brief response'}.",
                score=None  # Could add scoring logic here
            )
            category_feedback.append(section)
        
        return category_feedback
    
    def _generate_fallback_feedback(
        self, 
        session_id: str, 
        answers: List[InterviewAnswer]
    ) -> InterviewFeedback:
        """
        Generate basic fallback feedback if LLM fails.
        
        Args:
            session_id: Session ID
            answers: List of answers
            
        Returns:
            Basic InterviewFeedback object
        """
        return InterviewFeedback(
            session_id=session_id,
            overall_assessment="Thank you for completing the mock interview. You showed good effort in answering all questions.",
            strengths=[
                "Completed all interview questions",
                "Showed willingness to participate",
                "Provided thoughtful responses"
            ],
            areas_for_improvement=[
                "Try to provide more detailed responses",
                "Include specific examples when possible",
                "Structure your answers clearly"
            ],
            specific_suggestions=[
                "Practice the STAR method (Situation, Task, Action, Result) for behavioral questions",
                "Prepare specific examples from your experience beforehand",
                "Take a moment to organize your thoughts before answering"
            ],
            encouragement="Keep practicing and you will continue to improve. Every interview is a learning opportunity!",
            category_feedback=[],
            generated_at=datetime.now()
        )

