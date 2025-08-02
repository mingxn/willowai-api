
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from src.chroma import chroma_service
from agno.models.openai.chat import OpenAIChat

master_agent = Agent(
    name="Master Agent",
    role="You are the master orchestrator. Your job is to take a plant image, get a preliminary disease name, delegate tasks to other agents, and synthesize their results. Communicate using clear, concise Markdown.",
    model=OpenAIChat(id="GPT-4o-mini")
)

disease_querier = Agent(
    name="Disease Querier",
    role="You are a specialist in querying a vector database of plant diseases. Given a disease name, you will return relevant information. Communicate using clear, concise Markdown.",
    tools=[chroma_service.query_disease_info],
    model=OpenAIChat(id="GPT-4o-mini")
)

diagnosis_generator = Agent(
    name="Diagnosis Generator",
    role="""You are a plant disease expert. Your primary goal is to provide a detailed diagnosis based on the provided image description and context. You will ONLY provide the diagnosis text, without any additional formatting or action plan. Communicate using clear, concise Markdown.""",
    tools=[DuckDuckGoTools()],
    model=OpenAIChat(id="GPT-4o-mini")
)

action_plan_generator = Agent(
    name="Action Plan Generator",
    role="""You are a plant care expert. Given a diagnosis and additional context, your goal is to provide a clear, step-by-step action plan to help the plant recover or thrive. Communicate using clear, concise Markdown.""",
    model=OpenAIChat(id="GPT-4o-mini")
)

evaluation_agent = Agent(
    name="Evaluation Agent",
    role="You are a quality control specialist. Your job is to review a diagnosis and action plan for clarity, accuracy, and tone. You will then format the final, user-facing response as clear, readable Markdown text.",
    model=OpenAIChat(id="GPT-4o-mini")
)

parser_agent = Agent(
    name="Parser Agent",
    role="""You are a data formatting specialist. Your task is to take a diagnosis and action plan provided as text and convert it into a structured JSON object. The JSON must adhere to the following format:

```json
{
  "diagnoses": [
    {"id": 1, "diagnosis": "..."},
    {"id": 2, "diagnosis": "..."}
  ],
  "action_plan": [
    {"id": 1, "action": "..."},
    {"id": 2, "action": "..."}
  ]
}
```

Ensure that each diagnosis and action step has a unique 'id'. If there's only one diagnosis or action, it should still be in an array. If no specific diagnosis or action plan is found, provide empty arrays for 'diagnoses' and 'action_plan'.""",
    model=OpenAIChat(id="GPT-4o-mini")
)

