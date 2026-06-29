import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing /api/v1/ai/executive-summary")
response = client.get("/api/v1/ai/executive-summary")
print("Status:", response.status_code)
print("Response:", response.text)
