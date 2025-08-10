from pydantic import BaseModel
from typing import List

class DiagnosisRequest(BaseModel):
    pass

class ActionPlanItem(BaseModel):
    id: int
    action: str

class DiagnosisResponse(BaseModel):
    plant_name: str
    condition: str
    detail_diagnosis: str
    action_plan: List[ActionPlanItem]
