# basic import 
from mcp.server.fastmcp import FastMCP
import math

# instantiate an MCP server client
mcp = FastMCP("Hello World")

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return int(a + b)

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# execute and return the stdio output
if __name__ == "__main__":
    mcp.run(transport="stdio")