"""Independent evidence-aware aggregation example."""
from math import isfinite

def aggregate(signals):
    numerator = denominator = 0.0
    included, excluded, weights = [], [], {}
    for signal in signals:
        name = signal["name"]
        if not isinstance(name, str) or not name or name in weights:
            raise ValueError("names must be unique nonempty strings")
        score, weight, scope = signal["score"], signal["weight"], signal.get("scope")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not isfinite(weight) or weight <= 0:
            raise ValueError("weight must be finite and positive")
        if score is not None and (isinstance(score, bool) or not isinstance(score, (int, float)) or not isfinite(score) or not 0 <= score <= 100):
            raise ValueError("score must be null or a finite number in [0,100]")
        if scope not in (None, "standard", "directional", "unavailable"):
            raise ValueError("unsupported scope")
        reason = "evidence unavailable" if scope == "unavailable" else ("value missing" if score is None else None)
        weights[name] = 0.0 if reason else float(weight)
        if reason:
            excluded.append({"name": name, "reason": reason})
        else:
            included.append(name)
            numerator += score * weight
            denominator += weight
            if not isfinite(numerator) or not isfinite(denominator):
                raise ValueError("aggregation overflow")
    return {
        "score": numerator / denominator if denominator else None,
        "evaluation": "unavailable" if not included else ("partial" if excluded else "available"),
        "effective_weights": weights, "included": included, "excluded": excluded,
    }
