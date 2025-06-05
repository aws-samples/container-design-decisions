# # https://modelcontextprotocol.io/quickstart/server
from typing import List
from mcp.server.fastmcp import FastMCP
from langchain_core.messages import AIMessage, HumanMessage

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get weather for location."""
    return f"As per weather bureau, currently it is 28 degreee Celsius in {city}. This is considered a warm day."
    



@mcp.prompt(name="explain_code")
async def explain_code_prompt(code: str) -> str:
    return [
        {
            "role": "user",
            "content": f"Analyze this code focusing on non blocking:\n{code}"
        }
    ]    

@mcp.prompt(name="get_weather_prompt")
async def get_weather_prompt(city: str) -> list[AIMessage]:
    return [
        {
            "role": "user",
            "content": f"Get the temperature and humidity for {city}"
        }
    ]    

@mcp.resource("resource://{location}/weather")
async def city_weather(location: str) -> str:
    """Get temperature for location."""
    return f"It's 28 degreee Celsius at ${location}"

if __name__ == "__main__":
    mcp.run(transport="sse")