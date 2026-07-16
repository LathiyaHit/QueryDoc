"""
Tool definitions in OpenAI's function-calling format.
Groq can call these during a conversation turn.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. 'Mumbai'"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for up-to-date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder for the user at a specific date and time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "iso_datetime": {
                        "type": "string",
                        "description": "ISO 8601 datetime, e.g. 2025-11-01T09:00:00",
                    },
                },
                "required": ["message", "iso_datetime"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Return the current time in a given timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone, e.g. 'Asia/Kolkata'",
                    },
                },
                "required": ["timezone"],
            },
        },
    },
]
