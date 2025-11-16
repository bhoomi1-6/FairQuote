import streamlit as st
import requests
import uuid
import json
from typing import Optional

# ----------------------------
# CONFIG
# ----------------------------
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Intelligent Underwriting MAS",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ----------------------------
# API CLIENT
# ----------------------------
class MASAPIClient:
    """API client for Multi-Agent System backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30
    
    def health_check(self) -> dict:
        """Check if API is alive"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def create_session(self, session_id: Optional[str] = None) -> dict:
        """Create a new conversation session"""
        try:
            payload = {"session_id": session_id} if session_id else {}
            response = requests.post(
                f"{self.base_url}/sessions/create",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create session: {str(e)}")
    
    def send_message(self, session_id: str, message: str) -> dict:
        """Send a text message to the agent"""
        try:
            payload = {"session_id": session_id, "message": message}
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to send message: {str(e)}")
    
    def send_message_with_file(self, session_id: str, message: str, file) -> dict:
        """Send a message with file attachment"""
        try:
            files = {"file": (file.name, file.getvalue(), file.type)}
            data = {"session_id": session_id, "message": message}
            response = requests.post(
                f"{self.base_url}/chat/upload",
                data=data,
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def delete_session(self, session_id: str) -> dict:
        """Delete a conversation session"""
        try:
            response = requests.delete(
                f"{self.base_url}/sessions/{session_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"status": "error"}

# Initialize API client
api = MASAPIClient(API_BASE_URL)

# ----------------------------
# SESSION MANAGEMENT
# ----------------------------
def initialize_session():
    """Initialize or restore session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        try:
            result = api.create_session(st.session_state.session_id)
            st.session_state.session_status = "active"
        except Exception as e:
            st.session_state.session_status = "error"
            st.error(f"⚠️ Session creation failed: {e}")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_status" not in st.session_state:
        st.session_state.api_status = "unknown"

def reset_conversation():
    """Reset the conversation and create new session"""
    try:
        # Try to delete old session
        if "session_id" in st.session_state:
            api.delete_session(st.session_state.session_id)
    except:
        pass
    
    # Clear state
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    
    # Create new session
    try:
        api.create_session(st.session_state.session_id)
        st.session_state.session_status = "active"
        st.success("✅ New conversation started!")
    except Exception as e:
        st.error(f"Failed to create session: {e}")

# Initialize session
initialize_session()

# ----------------------------
# HEADER & STATUS
# ----------------------------
st.title("🚗 Intelligent Underwriting MAS")
st.caption("Multi-Agent System for Insurance Underwriting")

# API Health Check
health = api.health_check()
if health["status"] == "healthy":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ Connected to backend")
    with col2:
        if health["data"].get("active_sessions"):
            st.metric("Sessions", health["data"]["active_sessions"])
    st.session_state.api_status = "healthy"
else:
    st.error(f"❌ Backend offline: {health.get('error', 'Unknown error')}")
    st.warning(f"Trying to connect to: `{API_BASE_URL}`")
    st.info("💡 Make sure your FastAPI backend is running on port 8000")
    st.session_state.api_status = "error"
    st.stop()

st.divider()

# ----------------------------
# DISPLAY CHAT HISTORY
# ----------------------------
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    
    elif role == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)
    
    elif role == "tool":
        with st.chat_message("assistant", avatar="🔧"):
            st.info(content, icon="🔧")
    
    elif role == "error":
        with st.chat_message("assistant", avatar="⚠️"):
            st.error(content)

# ----------------------------
# FILE UPLOAD SECTION
# ----------------------------
with st.expander("📄 Upload Document", expanded=False):
    st.caption("Upload driver's license, insurance documents, vehicle registration, etc.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "jpg", "jpeg", "png"],
        key="file_uploader",
        help="Supported formats: PDF, JPG, PNG"
    )
    
    if uploaded_file:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.info(f"📎 {uploaded_file.name}")
        
        with col2:
            st.caption(f"{uploaded_file.size / 1024:.1f} KB")
        
        with col3:
            if st.button("📤 Send", type="primary", use_container_width=True):
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"📄 **Uploaded:** {uploaded_file.name}"
                })
                
                # Process file
                with st.spinner("🔄 Processing document..."):
                    try:
                        result = api.send_message_with_file(
                            session_id=st.session_state.session_id,
                            message="Please extract all relevant details from this document.",
                            file=uploaded_file
                        )
                        
                        # Add assistant response
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["message"]
                        })
                        
                        # Add tool outputs
                        if result.get("tool_calls"):
                            for tc in result["tool_calls"]:
                                st.session_state.messages.append({
                                    "role": "tool",
                                    "content": f"**{tc['name']}**\n\n{tc['output']}"
                                })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.session_state.messages.append({
                            "role": "error",
                            "content": f"Failed to process document: {str(e)}"
                        })
                        st.rerun()

# ----------------------------
# CHAT INPUT
# ----------------------------
if user_input := st.chat_input("💬 Ask about insurance, provide information, or request a quote..."):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # Get agent response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Thinking..."):
            try:
                result = api.send_message(
                    session_id=st.session_state.session_id,
                    message=user_input
                )
                
                # Display response
                st.markdown(result["message"])
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["message"]
                })
                
                # Display tool outputs
                if result.get("tool_calls"):
                    for tc in result["tool_calls"]:
                        tool_content = f"**{tc['name']}**\n\n{tc['output']}"
                        
                        with st.chat_message("assistant", avatar="🔧"):
                            st.info(tool_content, icon="🔧")
                        
                        st.session_state.messages.append({
                            "role": "tool",
                            "content": tool_content
                        })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "error",
                    "content": error_msg
                })

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.header("⚙️ Session Control")
    
    # Session info
    st.text_input(
        "Session ID",
        value=st.session_state.session_id[:16] + "...",
        disabled=True,
        help="Unique identifier for this conversation"
    )
    
    st.metric("Messages", len(st.session_state.messages))
    
    # Controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset", use_container_width=True, help="Start a new conversation"):
            reset_conversation()
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear chat display"):
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
    # Quick actions
    st.subheader("💡 Quick Actions")
    
    if st.button("📋 Get Quote", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "I'd like to get an insurance quote"
        })
        st.rerun()
    
    if st.button("📄 Upload License", use_container_width=True):
        st.info("👆 Use the upload section above")
    
    if st.button("🚗 Vehicle Info", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "I need to provide vehicle information"
        })
        st.rerun()
    
    st.divider()
    
    # Help section
    with st.expander("❓ Help & Tips"):
        st.markdown("""
        **How to use:**
        
        1. **Chat naturally** - Just type your questions
        2. **Upload documents** - Driver's license, registration
        3. **Provide details** - The agent will guide you
        
        **Example prompts:**
        - "I need car insurance for my new vehicle"
        - "Here's my registration: AB12 CDE"
        - "What documents do you need?"
        - "Calculate my premium"
        """)
    
    # Debug section
    with st.expander("🔍 Debug Info"):
        st.caption("Backend URL")
        st.code(API_BASE_URL, language=None)
        
        st.caption("API Status")
        st.json({
            "status": st.session_state.api_status,
            "session_status": st.session_state.get("session_status", "unknown")
        })
        
        if st.button("🔄 Check Health", use_container_width=True):
            health = api.health_check()
            st.json(health)
        
        if st.button("📥 Download Chat", use_container_width=True):
            chat_json = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                "💾 Download JSON",
                data=chat_json,
                file_name=f"chat_{st.session_state.session_id[:8]}.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.divider()
    st.caption("🔒 Secure • 🚀 Fast • 🤖 AI-Powered")