"""
Build enrichment plots: nu_max vs radius, delta_nu vs mass, luminosity vs radius,
mean_density_proxy vs nu_max, surface_gravity_proxy vs nu_max; by class if available.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from pathlib import Path

import pandas as pd


def _scatter(ax, x, y, label: str = "", **kwargs) -> None:
    valid = x.notna() & y.notna()
    valid = valid & (x > 0) & (y > 0) if (x > 0).all() or (y > 0).all() else valid
    if valid.any():
        ax.scatter(x[valid], y[valid], label=label or None, alpha=0.5, s=5, **kwargs)


def build_plots(df: pd.DataFrame, plots_dir: Path) -> None:
    """
    Save PNGs: numax_vs_radius, deltanu_vs_mass, luminosity_vs_radius,
    mean_density_proxy_vs_nu_max, surface_gravity_proxy_vs_nu_max.
    If evolutionary_stage present, add per-class panels or overlaid by class.
    """
    import matplotlib.pyplot as plt

    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams["figure.figsize"] = (6, 4)
    has_class = (
        "evolutionary_stage" in df.columns and df["evolutionary_stage"].notna().any()
    )

    # 1. nu_max vs radius
    fig, ax = plt.subplots()
    if has_class:
        for stage in df["evolutionary_stage"].dropna().unique():
            if not stage:
                continue
            sub = df[df["evolutionary_stage"] == stage]
            _scatter(ax, sub["radius"], sub["nu_max"], label=str(stage))
        ax.legend(loc="best", fontsize=6)
    else:
        _scatter(ax, df["radius"], df["nu_max"])
    ax.set_xlabel("Radius (Rsun)")
    ax.set_ylabel("nu_max (uHz)")
    ax.set_title("nu_max vs Radius")
    ax.set_xscale("log")
    fig.savefig(plots_dir / "numax_vs_radius.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 2. delta_nu vs mass
    fig, ax = plt.subplots()
    if has_class:
        for stage in df["evolutionary_stage"].dropna().unique():
            if not stage:
                continue
            sub = df[df["evolutionary_stage"] == stage]
            _scatter(ax, sub["mass"], sub["delta_nu"], label=str(stage))
        ax.legend(loc="best", fontsize=6)
    else:
        _scatter(ax, df["mass"], df["delta_nu"])
    ax.set_xlabel("Mass (Msun)")
    ax.set_ylabel("delta_nu (uHz)")
    ax.set_title("delta_nu vs Mass")
    fig.savefig(plots_dir / "deltanu_vs_mass.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 3. luminosity vs radius
    L = df.get("luminosity_computed", df.get("luminosity", pd.Series(dtype=float)))
    fig, ax = plt.subplots()
    if has_class:
        for stage in df["evolutionary_stage"].dropna().unique():
            if not stage:
                continue
            sub = df[df["evolutionary_stage"] == stage]
            _scatter(ax, sub["radius"], L.loc[sub.index], label=str(stage))
        ax.legend(loc="best", fontsize=6)
    else:
        _scatter(ax, df["radius"], L)
    ax.set_xlabel("Radius (Rsun)")
    ax.set_ylabel("Luminosity (Lsun)")
    ax.set_title("Luminosity vs Radius")
    ax.set_xscale("log")
    ax.set_yscale("log")
    fig.savefig(plots_dir / "luminosity_vs_radius.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 4. mean_density_proxy vs nu_max
    fig, ax = plt.subplots()
    if has_class:
        for stage in df["evolutionary_stage"].dropna().unique():
            if not stage:
                continue
            sub = df[df["evolutionary_stage"] == stage]
            _scatter(ax, sub["mean_density_proxy"], sub["nu_max"], label=str(stage))
        ax.legend(loc="best", fontsize=6)
    else:
        _scatter(ax, df["mean_density_proxy"], df["nu_max"])
    ax.set_xlabel("mean_density_proxy (mass/radius^3)")
    ax.set_ylabel("nu_max (uHz)")
    ax.set_title("Mean density proxy vs nu_max")
    ax.set_xscale("log")
    fig.savefig(
        plots_dir / "mean_density_proxy_vs_nu_max.png", dpi=150, bbox_inches="tight"
    )
    plt.close(fig)

    # 5. surface_gravity_proxy vs nu_max
    fig, ax = plt.subplots()
    if has_class:
        for stage in df["evolutionary_stage"].dropna().unique():
            if not stage:
                continue
            sub = df[df["evolutionary_stage"] == stage]
            _scatter(ax, sub["surface_gravity_proxy"], sub["nu_max"], label=str(stage))
        ax.legend(loc="best", fontsize=6)
    else:
        _scatter(ax, df["surface_gravity_proxy"], df["nu_max"])
    ax.set_xlabel("surface_gravity_proxy (mass/radius^2)")
    ax.set_ylabel("nu_max (uHz)")
    ax.set_title("Surface gravity proxy vs nu_max")
    ax.set_xscale("log")
    fig.savefig(
        plots_dir / "surface_gravity_proxy_vs_nu_max.png", dpi=150, bbox_inches="tight"
    )
    plt.close(fig)
