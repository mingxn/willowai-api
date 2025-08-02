from fastapi import FastAPI
from src.diagnose.router import router as diagnose_router
# from src.assistant.router import router as assistant_router
# from src.planner.router import router as planner_router

app = FastAPI()

app.include_router(diagnose_router, tags=["diagnose"])
# app.include_router(assistant_router, prefix="/assistant", tags=["assistant"])
# app.include_router(planner_router, prefix="/planner", tags=["planner"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Willow.ai"}
