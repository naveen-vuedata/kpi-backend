import os
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain imports - using the correct imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

# -----------------------------------------------------------
# Load environment variables
# -----------------------------------------------------------
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# -----------------------------------------------------------
# Initialize LLM
# -----------------------------------------------------------
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=api_key,
    temperature=0.3
)

# -----------------------------------------------------------
# Create prompt template
# -----------------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Have a conversation with the user."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Create the chain
chain = prompt | llm

# -----------------------------------------------------------
# Session store for chat histories
# -----------------------------------------------------------
store: Dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Get or create chat history for a session."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


# -----------------------------------------------------------
# Create chain with message history
# -----------------------------------------------------------
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# -----------------------------------------------------------
# FastAPI initialization
# -----------------------------------------------------------
app = FastAPI(title="LangChain Chatbot with Memory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------
# API Models
# -----------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


# -----------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------
@app.get("/")
def root():
    return {"message": "LangChain Chatbot API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat endpoint with session-based memory."""
    try:
        # Invoke the chain with history
        response = chain_with_history.invoke(
            {"input": request.message},
            config={"configurable": {"session_id": request.session_id}}
        )
        
        # Extract the content from the AIMessage
        reply = response.content if hasattr(response, 'content') else str(response)
        
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply=f"Error: {str(e)}")


@app.delete("/chat/{session_id}")
def clear_history(session_id: str):
    """Clear chat history for a session."""
    if session_id in store:
        store[session_id].clear()
        return {"message": f"History cleared for session {session_id}"}
    return {"message": "Session not found"}


@app.get("/chat/{session_id}/history")
def get_history(session_id: str):
    """Get chat history for a session."""
    if session_id in store:
        messages = store[session_id].messages
        return {
            "session_id": session_id,
            "message_count": len(messages),
            "messages": [
                {
                    "type": msg.__class__.__name__,
                    "content": msg.content
                }
                for msg in messages
            ]
        }
    return {"message": "Session not found", "messages": []}


