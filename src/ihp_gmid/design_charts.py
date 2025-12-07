#!/usr/bin/env python3
"""
IHP SG13G2 Design Charts Generator

Generates the 4 fundamental gm/ID design methodology charts:
1. Transit Frequency (fT) vs gm/ID
2. Intrinsic Gain (gm/gds) vs gm/ID
3. Current Density (ID/W) vs gm/ID
4. Transconductance Density (gm/W) vs gm/ID

Each chart displays traces for all available channel lengths.
"""

import sys
import os

# Prioritize vendorized mosplot over system installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vendor')))

import argparse
from pathlib import Path

import numpy as np
from mosplot.plot import Mosfet, Expression, load_lookup_table
from mosplot.plot.util import evaluate_expression


def create_gm_density_expression(width: float) -> Expression:
    """Create gm/W expression (transconductance density)."""
    return Expression(
        variables=["gm"],
        function=lambda x: x / width,
        label="$g_m/W\\ (S/m)$"
    )


def generate_ft_chart(mos: Mosfet, mos_type: str, output_dir: str) -> str:
    """Generate Transit Frequency (fT) vs gm/ID chart."""
    filename = f"{mos_type}_ft_vs_gmid.png"
    filepath = os.path.join(output_dir, filename)

    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=mos.transist_frequency_expression,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        y_eng_format=True,
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=filepath
    )
    return filepath


def generate_gain_chart(mos: Mosfet, mos_type: str, output_dir: str) -> str:
    """Generate Intrinsic Gain (gm/gds) vs gm/ID chart."""
    filename = f"{mos_type}_gain_vs_gmid.png"
    filepath = os.path.join(output_dir, filename)

    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=mos.gain_expression,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=filepath
    )
    return filepath


def generate_current_density_chart(mos: Mosfet, mos_type: str, output_dir: str) -> str:
    """Generate Current Density (ID/W) vs gm/ID chart."""
    filename = f"{mos_type}_id_w_vs_gmid.png"
    filepath = os.path.join(output_dir, filename)

    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=mos.current_density_expression,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        y_eng_format=True,
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=filepath
    )
    return filepath


def generate_gm_density_chart(mos: Mosfet, mos_type: str, output_dir: str) -> str:
    """Generate Transconductance Density (gm/W) vs gm/ID chart."""
    filename = f"{mos_type}_gm_w_vs_gmid.png"
    filepath = os.path.join(output_dir, filename)

    gm_density_expression = create_gm_density_expression(mos.width)

    mos.plot_by_expression(
        x_expression=mos.gmid_expression,
        y_expression=gm_density_expression,
        filtered_values=mos.length,
        x_limit=(5, 25),
        y_scale="log",
        y_eng_format=True,
        legend_placement="right",
        fig_size=(10, 6),
        save_fig=filepath
    )
    return filepath


def generate_design_charts(mos: Mosfet, mos_type: str, output_dir: str) -> dict:
    """
    Generate all 4 fundamental design charts for a transistor.

    Args:
        mos: Mosfet object with configured bias conditions
        mos_type: "nmos" or "pmos"
        output_dir: Directory to save the charts

    Returns:
        Dictionary with chart names and file paths
    """
    results = {}

    # Handle both scalar and array values for fixed parameters
    vds_val = float(mos.vds[0]) if hasattr(mos.vds, '__len__') else float(mos.vds)
    vbs_val = float(mos.vbs[0]) if hasattr(mos.vbs, '__len__') else float(mos.vbs)

    print(f"\n=== Generating {mos_type.upper()} Design Charts ===")
    print(f"  VDS = {vds_val:.2f}V, VBS = {vbs_val:.2f}V")
    print(f"  Lengths: {[f'{L*1e6:.2f}um' for L in mos.length]}")
    print(f"  Width: {mos.width*1e6:.1f}um")

    # 1. Transit Frequency
    results['ft'] = generate_ft_chart(mos, mos_type, output_dir)
    print(f"  [1/4] fT vs gm/ID: {os.path.basename(results['ft'])}")

    # 2. Intrinsic Gain
    results['gain'] = generate_gain_chart(mos, mos_type, output_dir)
    print(f"  [2/4] Gain vs gm/ID: {os.path.basename(results['gain'])}")

    # 3. Current Density
    results['id_w'] = generate_current_density_chart(mos, mos_type, output_dir)
    print(f"  [3/4] ID/W vs gm/ID: {os.path.basename(results['id_w'])}")

    # 4. Transconductance Density
    results['gm_w'] = generate_gm_density_chart(mos, mos_type, output_dir)
    print(f"  [4/4] gm/W vs gm/ID: {os.path.basename(results['gm_w'])}")

    return results


def extract_chart_statistics(mos: Mosfet, mos_type: str) -> dict:
    """Extract key statistics from the design charts."""
    stats = {}

    # Get gm/ID range
    gmid_data, _ = evaluate_expression(mos.gmid_expression, mos.extracted_table)
    valid_gmid = gmid_data[np.isfinite(gmid_data) & (gmid_data > 0)]
    stats['gmid_min'] = float(np.min(valid_gmid))
    stats['gmid_max'] = float(np.max(valid_gmid))

    # Get fT range
    ft_data, _ = evaluate_expression(mos.transist_frequency_expression, mos.extracted_table)
    valid_ft = ft_data[np.isfinite(ft_data) & (ft_data > 0)]
    stats['ft_max'] = float(np.max(valid_ft))

    # Get gain range
    gain_data, _ = evaluate_expression(mos.gain_expression, mos.extracted_table)
    valid_gain = gain_data[np.isfinite(gain_data) & (gain_data > 0)]
    stats['gain_max'] = float(np.max(valid_gain))
    stats['gain_max_db'] = 20 * np.log10(stats['gain_max'])

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Generate IHP SG13G2 gm/ID design charts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ihp_design_charts.py
  python ihp_design_charts.py --vds-nmos 0.75 --vds-pmos -0.75
  python ihp_design_charts.py --output-dir ./my_charts
        """
    )
    parser.add_argument(
        "--data-dir", type=str, default="../../data",
        help="Directory containing .npz lookup tables (default: ../../data)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./design_charts",
        help="Output directory for charts (default: ./design_charts)"
    )
    parser.add_argument(
        "--vds-nmos", type=float, default=0.6,
        help="VDS for NMOS charts in Volts (default: 0.6)"
    )
    parser.add_argument(
        "--vds-pmos", type=float, default=-0.6,
        help="VDS for PMOS charts in Volts (default: -0.6)"
    )
    parser.add_argument(
        "--vbs", type=float, default=0.0,
        help="VBS for all charts in Volts (default: 0.0)"
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent
    data_dir = script_dir / args.data_dir if not os.path.isabs(args.data_dir) else Path(args.data_dir)
    output_dir = script_dir / args.output_dir if not os.path.isabs(args.output_dir) else Path(args.output_dir)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    all_stats = {}

    # Process NMOS
    nmos_path = data_dir / "sg13_lv_nmos.npz"
    if nmos_path.exists():
        nmos_lt = load_lookup_table(str(nmos_path))
        nmos = Mosfet(
            lookup_table=nmos_lt,
            mos="sg13_lv_nmos",
            vbs=args.vbs,
            vds=args.vds_nmos,
            vgs=(0.3, 1.2)
        )
        generate_design_charts(nmos, "nmos", str(output_dir))
        all_stats['nmos'] = extract_chart_statistics(nmos, "nmos")
    else:
        print(f"Warning: NMOS lookup table not found at {nmos_path}")

    # Process PMOS
    pmos_path = data_dir / "sg13_lv_pmos.npz"
    if pmos_path.exists():
        pmos_lt = load_lookup_table(str(pmos_path))
        pmos = Mosfet(
            lookup_table=pmos_lt,
            mos="sg13_lv_pmos",
            vbs=args.vbs,
            vds=args.vds_pmos,
            vgs=(-1.2, -0.3)
        )
        generate_design_charts(pmos, "pmos", str(output_dir))
        all_stats['pmos'] = extract_chart_statistics(pmos, "pmos")
    else:
        print(f"Warning: PMOS lookup table not found at {pmos_path}")

    # Print summary statistics
    print("\n=== Summary Statistics ===")
    for mos_type, stats in all_stats.items():
        print(f"\n{mos_type.upper()}:")
        print(f"  gm/ID range: {stats['gmid_min']:.1f} to {stats['gmid_max']:.1f} S/A")
        print(f"  Max fT: {stats['ft_max']/1e9:.1f} GHz")
        print(f"  Max Gain: {stats['gain_max']:.0f} ({stats['gain_max_db']:.1f} dB)")

    print(f"\nCharts saved to: {output_dir}/")


if __name__ == "__main__":
    main()
