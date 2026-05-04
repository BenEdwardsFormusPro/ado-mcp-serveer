from fastapi import FastAPI, Request
import requests
import os
import json
import base64

app = FastAPI()

AZDO_ORG = os.getenv("AZDO_ORG")
AZDO_PAT = os.getenv("AZDO_PAT")


def auth_header():
    token = base64.b64encode(f":{AZDO_PAT}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def mcp_response(request_id, text):
    return {
        "id": request_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    }


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/")
async def root_post(request: Request):
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
    try:
        data = await request.json()
    except:
        data = {}

    request_id = data.get("id")

    if request_id is None:
        request_id = 1

    tool = data.get("tool")

    if tool == "get_projects":
        url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"
        res = requests.get(url, headers=auth_header(), timeout=10)

        return {
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