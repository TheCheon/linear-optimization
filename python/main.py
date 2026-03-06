#!/usr/bin/env python3
"""
main.py — Tkinter UI for interactive linear optimization.

Architecture
------------
  main.py          — UI + orchestration
  math.py           — math (solve via PuLP)
  plot.py          — PlotFrame (matplotlib embedded in Tkinter)
"""

import importlib.util
import pathlib
import tkinter as tk
from tkinter import messagebox, ttk

import plot as plot_module

# --------------------------------------------------------------------------
# Load math.py via importlib (hyphens prevent normal import syntax)
# --------------------------------------------------------------------------
def _load_math_lib():
    path = pathlib.Path(__file__).parent / "math.py"
    spec = importlib.util.spec_from_file_location("math", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

lib = _load_math_lib()


# ==========================================================================
# Domain widgets
# ==========================================================================

class VariableRow:
    """One row: variable name | objective coefficient | non-negative checkbox | remove btn."""

    def __init__(self, parent: tk.Frame, on_remove, on_name_change):
        self.frame = tk.Frame(parent, bd=1, relief="groove", padx=4, pady=3)
        self.frame.pack(fill=tk.X, pady=1, padx=2)

        self.name_var = tk.StringVar()
        self.coeff_var = tk.StringVar()
        self.non_neg_var = tk.BooleanVar(value=True)

        tk.Label(self.frame, text="Name:", width=5, anchor="e").pack(side=tk.LEFT)
        name_entry = tk.Entry(self.frame, textvariable=self.name_var, width=6, font=("Courier", 10))
        name_entry.pack(side=tk.LEFT, padx=(0, 6))
        name_entry.bind("<FocusOut>", lambda _: on_name_change())
        name_entry.bind("<Return>",   lambda _: on_name_change())

        tk.Label(self.frame, text="Obj. coeff:", anchor="e").pack(side=tk.LEFT)
        tk.Entry(self.frame, textvariable=self.coeff_var, width=6, font=("Courier", 10)).pack(side=tk.LEFT, padx=(0, 6))

        tk.Checkbutton(self.frame, text="≥ 0", variable=self.non_neg_var).pack(side=tk.LEFT)
        tk.Button(self.frame, text="−", command=on_remove, fg="red", width=2).pack(side=tk.RIGHT)

    def get_data(self) -> dict:
        name = self.name_var.get().strip() or "?"
        try:
            coeff = float(self.coeff_var.get())
        except ValueError:
            coeff = 0.0
        return {"name": name, "obj_coeff": coeff, "non_negative": self.non_neg_var.get()}


class ConstraintRow:
    """One row showing coefficient fields for every variable, operator, and RHS."""

    def __init__(self, parent: tk.Frame, var_names: list[str], on_remove):
        self.frame = tk.Frame(parent, bd=1, relief="groove", padx=4, pady=3)
        self.frame.pack(fill=tk.X, pady=1, padx=2)

        self.coeff_vars: dict[str, tk.StringVar] = {}
        self.op_var  = tk.StringVar(value="<=")
        self.rhs_var = tk.StringVar(value="0")
        self._on_remove = on_remove
        self._rebuild(var_names)

    def _rebuild(self, var_names: list[str]):
        for w in self.frame.winfo_children():
            w.destroy()
        # preserve StringVars for variables that still exist
        new_cvars: dict[str, tk.StringVar] = {}
        for n in var_names:
            new_cvars[n] = self.coeff_vars.get(n, tk.StringVar(value="0"))
        self.coeff_vars = new_cvars

        for i, n in enumerate(var_names):
            if i > 0:
                tk.Label(self.frame, text="+").pack(side=tk.LEFT, padx=1)
            tk.Entry(self.frame, textvariable=self.coeff_vars[n],
                     width=4, font=("Courier", 10)).pack(side=tk.LEFT)
            tk.Label(self.frame, text=f"·{n}", font=("Courier", 10)).pack(side=tk.LEFT, padx=(0, 4))

        tk.OptionMenu(self.frame, self.op_var, "<=", ">=", "=").pack(side=tk.LEFT, padx=4)
        tk.Entry(self.frame, textvariable=self.rhs_var, width=7,
                 font=("Courier", 10)).pack(side=tk.LEFT)
        tk.Button(self.frame, text="−", command=self._on_remove, fg="red",
                  width=2).pack(side=tk.RIGHT, padx=4)

    def update_variables(self, var_names: list[str]):
        self._rebuild(var_names)

    def get_data(self) -> dict:
        coeffs: dict[str, float] = {}
        for n, sv in self.coeff_vars.items():
            try:
                coeffs[n] = float(sv.get())
            except ValueError:
                coeffs[n] = 0.0
        try:
            rhs = float(self.rhs_var.get())
        except ValueError:
            rhs = 0.0
        return {"coeffs": coeffs, "op": self.op_var.get(), "rhs": rhs}


# ==========================================================================
# Main application
# ==========================================================================

class LinearOptimizerApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Linear Optimizer")
        self.geometry("1250x740")
        self.minsize(900, 600)

        self.variable_rows:   list[VariableRow]   = []
        self.constraint_rows: list[ConstraintRow] = []

        self._build_ui()
        # Load demo matching math.py default: max 3x+2y s.t. x+y<=4, x<=2
        self._add_variable("x", 3)
        self._add_variable("y", 2)
        self._add_constraint({"x": 1, "y": 1}, "<=", 4)
        self._add_constraint({"x": 1},          "<=", 2)

    # -----------------------------------------------------------------------
    def _build_ui(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        left  = tk.Frame(paned, width=400)
        left.pack_propagate(False)
        paned.add(left, weight=0)

        right = tk.Frame(paned)
        paned.add(right, weight=1)

        # -- Direction -------------------------------------------------------
        dir_lf = tk.LabelFrame(left, text="Direction")
        dir_lf.pack(fill=tk.X, padx=6, pady=(4, 2))
        self.sense_var = tk.StringVar(value="maximize")
        tk.Radiobutton(dir_lf, text="Maximize", variable=self.sense_var,
                       value="maximize").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(dir_lf, text="Minimize", variable=self.sense_var,
                       value="minimize").pack(side=tk.LEFT)

        # -- Variables -------------------------------------------------------
        var_lf = tk.LabelFrame(left, text="Variables   (name | obj. coefficient | ≥ 0)")
        var_lf.pack(fill=tk.X, padx=6, pady=(2, 2))
        self.var_container = tk.Frame(var_lf)
        self.var_container.pack(fill=tk.X)
        tk.Button(var_lf, text="+ Add Variable",
                  command=self._add_variable).pack(pady=3)

        # -- Constraints (scrollable) ----------------------------------------
        con_lf = tk.LabelFrame(left, text="Constraints")
        con_lf.pack(fill=tk.X, padx=6, pady=(2, 2))

        con_scroll = tk.Frame(con_lf)
        con_scroll.pack(fill=tk.X)
        self._con_canvas = tk.Canvas(con_scroll, height=190, highlightthickness=0)
        con_sb = ttk.Scrollbar(con_scroll, orient="vertical",
                                command=self._con_canvas.yview)
        self.con_inner = tk.Frame(self._con_canvas)
        self.con_inner.bind(
            "<Configure>",
            lambda e: self._con_canvas.configure(
                scrollregion=self._con_canvas.bbox("all")))
        self._con_canvas.create_window((0, 0), window=self.con_inner, anchor="nw")
        self._con_canvas.configure(yscrollcommand=con_sb.set)
        self._con_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        con_sb.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Button(con_lf, text="+ Add Constraint",
                  command=self._add_constraint).pack(pady=3)

        # -- Solve button ----------------------------------------------------
        tk.Button(
            left, text="▶  Solve & Render",
            command=self._solve_and_render,
            bg="#27ae60", fg="white", font=("Arial", 11, "bold"), pady=8,
        ).pack(fill=tk.X, padx=6, pady=6)

        # -- Result text -----------------------------------------------------
        res_lf = tk.LabelFrame(left, text="Result")
        res_lf.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 4))
        self.result_text = tk.Text(
            res_lf, height=8, state=tk.DISABLED,
            bg="#f5f5f5", font=("Courier", 10),
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # -- Plot (right side) -----------------------------------------------
        self.plot_frame = plot_module.PlotFrame(right)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

    # -----------------------------------------------------------------------  helpers
    def _get_var_names(self) -> list[str]:
        return [r.name_var.get().strip() or "?" for r in self.variable_rows]

    def _notify_constraints(self):
        names = self._get_var_names()
        for row in self.constraint_rows:
            row.update_variables(names)

    # -----------------------------------------------------------------------  variables
    def _add_variable(self, name: str | None = None, obj_coeff: float = 1.0):
        if name is None:
            used = set(self._get_var_names())
            name = next(
                (c for c in "xyzabcdefghijklmnopqrstuvw" if c not in used),
                f"v{len(self.variable_rows)}",
            )
        row = VariableRow(
            self.var_container,
            on_remove=lambda: self._remove_variable(row),
            on_name_change=self._notify_constraints,
        )
        row.name_var.set(name)
        row.coeff_var.set(str(obj_coeff))
        self.variable_rows.append(row)
        self._notify_constraints()

    def _remove_variable(self, row: VariableRow):
        if len(self.variable_rows) <= 1:
            messagebox.showwarning("Warning", "At least one variable is required.")
            return
        self.variable_rows.remove(row)
        row.frame.destroy()
        self._notify_constraints()

    # -----------------------------------------------------------------------  constraints
    def _add_constraint(self, coeffs: dict | None = None,
                        op: str = "<=", rhs: float = 0.0):
        names = self._get_var_names()
        row = ConstraintRow(
            self.con_inner, names,
            on_remove=lambda: self._remove_constraint(row),
        )
        if coeffs:
            for n, v in coeffs.items():
                if n in row.coeff_vars:
                    row.coeff_vars[n].set(str(v))
        row.op_var.set(op)
        row.rhs_var.set(str(rhs))
        self.constraint_rows.append(row)

    def _remove_constraint(self, row: ConstraintRow):
        self.constraint_rows.remove(row)
        row.frame.destroy()

    # -----------------------------------------------------------------------  solve
    def _solve_and_render(self):
        try:
            variables   = [r.get_data() for r in self.variable_rows]
            constraints = [r.get_data() for r in self.constraint_rows]
            sense       = self.sense_var.get()

            # validate unique names
            names = [v["name"] for v in variables]
            if len(names) != len(set(names)):
                messagebox.showerror("Error", "Variable names must be unique.")
                return

            result = lib.solve(variables, constraints, sense)

            # update result panel
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Status: {result['status']}\n\n")
            for n, v in result["variables"].items():
                val_str = f"{v:.6f}" if v is not None else "—"
                self.result_text.insert(tk.END, f"  {n} = {val_str}\n")
            obj = result["objective"]
            obj_str = f"{obj:.6f}" if obj is not None else "—"
            self.result_text.insert(tk.END, f"\nObjective = {obj_str}")
            self.result_text.config(state=tk.DISABLED)

            self.plot_frame.render(result, variables, constraints)

        except Exception as exc:
            messagebox.showerror("Error", str(exc))


# ==========================================================================
if __name__ == "__main__":
    app = LinearOptimizerApp()
    app.mainloop()
