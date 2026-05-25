import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()
project_id = os.getenv("GCP_PROJECT_ID")
location = os.getenv("GCP_LOCATION", "us-central1")

if project_id:
    print(f"Listing models for Vertex AI (Project: {project_id}, Location: {location}):")
    client = Client(vertexai=True, project=project_id, location=location)
else:
    print("Listing models for AI Studio (API Key):")
    api_key = os.getenv("GEMINI_API_KEY")
    client = Client(api_key=api_key)

print("\nAvailable models:")
for model in client.models.list():
    print(f"- {model.name} (supports: {model.supported_actions})")
