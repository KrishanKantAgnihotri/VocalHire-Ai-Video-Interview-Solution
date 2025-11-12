# VocalHire - Voice-Based Mock Interview Bot

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://reactjs.org/)
[![Watch the video]()](https://www.loom.com/share/03dc95bf3da0468483a757dd9a792150)


VocalHire is an AI-powered voice-based mock interview platform designed to help students from vocational training centres in India practice their interview skills. The system provides real-time, conversational interaction that simulates a genuine human interviewer experience.

##  Features

- **Real-time Voice Interaction**: Seamless conversation flow using Web Speech API
- **Agentic Architecture**: Intelligent interview agent powered by LangGraph
- **8 Comprehensive Questions**: Covers introduction, motivation, experience, and more
- **Personalized Feedback**: Detailed, actionable insights using Google Gemini
- **Modern UI**: Clean, intuitive interface with visual feedback
- **File-based Storage**: Simple persistence for interview sessions

##  Architecture

```
┌─────────────────┐         WebSocket          ┌─────────────────┐
│                 │◄──────────────────────────►│                 │
│  React Frontend │    Real-time Messages      │ FastAPI Backend │
│  (Web Speech)   │                            │  (LangGraph)    │
│                 │                            │                 │
└─────────────────┘                            └─────────────────┘
        │                                              │
        │                                              │
        ▼                                              ▼
  Browser APIs                              ┌──────────────────┐
  - SpeechRecognition                       │  Gemini LLM      │
  - SpeechSynthesis                         │  (Google AI)     │
                                            └──────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────┐
                                            │  File Storage    │
                                            │  (JSON Files)    │
                                            └──────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI - High-performance async web framework
- LangChain - LLM orchestration framework
- LangGraph - State machine for agentic architecture
- Google Gemini - Language model for validation and feedback
- Python 3.9+ - Programming language

**Frontend:**
- React 18 - UI framework
- Vite - Build tool and dev server
- Web Speech API - Browser-based STT/TTS
- WebSocket - Real-time communication

##  Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
- Modern browser with Web Speech API support (Chrome, Edge recommended)

##  Installation & Setup

### 1. Clone the Repository

```bash

cd VocalHire
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file

# Edit .env and add your Google API key
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

##  Running the Application

### Start Backend Server

```bash
# From backend directory with activated virtual environment
cd backend
python -m app.main

# Server will start on http://localhost:8000
```

### Start Frontend Development Server

```bash
# From frontend directory (in a new terminal)
cd frontend
npm run dev

# Frontend will start on http://localhost:3000
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

**Important:** Make sure to allow microphone access when prompted by your browser.

##  How to Use

1. **Start Interview**: Click "Start Interview Practice" button
2. **Listen**: The bot will greet you and ask the first question (audio)
3. **Respond**: Click "Start Speaking" and answer the question
4. **Continue**: The bot validates your answer and either:
   - Asks a follow-up if more detail is needed
   - Moves to the next question
5. **Receive Feedback**: After all 8 questions, receive comprehensive feedback
6. **Review**: Read detailed feedback on strengths and areas for improvement

##  Interview Questions Covered

1. **Introduction**: Tell me about yourself (name, family, education, employment)
2. **Motivation**: What motivated you to pursue this career?
3. **Industry Experience**: Internships and training programs completed
4. **Learnings**: Five things learned from internships
5. **Strengths & Weaknesses**: Two positive qualities and two areas for improvement
6. **Future Vision**: Where do you see yourself in five years?
7. **Unique Value**: Why should we hire you?
8. **Availability**: Can you start immediately?

##  Project Structure

```
VocalHire/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── agents/
│   │   │   ├── interview_graph.py  # LangGraph state machine
│   │   │   └── interviewer_agent.py # Interview logic
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── services/
│   │   │   ├── gemini_service.py   # LLM integration
│   │   │   └── feedback_service.py # Feedback generation
│   │   └── storage/
│   │       └── file_storage.py     # JSON-based storage
│   ├── data/                       # Interview sessions stored here
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InterviewSession.jsx  # Main interview UI
│   │   │   ├── VoiceControls.jsx     # Mic controls
│   │   │   └── FeedbackDisplay.jsx   # Feedback modal
│   │   ├── services/
│   │   │   ├── websocket.js          # WebSocket client
│   │   │   └── speechService.js      # Web Speech API wrapper
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
├── TECHNICAL_DOCUMENTATION.md
└── README.md
```

##  API Endpoints

### REST Endpoints

- `GET /` - Health check
- `GET /api/health` - Service health status
- `GET /api/sessions` - List all interview sessions
- `GET /api/sessions/{session_id}` - Get specific session data

### WebSocket Endpoint

- `WS /ws/interview` - Real-time interview communication

**Message Types:**
- `session_start` - Session initialization
- `question` - Bot asking a question
- `answer` - User providing an answer
- `feedback` - Final interview feedback
- `status` - Status updates
- `error` - Error messages
- `session_end` - Session completion

##  Testing

### Manual Testing

1. Start both backend and frontend servers
2. Open browser to http://localhost:3000
3. Click "Start Interview Practice"
4. Allow microphone access
5. Complete the interview flow
6. Verify feedback generation

### Backend Testing

```bash
cd backend
# Test API health
curl http://localhost:8000/api/health
```

##  Troubleshooting

### Common Issues

**1. Microphone not working**
- Ensure browser has microphone permissions
- Use Chrome or Edge (best Web Speech API support)
- Check system microphone settings

**2. Backend connection fails**
- Verify backend server is running on port 8000
- Check GOOGLE_API_KEY is set in .env file
- Ensure no firewall blocking WebSocket connections

**3. Speech recognition errors**
- Speak clearly and at a moderate pace
- Reduce background noise
- Check browser console for specific errors

**4. Gemini API errors**
- Verify API key is valid and active
- Check API quota limits
- Ensure internet connection is stable

##  Feedback System

The feedback system analyzes:
- **Response Completeness**: Coverage of expected points
- **Communication Quality**: Clarity and structure
- **Content Depth**: Detail and examples provided
- **Overall Performance**: Holistic assessment

Feedback includes:
-  Strengths identified
-  Areas for improvement
-  Specific actionable suggestions
-  Encouragement and motivation

##  Future Enhancements

- **Multilingual Support**: Hindi, Marathi, and other Indian languages
- **Role-specific Questions**: Customize for different job roles
- **Video Recording**: Record and replay interviews
- **Advanced Analytics**: Track progress over multiple sessions
- **Database Integration**: PostgreSQL for better scalability
- **Cloud Deployment**: AWS/Azure/GCP deployment guides
- **Mobile App**: Native mobile applications


