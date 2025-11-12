"""
LangGraph State Machine for Interview Flow.
Defines the interview process as a state graph with transitions.
"""
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from ..models.schemas import InterviewState, InterviewAnswer, QuestionCategory
from ..services.gemini_service import GeminiService
from ..services.feedback_service import FeedbackService
from .interviewer_agent import InterviewerAgent
import operator


class InterviewGraphState(TypedDict):
    """
    State definition for the interview graph.
    This extends InterviewState for use in LangGraph.
    """
    session_id: str
    current_question_index: int
    answers: Annotated[Sequence[InterviewAnswer], operator.add]
    is_completed: bool
    current_message: str
    next_action: str  # 'ask_question', 'follow_up', 'generate_feedback', 'end'


class InterviewGraph:
    """
    LangGraph-based state machine for managing interview flow.
    Orchestrates the interview process through defined states and transitions.
    """
    
    def __init__(self, gemini_service: GeminiService, feedback_service: FeedbackService):
        """
        Initialize interview graph with required services.
        
        Args:
            gemini_service: Gemini LLM service
            feedback_service: Feedback generation service
        """
        self.gemini = gemini_service
        self.feedback_service = feedback_service
        self.interviewer = InterviewerAgent(gemini_service)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for interview flow.
        
        States:
        - start: Initial greeting
        - ask_question: Present next question
        - process_answer: Validate answer and determine next step
        - follow_up: Ask follow-up question
        - generate_feedback: Create final feedback
        - end: Complete interview
        
        Returns:
            Compiled StateGraph
        """
        # Create the state graph
        workflow = StateGraph(InterviewGraphState)
        
        # Add nodes (states)
        workflow.add_node("start", self._start_node)
        workflow.add_node("ask_question", self._ask_question_node)
        workflow.add_node("process_answer", self._process_answer_node)
        workflow.add_node("follow_up", self._follow_up_node)
        workflow.add_node("generate_feedback", self._generate_feedback_node)
        
        # Define entry point
        workflow.set_entry_point("start")
        
        # Add edges (transitions)
        workflow.add_edge("start", "ask_question")
        workflow.add_edge("ask_question", "process_answer")
        workflow.add_edge("follow_up", "process_answer")
        
        # Conditional edges from process_answer
        workflow.add_conditional_edges(
            "process_answer",
            self._route_after_processing,
            {
                "ask_question": "ask_question",
                "follow_up": "follow_up",
                "generate_feedback": "generate_feedback",
                "end": END
            }
        )
        
        workflow.add_edge("generate_feedback", END)
        
        # Compile the graph
        return workflow.compile()
    
    def _start_node(self, state: InterviewGraphState) -> InterviewGraphState:
        """
        Initial node - sends greeting message.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with greeting message
        """
        greeting = self.interviewer.get_greeting()
        state["current_message"] = greeting
        state["next_action"] = "ask_question"
        return state
    
    def _ask_question_node(self, state: InterviewGraphState) -> InterviewGraphState:
        """
        Ask the next interview question.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with current question
        """
        # Convert graph state to InterviewState for agent
        interview_state = self._to_interview_state(state)
        question = self.interviewer.get_current_question(interview_state)
        
        if question:
            state["current_message"] = question.question_text
            state["next_action"] = "process_answer"
        else:
            state["next_action"] = "generate_feedback"
        
        return state
    
    async def _process_answer_node(self, state: InterviewGraphState) -> InterviewGraphState:
        """
        Process user's answer and determine next action.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with next action determined
        """
        # This is a placeholder - actual processing happens in validate_and_respond
        # which is called from the WebSocket handler
        return state
    
    def _follow_up_node(self, state: InterviewGraphState) -> InterviewGraphState:
        """
        Ask a follow-up question to get more complete answer.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with follow-up question
        """
        # Follow-up message should already be set by validate_and_respond
        state["next_action"] = "process_answer"
        return state
    
    async def _generate_feedback_node(self, state: InterviewGraphState) -> InterviewGraphState:
        """
        Generate final interview feedback.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with feedback
        """
        interview_state = self._to_interview_state(state)
        
        # Generate feedback using feedback service
        feedback = await self.feedback_service.generate_feedback(
            session_id=state["session_id"],
            answers=list(state["answers"])
        )
        
        # Format feedback as a message
        feedback_message = self._format_feedback_message(feedback)
        state["current_message"] = feedback_message
        state["is_completed"] = True
        state["next_action"] = "end"
        
        return state
    
    def _route_after_processing(self, state: InterviewGraphState) -> str:
        """
        Determine which node to go to after processing an answer.
        
        Args:
            state: Current graph state
            
        Returns:
            Next node name
        """
        return state.get("next_action", "end")
    
    def _to_interview_state(self, graph_state: InterviewGraphState) -> InterviewState:
        """
        Convert graph state to InterviewState model.
        
        Args:
            graph_state: LangGraph state
            
        Returns:
            InterviewState model instance
        """
        return InterviewState(
            session_id=graph_state["session_id"],
            current_question_index=graph_state["current_question_index"],
            answers=list(graph_state.get("answers", [])),
            is_completed=graph_state["is_completed"]
        )
    
    def _format_feedback_message(self, feedback) -> str:
        """
        Format feedback object into a readable message.
        
        Args:
            feedback: InterviewFeedback object
            
        Returns:
            Formatted feedback string
        """
        message = f"""🎉 Interview Complete! Here's your feedback:

OVERALL ASSESSMENT:
{feedback.overall_assessment}

STRENGTHS:
"""
        for i, strength in enumerate(feedback.strengths, 1):
            message += f"{i}. {strength}\n"
        
        message += "\nAREAS FOR IMPROVEMENT:\n"
        for i, area in enumerate(feedback.areas_for_improvement, 1):
            message += f"{i}. {area}\n"
        
        message += "\nSPECIFIC SUGGESTIONS:\n"
        for i, suggestion in enumerate(feedback.specific_suggestions, 1):
            message += f"{i}. {suggestion}\n"
        
        message += f"\nENCOURAGEMENT:\n{feedback.encouragement}\n"
        
        return message

