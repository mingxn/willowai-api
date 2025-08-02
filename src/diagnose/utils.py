import base64
from openai import OpenAI
from src.config import settings

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

def get_initial_disease_name(image_description: str) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that identifies the name of a plant disease from a description. If the description suggests the plant appears healthy, respond with 'HEALTHY_PLANT'. Otherwise, respond with only the name of the disease."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"What is the name of the disease described here: {image_description}"},
                ],
            }
        ],
        max_tokens=50,
    )
    return response.choices[0].message.content.strip()
