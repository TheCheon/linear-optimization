import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

_PALETTE = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22"]


class PlotFrame(tk.Frame):
    """Tkinter frame that embeds a matplotlib figure and re-renders on demand."""

    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.fig = Figure(dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

    # ------------------------------------------------------------------
    def render(self, result: dict, variables: list[dict], constraints: list[dict]):
        self.fig.clear()
        var_names = list(result["variables"])
        if len(var_names) == 2:
            self._render_2d(result, variables, constraints, var_names)
        else:
            self._render_bar(result, variables)
        self.fig.tight_layout()
        self.canvas.draw()

    # ------------------------------------------------------------------  2-variable plot
    def _render_2d(self, result, variables, constraints, var_names):
        ax = self.fig.add_subplot(111)
        xn, yn = var_names
        vmap = {v["name"]: v for v in variables}
        obj_x, obj_y = vmap[xn]["obj_coeff"], vmap[yn]["obj_coeff"]
        x_nn = vmap[xn].get("non_negative", True)
        y_nn = vmap[yn].get("non_negative", True)

        xv = result["variables"].get(xn) or 0.0
        yv = result["variables"].get(yn) or 0.0
        x_lo, x_hi, y_lo, y_hi = self._compute_bounds_2d(
            constraints, xn, yn, xv, yv, x_nn, y_nn
        )

        # --- dense grid & objective heatmap ---
        xx = np.linspace(x_lo, x_hi, 500)
        yy = np.linspace(y_lo, y_hi, 500)
        X, Y = np.meshgrid(xx, yy)
        Z = obj_x * X + obj_y * Y

        # --- feasibility mask ---
        mask = np.zeros(X.shape, dtype=bool)
        if x_nn:
            mask |= X < 0
        if y_nn:
            mask |= Y < 0
        for c in constraints:
            cx = c["coeffs"].get(xn, 0.0)
            cy = c["coeffs"].get(yn, 0.0)
            expr = cx * X + cy * Y
            op = c["op"]
            if op == "<=":
                mask |= expr > c["rhs"] + 1e-9
            elif op == ">=":
                mask |= expr < c["rhs"] - 1e-9
            else:
                mask |= np.abs(expr - c["rhs"]) > 1e-6

        Zm = np.ma.array(Z, mask=mask)
        pcm = ax.pcolormesh(X, Y, Zm, cmap="Reds", shading="auto")
        self.fig.colorbar(pcm, ax=ax, label="Objective value")

        # --- constraint boundary lines ---
        x_plot = np.linspace(x_lo, x_hi, 400)
        for i, c in enumerate(constraints):
            cx = c["coeffs"].get(xn, 0.0)
            cy = c["coeffs"].get(yn, 0.0)
            rhs, op = c["rhs"], c["op"]
            color = _PALETTE[i % len(_PALETTE)]
            parts = [f"{cx}·{xn}" if cx else "", f"{cy}·{yn}" if cy else ""]
            label = " + ".join(p for p in parts if p) + f" {op} {rhs}"
            if abs(cy) > 1e-9:
                ax.plot(x_plot, (rhs - cx * x_plot) / cy, color=color, lw=1.5, label=label)
            elif abs(cx) > 1e-9:
                ax.axvline(rhs / cx, color=color, lw=1.5, label=label)

        # axis guides
        if x_nn:
            ax.axvline(0, color="#aaa", lw=0.8, ls="--")
        if y_nn:
            ax.axhline(0, color="#aaa", lw=0.8, ls="--")

        # --- optimum star ---
        if result["variables"].get(xn) is not None:
            ax.scatter([xv], [yv], c="gold", s=220, marker="*", edgecolors="k", zorder=6, label="Optimum")
            ax.annotate(
                f"  ({xv:.3f}, {yv:.3f})\n  obj = {result['objective']:.4f}",
                (xv, yv), fontsize=9, zorder=7,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.85),
            )

        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(xn, fontsize=11)
        ax.set_ylabel(yn, fontsize=11)
        sense_str = result.get("sense", "maximize").capitalize()
        ax.set_title(f"{sense_str}  {obj_x}·{xn} + {obj_y}·{yn}", fontsize=12)
        ax.legend(loc="upper right", fontsize=8, framealpha=0.85)

    # ------------------------------------------------------------------  n-variable bar chart
    def _render_bar(self, result, variables):
        ax = self.fig.add_subplot(111)
        names = list(result["variables"])
        vals = [result["variables"][n] or 0.0 for n in names]
        bars = ax.bar(names, vals, color=_PALETTE[: len(names)], edgecolor="k")
        ax.bar_label(bars, fmt="%.4f", padding=3)
        ax.set_ylabel("Variable value")
        ax.set_title(
            f"{result.get('sense','maximize').capitalize()}  —  "
            f"objective = {result['objective']:.4f}\n"
            "(2-D plot available only for 2-variable problems)",
            fontsize=10,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _compute_bounds_2d(constraints, xn, yn, xv, yv, x_nn, y_nn, pad=0.5):
        """Return (x_lo, x_hi, y_lo, y_hi) tight bounds derived from constraints
        and the optimal point, matching the brute-force plotter's dynamic approach."""
        x_lo = 0.0 if x_nn else -1.0
        y_lo = 0.0 if y_nn else -1.0
        x_hi_vals, y_hi_vals = [], []

        for c in constraints:
            cx = c["coeffs"].get(xn, 0.0)
            cy = c["coeffs"].get(yn, 0.0)
            rhs = c["rhs"]
            # x intercept (y=0)
            if abs(cx) > 1e-9:
                x_hi_vals.append(abs(rhs / cx))
            # y intercept (x=0)
            if abs(cy) > 1e-9:
                y_hi_vals.append(abs(rhs / cy))

        # include the optimal point in bounds
        x_hi_vals.append(abs(xv))
        y_hi_vals.append(abs(yv))

        x_hi = max(x_hi_vals) * 1.15 + pad if x_hi_vals else 10.0
        y_hi = max(y_hi_vals) * 1.15 + pad if y_hi_vals else 10.0

        return x_lo - pad, x_hi, y_lo - pad, y_hi

def plot_solution(
    x_val=None,
    y_val=None,
    objective_value=None,
    x_var=None,
    y_var=None,
    prob=None,
    pulp=None,
    x_bounds=(-0.1, 2.1),
    y_bounds=(-0.1, 4.1),
    grid=(400, 400),
    cmap='viridis',
    show=True,
    ax=None,
):
    """
    Plot feasible region and objective for the toy LP.
    Provide either numeric x_val,y_val (and optionally objective_value)
    or provide solver variables x_var,y_var and optionally prob+pulp to read objective.
    Returns (fig, ax).
    """
    # resolve numeric solution values from variables if needed
    if x_val is None and x_var is not None:
        x_val = getattr(x_var, "varValue", None)
    if y_val is None and y_var is not None:
        y_val = getattr(y_var, "varValue", None)

    if x_val is None or y_val is None:
        raise ValueError("x_val and y_val must be provided either directly or via x_var/y_var.")

    # resolve objective value
    if objective_value is None:
        if prob is not None and pulp is not None:
            try:
                objective_value = pulp.value(prob.objective)
            except Exception:
                objective_value = None
        if objective_value is None:
            # fallback: compute 3x+2y
            objective_value = 3 * x_val + 2 * y_val

    # grid
    nx, ny = grid if isinstance(grid, (tuple, list)) else (grid, grid)
    xx = np.linspace(x_bounds[0], x_bounds[1], nx)
    yy = np.linspace(y_bounds[0], y_bounds[1], ny)
    X, Y = np.meshgrid(xx, yy)

    # objective on grid
    Z = 3 * X + 2 * Y

    # mask infeasible points (constraints: x+y<=4, 0<=x<=2, y>=0)
    mask = (X + Y > 4) | (X > 2) | (X < 0) | (Y < 0)
    Zm = np.ma.array(Z, mask=mask)

    # plotting
    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
        created_fig = True
    else:
        fig = ax.figure

    pcm = ax.pcolormesh(X, Y, Zm, cmap=cmap, shading='auto')
    if created_fig:
        fig.colorbar(pcm, ax=ax, label='Objective 3x+2y')

    # constraint boundaries
    ax.plot(xx, np.clip(4 - xx, -10 * abs(y_bounds[0] or 1), 10 * abs(y_bounds[1] or 1)), color='k', lw=1)
    ax.axvline(2, color='orange', lw=1)
    ax.axvline(0, color='k', lw=0.8)
    ax.axhline(0, color='k', lw=0.8)

    # mark solver result
    ax.scatter([x_val], [y_val], c='gold', s=150, marker='*', edgecolors='k')
    ann_text = f'({x_val:.2f}, {y_val:.2f})'
    if objective_value is not None:
        ann_text += f'\nObj={objective_value:.2f}'
    ax.annotate(ann_text, (x_val, y_val), textcoords='offset points', xytext=(8, 8))

    ax.set_xlim(*x_bounds)
    ax.set_ylim(*y_bounds)
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_aspect('equal')

    if show:
        plt.show()

    return fig, ax