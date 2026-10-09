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
    page_title="FairQuote",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# API CLIENT
# ----------------------------
class MASAPIClient:
    """Professional API client for Multi-Agent System backend."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = 1000
    
    def health_check(self) -> dict:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            resp.raise_for_status()
            return {"status": "healthy", "data": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def create_session(self, session_id: Optional[str] = None) -> dict:
        payload = {"session_id": session_id} if session_id else {}
        resp = requests.post(f"{self.base_url}/sessions/create", json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def send_message(self, session_id: str, message: str) -> dict:
        payload = {"session_id": session_id, "message": message}
        resp = requests.post(f"{self.base_url}/chat", json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def send_message_with_file(self, session_id: str, message: str, file) -> dict:
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {"session_id": session_id, "message": message}
        resp = requests.post(f"{self.base_url}/chat/upload", data=data, files=files, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def delete_session(self, session_id: str) -> dict:
        resp = requests.delete(f"{self.base_url}/sessions/{session_id}", timeout=self.timeout)
        if resp.ok:
            return resp.json()
        return {"status": "error"}

# Initialize API client
api = MASAPIClient(API_BASE_URL)

# ----------------------------
# SESSION MANAGEMENT
# ----------------------------
def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        try:
            api.create_session(st.session_state.session_id)
            st.session_state.session_status = "active"
        except Exception as e:
            st.session_state.session_status = "error"
            st.error(f"⚠️ Session creation failed: {e}")
    st.session_state.messages = st.session_state.get("messages", [])
    st.session_state.api_status = st.session_state.get("api_status", "unknown")

def reset_conversation():
    """Reset conversation state and start new session."""
    try:
        if "session_id" in st.session_state:
            api.delete_session(st.session_state.session_id)
    except:
        pass
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    try:
        api.create_session(st.session_state.session_id)
        st.session_state.session_status = "active"
        st.success("✅ New session started!")
    except Exception as e:
        st.session_state.session_status = "error"
        st.error(f"Failed to create session: {e}")

initialize_session()

# ----------------------------
# LAYOUT
# ----------------------------
st.title("🚗 FairQuote")
st.caption("Professional Multi-Agent System for Insurance Underwriting")

# API Health
health = api.health_check()
if health["status"] == "healthy":
    col1, col2 = st.columns([3,1])
    col1.success("✅ Backend connected")
    col2.metric("Active Sessions", health["data"].get("active_sessions", 0))
    st.session_state.api_status = "healthy"
else:
    st.error(f"❌ Backend offline: {health.get('error', 'Unknown error')}")
    st.stop()

st.divider()

# ----------------------------
# CHAT HISTORY
# ----------------------------
def display_messages():
    for msg in st.session_state.messages:
        role = msg.get("role")
        content = msg.get("content", "")
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

display_messages()

# ----------------------------
# FILE UPLOAD
# ----------------------------
with st.expander("📄 Upload Document", expanded=False):
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "jpg", "jpeg", "png"],
        key="file_uploader",
        help="Upload driver's license, registration, etc."
    )
    if uploaded_file:
        col1, col2, col3 = st.columns([2,1,1])
        col1.info(f"📎 {uploaded_file.name}")
        col2.caption(f"{uploaded_file.size / 1024:.1f} KB")
        if col3.button("📤 Send", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": f"📄 **Uploaded:** {uploaded_file.name}"})
            with st.spinner("🔄 Processing document..."):
                try:
                    result = api.send_message_with_file(
                        session_id=st.session_state.session_id,
                        message="Please extract all relevant details.",
                        file=uploaded_file
                    )
                    st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                    for tc in result.get("tool_calls", []):
                        st.session_state.messages.append({"role": "tool", "content": f"**{tc['name']}**\n\n{tc['output']}"})
                    st.rerun()
                except Exception as e:
                    st.session_state.messages.append({"role": "error", "content": str(e)})
                    st.rerun()

# ----------------------------
# CHAT INPUT
# ----------------------------
if user_input := st.chat_input("💬 Ask about insurance, upload documents, or get a quote..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Thinking..."):
            try:
                result = api.send_message(st.session_state.session_id, user_input)
                st.markdown(result["message"])
                st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                for tc in result.get("tool_calls", []):
                    tool_content = f"**{tc['name']}**\n\n{tc['output']}"
                    with st.chat_message("assistant", avatar="🔧"):
                        st.info(tool_content, icon="🔧")
                    st.session_state.messages.append({"role": "tool", "content": tool_content})
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.messages.append({"role": "error", "content": str(e)})

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.header("⚙️ Session Control")
    st.text_input("Session ID", value=st.session_state.session_id[:16]+"...", disabled=True)
    st.metric("Messages", len(st.session_state.messages))
    col1, col2 = st.columns(2)
    if col1.button("🔄 Reset"):
        reset_conversation()
        st.rerun()
    if col2.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.subheader("💡 Quick Actions")
    if st.button("📋 Get Quote"):
        st.session_state.messages.append({"role": "user", "content": "I'd like a quote"})
        st.rerun()
    if st.button("📄 Upload License"):
        st.info("Use the upload section above")
    if st.button("🚗 Vehicle Info"):
        st.session_state.messages.append({"role": "user", "content": "Provide vehicle information"})
        st.rerun()
    
    st.divider()
    with st.expander("❓ Help & Tips"):
        st.markdown("""
        **How to use:**
        - Chat naturally about insurance
        - Upload documents: driver's license, registration
        - Provide vehicle or personal info
        **Example prompts:**
        - "I need car insurance"
        - "Here's my registration: AB12 CDE"
        - "Calculate my premium"
        """)
    
    with st.expander("🔍 Debug Info"):
        st.caption("Backend URL & Status")
        st.code(API_BASE_URL)
        st.json({"api_status": st.session_state.api_status, "session_status": st.session_state.get("session_status", "unknown")})
        if st.button("🔄 Check Health"):
            health = api.health_check()
            st.json(health)
        if st.button("📥 Download Chat"):
            chat_json = json.dumps(st.session_state.messages, indent=2)
            st.download_button("💾 Download JSON", data=chat_json, file_name=f"chat_{st.session_state.session_id[:8]}.json", mime="application/json")

st.divider()
st.caption(" 🚀 Fast • 🤖 AI-Powered")
