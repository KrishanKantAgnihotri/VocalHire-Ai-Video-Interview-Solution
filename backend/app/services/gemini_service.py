"""
Gemini LLM service integration using LangChain.
Handles all interactions with Google's Gemini model.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Optional, Dict, Any
import os


class GeminiService:
    """Service for interacting with Google's Gemini LLM"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "models/gemini-2.5-flash"):
        """
        Initialize Gemini service with API credentials.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model_name: Name of the Gemini model to use
                       Options: 
                       - "models/gemini-1.5-flash" (fast, free tier, recommended)
                       - "models/gemini-1.5-pro" (more capable)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be provided or set in environment")
        
       
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=0.7
        )
    
    async def validate_answer_completeness(
        self, 
        question: str, 
        answer: str, 
        expected_coverage: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Validate if an answer adequately addresses the question.
        
        Args:
            question: The interview question asked
            answer: The candidate's answer
            expected_coverage: List of points that should be covered
            
        Returns:
            Dict with 'is_complete', 'missing_points', and 'follow_up' keys
        """
        coverage_text = ""
        if expected_coverage:
            coverage_text = f"\nExpected coverage points: {', '.join(expected_coverage)}"
        
        prompt = f"""You are evaluating a candidate's answer in a mock interview for vocational training students in India.

Question: {question}{coverage_text}

Candidate's Answer: {answer}

Evaluate if the answer adequately addresses the question. Consider:
1. Does it cover the main points expected?
2. Is it detailed enough or too vague?
3. If coverage points are listed, are they addressed?

Respond in this exact JSON format:
{{
    "is_complete": true/false,
    "missing_points": ["point1", "point2"],
    "follow_up": "A brief, encouraging follow-up question if incomplete, or empty string if complete"
}}
"""
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            # Parse the JSON response
            import json
            import re
            
            # Clean the response 
            content = response.content.strip()
            
            
            content = re.sub(r'^```(?:json)?\s*\n?', '', content)
            content = re.sub(r'\n?```\s*$', '', content)
            content = content.strip()
            
            
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"Error validating answer: {e}")
            print(f"Raw response: {response.content if 'response' in locals() else 'No response'}")
            # Default to accepting the answer if validation fails
            return {
                "is_complete": True,
                "missing_points": [],
                "follow_up": ""
            }
    
    async def generate_follow_up_question(
        self, 
        original_question: str, 
        answer: str, 
        missing_points: list
    ) -> str:
        """
        Generate a follow-up question to get missing information.
        
        Args:
            original_question: The original question asked
            answer: The candidate's incomplete answer
            missing_points: Points that need to be covered
            
        Returns:
            A follow-up question string
        """
        prompt = f"""You are a friendly interviewer conducting a mock interview with a vocational training student in India.

Original Question: {original_question}
Candidate's Answer: {answer}
Missing Points: {', '.join(missing_points)}

Generate a brief, encouraging follow-up question (1-2 sentences) to help the candidate provide the missing information. 
Be supportive and conversational. Don't make them feel they did poorly.
"""
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return f"Could you tell me more about {missing_points[0] if missing_points else 'that'}?"
    
    async def generate_chat_response(self, system_prompt: str, user_message: str) -> str:
        """
        Generate a general chat response from Gemini.
        
        Args:
            system_prompt: System context/instructions
            user_message: User's message
            
        Returns:
            LLM's response as a string
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating chat response: {e}")
            return "I apologize, I'm having trouble processing that. Could you please repeat?"

