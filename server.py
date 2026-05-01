from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

AZDO_ORG = os.getenv("AZDO_ORG")
AZDO_PROJECT = os.getenv("AZDO_PROJECT")

@app.get("/")
def root():
    return {"status": "MCP server running"}

@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()

    access_token = request.headers.get("authorization", "").replace("Bearer ", "")

    if not access_token:
        return {"error": "Missing token"}

    # Simple test call to Azure DevOps
    url = f"https://dev.azure.com/{AZDO_ORG}/_apis/projects?api-version=7.0"

    res = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    return {
        "status": res.status_code,
        "data": res.json()
    }