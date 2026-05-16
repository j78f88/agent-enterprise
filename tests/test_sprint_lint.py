"""Tests for tools.sprint_lint — at least one positive and one negative case per rule."""

from tools.sprint_lint import lint


def _item(item_id, idx, tier="P1", score=1.0, age=0, type_="feature"):
    return {
        "itemId": item_id,
        "type": type_,
        "tier": tier,
        "score": score,
        "age": age,
        "index": idx,
    }


def _base(items=None, excluded=None, feature=70, capacity=80, debt=10):
    return {
        "composition": items or [],
        "excluded": excluded or [],
        "constraints": {
            "featurePercent": feature,
            "capacityUsed": capacity,
            "debtPressure": debt,
        },
    }


# --- PRIORITY_ORDER ---------------------------------------------------------

def test_priority_order_violation():
    items = [_item("a", 0, tier="P2"), _item("b", 1, tier="P0")]
    result = lint(_base(items=items))
    assert any(v.startswith("PRIORITY_ORDER:") for v in result["violations"])


def test_priority_order_clean():
    items = [_item("a", 0, tier="P0"), _item("b", 1, tier="P1")]
    result = lint(_base(items=items))
    assert not any(v.startswith("PRIORITY_ORDER:") for v in result["violations"])


# --- SCORE_ORDER ------------------------------------------------------------

def test_score_order_violation():
    items = [_item("a", 0, tier="P1", score=1.0), _item("b", 1, tier="P1", score=5.0)]
    result = lint(_base(items=items))
    assert any(v.startswith("SCORE_ORDER:") for v in result["violations"])


def test_score_order_clean():
    items = [_item("a", 0, tier="P1", score=5.0), _item("b", 1, tier="P1", score=1.0)]
    result = lint(_base(items=items))
    assert not any(v.startswith("SCORE_ORDER:") for v in result["violations"])


# --- FEATURE_BALANCE --------------------------------------------------------

def test_feature_balance_too_low():
    result = lint(_base(feature=30))
    assert any("must be >= 50%" in v for v in result["violations"])


def test_feature_balance_too_high():
    result = lint(_base(feature=90))
    assert any("must be <= 80%" in v for v in result["violations"])


def test_feature_balance_clean():
    result = lint(_base(feature=65))
    assert not any(v.startswith("FEATURE_BALANCE:") for v in result["violations"])


# --- CAPACITY ---------------------------------------------------------------

def test_capacity_exceeded():
    result = lint(_base(capacity=120))
    assert any(v.startswith("CAPACITY_EXCEEDED:") for v in result["violations"])


def test_capacity_high_warning():
    result = lint(_base(capacity=95))
    assert any(w.startswith("CAPACITY_HIGH:") for w in result["warnings"])


def test_capacity_clean():
    result = lint(_base(capacity=70))
    assert not any(v.startswith("CAPACITY_EXCEEDED:") for v in result["violations"])
    assert not any(w.startswith("CAPACITY_HIGH:") for w in result["warnings"])


# --- BUG_POLICY -------------------------------------------------------------

def test_bug_policy_violation():
    excluded = [{"itemId": "bug1", "type": "bug", "tier": "P0"}]
    result = lint(_base(excluded=excluded))
    assert any(v.startswith("BUG_POLICY:") for v in result["violations"])


def test_bug_policy_clean():
    result = lint(_base(excluded=[]))
    assert not any(v.startswith("BUG_POLICY:") for v in result["violations"])


# --- DEBT_PRESSURE ----------------------------------------------------------

def test_debt_pressure_violation():
    items = [_item("a", 0, tier="P1")]
    result = lint(_base(items=items, debt=50))
    assert any(v.startswith("DEBT_PRESSURE:") for v in result["violations"])


def test_debt_pressure_satisfied():
    items = [_item("d", 0, tier="P2", type_="debt")]
    result = lint(_base(items=items, debt=50))
    assert not any(v.startswith("DEBT_PRESSURE:") for v in result["violations"])


# --- AGE_ESCALATION ---------------------------------------------------------

def test_age_escalation_warning():
    items = [_item("a", 0, tier="P3", age=5)]
    result = lint(_base(items=items))
    assert any(w.startswith("AGE_ESCALATION:") for w in result["warnings"])


def test_age_escalation_clean():
    items = [_item("a", 0, tier="P1", age=5)]
    result = lint(_base(items=items))
    assert not any(w.startswith("AGE_ESCALATION:") for w in result["warnings"])


# --- ITEM_COUNT -------------------------------------------------------------

def test_item_count_warning():
    items = [_item(f"i{n}", n, tier="P1") for n in range(20)]
    result = lint(_base(items=items))
    assert any(w.startswith("ITEM_COUNT:") for w in result["warnings"])


def test_item_count_clean():
    items = [_item(f"i{n}", n, tier="P1") for n in range(10)]
    result = lint(_base(items=items))
    assert not any(w.startswith("ITEM_COUNT:") for w in result["warnings"])
