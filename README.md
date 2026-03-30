---
title: AIRS Env
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---
# AIRS OpenEnv: Autonomous Incident Response Simulator

An OpenEnv-compatible FastAPI environment for training and evaluating AI agents on realistic production incident response.

Built for hackathon judging: fast to run, easy to inspect, and designed to demonstrate multi-step decision quality, not just one-shot classification.

---

## 🚀 Problem Statement

Modern systems fail in complex ways: API crashes, database outages, cache overloads, and cascading degradation. Teams need AI agents that can:

* Read noisy telemetry and logs
* Diagnose root cause accurately
* Choose effective remediation actions
* Explain decisions under time pressure

Most benchmarks test isolated predictions. Real incident operations require **stateful, sequential actions with measurable outcomes**.

---

## 🧠 Why This Is Unique

* Stateful incident simulation: actions modify system health over time
* Multi-objective reward system
* Partial credit + penalties (not binary scoring)
* Deterministic external grader
* Task ladder (easy → medium → hard)

---

## 🏗️ Architecture Overview

```
Agent
   -> POST /step (diagnosis, action, reason)
FastAPI API Layer (api/app.py)
   -> AIRSEnv (core/environment.py)
        -> SystemSimulator (core/simulator.py)
        -> Reward Computation
   -> Observation + Reward + Done + Info

Dataset: data/incidents_v1.json
Evaluator: evaluation/grader.py
Baseline: baseline/run.py
```

---

## ⚙️ Core Flow

1. `GET /reset` → loads a random incident
2. `POST /step` → agent takes action
3. Simulator updates system state
4. Reward reflects decision quality
5. Episode ends on resolution or max steps

---

## 🧾 Action Space

`POST /step` accepts:

* `diagnosis` (string): predicted root cause (e.g. `database_failure`, `api_crash`, `cache_overload`)
* `action` (string): remediation action (e.g. `restart_database`, `restart_api`, `scale_cache`, `restart_service`)
* `reason` (string): explanation of why the action is appropriate

---

## 👀 Observation Space

`GET /reset` and `POST /step` return observation fields:

* `incident_id` (string)
* `alert` (string)
* `logs` (list of strings)
* `system_status` (object mapping service -> status)
* `step` (integer)
* `version` (string)
* `hint` (optional string)

---

## 🎯 Task Design

* **Easy:** Single-service failures
* **Medium:** Mixed symptoms
* **Hard:** Cascading multi-service failures

Accessible via:

```
GET /tasks
```

---

## 🧪 Reward Function

The reward combines:

* Diagnosis accuracy (exact + partial match)
* Action correctness
* Reasoning quality
* Step efficiency
* Penalties for poor actions

---

## 🔌 API Endpoints

* `GET /reset` → start new episode
* `POST /step` → take action
* `GET /state` → inspect system
* `GET /tasks` → task definitions
* `POST /grader` → deterministic scoring
* `GET /baseline` → heuristic baseline

---

## 🧪 Try it Live

👉 Open API Docs:

```
/docs
```

Example:

```
https://huggingface.co/spaces/Naveenck10/airs-env
```

---

## 💻 Local Setup

```bash
pip install -r requirements.txt
uvicorn api.app:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

## Live Demo

* Live API Docs: https://naveenck10-airs-env.hf.space/docs
* Base URL: https://naveenck10-airs-env.hf.space

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
configs/openenv.yaml
```

---

## 🌍 Why This Matters

* Simulates real-world incident response
* Enables agent-based decision evaluation
* Encourages explainable AI actions
* Bridges gap between theory and production systems

---

## 🏆 Hackathon Value

This project demonstrates:

* Multi-step AI reasoning
* Realistic system simulation
* Strong backend engineering
* Practical AI evaluation framework

---

## 📌 Status

✅ Fully functional
✅ API deployed
✅ Ready for evaluation
Last updated: rebuild trigger