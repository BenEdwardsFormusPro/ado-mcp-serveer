from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

AZDO_ORG = os.getenv("AZDO_ORG")
AZDO_PROJECT = os.getenv("AZDO_PROJECT")

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "ado-mcp-server"
    }

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
    try:
        body = await request.json()

        tool = body.get("tool") or body.get("name")
        args = body.get("arguments") or body.get("input") or {}

        auth_header = request.headers.get("authorization", "")
        access_token = auth_header.replace("Bearer ", "") if auth_header else None

        if tool == "get_projects":

            if not AZDO_ORG:
                return {
                    "error": "AZDO_ORG environment variable not set"
                }

            url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"

            headers = {}

            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"

            res = requests.get(url, headers=headers)

            content_type = res.headers.get("content-type", "")

            if "application/json" in content_type:
                data = res.json()
            else:
                data = res.text

            return {
                "tool": tool,
                "status": res.status_code,
                "result": data
            }

        return {
            "error": f"Unknown tool: {tool}",
            "available_tools": ["get_projects"]
        }

    except Exception as e:
        return {
            "error": "MCP handler crashed",
            "details": str(e)
        }