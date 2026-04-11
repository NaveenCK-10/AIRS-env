---
title: AIRS Env
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 🚀 AIRS OpenEnv: Autonomous Incident Response Simulator

A production-grade OpenEnv environment that simulates **real-world incident response**, where AI agents must diagnose failures, take actions, and recover systems **step-by-step**.

Built for hackathon evaluation — fast, deterministic, and designed to test **sequential decision-making**, not just one-shot predictions.

---

## ⚡ 30-Second Demo (What This Actually Does)

### 🧪 Example Incident

**Logs:**
- "Database connection timeout"
- "API latency spiking"
- "Service returning 500 errors"

**System Status:**
- database: degraded  
- api: slow  
- cache: healthy  

---

### 🤖 Agent Decision

- **Diagnosis:** `database_failure`  
- **Action:** `restart_database`  
- **Reason:** Database instability is causing cascading API failures  

---

### ✅ Result

- System stabilizes  
- API latency returns to normal  
- Reward increases  

💡 This demonstrates **multi-step reasoning under real conditions**, not simple classification.

---

## 🎯 Problem Statement

Modern production systems fail in complex, interconnected ways:

- API crashes  
- Database outages  
- Cache overloads  
- Cascading failures  

AI agents must:

- Interpret noisy logs  
- Identify root causes  
- Take corrective actions  
- Justify decisions  

👉 Most benchmarks test **isolated predictions**  
👉 AIRS tests **real-world decision workflows**

---

## 🧠 Why AIRS Stands Out

- Stateful incident simulation (actions change system behavior)
- Evaluates **decision sequences**, not single outputs
- Multi-objective reward system
- Partial credit + penalties
- Deterministic external grader
- Mimics real **SRE (Site Reliability Engineering)** workflows
- Task ladder: easy → medium → hard

---

## 🏗️ Architecture Overview

```

Agent → POST /step (diagnosis, action, reason)

FastAPI API Layer (api/main.py)
↓
AIRSEnv (core/environment.py)
↓
SystemSimulator (core/simulator.py)
↓
Reward Engine

→ Returns: Observation + Reward + Done + Info

Dataset: data/incidents_v1.json
Evaluator: evaluation/grader.py
Baseline: inference.py

````

---

## ⚙️ Core Flow

1. `GET /reset` → Start new incident  
2. `POST /step` → Agent takes action  
3. Environment updates system state  
4. Reward computed based on decision quality  
5. Repeat until resolved or max steps  

---

## 🧪 Quick Example (API Usage)

### Step 1: Reset Environment

```bash
curl -X GET https://naveenck10-airs-env.hf.space/reset
````

---

### Step 2: Take Action

```bash
curl -X POST https://naveenck10-airs-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis": "database_failure",
    "action": "restart_database",
    "reason": "DB causing cascading failures"
  }'
```

---

## 🧾 Action Space

**POST /step**

| Field     | Description           |
| --------- | --------------------- |
| diagnosis | Root cause prediction |
| action    | Remediation action    |
| reason    | Explanation           |

**Supported Actions:**

* restart_database
* restart_api
* scale_cache
* restart_service

---

## 👀 Observation Space

Returned by `/reset` and `/step`:

* incident_id
* alert
* logs
* system_status
* step
* version
* hint (optional)

---

## 🎯 Task Design

| Level  | Description                      |
| ------ | -------------------------------- |
| Easy   | Single-service failure           |
| Medium | Mixed signals                    |
| Hard   | Cascading multi-service failures |

👉 Access via:

```
GET /tasks
```

---

## 🧪 Reward System

The reward reflects:

* Diagnosis accuracy
* Action correctness
* Reason quality
* Step efficiency
* Penalties for poor decisions

👉 Encourages correct AND efficient reasoning

---

## 📊 Baseline Performance

The provided baseline achieves:

* Easy: ~0.95
* Medium: ~0.15
* Hard: ~0.15
* Average: ~0.42

This highlights increasing difficulty and the need for stronger reasoning strategies.

---

## 🔌 API Endpoints

| Endpoint      | Purpose               |
| ------------- | --------------------- |
| GET /reset    | Start episode         |
| POST /step    | Take action           |
| GET /state    | Current system        |
| GET /tasks    | Task list             |
| POST /grader  | Deterministic scoring |
| GET /baseline | Baseline scores       |

---

## 🧪 Live Demo

👉 API Docs:
[https://naveenck10-airs-env.hf.space/docs](https://naveenck10-airs-env.hf.space/docs)

👉 Base URL:
[https://naveenck10-airs-env.hf.space](https://naveenck10-airs-env.hf.space)

---

## 💻 Local Setup

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

## 🐳 Docker Setup

```bash
docker build -t airs-env .
docker run -p 7860:7860 airs-env
```

Open:

```
http://127.0.0.1:7860/docs
```

---

## 🧩 OpenEnv Configuration

Defined in:

```
openenv.yaml
```

---

## ⚠️ Limitations

* Baseline uses heuristic logic (not learned policy)
* Complex cascading failures remain challenging
* Future work: integrate RL / LLM-based agents

---

## 🌍 Real-World Impact

AIRS enables:

* AI-driven incident response training
* Evaluation of reasoning under pressure
* Explainable system recovery decisions
* Simulation of real production failures

---

## 🏆 Hackathon Strength

This project demonstrates:

* Multi-step AI reasoning
* Realistic system simulation
* Clean backend architecture
* OpenEnv compliance
* Deterministic evaluation pipeline

---