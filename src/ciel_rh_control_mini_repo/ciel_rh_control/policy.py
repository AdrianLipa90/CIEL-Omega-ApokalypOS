BASE_POLICIES = {
    "normal_operation": {
        "severity": "low",
        "allowed_actions": ["run", "merge", "route", "compare", "report", "link"],
        "discouraged_actions": [],
        "actions": [
            "Proceed with normal execution.",
            "Keep manifests and README mesh synchronized.",
            "Monitor R_H but do not constrain throughput unnecessarily.",
        ],
        "notes": ["Low coherence defect: expansion is admissible."],
    },
    "slow_execution_local_correction": {
        "severity": "medium",
        "allowed_actions": ["resolve", "report", "link", "compare", "stabilize", "route"],
        "discouraged_actions": ["fast_merge", "broad_refactor"],
        "actions": [
            "Slow execution tempo.",
            "Prefer local correction over large global changes.",
            "Route only through explicit bridges.",
            "Increase reporting and dependency exposure.",
        ],
        "notes": ["Moderate coherence defect: restrict expansion and repair local drift."],
    },
    "freeze_and_rebuild_closure": {
        "severity": "high",
        "allowed_actions": ["resolve", "report", "stabilize", "link", "archive"],
        "discouraged_actions": ["merge", "broad_route", "speculative_refactor", "execution_burst"],
        "actions": [
            "Freeze merges.",
            "Isolate sectors contributing to high defect.",
            "Rebuild closure from constraints and manifests.",
            "Prioritize diagnosis over execution.",
        ],
        "notes": ["High coherence defect: the system should not expand."],
    },
}

SECTOR_OVERRIDES = {
    "runtime": [
        "Reduce execution tempo.",
        "Check memory synchronization before new runs.",
    ],
    "bridge": [
        "Restrict transport to explicit dependency paths.",
        "Audit semantic mismatch and broken bridges first.",
    ],
    "memory": [
        "Check path residue and disappearing-file history.",
        "Prefer stabilization over new writes.",
    ],
    "constraints": [
        "Re-evaluate closure residuals.",
        "Treat hidden bypasses as critical.",
    ],
    "generic": [],
}
