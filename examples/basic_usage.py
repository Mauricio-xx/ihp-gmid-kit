#!/usr/bin/env python3
"""
Basic usage example for IHP gm/ID Design Kit

Demonstrates how to load lookup tables and plot gm/ID design charts.
"""

import sys
import os

# Add vendor to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vendor')))

from mosplot.plot import load_lookup_table, Mosfet

def main():
    # Path to data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

    # Load NMOS lookup table
    nmos_path = os.path.join(data_dir, "sg13_lv_nmos.npz")
    print(f"Loading: {nmos_path}")

    lookup_table = load_lookup_table(nmos_path)

    # Create Mosfet instance with operating conditions
    nmos = Mosfet(
        lookup_table=lookup_table,
        mos="sg13_lv_nmos",
        vbs=0.0,      # Body-source voltage
        vds=0.6,      # Drain-source voltage
        vgs=(0.3, 1.2)  # Gate-source voltage range
    )

    print(f"Available lengths: {nmos.length * 1e6} um")

    # Plot Transit Frequency vs gm/ID
    print("\nPlotting fT vs gm/ID...")
    nmos.plot_by_expression(
        x_expression=nmos.gmid_expression,
        y_expression=nmos.transist_frequency_expression,
        filtered_values=nmos.length,
        x_limit=(5, 25),
        y_scale="log",
        y_eng_format=True,
        legend_placement="right",
        fig_size=(10, 6)
    )

    # Plot Intrinsic Gain vs gm/ID
    print("Plotting Gain vs gm/ID...")
    nmos.plot_by_expression(
        x_expression=nmos.gmid_expression,
        y_expression=nmos.gain_expression,
        filtered_values=nmos.length,
        x_limit=(5, 25),
        y_scale="log",
        legend_placement="right",
        fig_size=(10, 6)
    )

    print("\nDone! Close the plots to exit.")


if __name__ == "__main__":
    main()
