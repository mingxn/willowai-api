import os
import json
import uuid
import io
from fastapi import UploadFile
from src.config import settings
from src.minio import minio_client
from .schemas import DiagnosisResponse
from src.diagnose.agent.workflows import diagnosis_workflow

async def diagnose_plant(file: UploadFile) -> DiagnosisResponse:
    # 1. Read file content
    file_content = await file.read()

    # 2. Upload file to Minio (optional, but good for storage)
    object_name = f"{uuid.uuid4()}_{file.filename}"
    file_stream = io.BytesIO(file_content)
    minio_client.put_object(
        object_name,
        data=file_stream,
        length=len(file_content),
        content_type=file.content_type
    )

    # 3. Run the diagnosis workflow
    raw_output = diagnosis_workflow(file_content)
    parsed_output = json.loads(raw_output)

    diagnosis_list = parsed_output.get("diagnoses", [])
    action_plan_list = parsed_output.get("action_plan", [])

    # Format for DiagnosisResponse schema
    return DiagnosisResponse(
        diagnoses=diagnosis_list,
        action_plan=action_plan_list
    )

