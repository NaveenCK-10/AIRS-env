
from typing import Dict, Any

from core.environment import AIRSEnv
from core.simulator import SystemSimulator


def _predict_from_logs(logs_text: str) -> Dict[str, str]:
    if "db" in logs_text or "database" in logs_text:
        diagnosis = "database_failure"
        action = "restart_database"
    elif "cache" in logs_text:
        diagnosis = "cache_overload"
        action = "scale_cache"
    elif "api" in logs_text:
        diagnosis = "api_crash"
        action = "restart_api"
    else:
        diagnosis = "unknown_issue"
        action = "restart_service"

    return {
        "diagnosis": diagnosis,
        "action": action,
        "reason": "Heuristic based on keywords in logs to restore service quickly."
    }


def run_baseline() -> Dict[str, Any]:
    env = AIRSEnv()
    task_scores: Dict[str, float] = {}

    for difficulty in ["easy", "medium", "hard"]:
        incident = next((item for item in env.data if item.get("difficulty") == difficulty), None)
        if incident is None:
            task_scores[difficulty] = 0.0
            continue

        env.current = incident
        env.simulator = SystemSimulator(incident)
        env.steps = 0
        env.initialized = True

        logs_text = " ".join(incident.get("logs", [])).lower()
        pred = _predict_from_logs(logs_text)
        _, reward, _, _ = env.step(pred)
        task_scores[difficulty] = reward["score"]

    average = round(sum(task_scores.values()) / len(task_scores), 2)
    return {
        "scores": task_scores,
        "average_score": average,
        "deterministic": True
    }
