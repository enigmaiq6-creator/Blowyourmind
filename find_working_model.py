import os
import sys
from google.genai import Client, errors
from dotenv import load_dotenv

load_dotenv()
project_id = os.getenv("GCP_PROJECT_ID")
location = os.getenv("GCP_LOCATION", "us-central1")

client = Client(vertexai=True, project=project_id, location=location)

models_to_try = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-002",
    "gemini-2.0-flash-exp",
    "gemini-3-flash-preview",
    "gemini-3-pro-preview"
]

print(f"Testing models in {location}...")

for model_name in models_to_try:
    try:
        print(f"Trying {model_name}...", end=" ", flush=True)
        response = client.models.generate_content(model=model_name, contents="ping")
        print("SUCCESS!")
        print(f"Working model found: {model_name}")
        break
    except Exception as e:
        print(f"FAILED (Error: {str(e)[:50]}...)")
else:
    print("\nNo working models found in this project/location.")
