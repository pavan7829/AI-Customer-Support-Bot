🤖 AI Customer Support Bot

Welcome to the AI Customer Support Bot!

This project is a smart, hybrid customer support agent designed to handle user queries efficiently. It doesn't just blindly send everything to an AI—it first checks a predefined knowledge base (FAQs), and if that fails, it uses an LLM (Large Language Model) to generate a helpful response.

Most importantly, it knows its limits. If a user gets frustrated or asks for a human, the bot triggers an automatic escalation.

🚀 Key Features

Hybrid Intelligence: First checks a static FAQ database for instant, accurate answers. If no match is found, it consults the AI.

Contextual Memory: The bot remembers what you said earlier in the conversation (stored via SQLite), so you don't have to repeat yourself.

Smart Escalation: Detects sentiment. If a user says "I'm angry" or "stupid bot," the system flags the chat for human intervention.

REST API: Built on FastAPI, making it fast, documented, and easy to integrate with a frontend.

🛠️ Tech Stack

Language: Python 3.9+

Framework: FastAPI (for the backend API)

Server: Uvicorn

Database: SQLite (for simple, local session management)

Logic: Custom Python logic for FAQ matching + LLM integration.

🧠 Documentation of Prompts

Per the project requirements, here is the breakdown of the logic and prompts used to guide the AI's behavior.

Since this system handles both static data and AI generation, we use a "System Instruction" approach to govern how the bot behaves.

1. The "Persona" Prompt

When the bot is generating a response, it operates under this persona:

"You are a helpful, polite, and professional Customer Support Agent. Your goal is to assist the user based on the conversation history. If you do not know the answer, politely suggest checking the official documentation."

2. The "Escalation" Trigger Logic

Instead of a simple text prompt, we use a logical filter to decide when to stop the AI and call a human. The bot analyzes the user's input for specific keywords or sentiment.

The Logic:

Input Scan: Check user query for keywords: ['angry', 'manager', 'human', 'stupid', 'useless', 'complaint'].

If Match Found:

Internal Action: Set escalated = True.

Response Override: "I noticed you're upset. I am escalating this conversation to a human agent immediately."

3. Contextual Awareness

The bot is fed the previous 5-10 messages of the conversation history before generating an answer.

Prompt Structure: [User History] + [Current Query]

Goal: To ensure that if a user says "How much is it?", the bot knows "it" refers to the product discussed in the previous message.

⚡ How to Run This Project

Follow these steps to get the bot running on your local machine.

Prerequisites

Make sure you have Python installed.

Step 1: Install Dependencies

Open your terminal in the project folder and run:

pip install fastapi uvicorn pydantic requests


Step 2: Start the Server

Run the backend application:

python main.py


You should see a message saying Uvicorn running on http://127.0.0.1:8000.

Step 3: Test the Bot

You have two ways to test it:

Option A: The Browser UI (Easiest)

Go to http://127.0.0.1:8000/docs

Click POST /chat -> Try it out.

Send a JSON message:

{
  "session_id": "user1",
  "query": "how do i reset password"
}


Option B: The Console Client
Open a new terminal window (keep the server running in the first one) and run:

python client.py


Now you can chat with the bot directly in your terminal!


