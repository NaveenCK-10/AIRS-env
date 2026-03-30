import json
import sys
from core.environment import AIRSEnv


def predict(obs):
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


def run_task(difficulty):
    """Run a single task episode and return the cumulative reward."""
    env = AIRSEnv()

    # Advance env.idx to the first incident matching the requested difficulty
    for i, incident in enumerate(env.data):
        if incident.get("difficulty") == difficulty:
            env.idx = i
            break

    obs = env.reset()
    last_score = 0.0

    for _ in range(env.max_steps):
        action = predict(obs)
        obs, reward, done, info = env.step(action)
        last_score = reward["score"]
        if done:
            break

    return round(last_score, 2)


def main():
    scores = {}
    for difficulty in ("easy", "medium", "hard"):
        scores[difficulty] = run_task(difficulty)
    print(json.dumps(scores))


if __name__ == "__main__":
    main()
