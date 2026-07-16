"""
Implements the actual logic behind each tool Claude can call.
"""
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo


async def execute_tool(name: str, inputs: dict) -> str:
    """Dispatch tool call and return a plain-text result."""

    if name == "get_weather":
        city = inputs["city"].replace(" ", "+")
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"https://wttr.in/{city}?format=j1")
            data = r.json()
        cond = data["current_condition"][0]
        temp_c = cond["temp_C"]
        feels = cond["FeelsLikeC"]
        desc  = cond["weatherDesc"][0]["value"]
        return (
            f"Weather in {inputs['city']}: {desc}. "
            f"Temperature {temp_c}°C, feels like {feels}°C."
        )

    if name == "web_search":
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(
                "https://api.duckduckgo.com/",
                params={"q": inputs["query"], "format": "json", "no_html": "1"},
            )
            data = r.json()
        abstract = data.get("AbstractText")
        return abstract if abstract else "No direct result found for that query."

    if name == "set_reminder":
        return (
            f"Reminder set: '{inputs['message']}' "
            f"at {inputs['iso_datetime']}."
        )

    if name == "get_time":
        tz = ZoneInfo(inputs.get("timezone", "UTC"))
        now = datetime.now(tz).strftime("%I:%M %p, %A %d %B %Y")
        return f"Current time in {inputs['timezone']}: {now}."

    return f"Unknown tool: {name}"
