from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

AZDO_ORG = os.getenv("AZDO_ORG")
AZDO_PROJECT = os.getenv("AZDO_PROJECT")

@app.get("/")
def root():
    return {"status": "MCP server running"}

@app.get("/.well-known/mcp")
def mcp_manifest():
    return {
        "name": "ado-mcp-server",
        "version": "1.0",
        "description": "Azure DevOps MCP server",
        "tools": [
            {
                "name": "get_projects",
                "description": "Get Azure DevOps projects in an organization",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    }

@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()

    access_token = request.headers.get("authorization", "").replace("Bearer ", "")

    if not access_token:
        return {"error": "Missing token"}

    tool = body.get("tool") or body.get("name")
    args = body.get("arguments") or body.get("input") or {}

    if tool == "get_projects":

        url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"

        res = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        return {
            "tool": tool,
            "result": res.json()
        }

    return {"error": f"Unknown tool: {tool}"}