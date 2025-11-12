"""
Interviewer Agent - Core interview logic.
Manages question flow, answer validation, and conversational interaction.
"""
from typing import List, Optional, Dict, Any
from ..models.schemas import (
    InterviewQuestion, 
    QuestionCategory, 
    InterviewAnswer,
    InterviewState
)
from ..services.gemini_service import GeminiService


class InterviewerAgent:
    """
    Agent responsible for conducting the interview.
    Asks questions, validates answers, and manages follow-ups.
    """
    
    # Define all 8 interview questions - EXACTLY as specified in requirements.md
    QUESTIONS: List[InterviewQuestion] = [
        InterviewQuestion(
            category=QuestionCategory.INTRODUCTION,
            question_text="Tell me something about yourself (Include your name, family background, educational background, and whether you are an earning member of the family.)",
            expected_coverage=[
                "name",
                "family background",
                "educational background",
                "earning member status"
            ]
        ),
        InterviewQuestion(
            category=QuestionCategory.MOTIVATION,
            question_text="What motivated you to pursue a career in this field?",
            expected_coverage=None
        ),
        InterviewQuestion(
            category=QuestionCategory.INDUSTRY_EXPERIENCE,
            question_text="How many internships or industrial training programs have you completed so far? (Please include the names, durations, and the departments where you were trained.)",
            expected_coverage=[
                "number of internships",
                "names of organizations",
                "durations",
                "departments"
            ]
        ),
        InterviewQuestion(
            category=QuestionCategory.LEARNINGS,
            question_text="Tell me five things you have learned from the internships",
            expected_coverage=None
        ),
        InterviewQuestion(
            category=QuestionCategory.STRENGTHS_WEAKNESSES,
            question_text="Tell me two positive qualities about yourself and two areas where you think you need improvement.",
            expected_coverage=None
        ),
        InterviewQuestion(
            category=QuestionCategory.FUTURE_VISION,
            question_text="Where do you see yourself in five years?",
            expected_coverage=None
        ),
        InterviewQuestion(
            category=QuestionCategory.UNIQUE_VALUE,
            question_text="Give me a strong reason why I should hire you and how you are different from other candidates.",
            expected_coverage=None
        ),
        InterviewQuestion(
            category=QuestionCategory.AVAILABILITY,
            question_text="Are you available to start work immediately, or do you need time to complete other commitments?",
            expected_coverage=None
        )
    ]
    
    def __init__(self, gemini_service: GeminiService):
        """
        Initialize interviewer agent with Gemini service.
        
        Args:
            gemini_service: Initialized GeminiService for LLM interactions
        """
        self.gemini = gemini_service
        self.max_follow_ups = 2  # Maximum follow-up attempts per question
    
    def get_current_question(self, state: InterviewState) -> Optional[InterviewQuestion]:
        """
        Get the current question based on interview state.
        
        Args:
            state: Current interview state
            
        Returns:
            InterviewQuestion if available, None if interview is complete
        """
        if state.current_question_index >= len(self.QUESTIONS):
            return None
        return self.QUESTIONS[state.current_question_index]
    
    def get_greeting(self) -> str:
        """
        Get the initial greeting and introduction message for the interview.
        Bot introduces itself before starting the interview.
        
        Returns:
            Greeting string with bot introduction
        """
        return (
            "Hello! I am your AI interview assistant from VocalHire. "
            "I'm here to help you practice your interview skills in a supportive environment. "
            "I will ask you a series of questions commonly asked in job interviews. "
            "Please take your time to answer each question thoughtfully. "
            "If I feel your answer needs more detail, I may ask follow-up questions. "
            "This is a practice session, so there's no pressure - just be yourself and do your best. "
            "Are you ready? Let's begin with the first question."
        )
    
    async def validate_and_respond(
        self, 
        state: InterviewState, 
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Validate user's answer and determine next action.
        
        Args:
            state: Current interview state
            user_answer: User's answer text
            
        Returns:
            Dict with 'action' ('next_question', 'follow_up', or 'complete'),
            'message', and updated state
        """
        current_question = self.get_current_question(state)
        
        if not current_question:
            return {
                "action": "complete",
                "message": "Thank you for completing all the questions!",
                "state": state
            }
        
        # Get existing answer record if this is a follow-up
        existing_answer = self._get_or_create_answer(state, current_question, user_answer)
        
        # Validate answer completeness using Gemini
        validation = await self.gemini.validate_answer_completeness(
            question=current_question.question_text,
            answer=existing_answer.answer_text,
            expected_coverage=current_question.expected_coverage
        )
        
        # Update answer record
        existing_answer.is_complete = validation.get("is_complete", True)
        
        # Decide on next action
        if existing_answer.is_complete or existing_answer.follow_up_count >= self.max_follow_ups:
            # Move to next question
            state.current_question_index += 1
            next_question = self.get_current_question(state)
            
            if next_question:
                return {
                    "action": "next_question",
                    "message": next_question.question_text,
                    "state": state,
                    "question_category": next_question.category
                }
            else:
                # All questions completed
                state.is_completed = True
                return {
                    "action": "complete",
                    "message": "Thank you for completing all the questions! I'm now preparing your feedback.",
                    "state": state
                }
        else:
            # Ask follow-up question
            existing_answer.follow_up_count += 1
            follow_up = validation.get("follow_up", "Could you tell me more about that?")
            
            return {
                "action": "follow_up",
                "message": follow_up,
                "state": state,
                "question_category": current_question.category
            }
    
    def _get_or_create_answer(
        self, 
        state: InterviewState, 
        question: InterviewQuestion, 
        new_answer_text: str
    ) -> InterviewAnswer:
        """
        Get existing answer for current question or create new one.
        Appends to existing answer if this is a follow-up.
        
        Args:
            state: Current interview state
            question: Current question
            new_answer_text: New answer text from user
            
        Returns:
            InterviewAnswer object
        """
        # Find existing answer for this question category
        existing = None
        for answer in state.answers:
            if answer.question_category == question.category:
                existing = answer
                break
        
        if existing:
            # Append to existing answer
            existing.answer_text += " " + new_answer_text
            return existing
        else:
            # Create new answer record
            new_answer = InterviewAnswer(
                question_category=question.category,
                question_text=question.question_text,
                answer_text=new_answer_text,
                follow_up_count=0,
                is_complete=False
            )
            state.answers.append(new_answer)
            return new_answer
    
    def get_progress_status(self, state: InterviewState) -> str:
        """
        Get human-readable progress status.
        
        Args:
            state: Current interview state
            
        Returns:
            Progress status string
        """
        total = len(self.QUESTIONS)
        current = state.current_question_index
        return f"Question {current + 1} of {total}"

