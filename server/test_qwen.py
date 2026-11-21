import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv(override=True)

token = os.getenv("HF_TOKEN")

print("HF TOKEN FOUND:", bool(token))

client = InferenceClient(
    provider="fal-ai",
    api_key=token
)

image_path = "uploads/test_portrait.jpg"

with open(image_path, "rb") as f:
    image_bytes = f.read()

prompt = """
Edit ONLY the person's hairstyle.

Create a realistic long layered hairstyle.

Preserve:
- exact person identity
- face
- eyes
- eyebrows
- nose
- lips
- beard and moustache
- skin tone
- facial expression
- glasses
- clothing
- lighting
- background

Do NOT create a new person.
Do NOT modify the face.
Do NOT modify the background.
Only change the hairstyle.
Make the result photorealistic and natural.
"""

print("Sending image to Qwen...")

try:
    result = client.image_to_image(
        image_bytes,
        prompt=prompt,
        model="Qwen/Qwen-Image-Edit"
    )

    output_path = "uploads/qwen_test_output.png"

    result.save(output_path)

    print("SUCCESS")
    print("Output:", output_path)

except Exception as e:
    print("QWEN ERROR:")
    print(type(e).__name__)
    print(str(e))