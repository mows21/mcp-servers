#!/usr/bin/env python3
"""
Cline MCP Server - Internal workflow orchestration for agentic tasks
"""
import asyncio
import json
import sqlite3
import subprocess
import uuid
from typing import Any, Dict, List, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Initialize FastAPI app with MCP support
app = FastAPI(title="Cline MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = Path(__file__).parent / "data" / "cline.db"
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            key TEXT PRIMARY KEY,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT,
            config TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Models
class AgentTask(BaseModel):
    task: str
    input: str
    tool: str = "gpt4"
    context: str = "internal"

class WorkflowRequest(BaseModel):
    workflow_id: str
    trigger: str = "n8n"
    inputs: Dict[str, Any] = {}

class ExecCommand(BaseModel):
    command: str
    args: List[str] = []
    working_dir: Optional[str] = None

class MemoryItem(BaseModel):
    key: str
    value: Any

# Memory operations
def get_memory(key: str) -> Optional[Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

def set_memory(key: str, value: Any):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)",
        (key, json.dumps(value))
    )
    conn.commit()
    conn.close()

# MCP Protocol Endpoints
@app.all("/mcp")
async def mcp_endpoint(request: Request, authorization: Optional[str] = Header(None)):
    """Unified MCP endpoint for JSON-RPC communication"""
    if request.method == "GET":
        # Handle SSE connection
        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    if request.method == "POST":
        # Handle JSON-RPC requests
        try:
            body = await request.json()
            method = body.get("method")
            params = body.get("params", {})
            
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "run_agent_task",
                                "description": "Execute an agent task",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task": {"type": "string"},
                                        "input": {"type": "string"},
                                        "tool": {"type": "string"}
                                    }
                                }
                            },
                            {
                                "name": "execute_workflow",
                                "description": "Execute a workflow",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "workflow_id": {"type": "string"},
                                        "inputs": {"type": "object"}
                                    }
                                }
                            },
                            {
                                "name": "run_command",
                                "description": "Execute a system command",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {"type": "string"},
                                        "args": {"type": "array"}
                                    }
                                }
                            }
                        ]
                    }
                }
            
            return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32601, "message": "Method not found"}}
            
        except Exception as e:
            return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32000, "message": str(e)}}

async def generate_sse():
    """Generate Server-Sent Events for SSE transport"""
    while True:
        # Send periodic keep-alive events
        yield f"event: ping\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"
        await asyncio.sleep(30)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker containers"""
    try:
        # Test database connection
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
