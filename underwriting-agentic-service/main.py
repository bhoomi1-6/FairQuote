# main.py - FastAPI Backend
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
from dotenv import load_dotenv
load_dotenv()
from src.agents.intake_agent import IntakeAgent
from src.utils.document_extraction import extract_document
from strands.session.file_session_manager import FileSessionManager
from datetime import datetime
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
import json

import os

app = FastAPI(title="FairQuote Intake API", version="1.0.0")

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis in production)
sessions: Dict[str, IntakeAgent] = {}

# ----------------------------
# MODELS
# ----------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    tool_calls: Optional[List[Dict]] = []
    metadata: Optional[Dict] = {}

class SessionCreate(BaseModel):
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    status: str

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
async def get_or_create_agent(session_id: str) -> IntakeAgent:
    """Get existing agent or create new one with session manager and first user message."""
    actor_id = f"actor_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    memory_session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    agentcore_memory_config = AgentCoreMemoryConfig(
    memory_id= os.getenv("MEM_ID"),
    session_id=memory_session_id,
    actor_id=actor_id
    )
    session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=agentcore_memory_config,
    region_name="us-east-1")
    if session_id not in sessions:
        agent = IntakeAgent(session_manager=session_manager)
        sessions[session_id] = agent
    return sessions[session_id]

# ----------------------------
# ENDPOINTS
# ----------------------------
@app.get("/")
async def root():
    return {
        "service": "FairQuote Intake API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/sessions/create", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """Create a new conversation session"""
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id in sessions:
        return SessionResponse(session_id=session_id, status="existing")
    
    # Create new agent and initialize with dummy user message
    await get_or_create_agent(session_id)
    
    return SessionResponse(session_id=session_id, status="created")

@app.get("/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Check if session exists"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = sessions[session_id]
    return {
        "session_id": session_id,
        "exists": True,
        "agent_name": getattr(agent, "name", "IntakeAgent"),
        "tools_count": len(getattr(agent, "tools", []))
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"session_id": session_id, "status": "deleted"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a text message to the agent"""
    session_id = request.session_id
    agent = await get_or_create_agent(session_id)
    
    try:
        # Invoke agent
        result = await agent.invoke_async(request.message)
        
        # Extract response
        response_text = getattr(result, "final_message", str(result))
        
        # Extract tool calls
        tool_calls = []
        if hasattr(result, "tool_calls") and result.tool_calls:
            for tc in result.tool_calls:
                tool_calls.append({
                    "name": getattr(tc, "name", "unknown"),
                    "output": getattr(tc, "output", str(tc))
                })
        
        return ChatResponse(
            session_id=session_id,
            message=response_text,
            tool_calls=tool_calls,
            metadata={"status": "success"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.post("/chat/upload")
async def chat_with_upload(
    session_id: str = Form(...),
    message: str = Form(...),
    file: UploadFile = File(...)
):
    """Send a message with file upload, extract text and store in short-term memory"""
    

    try:
        # Step 2: Read file bytes
        file_bytes = await file.read()

        # Step 3: Extract text from document
        extracted_data = await extract_document(file_bytes)
        extracted_data_str = json.dumps(extracted_data)
        # Step 4: Get or create agent
        agent_intake = await get_or_create_agent(session_id)

        # Step 5: Invoke the IntakeAgent with the user message

        print(f"{type(extracted_data_str)} {type(message)}")
        message = {"text": message}
        extracted_data = {"text": extracted_data_str}
        result = await agent_intake.invoke_async([message, extracted_data])

        # Step 6: Prepare response
        response_text = getattr(result, "final_message", str(result))
        tool_calls = []
        if hasattr(result, "tool_calls") and result.tool_calls:
            for tc in result.tool_calls:
                tool_calls.append({
                    "name": getattr(tc, "name", "unknown"),
                    "output": getattr(tc, "output", str(tc))
                })

        return {
            "session_id": session_id,
            "message": response_text,
            "tool_calls": tool_calls,
            "file_processed": file.filename,
            "extracted_data": extracted_data,
            "metadata": {"status": "success"}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error:" +e)
    
@app.get("/sessions/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = sessions[session_id]
    
    try:
        messages = []
        if hasattr(agent.session_manager, "get_messages"):
            messages = agent.session_manager.get_messages()
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_sessions": len(sessions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
