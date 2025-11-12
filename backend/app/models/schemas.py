"""
Pydantic models for VocalHire interview bot.
Defines data structures for interview sessions, messages, and feedback.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Types of messages exchanged between client and server"""
    QUESTION = "question"  # Bot asking a question
    ANSWER = "answer"  # User providing an answer
    FEEDBACK = "feedback"  # Final feedback from bot
    ERROR = "error"  # Error message
    STATUS = "status"  # Status update
    SESSION_START = "session_start"  # Session initialization
    SESSION_END = "session_end"  # Session completion


class QuestionCategory(str, Enum):
    """Interview question categories matching requirements"""
    INTRODUCTION = "introduction"
    MOTIVATION = "motivation"
    INDUSTRY_EXPERIENCE = "industry_experience"
    LEARNINGS = "learnings"
    STRENGTHS_WEAKNESSES = "strengths_weaknesses"
    FUTURE_VISION = "future_vision"
    UNIQUE_VALUE = "unique_value"
    AVAILABILITY = "availability"


class Message(BaseModel):
    """WebSocket message structure"""
    type: MessageType
    content: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class InterviewQuestion(BaseModel):
    """Structure for an interview question"""
    category: QuestionCategory
    question_text: str
    expected_coverage: Optional[List[str]] = None
    follow_up_prompts: Optional[List[str]] = None


class InterviewAnswer(BaseModel):
    """Structure for storing user's answer"""
    question_category: QuestionCategory
    question_text: str
    answer_text: str
    follow_up_count: int = 0
    is_complete: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class InterviewState(BaseModel):
    """Current state of the interview session"""
    session_id: str
    current_question_index: int = 0
    answers: List[InterviewAnswer] = []
    is_completed: bool = False
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class FeedbackSection(BaseModel):
    """Individual section of feedback"""
    title: str
    content: str
    score: Optional[int] = None  # 1-10 scale


class InterviewFeedback(BaseModel):
    """Comprehensive feedback after interview completion"""
    session_id: str
    overall_assessment: str
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_suggestions: List[str]
    encouragement: str
    category_feedback: List[FeedbackSection] = []
    generated_at: datetime = Field(default_factory=datetime.now)


class SessionData(BaseModel):
    """Complete session data for storage"""
    session_id: str
    state: InterviewState
    feedback: Optional[InterviewFeedback] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

