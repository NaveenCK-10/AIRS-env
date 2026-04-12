---
title: AIRS Env
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 🚨 AIRS — Autonomous Incident Response Simulator

> **Every major cloud outage starts the same way: cascading alerts, conflicting signals, and an engineer who has seconds to find the root cause.**
>
> AIRS turns that problem into a benchmark. Your AI agent gets the same noisy logs, degraded dashboards, and time pressure a real SRE faces at 3 AM — and has to *reason* its way to recovery.

[![Live API](https://img.shields.io/badge/API-Live%20on%20HF%20Spaces-blue)](https://naveenck10-airs-env.hf.space/docs)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-green)](https://naveenck10-airs-env.hf.space)
[![Phase 1 ✅](https://img.shields.io/badge/Phase%201-Passed-brightgreen)]()
[![Phase 2 ✅](https://img.shields.io/badge/Phase%202-Passed-brightgreen)]()

---

## ⚡ What AIRS Does

- 🔍 **Diagnoses failures** — Agent receives production alerts, parses noisy logs, identifies root cause
- 🛠️ **Takes corrective actions** — Restarts services, scales infrastructure, resolves cascading issues
- 📊 **Scores decisions** — Multi-factor reward evaluating diagnosis accuracy, action correctness, reasoning quality, and efficiency
- 🔄 **Simulates realistic state** — Actions mutate live system state; wrong fixes make things worse
- 🎯 **Scales difficulty** — From obvious single failures to ambiguous cascading outages

---

## 🚀 Why This Matters

Production incident response is one of the **hardest real-world reasoning problems** in software engineering. Today's SRE teams handle it manually. Tomorrow, AI agents will need to.

| Problem | Why Existing Benchmarks Fail | How AIRS Solves It |
|---|---|---|
| Incidents are **stateful** | Static benchmarks use single input → output | AIRS actions change system state across steps |
| Diagnosis requires **causal reasoning** | Pattern matching isn't enough | Medium/hard tasks have ambiguous, conflicting signals |
| Wrong actions have **consequences** | No penalty for bad answers | AIRS penalizes incorrect actions and late failures |
| Reasoning must be **explainable** | Only final answer matters | AIRS scores the quality of agent explanations |

**If you're building AI agents for DevOps, SRE automation, or incident response — this is the evaluation environment you need.**

---

## 🧩 Task Design — Three Modes of Reasoning

Each difficulty level tests a fundamentally different cognitive challenge:

### 🟢 Easy — Direct Signal Mapping (4 incidents)
> *"One service is down. The logs say exactly why."*

Single point of failure with clear log evidence. Tests whether the agent can read signals and act decisively. Expected: **1 step**.

**Example:** `"DB connection timeout"` + database status `"down"` → restart database.

### 🟡 Medium — Conflicting Signals (4 incidents)
> *"Multiple services look unhealthy. The logs point in different directions."*

Ambiguous log entries with mixed status signals. Tests whether the agent can distinguish **root cause from symptoms**. Expected: **2 steps**.

**Example:** `"Cache miss rate high"` + `"DB query latency elevated"` — is this a database problem or a cache problem? The agent must reason through the dependency chain.

### 🔴 Hard — Cascading Failure Analysis (2 incidents)
> *"Everything is on fire. Which domino fell first?"*

All services degraded simultaneously. Logs show failures across every component. Tests whether the agent can perform **causal reasoning** to identify the origin failure that triggered the cascade. Expected: **3 steps**.

**Example:** API down + database slow + cache overloaded — the agent must identify that cache overload is the root cause, not just the loudest alert.

---

## 🧠 Reasoning Evaluation

AIRS doesn't just check answers — it evaluates **how the agent thinks**.

### Multi-Factor Scoring (6 Components)

| Factor | Weight | What It Measures |
|---|---|---|
| Correct diagnosis | **0.35** | Did the agent identify the root cause? |
| Correct action | **0.40** | Did it take the right remediation step? |
| Reasoning quality | **0.15** | Is the explanation substantive (>5 words)? |
| Efficiency bonus | **0.05** | Solved in ≤2 steps? |
| Bad action penalty | **−0.30** | Penalizes `do_nothing`, `ignore`, `random_action` |
| Late failure penalty | **−0.10** | Wrong action after step 3 |

> **Current approach:** Structured keyword-based validation ensures deterministic, reproducible scores. The reasoning evaluation serves as a baseline — designed to be extended with semantic similarity scoring and LLM-as-judge evaluation for richer assessment of agent explanations.

---

## 🧪 Example Interaction

**1. Start an incident:**

```bash
curl -X POST https://naveenck10-airs-env.hf.space/reset
```

```json
{
  "incident_id": "INC100",
  "alert": "High latency detected",
  "logs": ["DB connection timeout", "Retry failed"],
  "system_status": { "api": "degraded", "database": "down", "cache": "healthy" }
}
```

**2. Agent reasons and acts:**

```bash
curl -X POST https://naveenck10-airs-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis": "database_failure",
    "action": "restart_database",
    "reason": "DB connection timeout in logs + database is down → root cause is database failure"
  }'
```

**3. Environment responds:**

```json
{
  "reward": 0.95,
  "done": true,
  "info": { "effects": ["Database recovered"], "resolved": true }
}
```

✅ **System recovered in 1 step. Score: 0.95/1.00.**

---

## 🏗️ Architecture

```
 Agent ─── POST /step ──▶ ┌─────────────────┐
                          │   FastAPI Layer  │  ◀── POST /reset, GET /state
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │    AIRSEnv       │  Stateful episode manager
                          └────────┬────────┘
                                   │
                     ┌─────────────┼─────────────┐
                     ▼             ▼              ▼
              SystemSimulator  Reward Engine   Grader
              (state machine)  (6 factors)    (deterministic)
```

| Component | File | Role |
|---|---|---|
| API Layer | `api/main.py` | FastAPI endpoints (reset, step, state, tasks, grader, baseline) |
| Environment | `core/environment.py` | Stateful episode lifecycle + reward computation |
| Simulator | `core/simulator.py` | System state machine — actions mutate service health |
| Grader | `evaluation/grader.py` | Deterministic external scoring (mirrors environment logic) |
| Incidents | `data/incidents_v1.json` | 10 curated scenarios across 3 difficulty levels |
| Inference | `inference.py` | LiteLLM proxy client + heuristic fallback |

---

## 📊 Baseline Performance

| Difficulty | Baseline Score | Headroom | What's Missing |
|---|---|---|---|
| 🟢 Easy | **0.95** | 5% | Near-optimal — clear signals |
| 🟡 Medium | **0.15** | **85%** | Heuristic can't resolve ambiguous signals |
| 🔴 Hard | **0.15** | **85%** | Cascading failures require causal reasoning |
| **Average** | **0.42** | **58%** | **Massive room for intelligent agents** |

> The baseline uses simple keyword matching. It solves easy cases but **completely fails** when signals conflict or cascade — exactly the gap that LLM and RL agents should close.

---

## 🌍 Use Cases

| Domain | Application |
|---|---|
| **AI SRE Agents** | Train and evaluate LLM-based agents for autonomous incident response |
| **DevOps Automation** | Benchmark automated remediation pipelines before production deployment |
| **Incident Response Training** | Simulate realistic outage scenarios for on-call engineering teams |
| **LLM Evaluation** | Test sequential reasoning and causal analysis capabilities |
| **RL Research** | Multi-step decision environment with sparse, multi-factor reward signals |

---

## ⚙️ Quick Start

### Local

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
# → http://127.0.0.1:8000/docs
```

### Docker

```bash
docker build -t airs-env .
docker run -p 7860:7860 airs-env
# → http://127.0.0.1:7860/docs
```

---

## 🔌 API Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/reset` | GET / POST | Start a new incident episode |
| `/step` | POST | Submit diagnosis + action + reasoning |
| `/state` | GET | Current environment state |
| `/tasks` | GET | List available difficulty levels |
| `/grader` | POST | Deterministic external scoring |
| `/baseline` | GET | Baseline heuristic performance |

📖 **[Interactive API Docs →](https://naveenck10-airs-env.hf.space/docs)**

---

## 🧩 OpenEnv Configuration

```yaml
name: airs-env
version: 1.0.0
entrypoint:
  command: uvicorn api.main:app --host 0.0.0.0 --port 7860
endpoints:
  reset:    { method: POST, path: /reset }
  step:     { method: POST, path: /step }
  state:    { method: GET,  path: /state }
  tasks:    { method: GET,  path: /tasks }
  grader:   { method: POST, path: /grader }
  baseline: { method: GET,  path: /baseline }
```

---

## 📁 Project Structure

```
airs-env/
├── api/main.py              # FastAPI endpoints
├── core/
│   ├── environment.py       # Stateful AIRSEnv (reset / step / reward)
│   └── simulator.py         # System state machine
├── evaluation/grader.py     # Deterministic external grader
├── baseline/run.py          # Heuristic baseline runner
├── data/incidents_v1.json   # 10 incident scenarios (3 difficulty levels)
├── inference.py             # LiteLLM proxy inference + heuristic fallback
├── models.py                # Pydantic schemas
├── tasks.py                 # Task definitions (easy / medium / hard)
├── openenv.yaml             # OpenEnv specification
├── Dockerfile               # Production container
├── requirements.txt         # Dependencies
└── pyproject.toml           # Package configuration
```

---

## 🏆 Summary

AIRS is a **production-grade OpenEnv environment** that challenges AI agents with the same problems real SRE teams face: noisy logs, cascading failures, and time-critical decisions.

It's not a toy benchmark — it's a structured evaluation of **sequential reasoning, causal diagnosis, and explainable action** under realistic conditions.

**Phase 1 ✅ · Phase 2 ✅ · Live on HF Spaces ✅ · Deterministic Scoring ✅**