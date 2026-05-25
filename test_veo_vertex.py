import os
import time
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project=os.getenv("GCP_PROJECT_ID", "automatizacion-475715"),
    location="us-central1"
)

try:
    print("Testing generate_videos on Vertex AI...")
    operation = client.models.generate_videos(
        model='veo-2.0-generate-001',
        prompt="A stickman dancing",
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
        )
    )
    print("Operation started:", operation.name)
    
    while not operation.done:
        print("Polling...")
        time.sleep(10)
        operation = client.operations.get(operation)
        
    print("Operation done!")
    if operation.error:
        print("Error:", operation.error)
    else:
        response = operation.response
        print("Response:", response)
        video = response.generated_videos[0].video
        print("Video object:", video)
        print("Attributes of video:", dir(video))
        # video.save("test_video.mp4") # Let's see if this works
except Exception as e:
    print("Error:", e)
