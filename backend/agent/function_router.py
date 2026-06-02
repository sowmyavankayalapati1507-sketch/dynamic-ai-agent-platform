from tools.weather_tool import get_weather
from tools.email_tool import send_email
from tools.db_tool import search_database
import asyncio

# Map tool names to actual functions
FUNCTION_MAP = {
    "get_weather": get_weather,
    "send_email": send_email,
    "search_database": search_database
}

class FunctionRouter:
    @staticmethod
    async def execute(function_name: str, arguments: dict):
        """Execute the requested tool function"""
        if function_name not in FUNCTION_MAP:
            return {"error": f"Unknown function: {function_name}"}
        
        func = FUNCTION_MAP[function_name]
        # Handle async functions
        if asyncio.iscoroutinefunction(func):
            return await func(**arguments)
        else:
            return func(**arguments)