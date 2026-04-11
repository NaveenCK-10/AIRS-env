
TASKS = [
    {
        "id": "easy",
        "difficulty": "easy",
        "description": "Single-service failures with clear log signals. Agent must identify one failing component and take corrective action.",
        "num_incidents": 4,
        "expected_steps": 1
    },
    {
        "id": "medium",
        "difficulty": "medium",
        "description": "Mixed signals across services. Logs may be ambiguous; agent must reason about root cause vs symptoms.",
        "num_incidents": 4,
        "expected_steps": 2
    },
    {
        "id": "hard",
        "difficulty": "hard",
        "description": "Cascading multi-service failures. All systems degraded; agent must identify root cause and correct fix order.",
        "num_incidents": 2,
        "expected_steps": 3
    }
]
