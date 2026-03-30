
class SystemSimulator:
    def __init__(self, incident: dict):
        # Copy initial system state
        self.state = incident["system_status"].copy()

    def apply_action(self, action: str):
        effects = []

        if action == "restart_database":
            if self.state.get("database") != "healthy":
                self.state["database"] = "healthy"
                effects.append("Database recovered")

        elif action == "restart_api":
            if self.state.get("api") != "healthy":
                self.state["api"] = "healthy"
                effects.append("API restarted")

        elif action == "scale_cache":
            if self.state.get("cache") != "healthy":
                self.state["cache"] = "healthy"
                effects.append("Cache scaled")
                # Stabilize dependent services when cache is fixed
                if self.state.get("api") in ["degraded", "slow"]:
                    self.state["api"] = "healthy"
                    effects.append("API stabilized (cache dependency resolved)")
                if self.state.get("database") == "slow":
                    self.state["database"] = "healthy"
                    effects.append("Database stabilized (cache dependency resolved)")

        elif action == "restart_service":
            # Generic action: try to recover all degraded services partially
            for k, v in self.state.items():
                if v != "healthy":
                    self.state[k] = "degraded"
            effects.append("Generic restart attempted")

        else:
            effects.append("No meaningful effect")

        return self.state, effects

    def is_resolved(self):
        return all(v == "healthy" for v in self.state.values())
