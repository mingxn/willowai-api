

from agno.workflow import Workflow
from .agents import master_agent, disease_querier, diagnosis_generator, action_plan_generator, evaluation_agent, parser_agent
from src.diagnose.utils import get_initial_disease_name, get_image_description
import base64
import json

def diagnosis_workflow(image_bytes: bytes) -> str:
    # 1. Get textual description of the image
    image_description = get_image_description(image_bytes)

    # 2. Get initial disease name using the utility function with the image description
    disease_name = get_initial_disease_name(image_description)

    context = ""
    # Check if the plant is healthy based on the initial diagnosis
    if disease_name == "HEALTHY_PLANT":
        context = "The plant appears to be healthy. No specific disease context is available."
    else:
        # 3. Disease querier gets context from ChromaDB
        chroma_results = disease_querier.run(disease_name)
        if chroma_results and chroma_results["documents"]:
            context = "\n".join(chroma_results["documents"][0])
        else:
            context = f"No specific information found for '{disease_name}' in the knowledge base."

    # 4. Diagnosis generator creates a diagnosis using the image description
    diagnosis = diagnosis_generator.run(
        f"Here is a description of a plant: {image_description}. "
        f"Here is some context about a potential issue: {context}. "
        f"Please provide a detailed diagnosis. Do NOT provide an exact action plan. Communicate in Markdown."
    ).content

    # 5. Action plan generator creates the action plan
    action_plan = action_plan_generator.run(
        f"Given the following diagnosis: {diagnosis}. "
        f"And this context: {context}. "
        f"Please provide a step-by-step action plan to help the plant. If the plant is healthy, provide general care tips. Communicate in Markdown."
    ).content

    # 6. Evaluation agent refines the output
    evaluated_text_output = evaluation_agent.run(
        f"Please review the following diagnosis and action plan for clarity, accuracy, and tone. "
        f"Diagnosis: {diagnosis}\nAction Plan: {action_plan}"
    ).content

    # 7. Parser agent formats the output as JSON
    final_json_output_raw = parser_agent.run(
        f"Format the following text into JSON: {evaluated_text_output}"
    ).content

    # Extract JSON string from Markdown code block
    if final_json_output_raw.startswith("```json") and final_json_output_raw.endswith("```"):
        final_json_output = final_json_output_raw[len("```json\n"):-len("```")].strip()
    else:
        final_json_output = final_json_output_raw.strip()

    return final_json_output

