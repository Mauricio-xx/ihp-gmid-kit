#!/usr/bin/env python3
"""
IHP SG13G2 Lookup Table Visual Validation

Generates diagnostic plots to verify the generated lookup tables.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import argparse


def load_lookup_table(filepath):
    """Load lookup table from .npz file."""
    data = np.load(filepath, allow_pickle=True)
    return data['lookup_table'].item()


def plot_id_vs_vgs(model_data, model_name, output_path, vds_idx=15, vbs_idx=0):
    """Plot ID vs VGS for all lengths at fixed VDS and VBS."""
    fig, ax = plt.subplots(figsize=(10, 6))

    lengths = np.array(model_data['length']) * 1e6  # Convert to um
    vgs = model_data['vgs']
    vds_val = model_data['vds'][vds_idx]
    vbs_val = model_data['vbs'][vbs_idx]

    for l_idx, L in enumerate(lengths):
        id_data = model_data['id'][l_idx, vbs_idx, :, vds_idx]
        ax.semilogy(vgs, np.abs(id_data), label=f'L={L:.2f}um')

    ax.set_xlabel('VGS (V)')
    ax.set_ylabel('|ID| (A)')
    ax.set_title(f'{model_name}: ID vs VGS @ VDS={vds_val:.2f}V, VBS={vbs_val:.1f}V')
    ax.legend(loc='lower right')
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.set_xlim([vgs.min(), vgs.max()])

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_id_vs_vds(model_data, model_name, output_path, vbs_idx=0):
    """Plot ID vs VDS family for different VGS values at fixed length."""
    fig, ax = plt.subplots(figsize=(10, 6))

    lengths = np.array(model_data['length']) * 1e6
    vgs = model_data['vgs']
    vds = model_data['vds']
    vbs_val = model_data['vbs'][vbs_idx]

    # Use minimum length (L=130nm)
    l_idx = 0
    L = lengths[l_idx]

    # Select VGS values to plot
    vgs_indices = [30, 50, 70, 90, 110, 130]  # 0.3V, 0.5V, 0.7V, 0.9V, 1.1V, 1.3V

    for vgs_idx in vgs_indices:
        if vgs_idx < len(vgs):
            vgs_val = vgs[vgs_idx]
            id_data = model_data['id'][l_idx, vbs_idx, vgs_idx, :]
            ax.plot(np.abs(vds), np.abs(id_data) * 1e3, label=f'VGS={vgs_val:.1f}V')

    ax.set_xlabel('|VDS| (V)')
    ax.set_ylabel('|ID| (mA)')
    ax.set_title(f'{model_name}: ID vs VDS @ L={L:.2f}um, VBS={vbs_val:.1f}V')
    ax.legend(loc='lower right')
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_gmid_vs_id(model_data, model_name, output_path, vds_idx=15, vbs_idx=0):
    """Plot gm/ID vs ID for all lengths."""
    fig, ax = plt.subplots(figsize=(10, 6))

    lengths = np.array(model_data['length']) * 1e6
    vds_val = model_data['vds'][vds_idx]
    vbs_val = model_data['vbs'][vbs_idx]

    for l_idx, L in enumerate(lengths):
        id_data = model_data['id'][l_idx, vbs_idx, :, vds_idx]
        gm_data = model_data['gm'][l_idx, vbs_idx, :, vds_idx]

        # Filter out zeros and compute gm/ID
        valid = id_data > 1e-12
        gmid = np.zeros_like(id_data)
        gmid[valid] = gm_data[valid] / id_data[valid]

        ax.semilogx(np.abs(id_data[valid]), gmid[valid], label=f'L={L:.2f}um')

    ax.set_xlabel('|ID| (A)')
    ax.set_ylabel('gm/ID (V⁻¹)')
    ax.set_title(f'{model_name}: gm/ID vs ID @ VDS={vds_val:.2f}V, VBS={vbs_val:.1f}V')
    ax.legend(loc='upper right')
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.set_ylim([0, 35])

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate validation plots for IHP SG13G2 lookup tables")
    parser.add_argument("--data-dir", type=str, default="./ihp_sg13g2_data",
                        help="Directory containing .npz files")
    parser.add_argument("--output-dir", type=str, default="./plots",
                        help="Output directory for plots")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # NMOS plots
    nmos_path = os.path.join(args.data_dir, "sg13_lv_nmos.npz")
    if os.path.exists(nmos_path):
        print("\n=== Generating NMOS plots ===")
        lt = load_lookup_table(nmos_path)
        model = lt['sg13_lv_nmos']

        plot_id_vs_vgs(model, "sg13_lv_nmos",
                       os.path.join(args.output_dir, "nmos_id_vgs.png"))
        plot_id_vs_vds(model, "sg13_lv_nmos",
                       os.path.join(args.output_dir, "nmos_id_vds.png"))
        plot_gmid_vs_id(model, "sg13_lv_nmos",
                        os.path.join(args.output_dir, "nmos_gmid_id.png"))

    # PMOS plots
    pmos_path = os.path.join(args.data_dir, "sg13_lv_pmos.npz")
    if os.path.exists(pmos_path):
        print("\n=== Generating PMOS plots ===")
        lt = load_lookup_table(pmos_path)
        model = lt['sg13_lv_pmos']

        plot_id_vs_vgs(model, "sg13_lv_pmos",
                       os.path.join(args.output_dir, "pmos_id_vgs.png"))
        plot_id_vs_vds(model, "sg13_lv_pmos",
                       os.path.join(args.output_dir, "pmos_id_vds.png"))
        plot_gmid_vs_id(model, "sg13_lv_pmos",
                        os.path.join(args.output_dir, "pmos_gmid_id.png"))

    print(f"\nPlots saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()
