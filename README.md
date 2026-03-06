# linear-optimization

Brief
-----
Minimal utilities and examples for solving small linear optimization problems (LP/MIP) with a configurable solver backend.

Requirements
------------
- Python 3.8+
- pip
- Optional: a native solver (GLPK/COIN-OR/CPLEX/Gurobi) if used by the backend

Quickstart
----------
1. Create and activate a venv:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
2. Install dependencies:
    - pip install -r requirements.txt
3. Run an example:
    - python examples/simple.py
    - or: python scripts/solve.py --input data/problem.json --solver glpk --output results/

Usage
-----
- examples/ contains runnable demos.
- scripts/ or src/ contains the solver entrypoint(s).
- Common CLI flags:
  - --input <file>   Input model/data
  - --solver <name>  Solver backend to use
  - --output <dir>   Output directory for solutions/logs

Project layout
--------------
- examples/    — small demo problems
- data/        — sample input files
- src/ or scripts/ — solver code and utilities
- requirements.txt
- tests/       — unit/integration tests (if present)

Testing & Contributing
----------------------
- Run tests: pytest
- Open an issue or submit a PR with concise description and a reproducible example.

License
-------
Specify project license (e.g., MIT) in LICENSE file.