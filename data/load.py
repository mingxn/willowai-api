import os
import sys
import json
import base64
from openai import OpenAI

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import settings
from src.pinecone import pinecone_service

def extract_plant_and_condition_from_folder(folder_name: str):
    """
    Extract plant name and condition from folder name format: {plant}_{condition/disease_name}
    Example: 'apple_rust_leaf' -> ('apple', 'rust leaf')
    """
    parts = folder_name.split('_')
    if len(parts) < 2:
        return "Unknown Plant", "Unknown Condition"
    
    plant_name = parts[0].replace('_', ' ').title()
    condition_parts = parts[1:]
    
    # Remove 'leaf' if it's at the end as it's redundant for plant diseases
    if condition_parts[-1].lower() == 'leaf':
        condition_parts = condition_parts[:-1]
    
    condition = ' '.join(condition_parts).replace('_', ' ').title()
    
    # Handle special cases for healthy plants
    if 'healthy' in condition.lower():
        condition = 'Healthy'
    
    return plant_name, condition

def get_plant_analysis_with_openai(image_bytes: bytes, plant_name: str, condition: str) -> str:
    """
    Use OpenAI GPT-4o-mini to analyze the plant image with context of plant name and condition
    """
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    
    prompt = f"""
You are analyzing a plant image with the following context:
Plant Name: {plant_name}
Condition: {condition}

Please provide a detailed analysis in the following format:
plant name: [Plant Name]
condition: [Condition/Disease Name]
image description: [Detailed description of what you see in the image, focusing on visual symptoms, leaf appearance, color changes, spots, patterns, etc.]

Be specific about visual characteristics and symptoms you observe.
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a plant pathology expert. Analyze plant images and provide detailed descriptions of symptoms and conditions."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

def load_image_data_to_pinecone(image_path: str, folder_name: str):
    """
    Load image data to Pinecone vector store with only diagnosis (no action plan)
    """
    try:
        # Extract plant name and condition from folder name
        plant_name, condition = extract_plant_and_condition_from_folder(folder_name)
        
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Get analysis from OpenAI with context
        analysis = get_plant_analysis_with_openai(image_bytes, plant_name, condition)
        
        # Prepare document content for vector storage (only diagnosis, no action plan)
        document_content = f"Plant Name: {plant_name}\nCondition: {condition}\nAnalysis: {analysis}"
        
        metadata = {
            "plant_name": plant_name, 
            "condition": condition,
            "source": "training_data"
        }
        
        # Create unique document ID
        doc_id = f"{plant_name.replace(' ', '_').lower()}_{condition.replace(' ', '_').lower()}_{os.path.basename(image_path)}"

        # Add to Pinecone (will automatically use text-embedding-3-small for embeddings)
        pinecone_service.add_disease_info({
            "document": document_content,
            "metadata": metadata,
            "id": doc_id
        })
        
        print(f"✓ Loaded: {plant_name} ({condition}) - {os.path.basename(image_path)}")
        
    except Exception as e:
        print(f"✗ Error processing {image_path}: {str(e)}")

if __name__ == "__main__":
    data_dir = "data"
    
    print("Starting data loading process...")
    print("=" * 60)
    
    # Process each folder in the data directory
    for folder_name in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder_name)
        
        # Skip non-directories and hidden folders
        if not os.path.isdir(folder_path) or folder_name.startswith('.') or folder_name == '__pycache__':
            continue
            
        print(f"\nProcessing folder: {folder_name}")
        
        # Extract plant and condition info from folder name
        plant_name, condition = extract_plant_and_condition_from_folder(folder_name)
        print(f"Plant: {plant_name}, Condition: {condition}")
        
        # Process each image in the folder
        image_count = 0
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                image_path = os.path.join(folder_path, filename)
                load_image_data_to_pinecone(image_path, folder_name)
                image_count += 1
                
                # Limit to first 10 images per folder to avoid overwhelming the system
                if image_count >= 10:
                    print(f"  (Processed first 10 images, skipping remaining)")
                    break
        
        if image_count == 0:
            print(f"  No images found in {folder_name}")
            
    print("\n" + "=" * 60)
    print("Data loading completed!")
