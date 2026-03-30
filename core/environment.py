import json
from typing import Dict, Any, Tuple
from core.simulator import SystemSimulator


class AIRSEnv:
    VERSION = "1.0"

    def __init__(self, data_path: str = "data/incidents_v1.json"):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.current = None
        self.simulator = None
        self.steps = 0
        self.max_steps = 5
        self.initialized = False
        self.idx = 0

    def reset(self) -> Dict[str, Any]:
        self.current = self.data[self.idx % len(self.data)]
        self.idx += 1
        self.simulator = SystemSimulator(self.current)
        self.steps = 0
        self.initialized = True
        return self._get_obs(include_hint=True)

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, float], bool, Dict[str, Any]]:
        if not self.initialized:
            raise ValueError("Call /reset first")
        self.steps += 1

        # Normalize inputs (robustness)
        diagnosis = str(action.get("diagnosis", "")).lower()
        act = str(action.get("action", "")).lower()
        reason = str(action.get("reason", ""))

        action = {
            "diagnosis": diagnosis,
            "action": act,
            "reason": reason
        }

        # Apply action to simulator
        new_state, effects = self.simulator.apply_action(act)

        # Ensure state update
        self.simulator.state = new_state

        # Compute reward
        reward_score = self._compute_reward(action)

        # Done conditions
        resolved = self.simulator.is_resolved()
        done = resolved or self.steps >= self.max_steps

        # Penalize if unresolved at end
        if done and not resolved:
            reward_score = round(max(0.0, reward_score * 0.8), 2)

        obs = self._get_obs(include_hint=True)

        info = {
            "effects": effects,
            "resolved": resolved,
            "steps_taken": self.steps
        }

        return obs, {"score": reward_score}, done, info

    def _get_obs(self, include_hint: bool = False) -> Dict[str, Any]:
        obs = {
            "incident_id": self.current["id"],
            "alert": self.current["alert"],
            "logs": self.current["logs"],
            "system_status": self.simulator.state,
            "step": self.steps,
            "version": self.VERSION
        }

        if include_hint:
            obs["hint"] = "Look for patterns like timeouts, crashes, or overload signals in logs"

        return obs

    def _diagnosis_partial_match(self, diagnosis: str, expected_diagnosis: str) -> bool:
        if not diagnosis or not expected_diagnosis:
            return False

        diagnosis_norm = diagnosis.strip().lower()
        expected_norm = expected_diagnosis.strip().lower()

        # Substring similarity
        if expected_norm in diagnosis_norm or diagnosis_norm in expected_norm:
            return True

        # Token-based prefix match
        diagnosis_tokens = [t for t in diagnosis_norm.split("_") if t]
        expected_tokens = [t for t in expected_norm.split("_") if t]

        if not diagnosis_tokens or not expected_tokens:
            return False

        if diagnosis_tokens[0] == expected_tokens[0]:
            return True

        # Keyword overlap
        overlap = set(diagnosis_tokens).intersection(expected_tokens)
        return len(overlap) > 0

    def _compute_reward(self, action: Dict[str, Any]) -> float:
        expected = self.current["expected"]
        score = 0.0

        diagnosis = action.get("diagnosis", "")
        act = action.get("action", "")
        reason = action.get("reason", "")

        # 1) Diagnosis scoring
        if diagnosis == expected["diagnosis"]:
            score += 0.35
        elif self._diagnosis_partial_match(diagnosis, expected["diagnosis"]):
            score += 0.15

        # 2) Action correctness
        if act == expected["action"]:
            score += 0.4

        # 3) Reason quality
        if isinstance(reason, str) and len(reason.split()) > 5:
            score += 0.15

        # 4) Efficiency bonus
        if self.steps <= 2 and act == expected["action"]:
            score += 0.05

        # 5) Penalize bad actions
        bad_actions = {"do_nothing", "ignore", "random_action"}
        if act in bad_actions:
            score -= 0.3

        # 6) Late incorrect penalty
        if self.steps > 3 and act != expected["action"]:
            score -= 0.1

        # Clamp
        score = max(0.0, min(1.0, score))
        return round(score, 2)

    def state(self) -> Dict[str, Any]:
        return {
            "incident_id": self.current["id"] if self.current else None,
            "system_status": self.simulator.state if self.simulator else None,
            "step": self.steps
        }