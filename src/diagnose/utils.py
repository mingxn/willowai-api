import base64
from openai import OpenAI
from src.config import settings
import json

embedding_client = OpenAI(api_key=settings.OPENAI_EMBEDDING_API_KEY, base_url=settings.OPENAI_BASE_URL)

def get_embedding(text: str) -> list[float]:
    response = embedding_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

def get_image_description(image_bytes: bytes) -> str:
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that describes the key visual characteristics of a plant from an image, focusing on its health and any visible issues. Be concise and objective."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this plant image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()

def get_initial_plant_info(image_description: str) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that identifies the plant name and its condition (healthy or disease name) from a description. Respond with a JSON string like: { \"plant_name\": \"[Plant Name]\", \"condition\": \"[Healthy or Disease Name]\" }. If the plant appears healthy, set condition to 'healthy'."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Identify the plant name and its condition from this description: {image_description}"},
                ],
            }
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()
