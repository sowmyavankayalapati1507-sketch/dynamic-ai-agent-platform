import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from tools.search_tool import search_web

from tools.weather_tool import get_weather
from tools.email_tool import send_email
from tools.db_tool import search_database

# Load environment variables
load_dotenv()
print("DEBUG GROQ KEY =", os.getenv("GROQ_API_KEY"))
print("DEBUG WEATHER KEY =", os.getenv("WEATHER_API_KEY"))
print("RESEND KEY =", os.getenv("RESEND_API_KEY"))

# Initialize FastAPI
app = FastAPI(title="AI Agent System", description="Dynamic Function Calling with LLM")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
try:
    test = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":"hello"}]
    )
    print("GROQ WORKING")
except Exception as e:
    print("GROQ ERROR =", e)

# ============ FUNCTION SCHEMAS FOR LLM ============
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a specific location. Use this when user asks about weather, temperature, or climate conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., London, New York, Tokyo, Paris"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit - celsius for metric, fahrenheit for imperial",
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a recipient. Use when user asks to send email, notify someone, or contact via email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email content/body text"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search for records in database. Use when user asks to find, search, look up, or query data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to look for"
                    },
                    "collection": {
                        "type": "string",
                        "enum": ["users", "products"],
                        "description": "Which database table to search",
                        "default": "users"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the internet for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    }
}
]

# ============ AVAILABLE FUNCTIONS MAPPING ============
AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
    "send_email": send_email,
    "search_database": search_database,
    "search_web": search_web
}


# ============ REQUEST/RESPONSE MODELS ============
class UserRequest(BaseModel):
    message: str
    conversation_history: List[Dict] = []

class AgentResponse(BaseModel):
    final_response: str
    function_called: str
    tool_result: Any
    steps: List[str]

# ============ AI AGENT ENGINE ============
class AIAgent:
    def __init__(self):
        self.conversation_history = []
    
    async def process_request(self, user_message: str) -> AgentResponse:
        steps = []
        
        # Step 1: Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        steps.append(f"📝 Received: '{user_message}'")
        
        # Check if OpenAI client is available
        if not client:
            steps.append("❌ OpenAI API key not configured")
            return AgentResponse(
                final_response="⚠️ OpenAI API key is missing. Please add your API key to the .env file.",
                function_called="none",
                tool_result=None,
                steps=steps
            )
        
        # Step 2: LLM decides which function to call
        steps.append("🧠 Analyzing intent with GPT-4...")
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Using GPT-3.5 for cost efficiency
                messages=self.conversation_history,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.7
            )
        except Exception as e:
            steps.append(f"❌ OpenAI API Error: {str(e)}")
            return AgentResponse(
                final_response=f"Error calling OpenAI API: {str(e)}. Please check your API key.",
                function_called="none",
                tool_result=None,
                steps=steps
            )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # Step 3: Execute function if called
        function_called = "none"
        tool_result = None
        
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                steps.append(f"🔧 Calling function: {function_name}")
                steps.append(f"📦 Parameters: {json.dumps(function_args, indent=2)}")
                
                # Execute the actual function
                if function_name in AVAILABLE_FUNCTIONS:
                    function_to_call = AVAILABLE_FUNCTIONS[function_name]
                    # Handle async functions
                    import asyncio
                    if asyncio.iscoroutinefunction(function_to_call):
                        tool_result = await function_to_call(**function_args)
                    else:
                        tool_result = function_to_call(**function_args)
                    function_called = function_name
                    steps.append(f"✅ Tool Result: {json.dumps(tool_result, indent=2)[:200]}...")
                else:
                    tool_result = {"error": f"Function '{function_name}' not found"}
                    steps.append(f"❌ Function not found: {function_name}")
        
        # Step 4: Get final response from LLM with tool result
        if tool_calls and tool_result:
            # Add assistant message and tool response to conversation
            self.conversation_history.append(response_message)
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_calls[0].id,
                "content": json.dumps(tool_result)
            })
            
            # Generate final natural language response
            try:
                print("===== GROQ DEBUG =====")
                print("GROQ_API_KEY =", GROQ_API_KEY)
                
                final_response_obj = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=self.conversation_history,
                    temperature=0.7
                )
                
                final_response = final_response_obj.choices[0].message.content
                steps.append("💬 Generated natural language response")

            except Exception as e:
                print("===== GROQ ERROR =====")
                print(str(e))
                final_response = f"ERROR: {str(e)}"
                steps.append(f"❌ Response generation error: {str(e)}")
        else:
            # No function called, just return the LLM's direct response
            final_response = response_message.content if response_message.content else "I'm not sure how to respond to that."
            steps.append("💬 No function needed - direct response")
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        # Keep history manageable (last 10 messages)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return AgentResponse(
            final_response=final_response,
            function_called=function_called,
            tool_result=tool_result,
            steps=steps
        )

# Create global agent instance
agent = AIAgent()

# ============ API ENDPOINTS ============
@app.post("/api/chat", response_model=AgentResponse)
async def chat_endpoint(request: UserRequest):
    """Main endpoint for user interaction"""
    try:
        result = await agent.process_request(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def list_tools():
    """List all available tools"""
    return {
        "available_tools": [tool["function"]["name"] for tool in TOOLS_SCHEMA],
        "total_tools": len(TOOLS_SCHEMA),
        "status": "active"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "AI Agent is running",
        "openai_configured": bool(os.getenv("GROQ_API_KEY")),
        "weather_configured": bool(os.getenv("WEATHER_API_KEY")),
        "tools_available": len(TOOLS_SCHEMA)
    }