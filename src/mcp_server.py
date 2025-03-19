#!/usr/bin/env python3
import sys
from mcp.server.fastmcp import FastMCP
from eda_cli import run_rag_all  # ensure run_rag_all is importable from here
 
mcp = FastMCP("Edge Data Agent")

@mcp.tool()
def run_mcp(query: str, similarity_top_k: str = "3") -> str:
    """
    Runs the aggregated RAG process for all data directories in the registry.
    """
    return run_rag_all(query, similarity_top_k)

if __name__ == "__main__":
    # Run the server; this is blocking
    mcp.run(transport="stdio")
