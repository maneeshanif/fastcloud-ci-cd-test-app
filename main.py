import os
import re

from fastapi import FastAPI, HTTPException, Query
from fastmcp import Client
from pydantic import BaseModel

from mcp_server import mcp

ADDITION_PATTERN = re.compile(r"^\s*(?P<a>[+-]?\d+)\s*\+\s*(?P<b>[+-]?\d+)\s*$")
MCP_SSE_PATH = "/mcp/sse"
MCP_PUBLIC_BASE_URL = os.getenv(
    "MCP_PUBLIC_BASE_URL",
    "https://fastapi-simple-app.fastapicloud.dev",
).rstrip("/")
MCP_SSE_URL = f"{MCP_PUBLIC_BASE_URL}{MCP_SSE_PATH}"

mcp_app = mcp.http_app(path="/sse", transport="sse")
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)


class AskRequest(BaseModel):
    query: str


def parse_addition(query: str) -> tuple[int, int]:
    match = ADDITION_PATTERN.match(query)
    if not match:
        raise HTTPException(
            status_code=400,
            detail='Only simple addition is supported, for example "2 + 2".',
        )

    return int(match.group("a")), int(match.group("b"))


async def call_add_tool(a: int, b: int) -> int:
    client = Client(mcp)
    try:
        async with client:
            result = await client.call_tool("add", {"a": a, "b": b})
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not call the FastMCP addition tool.",
        ) from exc

    return result.data


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI! "}


@app.get("/name")
def read_root():
    return {"message": "Hello, Anees ... :)! "}



@app.get("/health")
def health_check():
    return {"status": "ok", "mcp_sse_endpoint": MCP_SSE_URL}


@app.get("/test/{item_id}")
def test_endpoint(item_id: int):
    return {"item_id": item_id, "message": f"Test endpoint for item {item_id}"}


@app.post("/ask")
async def ask_question(request: AskRequest):
    a, b = parse_addition(request.query)
    answer = await call_add_tool(a, b)
    return {
        "query": request.query,
        "tool": "add",
        "transport": "in-memory",
        "mcp_sse_endpoint": MCP_SSE_URL,
        "answer": answer,
    }


@app.get("/ask")
async def ask_question_get(query: str = Query(..., examples=["2 + 2"])):
    a, b = parse_addition(query)
    answer = await call_add_tool(a, b)
    return {
        "query": query,
        "tool": "add",
        "transport": "in-memory",
        "mcp_sse_endpoint": MCP_SSE_URL,
        "answer": answer,
    }
