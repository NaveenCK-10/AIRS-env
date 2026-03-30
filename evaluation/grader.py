
def diagnosis_partial_match(pred: str, expected: str) -> bool:
    if not pred or not expected:
        return False

    pred_norm = pred.strip().lower()
    expected_norm = expected.strip().lower()

    # Substring similarity (same logic as environment)
    if expected_norm in pred_norm or pred_norm in expected_norm:
        return True

    # Token-based prefix match (same logic as environment)
    pred_tokens = [t for t in pred_norm.split("_") if t]
    expected_tokens = [t for t in expected_norm.split("_") if t]

    if not pred_tokens or not expected_tokens:
        return False

    if pred_tokens[0] == expected_tokens[0]:
        return True

    # Keyword overlap (same logic as environment)
    overlap = set(pred_tokens).intersection(expected_tokens)
    return len(overlap) > 0


def grade(pred: dict, expected: dict) -> float:
    score = 0.0

    # Normalize inputs to mirror environment behavior
    diagnosis = str(pred.get("diagnosis", "")).lower()
    act = str(pred.get("action", "")).lower()
    reason = str(pred.get("reason", ""))

    expected_diagnosis = str(expected.get("diagnosis", "")).lower()
    expected_action = str(expected.get("action", "")).lower()

    # 1) Diagnosis scoring
    if diagnosis == expected_diagnosis:
        score += 0.35
    elif diagnosis_partial_match(diagnosis, expected_diagnosis):
        score += 0.15

    # 2) Action correctness
    if act == expected_action:
        score += 0.4

    # 3) Reason quality
    if isinstance(reason, str) and len(reason.split()) > 5:
        score += 0.15

    # 4) Efficiency bonus (default step=1 for deterministic grading)
    step = pred.get("step", 1)
    try:
        step = int(step)
    except (TypeError, ValueError):
        step = 1

    if step <= 2 and act == expected_action:
        score += 0.05

    # 5) Penalize bad actions
    bad_actions = {"do_nothing", "ignore", "random_action"}
    if act in bad_actions:
        score -= 0.3

    # 6) Late incorrect penalty
    if step > 3 and act != expected_action:
        score -= 0.1

    score = max(0.0, min(1.0, score))
    return round(score, 2)
