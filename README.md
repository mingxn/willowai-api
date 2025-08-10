# Willow.ai Server

This is the server for the Willow.ai application, built with FastAPI.

## AI Models

The application utilizes the `GPT-4o-mini` model for its AI-powered diagnosis features and Pinecone for vector database operations to store and retrieve plant disease information.

## Local Setup

1.  **Prerequisites:**
    *   Python 3.9+
    *   PostgreSQL
    *   Pinecone API Key

2.  **Installation:**

    *   Clone the repository.
    *   Create and activate a virtual environment:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    *   Install the required dependencies:
        ```bash
        pip install -r requirements/base.txt
        ```

3.  **Configuration:**

    *   Copy the environment template file:
        ```bash
        cp .env-template .env
        ```
    *   Create a PostgreSQL database named `willow`.
    *   Update the `.env` file with your credentials:
        *   Set your database URL: `DATABASE_URL=postgresql://user:password@localhost/willow`
        *   Set your OpenAI API key: `OPENAI_API_KEY=your_openai_api_key_here`
        *   Set your Pinecone API key: `PINECONE_API_KEY=your_pinecone_api_key_here`
        *   Configure Pinecone environment if different from default: `PINECONE_ENVIRONMENT=us-east-1-aws`


4.  **Initialize Data Source**

    The source of trust data is partial of the [PlantDoc Dataset](https://github.com/pratikkayal/PlantDoc-Dataset), piped to `data/` folder which is ingested into the vector store using the `data/load.py` script. This dataset contains labeled plant disease images that serve as the knowledge base for plant diagnosis.

    To load the training data into your Pinecone vector store:
    ```bash
    python data/load.py
    ```

4.  **Running the Application:**

    ```bash
    uvicorn src.main:app --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

## Agent architecture
```mermaid
graph TD
    subgraph Diagnosis Workflow Agents
        A[Image Input] --> B{Initial Image Processing}
        B -->|Image Description| C[security_agent Agent]
        C -->|Security Validation| D{Security Check}
        D -->|Pass| E[disease_querier Agent]
        D -->|Fail| I[Security Error Response]
        E -->|Pinecone Context| F[diagnosis_generator Agent]
        F -->|Diagnosis Text| G[action_plan_generator Agent]
        G -->|Action Plan Text| H[evaluation_agent Agent]
        H -->|Evaluated Text Output| J[parser_agent Agent]
        J -->|Final JSON Output| K[API Response]
    end

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#ff9999,stroke:#333,stroke-width:2px
    style D fill:#ff9999,stroke:#333,stroke-width:2px
    style I fill:#ffcccc,stroke:#333,stroke-width:2px
    style K fill:#f9f,stroke:#333,stroke-width:2px

    %% Notes on B (Initial Image Processing)
    subgraph Notes
        note1[Note: Initial Image Processing includes utility functions like get_image_description and get_initial_plant_info.]
        note2[Note: Security Agent validates if image contains plants and checks for illegal/prohibited species.]
    end
    B --- note1
    C --- note2
```

## Data Sources

### Training Data
The source of trust data is partial of the [PlantDoc Dataset](https://github.com/pratikkayal/PlantDoc-Dataset), piped to `data/` folder which is ingested into the vector store using the `data/load.py` script. This dataset contains labeled plant disease images that serve as the knowledge base for plant diagnosis.

To load the training data into your Pinecone vector store:
```bash
python data/load.py
```

### Test Data
Test data is located under `tests/data/` and covers 4 specific test cases:

1. **Unknown plant condition**: `tomato.jpeg` - User uploads data which could not be found in source of trust
2. **Known plant disease**: `early_blight_tomato.jpg` - User uploads data which can be found in source of trust  
3. **Non-plant image**: `anh-nguoi-mau-27.jpg` - User uploads other image not related to plant
4. **Illegal plant**: `illegal.webp` - User uploads illegal plant

These test cases help validate the security agent, disease querying, and overall diagnosis workflow.

## API Endpoints

*   **POST** `/diagnose`: Upload an image of a plant to get a diagnosis and action plan.