from fastapi import APIRouter, UploadFile, File
from .schemas import DiagnosisResponse
from . import service

router = APIRouter()

@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(file: UploadFile = File(...)):
    """
    Diagnose a plant from an uploaded image.
    """
    return await service.diagnose_plant(file)
