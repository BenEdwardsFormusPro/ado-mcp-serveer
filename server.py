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

    request_id = 1
    tool = None

    try:
        raw = await request.body()
        if raw:
            data = json.loads(raw.decode("utf-8"))
        else:
            data = {}

        request_id = data.get("id", 1)
        tool = data.get("tool")

    except Exception as e:
        return mcp_response(request_id, f"Invalid request: {str(e)}")

    if not AZDO_ORG or not AZDO_PAT:
        return mcp_response(request_id, "Missing AZDO_ORG or AZDO_PAT")

    headers = auth_header()

    try:

        if tool == "get_projects":

            url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"
            res = requests.get(url, headers=headers, timeout=10)

            return mcp_response(
                request_id,
                json.dumps(res.json(), indent=2)
            )

        return mcp_response(request_id, f"Unknown tool: {tool}")

    except Exception as e:
        return mcp_response(request_id, str(e))