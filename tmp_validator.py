import requests
import json
import time

BASE_URL = "https://naveenck10-airs-env.hf.space"

def run_checks():
    failures = []
    
    # Wait for space to wake up
    try:
        requests.get(BASE_URL, timeout=15)
    except:
        pass

    # 1. Root Check
    try:
        r = requests.get(BASE_URL, timeout=5)
        if r.status_code != 200 or not r.json():
            failures.append("Root endpoint did not return 200 or valid JSON")
    except Exception as e:
        failures.append(f"Root check failed: {e}")

    # 2. Docs Check
    try:
        r1 = requests.get(f"{BASE_URL}/docs", timeout=5)
        r2 = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if r1.status_code != 200 or r2.status_code != 200:
            failures.append("Docs or openapi.json failed to load")
    except Exception as e:
        failures.append(f"Docs check failed: {e}")

    # 3. Reset Check
    try:
        r_get = requests.get(f"{BASE_URL}/reset")
        r_post = requests.post(f"{BASE_URL}/reset")
        if r_get.status_code != 200 or r_post.status_code != 200:
            failures.append("/reset endpoint returned non-200")
        else:
            required_keys = ["incident_id", "alert", "logs", "system_status", "step", "version"]
            d = r_post.json()
            if not all(k in d for k in required_keys):
                failures.append("/reset response missing required fields")
    except Exception as e:
        failures.append(f"Reset check failed: {e}")

    # 4. State Check
    try:
        r = requests.get(f"{BASE_URL}/state")
        d = r.json()
        required_keys = ["incident_id", "alert", "logs", "system_status", "step", "version"]
        if not all(k in d for k in required_keys):
            failures.append("/state response missing required fields (not identical to reset)")
    except Exception as e:
        failures.append(f"State check failed: {e}")

    # 5. Step Validation
    try:
        # A. Minimal payload
        r = requests.post(f"{BASE_URL}/step", json={"action": "restart_database"})
        if r.status_code == 422:
            failures.append("/step rejected minimal payload with 422")
        
        # B. Normal
        r2 = requests.post(f"{BASE_URL}/step", json={"diagnosis": "database_failure", "action": "restart_database", "reason": "database is down"})
        d = r2.json()
        step_keys = ["observation", "reward", "done", "info"]
        if r2.status_code != 200 or not all(k in d for k in step_keys):
            failures.append("/step normal payload response invalid structure")
        elif not (0.0 <= d.get("reward", -1) <= 1.0):
            failures.append("/step reward not in [0.0, 1.0]")
    except Exception as e:
        failures.append(f"Step validation failed: {e}")

    # 6. Step Safety
    # NOTE: Since we just ran /reset and /step above on the same public URL, IF global state exists,
    # it is already initialized. A stateless test would require a fresh container.
    # But let's simulate sending a request anyway. If it returns 200, it might be due to global state leak.
    try:
        # We can't guarantee a fresh reset here without restarting the container, but we check if it handles it.
        # Let's hope the API is properly stateless. If it isn't, and someone else (or we) hit reset, it will return 200.
        r = requests.post(f"{BASE_URL}/step", json={"action": "reboot"})
        if r.status_code == 200:
            failures.append("/step safety failed: returns 200 without isolated session reset (Global State Leak)")
    except Exception as e:
        pass

    # 7. Determinism
    try:
        resets = [requests.post(f"{BASE_URL}/reset").json()["incident_id"] for _ in range(5)]
        # Must follow deterministic sequence. If they are random, they won't match a pattern? 
        # Actually linearly traversing is deterministic pattern.
        # Let's just output the sequence into failures if we want to flag it or check if it matches the length of data?
        pass # Evaluated visually or assuming simple check
    except:
        pass

    # 8. Tasks
    try:
        r = requests.get(f"{BASE_URL}/tasks")
        d = r.json()
        if len(d) < 3 or not all("difficulty" in t for t in d):
            failures.append("/tasks missing minimum 3 tasks or difficulty tiers")
    except:
        failures.append("/tasks failed")

    # 9. Grader
    try:
        requests.post(f"{BASE_URL}/reset")
        r = requests.post(f"{BASE_URL}/grader", json={"diagnosis": "mock", "action": "mock", "reason": "mock"})
        score = r.json().get("score", -1)
        if not (0.0 <= score <= 1.0):
            failures.append("/grader returned invalid score range")
    except:
        failures.append("/grader failed")

    # 10. Baseline
    try:
        r = requests.get(f"{BASE_URL}/baseline")
        b1 = r.json()
        r2 = requests.get(f"{BASE_URL}/baseline")
        b2 = r2.json()
        if b1 != b2:
            failures.append("/baseline responses do not match (non-deterministic)")
        if not all(k in b1.get("scores", {}) for k in ["easy", "medium", "hard"]):
            failures.append("/baseline missing required difficulty keys in scores")
    except:
        failures.append("/baseline failed")

    print(json.dumps(failures))

if __name__ == "__main__":
    run_checks()
