import requests
import time
import sys

BASE_URL = "https://naveenck10-airs-env.hf.space"
failures = []

def fail(msg):
    failures.append(msg)
    print(f"FAIL: {msg}")

def check(condition, msg):
    if not condition:
        fail(msg)
    else:
        print(f"PASS: {msg}")

try:
    print("Testing 1. ROOT")
    r = requests.get(BASE_URL, allow_redirects=False)
    check(r.status_code == 200, "Root must return HTTP 200")
    check(r.headers.get("content-type", "").startswith("application/json"), "Root must return JSON")
    check("location" not in r.headers, "No redirect loop")

    print("\nTesting 2. DOCS")
    r = requests.get(BASE_URL + "/docs")
    check(r.status_code == 200, "Swagger UI loads")
    r = requests.get(BASE_URL + "/openapi.json")
    check(r.status_code == 200, "openapi.json exists")

    print("\nTesting 6. STEP SAFETY (CRITICAL)")
    r = requests.post(BASE_URL + "/step", json={"action": "restart_database"})
    check(r.status_code == 400, "Step before reset must return 400")

    print("\nTesting 3. RESET")
    r = requests.get(BASE_URL + "/reset")
    check(r.status_code == 200, "GET /reset returns 200")
    data = r.json()
    expected_keys = {"incident_id", "alert", "logs", "system_status", "step", "version"}
    check(expected_keys.issubset(data.keys()), f"/reset must return {expected_keys}")

    r = requests.post(BASE_URL + "/reset", json={"task": "easy"})
    check(r.status_code == 200, "POST /reset returns 200")

    print("\nTesting 4. STATE")
    r = requests.get(BASE_URL + "/state")
    check(r.status_code == 200, "GET /state returns 200")
    state_data = r.json()
    check(expected_keys.issubset(state_data.keys()), "/state must match /reset schema")

    print("\nTesting 5. STEP VALIDATION")
    r = requests.post(BASE_URL + "/step", json={"action": "restart_database"})
    check(r.status_code != 422, "Minimal payload must NOT return 422")
    
    r = requests.post(BASE_URL + "/step", json={
        "diagnosis": "database_failure",
        "action": "restart_database",
        "reason": "database is down"
    })
    step_data = r.json()
    check("observation" in step_data and "reward" in step_data and "done" in step_data and "info" in step_data, "Full payload must return robust schema")
    
    print("\nTesting 7. DETERMINISM")
    incidents = []
    for _ in range(5):
        r = requests.get(BASE_URL + "/reset")
        if r.status_code == 200:
            incidents.append(r.json().get("incident_id"))
    check(len(incidents) == 5, "/reset 5 times")
    # Check if they are sequential (assuming they end in numbers, e.g., INC100, INC101...)
    # Or just that it's not totally random if there is a sequence logic.
    print(f"Sequence seen: {incidents}")

    print("\nTesting 8. TASKS")
    r = requests.get(BASE_URL + "/tasks")
    check(r.status_code == 200, "GET /tasks returns 200")
    if r.status_code == 200:
        tasks = r.json()
        check(len(tasks) >= 3, "Must return >= 3 tasks")
        if len(tasks) > 0:
            check("difficulty" in tasks[0], "Must include difficulty")
            
    print("\nTesting 9. GRADER")
    r = requests.post(BASE_URL + "/grader", json={"logs": [], "system_status": {}, "incident_id": incidents[0]})
    if r.status_code == 200:
        score = r.json().get("score", -1)
        check(0.0 <= score <= 1.0, "Score must be [0.0, 1.0]")
    else:
        fail("POST /grader failed")

    print("\nTesting 10. BASELINE")
    r = requests.get(BASE_URL + "/baseline")
    check(r.status_code == 200, "GET /baseline returns 200")
    if r.status_code == 200:
        bs1 = r.json()
        r2 = requests.get(BASE_URL + "/baseline")
        bs2 = r2.json()
        check("easy" in bs1 and "medium" in bs1 and "hard" in bs1, "Must return easy, medium, hard")
        check(bs1 == bs2, "Baseline must be deterministic")

except Exception as e:
    fail(f"Exception during testing: {e}")

if failures:
    print("\n\nFAILURES:")
    for f in failures[:5]:
        print("-", f)
    sys.exit(1)
else:
    print("\n\nPASS")
    sys.exit(0)
