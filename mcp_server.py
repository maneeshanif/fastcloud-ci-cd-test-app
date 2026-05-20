import os

from fastmcp import FastMCP


mcp = FastMCP("addition-server")


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host=os.getenv("MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("MCP_PORT", "8001")),
    )
