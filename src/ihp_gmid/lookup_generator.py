#!/usr/bin/env python3
"""
IHP SG13G2 Lookup Table Generator

Generates MOSFET characterization lookup tables for the IHP SG13G2 130nm PDK
using the mosplot (gmid) NgspiceSimulator backend.

Usage:
    python ihp_lookup_generator.py [--output-dir OUTPUT_DIR] [--n-process N]

Requirements:
    - PDK_ROOT environment variable set to IHP-Open-PDK path
    - ngspice installed and in PATH

Output:
    - ihp_sg13g2_data.npz containing lookup tables for sg13_lv_nmos and sg13_lv_pmos
"""

import sys
import os

# Prioritize vendorized mosplot over system installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vendor')))

import argparse

from mosplot.lookup_table_generator import LookupTableGenerator
from mosplot.lookup_table_generator.simulators import NgspiceSimulator

from .sweep_config import nmos_sweep, pmos_sweep


def get_pdk_root():
    """Get PDK_ROOT from environment or raise error."""
    pdk_root = os.environ.get("PDK_ROOT")
    if not pdk_root:
        raise EnvironmentError(
            "PDK_ROOT environment variable not set. "
            "Please set it to the IHP-Open-PDK directory path."
        )
    return pdk_root


def create_nmos_simulator(pdk_root: str) -> NgspiceSimulator:
    """Create NgspiceSimulator configured for IHP SG13G2 NMOS."""
    corner_lib = os.path.join(
        pdk_root,
        "ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib"
    )

    return NgspiceSimulator(
        simulator_path="ngspice",
        temperature=27,
        lib_mappings=[(corner_lib, "mos_tt")],
        # For subcircuit: ("instance_name", "path.to.internal.mosfet")
        # IHP uses subcircuit sg13_lv_nmos with internal MOSFET Nsg13_lv_nmos
        mos_spice_symbols=("x1", "n.x1.nsg13_lv_nmos"),
        device_parameters={
            "w": 10e-6,
            "ng": 1,
            "m": 1
        },
        parameters_to_save=[
            "id",      # Drain current
            "gm",      # Transconductance
            "gds",     # Output conductance
            "vth",     # Threshold voltage
            "vdsat",   # Saturation voltage
            "cgg",     # Gate capacitance
            "cgs",     # Gate-source capacitance
            "cgd",     # Gate-drain capacitance
        ]
    )


def create_pmos_simulator(pdk_root: str) -> NgspiceSimulator:
    """Create NgspiceSimulator configured for IHP SG13G2 PMOS."""
    corner_lib = os.path.join(
        pdk_root,
        "ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib"
    )

    return NgspiceSimulator(
        simulator_path="ngspice",
        temperature=27,
        lib_mappings=[(corner_lib, "mos_tt")],
        # For subcircuit: ("instance_name", "path.to.internal.mosfet")
        # IHP uses subcircuit sg13_lv_pmos with internal MOSFET Nsg13_lv_pmos
        mos_spice_symbols=("x1", "n.x1.nsg13_lv_pmos"),
        device_parameters={
            "w": 10e-6,
            "ng": 1,
            "m": 1
        },
        parameters_to_save=[
            "id",      # Drain current
            "gm",      # Transconductance
            "gds",     # Output conductance
            "vth",     # Threshold voltage
            "vdsat",   # Saturation voltage
            "cgg",     # Gate capacitance
            "cgs",     # Gate-source capacitance
            "cgd",     # Gate-drain capacitance
        ]
    )


def generate_lookup_tables(output_dir: str = "../../data", n_process: int = 4):
    """
    Generate lookup tables for IHP SG13G2 NMOS and PMOS.

    Args:
        output_dir: Directory to save the .npz lookup table files
        n_process: Number of parallel processes for simulation
    """
    pdk_root = get_pdk_root()
    print(f"Using PDK_ROOT: {pdk_root}")

    # Verify PDK path exists
    corner_lib = os.path.join(
        pdk_root,
        "ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib"
    )
    if not os.path.exists(corner_lib):
        raise FileNotFoundError(
            f"Corner library not found: {corner_lib}\n"
            "Please verify PDK_ROOT is set correctly."
        )

    print("=" * 60)
    print("IHP SG13G2 Lookup Table Generator")
    print("=" * 60)

    # Generate NMOS lookup table
    print("\n[1/2] Generating NMOS lookup table...")
    nmos_simulator = create_nmos_simulator(pdk_root)

    nmos_generator = LookupTableGenerator(
        description="IHP SG13G2 LV NMOS",
        simulator=nmos_simulator,
        model_sweeps={"sg13_lv_nmos": nmos_sweep},
        n_process=n_process,
    )

    nmos_output = os.path.join(output_dir, "sg13_lv_nmos")
    print(f"    Output: {nmos_output}.npz")
    nmos_generator.build(nmos_output)
    print("    NMOS lookup table generated successfully!")

    # Generate PMOS lookup table
    print("\n[2/2] Generating PMOS lookup table...")
    pmos_simulator = create_pmos_simulator(pdk_root)

    pmos_generator = LookupTableGenerator(
        description="IHP SG13G2 LV PMOS",
        simulator=pmos_simulator,
        model_sweeps={"sg13_lv_pmos": pmos_sweep},
        n_process=n_process,
    )

    pmos_output = os.path.join(output_dir, "sg13_lv_pmos")
    print(f"    Output: {pmos_output}.npz")
    pmos_generator.build(pmos_output)
    print("    PMOS lookup table generated successfully!")

    print("\n" + "=" * 60)
    print("Generation complete!")
    print(f"Output files:")
    print(f"  - {nmos_output}.npz")
    print(f"  - {pmos_output}.npz")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Generate IHP SG13G2 MOSFET lookup tables for gm/ID methodology"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="../../data",
        help="Output directory for lookup table files (default: ../../data)"
    )
    parser.add_argument(
        "--n-process",
        type=int,
        default=4,
        help="Number of parallel processes (default: 4)"
    )

    args = parser.parse_args()

    try:
        generate_lookup_tables(
            output_dir=args.output_dir,
            n_process=args.n_process
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
