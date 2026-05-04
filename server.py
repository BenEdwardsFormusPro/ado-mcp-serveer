from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import requests
import os
import json

app = FastAPI()

AZDO_ORG = "formuspro"
AZDO_PROJECT = os.getenv("AZDO_PROJECT")

@app.api_route("/", methods=["GET", "HEAD", "OPTIONS", "POST"])
def root():
    return {"status": "ok", "service": "ado-mcp-server"}

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

@app.get("/debug")
def debug():
    return {
        "AZDO_ORG": AZDO_ORG,
        "AZDO_PROJECT": AZDO_PROJECT
    }

@app.post("/mcp")
async def mcp_handler(request: Request):
    try:
        body = await request.json()
    except:
        body = {}

    tool = body.get("tool") or body.get("name")
    request_id = body.get("id", 1)

    if tool == "get_projects":

        url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"

        try:
            import requests
            res = requests.get(url)

            content = res.json() if "application/json" in res.headers.get("content-type", "") else res.text

            return {
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(content)
                        }
                    ]
                }
            }

        except Exception as e:
            return {
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Azure DevOps call failed: {str(e)}"
                        }
                    ]
                }
            }

    return {
        "id": request_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": f"Unknown tool: {tool}"
                }
            ]
        }
    }