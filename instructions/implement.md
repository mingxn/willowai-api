# Willow.ai Feature Implementation Plan (FastAPI)

This document outlines the API design for implementing the core features of Willow.ai using the FastAPI framework, following RESTful principles.

## 1. AI Plant Doctor

This feature provides an on-demand expert to diagnose and solve plant health issues.

*   **Feature:** Diagnose a plant health issue.
*   **API Endpoint:** `/diagnose`
*   **HTTP Method:** `POST`
*   **Input:**
    *   `file`: An uploaded image file of the affected plant part (`multipart/form-data`).
*   **Output:**
    *   A JSON object containing the diagnosis and a step-by-step action plan.
    ```json
    {
      "diagnosis": "Powdery Mildew",
      "action_plan": "1. Isolate the plant. 2. Prune affected leaves. 3. Apply fungicide."
    }
    ```

## 2. Personal Care Assistant

This feature automates and simplifies the ongoing task of plant care through smart scheduling and reminders. The API is designed around the concept of a user's plant collection.

*   **Feature:** Add a plant to the user's collection.
*   **API Endpoint:** `/plants`
*   **HTTP Method:** `POST`
*   **Input:**
    *   A JSON object with the plant's details.
    ```json
    {
      "plant_name": "Snake Plant",
      "user_id": "user123"
    }
    ```
*   **Output:**
    *   A JSON object confirming the addition.
    ```json
    {
      "id": "plant_abc123",
      "plant_name": "Snake Plant",
      "user_id": "user123"
    }
    ```

*   **Feature:** Get the user's plant collection.
*   **API Endpoint:** `/plants`
*   **HTTP Method:** `GET`
*   **Input:** None (assumes user is authenticated).
*   **Output:**
    *   A JSON array of the user's plants.
    ```json
    [
        {
          "id": "plant_abc123",
          "plant_name": "Snake Plant",
          "user_id": "user123"
        }
    ]
    ```

*   **Feature:** Get the dynamic care schedule for the user's plants.
*   **API Endpoint:** `/schedule`
*   **HTTP Method:** `GET`
*   **Input:** None (assumes user is authenticated).
*   **Output:**
    *   A JSON object representing the dynamic care schedule.
    ```json
    {
      "schedule": [
        {
          "plant_id": "plant_abc123",
          "plant_name": "Snake Plant",
          "task": "Water",
          "due_date": "2025-08-05"
        }
      ]
    }
    ```

*   **Feature:** Smart Alerts
*   **Implementation:** This is not a direct API endpoint. A background task will run periodically to fetch weather data and send push notifications with context-aware alerts.

## 3. Green Space Planner

This feature helps users discover the ideal plants for their specific environment and aesthetic preferences.

*   **Feature:** Get plant recommendations.
*   **API Endpoint:** `/recommendations`
*   **HTTP Method:** `POST`
*   **Input:**
    *   A JSON object with environmental conditions and preferences.
    ```json
    {
      "environment": {
        "light": "High",
        "humidity": "Medium"
      },
      "experience": "Beginner",
      "style": "Minimalist"
    }
    ```
*   **Output:**
    *   A JSON array with the top 3 recommended plants.
    ```json
    [
      {
        "plant_name": "Snake Plant",
        "description": "A low-maintenance plant that thrives in a variety of light conditions."
      },
      {
        "plant_name": "ZZ Plant",
        "description": "An extremely drought-tolerant plant perfect for beginners."
      },
      {
        "plant_name": "Pothos",
        "description": "A versatile and easy-to-care-for trailing plant."
      }
    ]
    ```

*   **Feature:** Get a 3D model for AR visualization.
*   **API Endpoint:** `/models/{plant_name}`
*   **HTTP Method:** `GET`
*   **Input:**
    *   `plant_name`: The name of the plant.
*   **Output:**
    *   The 3D model file (e.g., in `.glb` or `.usdz` format).
