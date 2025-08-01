# Willow.ai Technology Stack

This document outlines the technology stack for the Willow.ai server-side application.

## Core Framework

*   **Framework:** **FastAPI (Python)**
    *   **Reasoning:** A modern, high-performance web framework for building APIs with Python. Its asynchronous capabilities make it highly efficient, and its automatic interactive documentation is a significant development advantage.

## Database

*   **Database:** **PostgreSQL**
    *   **Reasoning:** A powerful, open-source, and highly reliable object-relational database system. It provides strong data integrity and is well-suited for the structured data we anticipate (e.g., user accounts, plant collections, care schedules).
    *   **Python Integration:** **SQLAlchemy** will be used as the Object-Relational Mapper (ORM) to interact with the database.

## AI / Machine Learning

*   **Platform Choice:** To be decided between **OpenAI API** and **Google Cloud Vision API**.
    *   **Reasoning:** Both services provide powerful, pre-trained models for image analysis, which are essential for the AI Plant Doctor feature. The final choice will depend on a comparative analysis of their accuracy for plant disease identification, API ease of use, and pricing.

## File/Image Storage

*   **Storage:** **Local File Storage**
    *   **Reasoning:** For initial development, user-uploaded images will be stored directly on the local filesystem. This approach is simple to implement and sufficient for development and testing purposes without requiring external infrastructure. For more advanced local development that mimics a cloud environment, **MinIO** can be set up later.