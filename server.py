from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import requests
import os
import json

app = FastAPI()

AZDO_ORG = os.getenv("AZDO_ORG")
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

@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()

    tool = body.get("tool") or body.get("name")
    request_id = body.get("id", 1)

    auth_header = request.headers.get("authorization", "")
    access_token = auth_header.replace("Bearer ", "") if auth_header else None

    def stream():

        try:
            if tool != "get_projects":
                yield f"event: message\ndata: {json.dumps({
                    'id': request_id,
                    'result': {
                        'content': [{
                            'type': 'text',
                            'text': f'Unknown tool: {tool}'
                        }]
                    }
                })}\n\n"
                return

            if not AZDO_ORG:
                yield f"event: message\ndata: {json.dumps({
                    'id': request_id,
                    'result': {
                        'content': [{
                            'type': 'text',
                            'text': 'AZDO_ORG not configured'
                        }]
                    }
                })}\n\n"
                return

            url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"

            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"

            res = requests.get(url, headers=headers)

            content = res.json() if "application/json" in res.headers.get("content-type", "") else res.text

            yield f"event: message\ndata: {json.dumps({
                'id': request_id,
                'result': {
                    'content': [{
                        'type': 'text',
                        'text': str(content)
                    }]
                }
            })}\n\n"

        except Exception as e:
            yield f"event: message\ndata: {json.dumps({
                'id': request_id,
                'result': {
                    'content': [{
                        'type': 'text',
                        'text': f'Error: {str(e)}'
                    }]
                }
            })}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")