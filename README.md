# Willow.ai Server

This is the server for the Willow.ai application, built with FastAPI.

## Local Setup

1.  **Prerequisites:**
    *   Python 3.9+
    *   PostgreSQL
    *   [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver)

2.  **Installation:**

    *   Clone the repository.
    *   Create and activate a virtual environment using `uv`:
        ```bash
        uv venv
        source .venv/bin/activate
        ```
    *   Install the required dependencies using `uv`:
        ```bash
        uv pip install -r requirements/base.txt
        ```

3.  **Database Setup:**

    *   Create a PostgreSQL database named `willow`.
    *   Create a `.env` file in the `server` directory and add the following line, replacing the credentials with your own:
        ```
        DATABASE_URL=postgresql://user:password@localhost/willow
        ```

4.  **Running the Application:**

    ```bash
    uvicorn src.main:app --reload --app-dir server
    ```

    The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

### AI Plant Doctor

*   **POST** `/diagnose`: Upload an image of a plant to get a diagnosis and action plan.

### Personal Care Assistant

*   **POST** `/plants`: Add a new plant to your collection.
*   **GET** `/plants`: Get a list of all plants in your collection.
*   **GET** `/schedule`: Get the dynamic care schedule for your plants.

### Green Space Planner

*   **POST** `/recommendations`: Get plant recommendations based on your environment and preferences.
*   **GET** `/models/{plant_name}`: Get the 3D model for a specific plant.