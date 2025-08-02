from pydantic import BaseModel
from typing import List

class DiagnosisRequest(BaseModel):
    pass

class DiagnosisItem(BaseModel):
    id: int
    diagnosis: str

class ActionPlanItem(BaseModel):
    id: int
    action: str

class DiagnosisResponse(BaseModel):
    diagnoses: List[DiagnosisItem]
    action_plan: List[ActionPlanItem]
