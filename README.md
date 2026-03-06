# linear-optimization

An interactive desktop app for solving and visualising linear optimisation problems.
Define variables and constraints through a graphical UI, solve with one click, and see the
feasible region rendered as a smooth heatmap with the optimal point highlighted.

---

## Requirements

- Python 3.10+
- Tkinter (usually bundled with Python; on Debian/Ubuntu: `sudo apt install python3-tk`)
- All other dependencies are installed automatically on first launch

---

## Quickstart

**Linux / macOS**

```bash
bash start.sh
```

**Windows**

Double-click `start.bat`, or run it from a terminal:

```bat
start.bat
```

On first run the script creates a `.venv` virtualenv and installs all dependencies
(`numpy`, `matplotlib`, `pulp`, `Pillow`). Subsequent launches skip setup and start
the app directly.

---

## Project layout

```
python/
  main.py      — Tkinter UI (variables, constraints, solve button)
  solver.py    — PuLP backend; exposes solve()
  plot.py      — PlotFrame with matplotlib heatmap visualisation
start.sh       — Linux/macOS launcher (setup + run)
start.bat      — Windows launcher (setup + run)
requirements.txt
```

---

## Usage

1. Add **variables** (name, objective coefficient, non-negative flag).
2. Add **constraints** (coefficients for each variable, operator `<=` / `>=` / `=`, RHS value).
3. Choose **Maximise** or **Minimise** and click **Solve**.
4. The result and a heatmap of the feasible region appear on the right.

For two variables the heatmap shows the full feasible region; for more variables pairwise
projections are displayed. If the problem is infeasible or unbounded, a clear message is
shown instead of crashing.

---

## Pre-built binaries

GitHub Actions builds a single-file executable for Linux, Windows, and macOS on every push
to `main`. Download the artifact for your platform from the
[Actions tab](../../actions) — no Python installation required.

---

## License

MIT
