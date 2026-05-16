"""Sprint composition linter — pure-Python port of policies/composition.rego.

Public API:
    lint(composition: dict) -> dict   # {'violations': [...], 'warnings': [...]}

Input shape mirrors what the original Rego policy consumed:

    {
      "composition": [
        {"itemId": str, "type": "feature"|"bug"|"debt", "tier": "P0".."P6",
         "score": float, "age": int, "index": int},
        ...
      ],
      "excluded": [
        {"itemId": str, "type": ..., "tier": ...},
        ...
      ],
      "constraints": {
        "featurePercent": float,   # 0-100
        "capacityUsed": float,     # 0-100+
        "debtPressure": float      # 0-100
      }
    }

Message prefixes match composition.rego exactly so existing references stay valid.
"""

from __future__ import annotations

_TIER_VALUE = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5, "P6": 6}


def _priority_value(tier: str) -> int:
    return _TIER_VALUE[tier]


def lint(composition: dict) -> dict:
    violations: list[str] = []
    warnings: list[str] = []

    items = composition.get("composition", [])
    excluded = composition.get("excluded", [])
    constraints = composition.get("constraints", {})

    # Priority order
    for i in items:
        for j in items:
            if i["index"] < j["index"] and _priority_value(i["tier"]) > _priority_value(j["tier"]):
                violations.append(
                    f"PRIORITY_ORDER: {i['itemId']} (tier {i['tier']}) appears before "
                    f"{j['itemId']} (tier {j['tier']}) at positions {i['index']} and {j['index']}"
                )

    # Intra-tier score order
    for i in items:
        for j in items:
            if i["index"] < j["index"] and i["tier"] == j["tier"] and i["score"] < j["score"]:
                violations.append(
                    f"SCORE_ORDER: Within tier {i['tier']}, {i['itemId']} (score {i['score']}) "
                    f"appears before {j['itemId']} (score {j['score']})"
                )

    # Feature balance
    feature_pct = constraints.get("featurePercent")
    if feature_pct is not None:
        if feature_pct < 50:
            violations.append(
                f"FEATURE_BALANCE: Feature allocation is {feature_pct}%, must be >= 50%"
            )
        if feature_pct > 80:
            violations.append(
                f"FEATURE_BALANCE: Feature allocation is {feature_pct}%, must be <= 80%"
            )

    # Capacity
    capacity = constraints.get("capacityUsed")
    if capacity is not None:
        if capacity > 100:
            violations.append(
                f"CAPACITY_EXCEEDED: Sprint uses {capacity}% of capacity (max 100%)"
            )
        elif capacity > 90:
            warnings.append(
                f"CAPACITY_HIGH: Sprint uses {capacity}% of capacity, leaving little buffer"
            )

    # Bug policy
    excluded_p0_bugs = sum(1 for x in excluded if x.get("type") == "bug" and x.get("tier") == "P0")
    if excluded_p0_bugs > 0:
        violations.append(
            f"BUG_POLICY: {excluded_p0_bugs} P0 bugs excluded. All P0 bugs must be included."
        )

    # Debt pressure
    debt_pressure = constraints.get("debtPressure")
    if debt_pressure is not None and debt_pressure >= 40:
        p2_debt = sum(1 for it in items if it.get("type") == "debt" and it.get("tier") == "P2")
        if p2_debt == 0:
            violations.append(
                f"DEBT_PRESSURE: Debt pressure is {debt_pressure} (>= 40) but no P2 debt items included"
            )

    # Age escalation
    for it in items:
        if it.get("age", 0) >= 3 and _priority_value(it["tier"]) >= 3:
            warnings.append(
                f"AGE_ESCALATION: {it['itemId']} has age {it['age']} and tier {it['tier']}. "
                f"Consider escalating."
            )

    # Item count
    if len(items) > 15:
        warnings.append(
            f"ITEM_COUNT: Sprint has {len(items)} items. Consider reducing scope "
            f"(typical: 8-12 items)."
        )

    return {"violations": violations, "warnings": warnings}
