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

**Train and evaluate AI agents on the hardest part of DevOps: real-time incident diagnosis and recovery.**

AIRS is a stateful, multi-step RL environment where AI agents receive live production alerts, interpret noisy logs, diagnose root causes, and take corrective actions — just like a real Site Reliability Engineer during a 3 AM outage.

> **Unlike static benchmarks, AIRS tests what actually matters: can your agent reason sequentially under pressure, or does it just guess?**

[![Live API](https://img.shields.io/badge/API-Live%20on%20HF%20Spaces-blue)](https://naveenck10-airs-env.hf.space/docs)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-green)](https://naveenck10-airs-env.hf.space)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)](https://naveenck10-airs-env.hf.space)
[![Phase 1](https://img.shields.io/badge/Phase%201-Passed-brightgreen)]()
[![Phase 2](https://img.shields.io/badge/Phase%202-Passed-brightgreen)]()

---

## ⚡ See It In Action (30 Seconds)

**Your agent receives this alert:**

```
🚨 Alert: "High latency detected"
📋 Logs:  ["DB connection timeout", "Retry failed"]
🖥️ Status: { api: "degraded", database: "down", cache: "healthy" }
```

**Agent reasons and acts:**

```json
{
  "diagnosis": "database_failure",
  "action": "restart_database",
  "reason": "Database is down causing cascading API degradation"
}
```

**Environment responds:**

```json
{
  "observation": {
    "system_status": { "api": "healthy", "database": "healthy", "cache": "healthy" },
    "step": 1
  },
  "reward": 0.95,
  "done": true,
  "info": { "effects": ["Database recovered"], "resolved": true }
}
```

✅ System recovered. Agent scored **0.95** in one step.

> This is multi-step reasoning under realistic conditions — not pattern matching.

---

## 🔥 Why AIRS Matters

Every major cloud outage — AWS, Google, Azure — involves cascading failures where multiple systems degrade simultaneously. Human SREs must triage noisy signals, identify root causes, and take precise corrective actions under time pressure.

**AIRS brings this challenge to AI agents.**

| Real SRE Problem | How AIRS Tests It |
|---|---|
| Noisy, ambiguous logs | Agents must parse conflicting signals |
| Cascading failures | Multiple services degrade — which is the root cause? |
| Action consequences | Wrong fix makes things worse (penalties applied) |
| Time pressure | Fewer steps = higher reward (efficiency bonus) |
| Explainability | Agents must provide reasoning, not just answers |

Most AI benchmarks test **what** the agent knows. AIRS tests **how** it thinks.

---

## 🧠 Why AIRS Is Unique

| Feature | AIRS | Typical Benchmark |
|---|---|---|
| **Stateful simulation** | ✅ Actions change system state | ❌ Static input/output |
| **Multi-step episodes** | ✅ Up to 5 steps per incident | ❌ Single prediction |
| **Partial credit** | ✅ Rewards diagnosis, action, and reasoning separately | ❌ Binary correct/wrong |
| **Penalties** | ✅ Bad actions and late failures are penalized | ❌ No consequence for errors |
| **Difficulty ladder** | ✅ Easy → Medium → Hard with increasing ambiguity | ❌ Flat difficulty |
| **Deterministic grader** | ✅ Reproducible scores, external evaluator | ❌ Subjective evaluation |
| **Explainable decisions** | ✅ Reason field scored on quality | ❌ No reasoning required |

---

## 🌍 Real-World Use Cases

- **AI SRE Agents** — Train LLM-based agents to handle production incidents autonomously
- **DevOps Automation** — Benchmark automated remediation systems before deploying to prod
- **Incident Response Training** — Simulate realistic outage scenarios for engineering teams
- **LLM Evaluation** — Test whether language models can reason sequentially, not just retrieve
- **RL Research** — Multi-step decision environments with sparse, multi-factor rewards

---

## 🏗️ Architecture

```
Agent → POST /step { diagnosis, action, reason }
                      │
              ┌───────▼────────┐
              │  FastAPI Layer  │  api/main.py
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │    AIRSEnv     │  core/environment.py
              │  (Stateful)    │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │ SystemSimulator│  core/simulator.py
              │  (State Machine)│
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │  Reward Engine │  Multi-factor scoring
              └───────┬────────┘
                      │
              ▼ Returns: Observation + Reward + Done + Info


 Dataset:   data/incidents_v1.json  (10 incidents × 3 difficulty levels)
 Grader:    evaluation/grader.py    (deterministic, mirrors environment)
 Baseline:  inference.py            (heuristic + LiteLLM proxy)
```

---

## ⚙️ Environment Flow

```
1. POST /reset  →  Start incident episode
                    Returns: alert, logs, system_status

2. POST /step   →  Agent takes action
                    Returns: updated observation, reward, done, info

3. Repeat        →  Until system resolved or max steps (5) reached

4. Score         →  reward ∈ [0.0, 1.0] based on 6 scoring factors
```

---

## 🧪 Full Example Interaction

### Step 1 — Reset

```bash
curl -X POST https://naveenck10-airs-env.hf.space/reset
```

**Response:**

```json
{
  "incident_id": "INC100",
  "alert": "High latency detected",
  "logs": ["DB connection timeout", "Retry failed"],
  "system_status": { "api": "degraded", "database": "down", "cache": "healthy" },
  "step": 0,
  "version": "1.0",
  "hint": "Look for patterns like timeouts, crashes, or overload signals in logs"
}
```

### Step 2 — Agent Acts

```bash
curl -X POST https://naveenck10-airs-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis": "database_failure",
    "action": "restart_database",
    "reason": "DB connection timeout in logs + database status is down, causing cascading API degradation"
  }'
```

**Response:**

```json
{
  "observation": {
    "incident_id": "INC100",
    "system_status": { "api": "healthy", "database": "healthy", "cache": "healthy" },
    "step": 1
  },
  "reward": 0.95,
  "done": true,
  "info": {
    "effects": ["Database recovered"],
    "resolved": true,
    "steps_taken": 1
  }
}
```

### Reward Breakdown

| Factor | Weight | This Score |
|---|---|---|
| Correct diagnosis | 0.35 | ✅ 0.35 |
| Correct action | 0.40 | ✅ 0.40 |
| Quality reasoning (>5 words) | 0.15 | ✅ 0.15 |
| Efficiency bonus (≤2 steps) | 0.05 | ✅ 0.05 |
| **Total** | **1.00** | **0.95** |

---

## 🎯 Task Design

| Level | Incidents | What Makes It Hard | Expected Steps |
|---|---|---|---|
| **Easy** | 4 | Single-service failure with clear log signals | 1 |
| **Medium** | 4 | Ambiguous logs, mixed signals across services | 2 |
| **Hard** | 2 | All services degraded — agent must find root cause in cascading failure | 3 |

```bash
curl https://naveenck10-airs-env.hf.space/tasks
```

---

## 🧾 Action & Observation Space

### Action (POST /step)

| Field | Type | Description |
|---|---|---|
| `diagnosis` | string | Root cause prediction (e.g., `database_failure`) |
| `action` | string | Remediation action to take |
| `reason` | string | Explanation for the decision |

**Valid Actions:** `restart_database` · `restart_api` · `scale_cache` · `restart_service`

### Observation (returned by /reset and /step)

| Field | Type | Description |
|---|---|---|
| `incident_id` | string | Unique incident identifier |
| `alert` | string | Alert message |
| `logs` | list[str] | Noisy log entries |
| `system_status` | dict | Current health of each service |
| `step` | int | Current step number |
| `version` | string | Environment version |
| `hint` | string | Optional guidance |

---

## 📊 Baseline Performance

| Difficulty | Heuristic Score | Room for Improvement |
|---|---|---|
| Easy | **0.95** | Near-optimal |
| Medium | **0.15** | 85% gap — ambiguous signals trip the heuristic |
| Hard | **0.15** | 85% gap — cascading failures need causal reasoning |
| **Average** | **0.42** | **Significant room for LLM/RL agents to beat** |

> The baseline uses keyword heuristics. An agent with real reasoning ability should dramatically outperform it on medium and hard tasks.

---

## 🔌 API Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/reset` | GET / POST | Start new incident episode |
| `/step` | POST | Submit agent action |
| `/state` | GET | Current environment state |
| `/tasks` | GET | List difficulty levels |
| `/grader` | POST | Deterministic external scoring |
| `/baseline` | GET | Baseline performance scores |

**Live API Docs:** [https://naveenck10-airs-env.hf.space/docs](https://naveenck10-airs-env.hf.space/docs)

---

## 💻 Quick Start

### Local

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
# Open http://127.0.0.1:8000/docs
```

### Docker

```bash
docker build -t airs-env .
docker run -p 7860:7860 airs-env
# Open http://127.0.0.1:7860/docs
```

---

## 🧩 OpenEnv Configuration

```yaml
# openenv.yaml
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
│   ├── environment.py       # Stateful AIRSEnv (reset/step/reward)
│   └── simulator.py         # System state machine
├── evaluation/grader.py     # Deterministic external grader
├── baseline/run.py          # Heuristic baseline runner
├── data/incidents_v1.json   # 10 incident scenarios
├── inference.py             # LiteLLM proxy inference script
├── models.py                # Pydantic schemas
├── tasks.py                 # Task definitions
├── openenv.yaml             # OpenEnv spec
├── Dockerfile               # Production container
├── requirements.txt         # Dependencies
└── pyproject.toml           # Package config
```

---

## ⚠️ Limitations & Future Work

- Baseline uses keyword heuristics — an RL/LLM agent would significantly outperform it
- Current dataset covers database, API, and cache failures — extensible to more service types
- Future: add network partition, memory leak, and disk pressure scenarios
- Future: support multi-agent coordination for complex outages

---

## 🏆 Summary

AIRS is a **production-grade OpenEnv environment** that challenges AI agents with the same problems real SRE teams face every day: noisy logs, cascading failures, and time-critical decisions.

It's not a toy benchmark — it's a structured evaluation of **sequential reasoning, causal diagnosis, and explainable action** under realistic conditions.

**Passed Phase 1 ✅ | Passed Phase 2 ✅ | Live on HF Spaces ✅ | Deterministic ✅**