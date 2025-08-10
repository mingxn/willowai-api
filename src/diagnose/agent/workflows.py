

from agno.workflow import Workflow
from .agents import master_agent, disease_querier, diagnosis_generator, action_plan_generator, evaluation_agent, parser_agent, security_agent
from src.diagnose.utils import get_initial_plant_info, get_image_description
import base64
import json

def diagnosis_workflow(image_bytes: bytes) -> str:
    # 1. Get textual description of the image
    image_description = get_image_description(image_bytes)

    # 2. Security validation - check if image is plant-related and legal
    security_check = security_agent.run(
        f"Please validate this image description for plant content and legality: {image_description}"
    )
    
    try:
        security_result = json.loads(security_check.content)
    except json.JSONDecodeError:
        # If security agent doesn't return valid JSON, create a default response
        security_result = {
            "is_plant_image": False,
            "is_legal_plant": False,
            "plant_type": "unknown",
            "security_notes": "Unable to validate image content",
            "allow_processing": False
        }
    
    # Check if processing should continue based on security validation
    if not security_result.get("allow_processing", False):
        # Determine specific error type and create appropriate response
        is_plant_image = security_result.get("is_plant_image", False)
        is_legal_plant = security_result.get("is_legal_plant", False)
        plant_type = security_result.get("plant_type", "unknown")
        security_notes = security_result.get("security_notes", "Unknown security issue")
        
        if not is_plant_image:
            # Image is not plant-related
            error_response = {
                "plant_name": "Not a Plant",
                "condition": "Invalid Image Content",
                "detail_diagnosis": "The uploaded image does not appear to contain a plant. Please upload a clear image of a plant for diagnosis.",
                "action_plan": [
                    {"id": 1, "action": "Upload an image that clearly shows a plant"},
                    {"id": 2, "action": "Ensure the plant is the main subject of the image"},
                    {"id": 3, "action": "Use good lighting and focus for better plant identification"}
                ]
            }
        elif is_plant_image and not is_legal_plant:
            # Plant is specifically illegal/prohibited (Cannabis, Opium Poppy, etc.)
            error_response = {
                "plant_name": plant_type,
                "condition": "Prohibited Plant Species",
                "detail_diagnosis": f"The identified plant ({plant_type}) is specifically prohibited and illegal in most jurisdictions. This service cannot provide diagnosis or care advice for controlled substances or illegal plants. {security_notes}",
                "action_plan": [
                    {"id": 1, "action": "Please upload an image of a legal plant such as houseplants, vegetables, fruits, or garden plants"},
                    {"id": 2, "action": "Common allowed plants include tomatoes, peppers, herbs, flowers, succulents, and ornamental plants"},
                    {"id": 3, "action": "Ensure compliance with local laws regarding plant cultivation"}
                ]
            }
        else:
            # Generic security failure
            error_response = {
                "plant_name": "Security Check Failed",
                "condition": "Invalid Content",
                "detail_diagnosis": f"Security validation failed: {security_notes}",
                "action_plan": [
                    {"id": 1, "action": "Please upload a clear image of a legal plant for diagnosis"}
                ]
            }
        
        return json.dumps(error_response)
    
    # 3. Get initial plant info (name and condition) using the utility function
    initial_plant_info_json = get_initial_plant_info(image_description)
    initial_plant_info = json.loads(initial_plant_info_json)
    plant_name = initial_plant_info.get("plant_name", "Unknown Plant")
    condition = initial_plant_info.get("condition", "Unknown Condition")

    context = ""
    # Check if the plant is healthy based on the initial diagnosis
    if condition.lower() == "healthy":
        context = "The plant appears to be healthy. No specific disease context is available."
    else:
        # 4. Disease querier gets context from Pinecone
        pinecone_results = disease_querier.run(condition)
        if pinecone_results and pinecone_results.content:
            context = pinecone_results.content
        else:
            context = f"No specific information found for '{condition}' in the knowledge base."

    # 5. Diagnosis generator creates a diagnosis using the image description
    diagnosis = diagnosis_generator.run(
        f"Plant Name: {plant_name}\nCondition: {condition}\nImage Description: {image_description}. "
        f"Here is some context about a potential issue: {context}. "
        f"Please provide a detailed diagnosis. Do NOT provide an exact action plan. Communicate in Markdown."
    ).content

    # 6. Action plan generator creates the action plan
    action_plan = action_plan_generator.run(
        f"Given the following diagnosis: {diagnosis}. "
        f"And this context: {context}. "
        f"Please provide a step-by-step action plan to help the plant. If the plant is healthy, provide general care tips. Communicate in Markdown."
    ).content

    # 7. Evaluation agent refines the output
    evaluated_text_output = evaluation_agent.run(
        f"Please review the following diagnosis and action plan for clarity, accuracy, and tone. "
        f"Plant Name: {plant_name}\nCondition: {condition}\nDiagnosis: {diagnosis}\nAction Plan: {action_plan}"
    ).content

    # 8. Parser agent formats the output as JSON
    final_json_output_raw = parser_agent.run(
        f"Plant Name: {plant_name}\nCondition: {condition}\nDiagnosis: {diagnosis}\nAction Plan: {action_plan}"
    ).content

    # Extract JSON string from Markdown code block
    if final_json_output_raw.startswith("```json") and final_json_output_raw.endswith("```"):
        final_json_output = final_json_output_raw[len("```json\n"):-len("```")].strip()
    else:
        final_json_output = final_json_output_raw.strip()

    return final_json_output

