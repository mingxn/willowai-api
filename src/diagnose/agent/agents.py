from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from src.pinecone import pinecone_service
from agno.models.openai.chat import OpenAIChat

master_agent = Agent(
    name="Master Agent",
    role="You are the master orchestrator. Your job is to take a plant image, get a preliminary disease name, delegate tasks to other agents, and synthesize their results. Communicate using clear, concise Markdown.",
    model=OpenAIChat(id="GPT-4o-mini")
)

security_agent = Agent(
    name="Security Agent",
    role="""You are a security specialist responsible for validating image content and plant legality. Your tasks are:
    1. Verify if the uploaded image contains a plant (not animals, people, objects, etc.)
    2. Check if the identified plant is specifically illegal or prohibited (NOT just any plant)
    3. Return a JSON response with validation results
    
    Response format:
    {
        "is_plant_image": true/false,
        "is_legal_plant": true/false,
        "plant_type": "plant name or 'unknown'",
        "security_notes": "explanation of any concerns",
        "allow_processing": true/false
    }
    
    ONLY flag these SPECIFIC illegal plants: Cannabis/Marijuana, Opium Poppy (Papaver somniferum), Peyote cactus, Khat, Coca plants.
    
    ALLOW ALL of these common plants: tomatoes, peppers, cucumbers, lettuce, herbs, houseplants, flowers, fruit trees (apple, orange, etc), vegetables, garden plants, ornamental plants, succulents, ferns, etc.
    
    Be PERMISSIVE - only set is_legal_plant to false if you can definitively identify one of the specific illegal plants listed above. For all other plants including food crops, vegetables, fruits, herbs, houseplants, and ornamental plants, set is_legal_plant to true.
    
    If uncertain about plant identification, default to allowing processing (is_legal_plant: true) unless you can clearly identify illegal species.""",
    tools=[DuckDuckGoTools()],
    model=OpenAIChat(id="GPT-4o-mini")
)

disease_querier = Agent(
    name="Disease Querier",
    role="You are a specialist in querying a vector database of plant diseases. Given a disease name, you will return relevant information. Communicate using clear, concise Markdown.",
    tools=[pinecone_service.query_disease_info],
    model=OpenAIChat(id="GPT-4o-mini")
)

diagnosis_generator = Agent(
    name="Diagnosis Generator",
    role="""You are a plant disease expert. Your primary goal is to provide a detailed diagnosis based on the provided plant name, condition, image description, and context. You will ONLY provide the diagnosis text, without any additional formatting or action plan. Communicate using clear, concise Markdown.""",
    tools=[DuckDuckGoTools()],
    model=OpenAIChat(id="GPT-4o-mini")
)

action_plan_generator = Agent(
    name="Action Plan Generator",
    role="""You are a plant care expert. Given a plant name, condition, diagnosis, and additional context, your goal is to provide a clear, step-by-step action plan to help the plant recover or thrive. Communicate using clear, concise Markdown.""",
    model=OpenAIChat(id="GPT-4o-mini")
)

evaluation_agent = Agent(
    name="Evaluation Agent",
    role="""You are a quality control specialist. Your job is to review a diagnosis and action plan for clarity, accuracy, and tone. You will then format the final, user-facing response as clear, readable Markdown text, including the plant name and condition.""",
    model=OpenAIChat(id="GPT-4o-mini")
)

parser_agent = Agent(
    name="Parser Agent",
    role="""You are a data formatting specialist. Your task is to take the provided plant name, condition, diagnosis, and action plan (as text) and convert it into a structured JSON object. The JSON must adhere to the following format:

```json
{
  "plant_name": "[Plant Name]",
  "condition": "[Healthy or Disease Name]",
  "detail_diagnosis": "[Detailed Diagnosis Text]",
  "action_plan": [
    {"id": 1, "action": "[Action Step 1]"},
    {"id": 2, "action": "[Action Step 2]"}
  ]
}
```

Ensure that each action step has a unique 'id'. If no specific diagnosis or action plan is found, provide empty arrays for 'action_plan' and appropriate default values for other fields.""",
    model=OpenAIChat(id="GPT-4o-mini")
)

