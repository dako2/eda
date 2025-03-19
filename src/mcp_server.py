
# basic import 
from mcp.server.fastmcp import FastMCP
import math

# instantiate an MCP server client
mcp = FastMCP("Edge Data Agent")

# addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return int(a + b)
    
# execute and return the stdio output
if __name__ == "__main__":
    mcp.run(transport="stdio")
