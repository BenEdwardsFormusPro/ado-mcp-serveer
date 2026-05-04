from fastapi import FastAPI, Request
import requests
import os
import json
import base64

app = FastAPI()

AZDO_ORG = os.getenv("AZDO_ORG")
AZDO_PAT = os.getenv("AZDO_PAT")


def make_auth_header():
    token = base64.b64encode(f":{AZDO_PAT}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@app.get("/")
def root():
    return {"status": "ok", "message": "MCP server running"}


@app.post("/")
async def root_post(request: Request):
    try:
        body = await request.body()
        parsed = json.loads(body.decode("utf-8")) if body else {}
    except:
        parsed = {}

    return {
        "status": "ok",
        "message": "Use /mcp for MCP requests",
        "received": parsed
    }


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

    try:
        body = await request.body()
        data = json.loads(body.decode("utf-8")) if body else {}
    except:
        data = {}

    tool = data.get("tool")
    request_id = data.get("id", 1)

    if not AZDO_ORG or not AZDO_PAT:
        return {
            "id": request_id,
            "error": "Missing AZDO_ORG or AZDO_PAT"
        }

    headers = make_auth_header()

    try:

        if tool == "get_projects":

            url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"
            res = requests.get(url, headers=headers)

            result_text = res.text

            payload = {
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
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

    return payload