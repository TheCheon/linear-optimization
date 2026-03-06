# Constraints
# x+y <= 100
# x > 60
# y > 23
"""x=5, y=10   ---> Gewinn; f(x,y)=5x+10y | while conditions met"""

# Generate all valid (x,y) points that satisfy the constraints
# x ranges from 61 to 76 (x > 60)
# y ranges from 24 to (100-x) (y > 23 and x+y <= 100)

DEBUG = True

import matplotlib.pyplot as plt # pyright: ignore[reportMissingModuleSource]
import numpy as np

def opt_ln():
    opt_v = [(5*x + 10*y, x, y) for x in range(60,77) for y in range(24, 100-x+1)]
    print(f"Generated {len(opt_v)} valid (profit, x, y) tuples") if DEBUG else None
    return opt_v # return all points with 3d tuple with scheme (gain,x,y)

def plot_smooth_gradient(opt_v):
    """Plot a smooth profit gradient over the feasible region with
    - dynamic plotting bounds derived from `opt_v` (with safe fallbacks)
    - configurable `grid` density and optional plotting of integer points
    - strict masking that matches the constraints (x+y>100, x<=60, y<=23)

    Parameters:
    - opt_v: list of (profit, x, y) tuples
    - grid: resolution per axis (default 400)
    - show_points: if True, overlay integer feasible points
    - eps: small offset to respect strict inequalities
    """
    def _safe_bounds(xs_arr, ys_arr, eps):
        # derive bounds from data and constraints, with padding
        x_min = max(60 + eps, xs_arr.min() - 1)
        x_max = min(100 - (23 + eps), xs_arr.max() + 1)
        y_min = max(23 + eps, ys_arr.min() - 1)
        y_max = min(100 - (60 + eps), ys_arr.max() + 1)
        # fallbacks if derived bounds are degenerate
        if x_min >= x_max:
            x_min, x_max = 60 + eps, 76.99
        if y_min >= y_max:
            y_min, y_max = 23 + eps, 39.99
        print(f"Plot bounds: x [{x_min:.2f}, {x_max:.2f}], y [{y_min:.2f}, {y_max:.2f}]") if DEBUG else None
        return x_min, x_max, y_min, y_max

    # Parameters
    grid = 400
    show_points = False
    eps = 1e-3

    if not opt_v:
        raise ValueError("opt_v is empty — nothing to plot")

    profits, xs_t, ys_t = zip(*opt_v)
    xs = np.array(xs_t, dtype=float)
    ys = np.array(ys_t, dtype=float)

    x_min, x_max, y_min, y_max = _safe_bounds(xs, ys, eps)

    x_vals = np.linspace(x_min, x_max, grid)
    y_vals = np.linspace(y_min, y_max, grid)
    X, Y = np.meshgrid(x_vals, y_vals)

    # continuous profit function (analytic)
    Profit = 5 * X + 10 * Y

    # mask outside feasible region: keep points meeting x>60, y>23, x+y<=100
    mask = (X + Y > 100) | (X <= 60) | (Y <= 23)
    Profit_masked = np.ma.array(Profit, mask=mask)

    fig, ax = plt.subplots(figsize=(6, 6))
    pcm = ax.pcolormesh(X, Y, Profit_masked, cmap="Reds", shading="auto")
    fig.colorbar(pcm, ax=ax, label="profit")

    # constraint lines
    x = np.linspace(60, 100, 200)
    ax.plot(x, 100 - x, color="k", lw=1, label="x+y=100")
    ax.axvline(60, color="orange", label="x=60")
    ax.axhline(23, color="green", label="y=23")

    # highlight best integer point
    best = max(opt_v, key=lambda t: t[0])
    ax.scatter([best[1]], [best[2]], s=160, c="gold", marker="*", edgecolor="k", label=f"best {best}")

    ax.set_xlim(x_min - 0.5, x_max + 0.5)
    ax.set_ylim(y_min - 0.5, y_max + 0.5)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="box")
    ax.legend()
    plt.tight_layout()
    plt.show()


def main():
    opt_v = opt_ln()
    plot_smooth_gradient(opt_v)



if __name__ == "__main__":
    main()