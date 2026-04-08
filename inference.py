import sys
import os
import json
import requests
from core.environment import AIRSEnv

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")


def heuristic_predict(obs):
    """Deterministic heuristic: inspect logs and system_status to pick the best action."""
    logs_text = " ".join(obs.get("logs", [])).lower()
    status = obs.get("system_status", {})

    # Check logs for keyword signals
    has_db = "db" in logs_text or "database" in logs_text
    has_api = "api" in logs_text
    has_cache = "cache" in logs_text

    # Also check system_status for unhealthy components
    db_bad = status.get("database", "healthy") in ("down", "slow", "degraded")
    api_bad = status.get("api", "healthy") in ("down", "slow", "degraded")
    cache_bad = status.get("cache", "healthy") in ("down", "overloaded", "degraded")

    # Priority: database > api > cache > generic restart
    if has_db or (db_bad and not has_cache):
        return {
            "diagnosis": "database_failure",
            "action": "restart_database",
            "reason": "Log analysis indicates database connectivity issues causing service degradation",
        }
    if has_api and not has_cache:
        return {
            "diagnosis": "api_crash",
            "action": "restart_api",
            "reason": "Log analysis indicates API process crash requiring immediate restart",
        }
    if has_cache:
        return {
            "diagnosis": "cache_overload",
            "action": "scale_cache",
            "reason": "Log analysis indicates cache saturation leading to cascading performance issues",
        }
    # Fallback: use system_status when logs are ambiguous
    if cache_bad:
        return {
            "diagnosis": "cache_overload",
            "action": "scale_cache",
            "reason": "System status shows cache overloaded requiring horizontal scaling",
        }
    if db_bad:
        return {
            "diagnosis": "database_failure",
            "action": "restart_database",
            "reason": "System status shows database unhealthy requiring restart",
        }
    if api_bad:
        return {
            "diagnosis": "api_crash",
            "action": "restart_api",
            "reason": "System status shows API service down requiring restart",
        }
    return {
        "diagnosis": "unknown_issue",
        "action": "restart_service",
        "reason": "No clear root cause identified, attempting generic service restart",
    }


def predict(obs):
    prompt = f"{json.dumps(obs)}"

    try:
        base_url = os.environ["API_BASE_URL"]
        api_key = os.environ["API_KEY"]

        response = requests.post(
            f"{base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0
            },
            timeout=5
        )

        data = response.json()

        content = data["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        result = json.loads(content)

        if all(k in result for k in ["diagnosis", "action", "reason"]):
            return result

    except Exception:
        pass

    return heuristic_predict(obs)

def main():
    for task in ["easy", "medium", "hard"]:
        print(f"[START] task={task}", flush=True)

        env = AIRSEnv()

        # Advance env.idx to the first incident matching the requested difficulty
        for i, incident in enumerate(env.data):
            if incident.get("difficulty") == task:
                env.idx = i
                break

        obs = env.reset()
        done = False
        step_count = 0
        reward = {"score": 0.0}

        while not done:
            step_count += 1
            action = predict(obs)
            obs, reward, done, info = env.step(action)
            print(f"[STEP] step={step_count} reward={reward['score']}", flush=True)

            if step_count >= env.max_steps:
                break

        print(f"[END] task={task} score={reward['score']} steps={step_count}", flush=True)


if __name__ == "__main__":
    main()

