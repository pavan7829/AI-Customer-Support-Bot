import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import sqlite3
import json
import os
from typing import List, Optional

# --- Configuration ---
# ideally, set your OPENAI_API_KEY in environment variables
# os.environ["OPENAI_API_KEY"] = "sk-..." 

app = FastAPI(title="AI Customer Support Bot")

# --- Database Setup (SQLite) ---
DB_NAME = "chat_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table to store chat history
    c.execute('''CREATE TABLE IF NOT EXISTS sessions 
                 (session_id TEXT PRIMARY KEY, history TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- Mock FAQ Dataset ---
faq_dataset = {
    "reset password": "To reset your password, go to Settings > Security > Reset Password.",
    "refund policy": "Refunds are processed within 5-7 business days for eligible items.",
    "contact support": "You can reach us at support@example.com or call 1-800-123-4567."
}

# --- Data Models ---
class UserQuery(BaseModel):
    session_id: str
    query: str

class BotResponse(BaseModel):
    response: str
    escalated: bool

# --- Helper Functions ---

def get_history(session_id: str) -> List[dict]:
    """Retrieve chat history from DB."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT history FROM sessions WHERE session_id=?", (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return []

def save_history(session_id: str, history: List[dict]):
    """Save updated chat history to DB."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO sessions (session_id, history) VALUES (?, ?)", 
              (session_id, json.dumps(history)))
    conn.commit()
    conn.close()

def mock_llm_response(query: str, history: List[dict]) -> dict:
    """
    Simulates an LLM response. 
    In production, replace this with OpenAI/Anthropic API calls.
    """
    query_lower = query.lower()
    
    # 1. Check for Frustration/Escalation triggers
    escalation_keywords = ["human", "manager", "angry", "stupid", "useless"]
    if any(k in query_lower for k in escalation_keywords):
        return {
            "text": "I noticed you're upset. I am escalating this conversation to a human agent immediately.",
            "escalate": True
        }

    # 2. Contextual logic (Simulating LLM memory)
    # If the user says "thanks" or "bye", look at previous context
    if "thank" in query_lower or "bye" in query_lower:
        return {"text": "You're welcome! Let me know if you need anything else.", "escalate": False}

    # 3. Fallback LLM generation simulation
    return {
        "text": f"I understood you asked about '{query}'. As an AI, I suggest checking our documentation or rephrasing.",
        "escalate": False
    }

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "AI Support Bot is running"}

@app.post("/chat", response_model=BotResponse)
def chat_endpoint(user_input: UserQuery):
    session_id = user_input.session_id
    query = user_input.query.strip()
    
    # 1. Load History
    history = get_history(session_id)
    history.append({"role": "user", "content": query})

    response_text = ""
    escalation_status = False

    # 2. Check Static FAQ (Fast retrieval)
    found_faq = False
    for key, answer in faq_dataset.items():
        if key in query.lower():
            response_text = answer
            found_faq = True
            break
    
    # 3. If no FAQ match, call LLM
    if not found_faq:
        llm_result = mock_llm_response(query, history)
        response_text = llm_result["text"]
        escalation_status = llm_result["escalate"]

    # 4. Update History and Save
    history.append({"role": "bot", "content": response_text})
    save_history(session_id, history)

    return BotResponse(response=response_text, escalated=escalation_status)

@app.get("/history/{session_id}")
def get_session_history(session_id: str):
    """View the memory of the bot for a specific user."""
    return get_history(session_id)

# --- Execution Entry Point ---
if __name__ == "__main__":
    #import nest_asyncio
    #nest_asyncio.apply() # <--- This fixes the error in Notebooks/Colab
    
    print("Starting server... (Stop the cell to exit)")
    # Runs the server on localhost:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)