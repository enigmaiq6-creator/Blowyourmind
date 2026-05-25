import os
from google.genai import Client, types

client = Client(
    vertexai=True,
    project=os.getenv("GCP_PROJECT_ID", "automatizacion-475715"),
    location="us-central1"
)

response = client.models.generate_images(
    model='imagen-3.0-generate-001',
    prompt="A red ball",
    config=types.GenerateImagesConfig(
        number_of_images=1,
    )
)

print(dir(response.generated_images[0]))
