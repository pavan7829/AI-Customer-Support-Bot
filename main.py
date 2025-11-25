import sqlite3
import uvicorn
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from openai import OpenAI

# ==========================================
# CONFIGURATION
# ==========================================
# [Requirement: LLM Integration]
# Replace with your actual OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"
client = OpenAI()

app = FastAPI()

# Database file name
DB_NAME = "support_bot.db"

# ==========================================
# DATABASE SETUP (Session Tracking)
# [Requirement: Database for session tracking]
# ==========================================
def init_db():
    """Initializes the SQLite database to store chat history."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (session_id TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# ==========================================
# DATA MODELS (Input/Output)
# ==========================================
class ChatRequest(BaseModel):
    session_id: str  # Unique ID for the user session
    query: str       # The customer's message

class ChatResponse(BaseModel):
    response: str
    status: str      # "resolved" or "escalated"

# ==========================================
# KNOWLEDGE BASE & SYSTEM PROMPT
# [Requirement: Input FAQs dataset]
# ==========================================
SYSTEM_PROMPT = """
You are a Customer Support AI for "TechFlow". 
Use the following FAQ to answer questions.

FAQ DATASET:
1. Reset Password: Go to Settings > Security > Reset.
2. Pricing: Basic Plan is $10/mo, Pro Plan is $20/mo.
3. Refunds: Refunds take 3-5 business days. Contact billing@techflow.com.
4. Hours: Support is available 9 AM - 5 PM EST.

RULES:
1. If the answer is in the FAQ, answer politely.
2. [Requirement: Contextual Memory] Use previous conversation history to understand context.
3. [Requirement: Escalation Simulation] If the user is angry, abusive, or asks a question NOT in the FAQ, 
   you MUST reply with exactly: "ACTION: ESCALATE_TO_AGENT". 
   Do not add any other text if you are escalating.
"""

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_chat_history(session_id: str):
    """Retrieves conversation history for context."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM sessions WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = c.fetchall()
    conn.close()
    
    # Format for OpenAI API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for row in rows:
        messages.append({"role": row[0], "content": row[1]})
    return messages

def save_interaction(session_id: str, role: str, content: str):
    """Saves a message to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

# ==========================================
# API ENDPOINT
# [Requirement: Backend API with REST endpoints]
# ==========================================
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_query = request.query

    # 1. Save User Query to DB
    save_interaction(session_id, "user", user_query)

    # 2. Retrieve History (Context)
    # [Requirement: Contextual memory]
    history = get_chat_history(session_id)

    # 3. Generate Response using LLM
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            temperature=0.5
        )
        bot_content = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4. Check for Escalation Flag
    # [Requirement: Escalation simulation]
    status = "resolved"
    final_response = bot_content

    if "ACTION: ESCALATE_TO_AGENT" in bot_content:
        status = "escalated"
        final_response = "I am unable to resolve this issue based on my current instructions. I am transferring you to a human agent now."
    
    # 5. Save Bot Response to DB
    save_interaction(session_id, "assistant", final_response)

    return {"response": final_response, "status": status}

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("Starting AI Support Bot API...")
    # Runs the server locally
    uvicorn.run(app, host="127.0.0.1", port=8000)
