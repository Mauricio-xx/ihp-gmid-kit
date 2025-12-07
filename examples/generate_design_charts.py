#!/usr/bin/env python3
"""
Generate gm/ID Design Charts for IHP SG13G2

Generates the 4 fundamental design charts for NMOS and PMOS:
- Transit Frequency (fT) vs gm/ID
- Intrinsic Gain (gm/gds) vs gm/ID
- Current Density (ID/W) vs gm/ID
- Transconductance Density (gm/W) vs gm/ID

Output: 8 PNG files at 300 dpi in ./design_charts/
"""

import sys
import os

# Add vendor to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vendor')))

from pathlib import Path
import matplotlib.pyplot as plt

# Configure 300 dpi output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

from mosplot.plot import Mosfet, Expression, load_lookup_table


def create_gm_density_expression(width: float) -> Expression:
    """Create gm/W expression."""
    return Expression(
        variables=["gm"],
        function=lambda x: x / width,
        label="$g_m/W\\ (S/m)$"
    )


def generate_charts(mos: Mosfet, mos_type: str, output_dir: str):
    """Generate all 4 design charts for a transistor type."""
    print(f"\n{mos_type.upper()} Charts:")

    # fT vs gm/ID
    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=mos.transist_frequency_expression,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        y_eng_format=True,
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=os.path.join(output_dir, f"{mos_type}_ft_vs_gmid.png")
    )
    print(f"  {mos_type}_ft_vs_gmid.png")

    # Gain vs gm/ID
    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=mos.gain_expression,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=os.path.join(output_dir, f"{mos_type}_gain_vs_gmid.png")
    )
    print(f"  {mos_type}_gain_vs_gmid.png")

    # ID/W vs gm/ID
    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=mos.current_density_expression,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        y_eng_format=True,
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=os.path.join(output_dir, f"{mos_type}_id_w_vs_gmid.png")
    )
    print(f"  {mos_type}_id_w_vs_gmid.png")

    # gm/W vs gm/ID
    gm_density = create_gm_density_expression(mos.width)
    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=gm_density,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        y_eng_format=True,
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=os.path.join(output_dir, f"{mos_type}_gm_w_vs_gmid.png")
    )
    print(f"  {mos_type}_gm_w_vs_gmid.png")


def main():
    script_dir = Path(__file__).parent
    data_dir = script_dir / ".." / "data"
    output_dir = script_dir / "design_charts"

    os.makedirs(output_dir, exist_ok=True)
    print(f"Output: {output_dir}")

    # NMOS
    nmos_path = data_dir / "sg13_lv_nmos.npz"
    if nmos_path.exists():
        nmos_lt = load_lookup_table(str(nmos_path))
        nmos = Mosfet(
            lookup_table=nmos_lt,
            mos="sg13_lv_nmos",
            vbs=0.0,
            vds=0.6,
            vgs=(0.3, 1.2)
        )
        generate_charts(nmos, "nmos", str(output_dir))

    # PMOS
    pmos_path = data_dir / "sg13_lv_pmos.npz"
    if pmos_path.exists():
        pmos_lt = load_lookup_table(str(pmos_path))
        pmos = Mosfet(
            lookup_table=pmos_lt,
            mos="sg13_lv_pmos",
            vbs=0.0,
            vds=-0.6,
            vgs=(-1.2, -0.3)
        )
        generate_charts(pmos, "pmos", str(output_dir))

    print(f"\nDone. Charts saved to {output_dir}/")


if __name__ == "__main__":
    main()
