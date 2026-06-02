from groq import Groq
import os
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Tool schemas for LLM function calling
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a recipient",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search for records in database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "collection": {"type": "string", "enum": ["users", "products"], "default": "users"}
                },
                "required": ["query"]
            }
        }
    }
]

class IntentAnalyzer:
    def __init__(self):
        self.conversation_history = []
    
    def analyze(self, user_message: str):
        """Call LLM to decide which tool (if any) to use"""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.conversation_history,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        tool_calls = message.tool_calls
        
        # Store assistant response for later (when we have tool result)
        self.conversation_history.append(message)
        
        if not tool_calls:
            # No function needed – direct response
            return {"function": None, "args": None, "direct_response": message.content}
        
        # Extract first tool call (LLM may call multiple, but we'll use first)
        tool = tool_calls[0].function
        return {
            "function": tool.name,
            "args": json.loads(tool.arguments),
            "tool_call_id": tool_calls[0].id,
            "direct_response": None
        }
    
    def finalize_response(self, tool_result: dict, tool_call_id: str):
        """After tool execution, get final natural language response"""
        self.conversation_history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(tool_result)
        })
        
        final = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.conversation_history
        )
        response_text = final.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": response_text})
        return response_text