from fastapi import FastAPI, Request
from fastapi.responses import Response
import requests
import os
import json
import base64

app = FastAPI()

AZDO_ORG = os.getenv("AZDO_ORG")
AZDO_PAT = os.getenv("AZDO_PAT")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/.well-known/mcp")
def manifest():
    return {
        "name": "ado-mcp-server",
        "version": "1.0",
        "description": "Azure DevOps MCP server",
        "tools": [
            {
                "name": "get_projects",
                "description": "Get Azure DevOps projects",
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
    tool = body.get("tool")
    request_id = body.get("id", 1)

    if not AZDO_PAT or not AZDO_ORG:
        payload = {
            "id": request_id,
            "result": {
                "content": [
                    {"type": "text", "text": "Missing AZDO_PAT or AZDO_ORG"}
                ]
            }
        }
        return Response(
            content="data: " + json.dumps(payload) + "\n\n",
            media_type="text/event-stream"
        )

    token = base64.b64encode(f":{AZDO_PAT}".encode()).decode()

    headers = {
        "Authorization": f"Basic {token}"
    }

    try:

        if tool == "get_projects":

            url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"
            res = requests.get(url, headers=headers)

            payload = {
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": res.text
                        }
                    ]
                }
            }

        else:

            payload = {
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

    except Exception as e:

        payload = {
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": str(e)
                    }
                ]
            }
        }

    return Response(
        content="data: " + json.dumps(payload) + "\n\n",
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )