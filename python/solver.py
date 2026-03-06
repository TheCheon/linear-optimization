#!/usr/bin/env python3
"""
solver.py — math backend for the linear optimizer UI.

Public API
----------
solve(variables, constraints, sense) -> dict
    variables   : [{"name": str, "obj_coeff": float, "non_negative": bool}, ...]
    constraints : [{"coeffs": {var_name: float}, "op": "<="|">="|"=", "rhs": float}, ...]
    sense       : "maximize" | "minimize"
    returns     : {"status": str, "variables": {name: float}, "objective": float, "sense": str}
"""

import pulp as pl


def solve(variables: list[dict], constraints: list[dict], sense: str = "maximize") -> dict:
    sense_map = {"maximize": pl.LpMaximize, "minimize": pl.LpMinimize}
    prob = pl.LpProblem("LinOpt", sense_map.get(sense.lower(), pl.LpMaximize))

    lp_vars: dict[str, pl.LpVariable] = {}
    for v in variables:
        lb = 0.0 if v.get("non_negative", True) else None
        lp_vars[v["name"]] = pl.LpVariable(v["name"], lowBound=lb)

    # objective
    prob += pl.lpSum(v["obj_coeff"] * lp_vars[v["name"]] for v in variables)

    # constraints
    for c in constraints:
        expr = pl.lpSum(
            coeff * lp_vars[name]
            for name, coeff in c["coeffs"].items()
            if name in lp_vars
        )
        op, rhs = c["op"], c["rhs"]
        if op == "<=":
            prob += expr <= rhs
        elif op == ">=":
            prob += expr >= rhs
        else:  # "="
            prob += expr == rhs

    prob.solve(pl.PULP_CBC_CMD(msg=0))

    return {
        "status": pl.LpStatus[prob.status],
        "variables": {v["name"]: lp_vars[v["name"]].varValue for v in variables},
        "objective": pl.value(prob.objective),
        "sense": sense,
    }


# ---------------------------------------------------------------------------
# Demo — runs only when this file is executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    result = solve(
        variables=[
            {"name": "x", "obj_coeff": 3, "non_negative": True},
            {"name": "y", "obj_coeff": 2, "non_negative": True},
        ],
        constraints=[
            {"coeffs": {"x": 1, "y": 1}, "op": "<=", "rhs": 4},
            {"coeffs": {"x": 1},          "op": "<=", "rhs": 2},
        ],
        sense="maximize",
    )
    print("Status   :", result["status"])
    for name, val in result["variables"].items():
        print(f"  {name} = {val}")
    print("Objective:", result["objective"])
