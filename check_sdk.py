import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = Client(
    vertexai=True,
    project=os.getenv("GCP_PROJECT_ID"),
    location="us-central1"
)

print("Methods in client.models:")
print(dir(client.models))
