# Composition Policies - Rego Rules for Sprint Planning
#
# These policies enforce composition rules from composition-rules.instructions.md
# Run with: opa eval -d policies/ -i composition.json data.composition

package composition

# ==============================================================================
# Priority Ordering (P0 > P1 > P2 > ...)
# ==============================================================================

# Violation: Lower priority item ahead of higher priority item
violation[msg] {
    composition := input.composition
    
    # Find adjacent items
    i := composition[_]
    j := composition[_]
    i.index < j.index
    
    # Compare priorities (P0=0, P1=1, etc.)
    priority_value(i.tier) > priority_value(j.tier)
    
    msg := sprintf(
        "PRIORITY_ORDER: %s (tier %s) appears before %s (tier %s) at positions %d and %d",
        [i.itemId, i.tier, j.itemId, j.tier, i.index, j.index]
    )
}

# Helper: Convert priority tier to numeric value
priority_value(tier) = value {
    tier_map := {
        "P0": 0,
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,
        "P5": 5,
        "P6": 6
    }
    value := tier_map[tier]
}

# ==============================================================================
# Intra-Tier Score Ordering
# ==============================================================================

# Violation: Within same tier, lower score appears before higher score
violation[msg] {
    composition := input.composition
    
    # Find adjacent items in same tier
    i := composition[_]
    j := composition[_]
    i.index < j.index
    i.tier == j.tier
    
    # Score ordering violated
    i.score < j.score
    
    msg := sprintf(
        "SCORE_ORDER: Within tier %s, %s (score %v) appears before %s (score %v)",
        [i.tier, i.itemId, i.score, j.itemId, j.score]
    )
}

# ==============================================================================
# Feature/Bug Balance
# ==============================================================================

# Violation: Feature percentage below minimum (50%)
violation[msg] {
    input.constraints.featurePercent < 50
    
    msg := sprintf(
        "FEATURE_BALANCE: Feature allocation is %v%%, must be >= 50%%",
        [input.constraints.featurePercent]
    )
}

# Violation: Feature percentage above maximum (80%)
violation[msg] {
    input.constraints.featurePercent > 80
    
    msg := sprintf(
        "FEATURE_BALANCE: Feature allocation is %v%%, must be <= 80%%",
        [input.constraints.featurePercent]
    )
}

# ==============================================================================
# Capacity Constraints
# ==============================================================================

# Violation: Sprint composition exceeds capacity
violation[msg] {
    input.constraints.capacityUsed > 100
    
    msg := sprintf(
        "CAPACITY_EXCEEDED: Sprint uses %v%% of capacity (max 100%%)",
        [input.constraints.capacityUsed]
    )
}

# Warning: Sprint composition very close to capacity
warning[msg] {
    capacity := input.constraints.capacityUsed
    capacity > 90
    capacity <= 100
    
    msg := sprintf(
        "CAPACITY_HIGH: Sprint uses %v%% of capacity, leaving little buffer",
        [capacity]
    )
}

# ==============================================================================
# Bug Policy
# ==============================================================================

# Violation: P0 bugs exist but not all included
violation[msg] {
    # Count P0 bugs in composition
    included_p0_bugs := count([item |
        item := input.composition[_]
        item.type == "bug"
        item.tier == "P0"
    ])
    
    # Get total P0 bugs from excluded list
    excluded_p0_bugs := count([item |
        item := input.excluded[_]
        item.type == "bug"
        item.tier == "P0"
    ])
    
    excluded_p0_bugs > 0
    
    msg := sprintf(
        "BUG_POLICY: %d P0 bugs excluded. All P0 bugs must be included.",
        [excluded_p0_bugs]
    )
}

# ==============================================================================
# Debt Pressure
# ==============================================================================

# Violation: High debt pressure without P2 debt items
violation[msg] {
    input.constraints.debtPressure >= 40
    
    # Count P2 debt items
    debt_count := count([item |
        item := input.composition[_]
        item.type == "debt"
        item.tier == "P2"
    ])
    
    debt_count == 0
    
    msg := sprintf(
        "DEBT_PRESSURE: Debt pressure is %v (>= 40) but no P2 debt items included",
        [input.constraints.debtPressure]
    )
}

# ==============================================================================
# Age Escalation
# ==============================================================================

# Warning: Old items (age >= 3) in P3 or lower
warning[msg] {
    item := input.composition[_]
    item.age >= 3
    priority_value(item.tier) >= 3  # P3 or lower
    
    msg := sprintf(
        "AGE_ESCALATION: %s has age %d and tier %s. Consider escalating.",
        [item.itemId, item.age, item.tier]
    )
}

# ==============================================================================
# Item Count Limits
# ==============================================================================

# Warning: Too many items in sprint
warning[msg] {
    item_count := count(input.composition)
    item_count > 15
    
    msg := sprintf(
        "ITEM_COUNT: Sprint has %d items. Consider reducing scope (typical: 8-12 items).",
        [item_count]
    )
}

# ==============================================================================
# Validation Summary
# ==============================================================================

# Policy passes if no violations
allow {
    count(violation) == 0
}

# Detailed result
result = {
    "allow": allow,
    "violations": violation,
    "warnings": warning,
    "summary": {
        "violation_count": count(violation),
        "warning_count": count(warning),
        "capacity_used": input.constraints.capacityUsed,
        "feature_percent": input.constraints.featurePercent,
        "item_count": count(input.composition)
    }
}
