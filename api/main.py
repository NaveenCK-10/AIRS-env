from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from core.environment import AIRSEnv
from models import Action, StepResponse, Observation, GradeRequest
from evaluation.grader import grade
from tasks import TASKS
from baseline.run import run_baseline

app = FastAPI(
    title="AIRS v1.0 — Autonomous Incident Response Simulator",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

env = None

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AIRS OpenEnv running",
        "docs": "/docs"
    }

@app.api_route("/reset", methods=["GET", "POST"], response_model=Observation)
def reset():
    global env
    env = AIRSEnv()
    return env.reset()

@app.post("/step", response_model=StepResponse)
def step(action: Action):
    global env

    if env is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")

    try:
        obs, reward, done, info = env.step(action.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StepResponse(
        observation=obs,
        reward=reward["score"],
        done=done,
        info=info
    )

@app.get("/state", response_model=Dict[str, Any])
def state() -> Dict[str, Any]:
    if env is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")
    return env.state()

@app.get("/tasks", response_model=List[Dict[str, str]])
def tasks() -> List[Dict[str, str]]:
    return TASKS

@app.post("/grader", response_model=Dict[str, float])
def grader(pred: GradeRequest) -> Dict[str, float]:
    if env is None or env.current is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")

    expected = env.current["expected"]
    return {"score": grade(pred.model_dump(), expected)}

@app.get("/baseline", response_model=Dict)
def baseline():
    return run_baseline()

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
