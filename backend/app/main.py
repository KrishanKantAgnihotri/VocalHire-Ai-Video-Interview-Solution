"""
VocalHire FastAPI Backend - Main Application Entry Point.
Provides WebSocket endpoint for real-time interview interaction.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import uuid
from datetime import datetime
from typing import Dict
import os
from dotenv import load_dotenv

from .models.schemas import (
    Message, 
    MessageType, 
    InterviewState, 
    SessionData
)
from .services.gemini_service import GeminiService
from .services.feedback_service import FeedbackService
from .agents.interviewer_agent import InterviewerAgent
from .storage.file_storage import FileStorage

# Load environment variables
load_dotenv()

# Global services
gemini_service = None
feedback_service = None
storage = None
interviewer = None

# Active sessions (in-memory tracking)
active_sessions: Dict[str, InterviewState] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Initializes services on startup and cleans up on shutdown.
    """
    global gemini_service, feedback_service, storage, interviewer
    
    # Startup: Initialize services
    print("Initializing VocalHire services...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    data_dir = os.getenv("DATA_DIR", "./data")
    
    gemini_service = GeminiService(api_key=api_key)
    feedback_service = FeedbackService(gemini_service)
    storage = FileStorage(data_dir=data_dir)
    interviewer = InterviewerAgent(gemini_service)
    
    print("Services initialized successfully")
    
    yield
    
    # Shutdown: Cleanup
    print("Shutting down VocalHire services...")


# Create FastAPI app
app = FastAPI(
    title="VocalHire API",
    description="Voice-based Mock Interview Bot Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "VocalHire API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "gemini": gemini_service is not None,
            "storage": storage is not None,
            "interviewer": interviewer is not None
        }
    }


@app.websocket("/ws/interview")
async def interview_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time interview interaction.
    
    Flow:
    1. Client connects and receives greeting
    2. Bot asks questions one by one
    3. Client sends voice transcribed answers
    4. Bot validates and either asks follow-up or moves to next question
    5. After all questions, bot generates and sends feedback
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    print(f"New interview session started: {session_id}")
    
    try:
        # Initialize new interview session
        interview_state = InterviewState(
            session_id=session_id,
            current_question_index=0,
            answers=[],
            is_completed=False,
            started_at=datetime.now()
        )
        active_sessions[session_id] = interview_state
        
        # Save initial session
        session_data = SessionData(
            session_id=session_id,
            state=interview_state,
            feedback=None
        )
        await storage.save_session(session_data)
        
        # Send session start message
        start_message = Message(
            type=MessageType.SESSION_START,
            content=session_id,
            session_id=session_id,
            metadata={"message": "Session initialized"}
        )
        await websocket.send_json(start_message.model_dump(mode='json'))
        
        # Send greeting
        greeting = interviewer.get_greeting()
        greeting_message = Message(
            type=MessageType.QUESTION,
            content=greeting,
            session_id=session_id,
            metadata={"is_greeting": True}
        )
        await websocket.send_json(greeting_message.model_dump(mode='json'))
        
        # Send first question
        first_question = interviewer.get_current_question(interview_state)
        if first_question:
            question_message = Message(
                type=MessageType.QUESTION,
                content=first_question.question_text,
                session_id=session_id,
                metadata={
                    "category": first_question.category.value,
                    "progress": interviewer.get_progress_status(interview_state)
                }
            )
            await websocket.send_json(question_message.model_dump(mode='json'))
        
        # Main conversation loop
        while True:
            # Receive answer from client
            data = await websocket.receive_text()
            client_message = json.loads(data)
            
            # Extract answer text
            if isinstance(client_message, dict):
                answer_text = client_message.get("content", "")
                msg_type = client_message.get("type", MessageType.ANSWER)
            else:
                answer_text = client_message
                msg_type = MessageType.ANSWER
            
            # Validate answer text
            if not answer_text or not answer_text.strip():
                # Send error for empty answer
                error_message = Message(
                    type=MessageType.ERROR,
                    content="I didn't catch that. Could you please repeat your answer?",
                    session_id=session_id
                )
                await websocket.send_json(error_message.model_dump(mode='json'))
                continue
            
            # Limit answer length to prevent abuse and excessive API costs
            MAX_ANSWER_LENGTH = 2000
            if len(answer_text) > MAX_ANSWER_LENGTH:
                error_message = Message(
                    type=MessageType.ERROR,
                    content=f"Your answer is too long. Please keep it under {MAX_ANSWER_LENGTH} characters.",
                    session_id=session_id
                )
                await websocket.send_json(error_message.model_dump(mode='json'))
                continue
            
            print(f"Received answer for session {session_id}: {answer_text[:50]}...")
            
            # Validate answer and get next action
            result = await interviewer.validate_and_respond(interview_state, answer_text)
            
            action = result["action"]
            message_text = result["message"]
            interview_state = result["state"]
            
            # Update session in memory
            active_sessions[session_id] = interview_state
            
            # Save updated session
            session_data.state = interview_state
            await storage.save_session(session_data)
            
            if action == "next_question":
                # Send next question
                response = Message(
                    type=MessageType.QUESTION,
                    content=message_text,
                    session_id=session_id,
                    metadata={
                        "category": result.get("question_category", "").value if result.get("question_category") else "",
                        "progress": interviewer.get_progress_status(interview_state)
                    }
                )
                await websocket.send_json(response.model_dump(mode='json'))
                
            elif action == "follow_up":
                # Send follow-up question
                response = Message(
                    type=MessageType.QUESTION,
                    content=message_text,
                    session_id=session_id,
                    metadata={
                        "is_follow_up": True,
                        "category": result.get("question_category", "").value if result.get("question_category") else "",
                        "progress": interviewer.get_progress_status(interview_state)
                    }
                )
                await websocket.send_json(response.model_dump(mode='json'))
                
            elif action == "complete":
                # Generate feedback
                print(f"Generating feedback for session {session_id}")
                
                # Send status update
                status_message = Message(
                    type=MessageType.STATUS,
                    content="Generating your personalized feedback...",
                    session_id=session_id
                )
                await websocket.send_json(status_message.model_dump(mode='json'))
                
                # Generate comprehensive feedback
                feedback = await feedback_service.generate_feedback(
                    session_id=session_id,
                    answers=interview_state.answers
                )
                
                # Save feedback with session
                interview_state.is_completed = True
                interview_state.completed_at = datetime.now()
                session_data.state = interview_state
                session_data.feedback = feedback
                await storage.save_session(session_data)
                
                # Format and send feedback
                feedback_text = _format_feedback(feedback)
                feedback_message = Message(
                    type=MessageType.FEEDBACK,
                    content=feedback_text,
                    session_id=session_id,
                    metadata={"feedback": feedback.model_dump(mode='json')}
                )
                await websocket.send_json(feedback_message.model_dump(mode='json'))
                
                # Send session end message
                end_message = Message(
                    type=MessageType.SESSION_END,
                    content="Interview completed successfully!",
                    session_id=session_id
                )
                await websocket.send_json(end_message.model_dump(mode='json'))
                
                print(f"Interview session {session_id} completed")
                break
    
    except WebSocketDisconnect:
        print(f"🔌 Client disconnected from session {session_id}")
        if session_id in active_sessions:
            del active_sessions[session_id]
    
    except Exception as e:
        print(f"❌ Error in session {session_id}: {str(e)}")
        try:
            error_message = Message(
                type=MessageType.ERROR,
                content=f"An error occurred: {str(e)}",
                session_id=session_id
            )
            await websocket.send_json(error_message.model_dump(mode='json'))
        except:
            pass
    
    finally:
        # Cleanup
        if session_id in active_sessions:
            del active_sessions[session_id]


def _format_feedback(feedback) -> str:
    """
    Format feedback object into a readable text message.
    
    Args:
        feedback: InterviewFeedback object
        
    Returns:
        Formatted feedback string
    """
    message = f""" Interview Complete! Here's Your Personalized Feedback:

OVERALL ASSESSMENT:
{feedback.overall_assessment}

 YOUR STRENGTHS:
"""
    for i, strength in enumerate(feedback.strengths, 1):
        message += f"  {i}. {strength}\n"
    
    message += "\n AREAS FOR IMPROVEMENT:\n"
    for i, area in enumerate(feedback.areas_for_improvement, 1):
        message += f"  {i}. {area}\n"
    
    message += "\n SPECIFIC SUGGESTIONS:\n"
    for i, suggestion in enumerate(feedback.specific_suggestions, 1):
        message += f"  {i}. {suggestion}\n"
    
    message += f"\n WORDS OF ENCOURAGEMENT:\n{feedback.encouragement}\n"
    message += "\n---\nThank you for using VocalHire! Keep practicing and you'll excel in your next interview! 🚀"
    
    return message


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve a specific interview session.
    
    Args:
        session_id: ID of the session to retrieve
        
    Returns:
        Session data or error
    """
    session_data = await storage.load_session(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data.model_dump(mode='json')


@app.get("/api/sessions")
async def list_sessions():
    """
    List all interview sessions.
    
    Returns:
        List of session IDs
    """
    session_ids = await storage.list_sessions()
    return {"sessions": session_ids, "count": len(session_ids)}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting VocalHire server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

