import requests
import sys
import json
import time

BASE_URL = "https://naveenck10-airs-env.hf.space"
results = {}

def print_res(name, passed, msg=""):
    results[name] = "PASS" if passed else "FAIL"
    status = "PASS" if passed else "FAIL"
    print(f"{name:20}: {status} {msg}")

def test_api():
    print(f"Testing {BASE_URL}...\n")
    
    # Wait for container to be ready if it's asleep
    try:
        requests.get(BASE_URL, timeout=30)
    except Exception:
        pass

    # 1. Root
    try:
        r = requests.get(f"{BASE_URL}/", timeout=10)
        data = r.json()
        print_res("Root", data.get("status") == "ok", f"Got: {data}")
    except Exception as e:
        print_res("Root", False, str(e))

    # 2. Docs
    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=10)
        print_res("Docs", r.status_code == 200 and "swagger" in r.text.lower(), f"Status: {r.status_code}")
    except Exception as e:
        print_res("Docs", False, str(e))

    # 7. Step Safety (Before Reset)
    try:
        r = requests.post(f"{BASE_URL}/step", json={"action": "restart_service", "target": "database"})
        print_res("Step Safety", r.status_code == 400, f"Status: {r.status_code}, expected 400")
    except Exception as e:
        print_res("Step Safety", False, str(e))

    # 3. Reset GET & POST
    try:
        r_get = requests.get(f"{BASE_URL}/reset")
        d_get = r_get.json()
        r_post = requests.post(f"{BASE_URL}/reset")
        d_post = r_post.json()
        passed = "logs" in d_get and "system_status" in d_get and "logs" in d_post
        print_res("Reset GET/POST", passed, "Structure looks correct")
        reset_output = d_post
    except Exception as e:
        print_res("Reset GET/POST", False, str(e))
        reset_output = {}

    # 4. State
    try:
        r = requests.get(f"{BASE_URL}/state")
        d = r.json()
        passed = isinstance(d, dict) and "logs" in d and "system_status" in d
        print_res("State", passed, f"Struct is: {d}")
    except Exception as e:
        print_res("State", False, str(e))

    # 5. Tasks
    try:
        r = requests.get(f"{BASE_URL}/tasks")
        d = r.json()
        has_tasks = len(d) == 3 and all("difficulty" in t or "name" in t for t in d)
        print_res("Tasks", has_tasks, f"Found {len(d) if isinstance(d, list) else 'invalid'} tasks")
    except Exception as e:
        print_res("Tasks", False, str(e))

    # 6. Step Flow
    try:
        r = requests.post(f"{BASE_URL}/step", json={"action": "restart_service", "target": "database"})
        if r.status_code == 422:
            print_res("Step Flow", False, f"422 Validation Error (User sample invalid): {r.text}")
        else:
            d = r.json()
            passed = "observation" in d and "reward" in d and "done" in d and "info" in d
            print_res("Step Flow", passed, f"Received: {d}")
    except Exception as e:
        print_res("Step Flow", False, str(e))

    # 7. Step Safety (Before Reset) WITH VALID BODY
    try:
        r = requests.post(f"{BASE_URL}/step", json={"diagnosis": "mock", "action": "mock", "reason": "mock"})
        print_res("Step Safety", r.status_code == 400, f"Status: {r.status_code}, expected 400. Text: {r.text}")
    except Exception as e:
        print_res("Step Safety", False, str(e))

    # 8. Grader
    try:
        r = requests.post(f"{BASE_URL}/grader", json={"diagnosis": "mock", "action": "mock", "reason": "mock"})
        if r.status_code != 200:
            print_res("Grader", False, f"Status: {r.status_code}, expected 200. Text: {r.text}")
        else:
            d = r.json()
            passed = "score" in d and isinstance(d["score"], (int, float))
            print_res("Grader", passed, f"Returned: {d}")
    except Exception as e:
        print_res("Grader", False, str(e))


    # 9. Baseline
    try:
        r = requests.get(f"{BASE_URL}/baseline")
        d = r.json()
        passed = "scores" in d and all(k in d["scores"] for k in ["easy", "medium", "hard"])
        print_res("Baseline", passed, "Valid baseline scores")
    except Exception as e:
        print_res("Baseline", False, str(e))

    # 10. Determinism
    try:
        r1 = requests.post(f"{BASE_URL}/reset").json()
        r2 = requests.post(f"{BASE_URL}/reset").json()
        
        passed = str(r1) == str(r2) 
        if not passed:
            print_res("Determinism", passed, f"r1: {r1} != r2: {r2}")
        else:
            print_res("Determinism", passed, "Reset output is deterministic")
    except Exception as e:
        print_res("Determinism", False, str(e))


if __name__ == "__main__":
    test_api()
