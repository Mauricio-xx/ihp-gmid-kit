#!/usr/bin/env python3
"""
IHP SG13G2 Common Source Amplifier Design Script

Implements the gm/ID design methodology for a CS amplifier with the following specs:
- VDD = 1.2V
- Av > 20 dB (10 V/V)
- BW > 100 MHz (with CL = 100 fF)
- CL = 100 fF

Uses color-blind friendly palettes for accessibility.
"""

import sys
import os

# Prioritize vendorized mosplot over system installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vendor')))

import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from mosplot.plot import Mosfet, Expression, load_lookup_table
from mosplot.plot.util import evaluate_expression


# =============================================================================
# Color-Blind Friendly Configuration
# =============================================================================

# Tol Bright palette - optimized for color blindness
TOL_BRIGHT = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB']

# Markers and linestyles for additional distinction
MARKERS = ['o', 's', '^', 'D', 'v', 'p', '*']
LINESTYLES = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 1)), (0, (1, 1))]


def setup_colorblind_style():
    """Configure matplotlib for color-blind accessibility."""
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=TOL_BRIGHT)
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['lines.markersize'] = 6
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.dpi'] = 150
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3


# =============================================================================
# Design Specifications
# =============================================================================

class DesignSpecs:
    """Design specifications for the CS amplifier."""
    VDD = 1.2           # Supply voltage (V)
    AV_MIN = 10.0       # Minimum voltage gain (V/V)
    AV_MIN_DB = 20.0    # Minimum gain in dB
    BW_MIN = 100e6      # Minimum bandwidth (Hz)
    CL = 100e-15        # Load capacitance (F)
    VDS_OP = 0.6        # Operating VDS (V) - allows headroom
    VBS = 0.0           # Body-source voltage (V)
    VGS_RANGE = (0.3, 1.2)  # VGS sweep range (V)


# =============================================================================
# Lookup Table Access Functions
# =============================================================================

def load_nmos_data(data_dir: str) -> tuple:
    """
    Load NMOS lookup table and create Mosfet object.

    Returns:
        tuple: (Mosfet object, raw lookup table dict)
    """
    nmos_path = os.path.join(data_dir, "sg13_lv_nmos.npz")
    if not os.path.exists(nmos_path):
        raise FileNotFoundError(f"NMOS lookup table not found: {nmos_path}")

    lt = load_lookup_table(nmos_path)
    nmos = Mosfet(
        lookup_table=lt,
        mos="sg13_lv_nmos",
        vbs=DesignSpecs.VBS,
        vds=DesignSpecs.VDS_OP,
        vgs=DesignSpecs.VGS_RANGE
    )
    return nmos, lt


def get_raw_data(lt: dict) -> dict:
    """Extract raw data arrays from lookup table."""
    return lt['sg13_lv_nmos']


# =============================================================================
# Design Space Analysis
# =============================================================================

def analyze_gain_vs_length(nmos: Mosfet) -> dict:
    """
    Analyze intrinsic gain (gm/gds) for each channel length.

    Returns:
        dict: Analysis results with gain statistics per length
    """
    gmid_data, _ = evaluate_expression(nmos.gmid_expression, nmos.extracted_table)
    gain_data, _ = evaluate_expression(nmos.gain_expression, nmos.extracted_table)

    results = {'lengths': [], 'max_gains': [], 'gain_at_gmid_10': []}

    for l_idx, L in enumerate(nmos.length):
        gmid_row = gmid_data[l_idx, :]
        gain_row = gain_data[l_idx, :]

        # Filter valid data
        valid = np.isfinite(gmid_row) & np.isfinite(gain_row) & (gain_row > 0)

        results['lengths'].append(L)
        results['max_gains'].append(np.max(gain_row[valid]) if np.any(valid) else 0)

        # Find gain at gm/ID = 10
        if np.any(valid):
            idx_10 = np.argmin(np.abs(gmid_row[valid] - 10))
            results['gain_at_gmid_10'].append(gain_row[valid][idx_10])
        else:
            results['gain_at_gmid_10'].append(0)

    return results


def select_optimal_length(nmos: Mosfet, target_gain: float) -> tuple:
    """
    Select optimal channel length based on gain requirement.

    Args:
        nmos: Mosfet object
        target_gain: Minimum required intrinsic gain (V/V)

    Returns:
        tuple: (selected length in m, length index, justification string)
    """
    analysis = analyze_gain_vs_length(nmos)

    # Find lengths that meet gain requirement at gm/ID = 10
    suitable_lengths = []
    for i, (L, gain) in enumerate(zip(analysis['lengths'], analysis['gain_at_gmid_10'])):
        if gain >= target_gain:
            suitable_lengths.append((L, i, gain))

    if not suitable_lengths:
        # Fall back to length with highest gain
        best_idx = np.argmax(analysis['max_gains'])
        L = analysis['lengths'][best_idx]
        justification = f"No length meets gain={target_gain:.0f} at gm/ID=10. Using L={L*1e6:.2f}um (max gain)."
        return L, best_idx, justification

    # Select smallest length that meets requirement (best fT)
    suitable_lengths.sort(key=lambda x: x[0])
    L, idx, gain = suitable_lengths[0]
    justification = f"L={L*1e6:.2f}um provides gain={gain:.1f} at gm/ID=10, meeting Av>{target_gain:.0f} requirement."

    return L, idx, justification


def find_operating_point(nmos: Mosfet, L_idx: int, target_gmid: float = 10.0) -> dict:
    """
    Find operating point parameters for selected length and gm/ID.

    Args:
        nmos: Mosfet object
        L_idx: Index of selected length
        target_gmid: Target gm/ID value (S/A)

    Returns:
        dict: Operating point parameters
    """
    gmid_data, _ = evaluate_expression(nmos.gmid_expression, nmos.extracted_table)
    gain_data, _ = evaluate_expression(nmos.gain_expression, nmos.extracted_table)
    id_w_data, _ = evaluate_expression(nmos.current_density_expression, nmos.extracted_table)
    ft_data, _ = evaluate_expression(nmos.transist_frequency_expression, nmos.extracted_table)

    gmid_row = gmid_data[L_idx, :]
    gain_row = gain_data[L_idx, :]
    id_w_row = id_w_data[L_idx, :]
    ft_row = ft_data[L_idx, :]
    vgs_arr = nmos.vgs

    # Find index closest to target gm/ID
    valid = np.isfinite(gmid_row) & (gmid_row > 0)
    valid_indices = np.where(valid)[0]
    gmid_valid = gmid_row[valid]

    closest_idx = np.argmin(np.abs(gmid_valid - target_gmid))
    actual_idx = valid_indices[closest_idx]

    return {
        'L': nmos.length[L_idx],
        'L_idx': L_idx,
        'VGS': vgs_arr[actual_idx],
        'gmid': gmid_row[actual_idx],
        'gain': gain_row[actual_idx],
        'id_w': id_w_row[actual_idx],
        'ft': ft_row[actual_idx],
        'vgs_idx': actual_idx
    }


# =============================================================================
# Design Calculations
# =============================================================================

def calculate_dimensions(specs: DesignSpecs, op: dict) -> dict:
    """
    Calculate transistor dimensions based on operating point.

    Args:
        specs: Design specifications
        op: Operating point parameters

    Returns:
        dict: Calculated dimensions
    """
    # gm required for bandwidth: BW = gm / (2*pi*CL)
    gm_required = 2 * np.pi * specs.BW_MIN * specs.CL

    # ID from gm/ID
    id_required = gm_required / op['gmid']

    # W from ID/W
    w_required = id_required / op['id_w']

    # Verify gain
    expected_gain = op['gain']
    expected_gain_db = 20 * np.log10(expected_gain) if expected_gain > 0 else 0

    # Verify fT margin (should be >> BW)
    ft_margin = op['ft'] / specs.BW_MIN if specs.BW_MIN > 0 else 0

    return {
        'gm_required': gm_required,
        'id_required': id_required,
        'w_required': w_required,
        'expected_gain': expected_gain,
        'expected_gain_db': expected_gain_db,
        'ft_margin': ft_margin,
        'L': op['L'],
        'VGS': op['VGS']
    }


# =============================================================================
# Plotting Functions
# =============================================================================

def plot_gain_vs_gmid_design(nmos: Mosfet, op: dict, output_dir: str) -> str:
    """Plot intrinsic gain vs gm/ID with operating point marked."""
    gmid_data, _ = evaluate_expression(nmos.gmid_expression, nmos.extracted_table)
    gain_data, _ = evaluate_expression(nmos.gain_expression, nmos.extracted_table)

    fig, ax = plt.subplots()

    for l_idx, L in enumerate(nmos.length):
        gmid_row = gmid_data[l_idx, :]
        gain_row = gain_data[l_idx, :]
        valid = np.isfinite(gmid_row) & np.isfinite(gain_row) & (gain_row > 0)

        ax.semilogy(
            gmid_row[valid], gain_row[valid],
            color=TOL_BRIGHT[l_idx % len(TOL_BRIGHT)],
            linestyle=LINESTYLES[l_idx % len(LINESTYLES)],
            marker=MARKERS[l_idx % len(MARKERS)],
            markevery=10,
            label=f'L={L*1e6:.2f}$\\mu$m'
        )

    # Mark operating point
    ax.plot(op['gmid'], op['gain'], 'k*', markersize=15, markeredgewidth=2,
            label=f'Design Point', zorder=10)

    # Mark target gain line
    ax.axhline(y=DesignSpecs.AV_MIN, color='gray', linestyle='--', alpha=0.7,
               label=f'Target Av={DesignSpecs.AV_MIN:.0f}')

    ax.set_xlabel('$g_m/I_D$ (S/A)')
    ax.set_ylabel('$g_m/g_{ds}$ (V/V)')
    ax.set_title('Intrinsic Gain vs $g_m/I_D$ - Design Space')
    ax.set_xlim(5, 25)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    filepath = os.path.join(output_dir, 'gain_vs_gmid_design.png')
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def plot_ft_vs_gmid_design(nmos: Mosfet, op: dict, output_dir: str) -> str:
    """Plot transit frequency vs gm/ID with operating point marked."""
    gmid_data, _ = evaluate_expression(nmos.gmid_expression, nmos.extracted_table)
    ft_data, _ = evaluate_expression(nmos.transist_frequency_expression, nmos.extracted_table)

    fig, ax = plt.subplots()

    for l_idx, L in enumerate(nmos.length):
        gmid_row = gmid_data[l_idx, :]
        ft_row = ft_data[l_idx, :]
        valid = np.isfinite(gmid_row) & np.isfinite(ft_row) & (ft_row > 0)

        ax.semilogy(
            gmid_row[valid], ft_row[valid] / 1e9,
            color=TOL_BRIGHT[l_idx % len(TOL_BRIGHT)],
            linestyle=LINESTYLES[l_idx % len(LINESTYLES)],
            marker=MARKERS[l_idx % len(MARKERS)],
            markevery=10,
            label=f'L={L*1e6:.2f}$\\mu$m'
        )

    # Mark operating point
    ax.plot(op['gmid'], op['ft'] / 1e9, 'k*', markersize=15, markeredgewidth=2,
            label=f'Design Point', zorder=10)

    # Mark BW requirement
    ax.axhline(y=DesignSpecs.BW_MIN / 1e9, color='gray', linestyle='--', alpha=0.7,
               label=f'BW={DesignSpecs.BW_MIN/1e6:.0f}MHz')

    ax.set_xlabel('$g_m/I_D$ (S/A)')
    ax.set_ylabel('$f_T$ (GHz)')
    ax.set_title('Transit Frequency vs $g_m/I_D$ - Design Space')
    ax.set_xlim(5, 25)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    filepath = os.path.join(output_dir, 'ft_vs_gmid_design.png')
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def plot_id_w_vs_gmid_design(nmos: Mosfet, op: dict, output_dir: str) -> str:
    """Plot current density vs gm/ID with operating point marked."""
    gmid_data, _ = evaluate_expression(nmos.gmid_expression, nmos.extracted_table)
    id_w_data, _ = evaluate_expression(nmos.current_density_expression, nmos.extracted_table)

    fig, ax = plt.subplots()

    for l_idx, L in enumerate(nmos.length):
        gmid_row = gmid_data[l_idx, :]
        id_w_row = id_w_data[l_idx, :]
        valid = np.isfinite(gmid_row) & np.isfinite(id_w_row) & (id_w_row > 0)

        ax.semilogy(
            gmid_row[valid], id_w_row[valid],
            color=TOL_BRIGHT[l_idx % len(TOL_BRIGHT)],
            linestyle=LINESTYLES[l_idx % len(LINESTYLES)],
            marker=MARKERS[l_idx % len(MARKERS)],
            markevery=10,
            label=f'L={L*1e6:.2f}$\\mu$m'
        )

    # Mark operating point
    ax.plot(op['gmid'], op['id_w'], 'k*', markersize=15, markeredgewidth=2,
            label=f'Design Point', zorder=10)

    ax.set_xlabel('$g_m/I_D$ (S/A)')
    ax.set_ylabel('$I_D/W$ (A/m)')
    ax.set_title('Current Density vs $g_m/I_D$ - Design Space')
    ax.set_xlim(5, 25)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    filepath = os.path.join(output_dir, 'id_w_vs_gmid_design.png')
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def plot_id_vs_vgs(raw_data: dict, design: dict, output_dir: str) -> str:
    """Plot ID vs VGS for the designed transistor."""
    vgs = raw_data['vgs']
    vds_idx = np.argmin(np.abs(raw_data['vds'] - DesignSpecs.VDS_OP))
    vbs_idx = 0  # VBS = 0

    fig, ax = plt.subplots()

    for l_idx, L in enumerate(raw_data['length']):
        id_data = raw_data['id'][l_idx, vbs_idx, :, vds_idx]
        # Scale by W ratio for the designed W
        W_table = 10e-6  # Width used in lookup table
        W_design = design['w_required']
        id_scaled = id_data * (W_design / W_table)

        ax.semilogy(
            vgs, np.abs(id_scaled) * 1e6,
            color=TOL_BRIGHT[l_idx % len(TOL_BRIGHT)],
            linestyle=LINESTYLES[l_idx % len(LINESTYLES)],
            marker=MARKERS[l_idx % len(MARKERS)],
            markevery=15,
            label=f'L={L*1e6:.2f}$\\mu$m'
        )

    # Mark design point
    ax.axvline(x=design['VGS'], color='gray', linestyle='--', alpha=0.7,
               label=f'$V_{{GS}}$={design["VGS"]:.3f}V')
    ax.axhline(y=design['id_required'] * 1e6, color='gray', linestyle=':', alpha=0.7,
               label=f'$I_D$={design["id_required"]*1e6:.2f}$\\mu$A')

    ax.set_xlabel('$V_{GS}$ (V)')
    ax.set_ylabel(f'$I_D$ ($\\mu$A) @ W={design["w_required"]*1e6:.2f}$\\mu$m')
    ax.set_title(f'$I_D$ vs $V_{{GS}}$ @ $V_{{DS}}$={DesignSpecs.VDS_OP}V')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    filepath = os.path.join(output_dir, 'cs_amp_id_vgs.png')
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


def plot_id_vs_vds(raw_data: dict, design: dict, output_dir: str) -> str:
    """Plot ID vs VDS family curves."""
    vds = raw_data['vds']
    vgs = raw_data['vgs']
    vbs_idx = 0

    # Find design length index
    L_idx = np.argmin(np.abs(np.array(raw_data['length']) - design['L']))

    # VGS values to plot (around operating point)
    vgs_design = design['VGS']
    vgs_values = [vgs_design - 0.1, vgs_design, vgs_design + 0.1, vgs_design + 0.2]

    fig, ax = plt.subplots()

    W_table = 10e-6
    W_design = design['w_required']

    for i, vgs_target in enumerate(vgs_values):
        vgs_idx = np.argmin(np.abs(vgs - vgs_target))
        actual_vgs = vgs[vgs_idx]

        id_data = raw_data['id'][L_idx, vbs_idx, vgs_idx, :]
        id_scaled = id_data * (W_design / W_table)

        ax.plot(
            vds, np.abs(id_scaled) * 1e6,
            color=TOL_BRIGHT[i % len(TOL_BRIGHT)],
            linestyle=LINESTYLES[i % len(LINESTYLES)],
            marker=MARKERS[i % len(MARKERS)],
            markevery=5,
            label=f'$V_{{GS}}$={actual_vgs:.2f}V'
        )

    # Mark operating point
    ax.axvline(x=DesignSpecs.VDS_OP, color='gray', linestyle='--', alpha=0.7,
               label=f'$V_{{DS,op}}$={DesignSpecs.VDS_OP}V')

    ax.set_xlabel('$V_{DS}$ (V)')
    ax.set_ylabel(f'$I_D$ ($\\mu$A)')
    ax.set_title(f'$I_D$ vs $V_{{DS}}$ @ L={design["L"]*1e6:.2f}$\\mu$m, W={W_design*1e6:.2f}$\\mu$m')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(True, alpha=0.3)

    filepath = os.path.join(output_dir, 'cs_amp_id_vds.png')
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


# =============================================================================
# Netlist Generation
# =============================================================================

def generate_ngspice_netlist(design: dict, output_path: str, pdk_root: str = None) -> str:
    """Generate ngspice netlist for operating point verification."""
    # Resolve PDK path
    if pdk_root is None:
        pdk_root = os.environ.get('PDK_ROOT', '/path/to/IHP-Open-PDK')

    lib_path = os.path.join(pdk_root, 'ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib')

    netlist = f"""* IHP SG13G2 CS Amplifier - Operating Point Verification
* Generated by gm/ID design methodology
* Design Parameters:
*   L = {design['L']*1e6:.3f} um
*   W = {design['w_required']*1e6:.3f} um
*   VGS = {design['VGS']:.4f} V
*   Expected ID = {design['id_required']*1e6:.3f} uA
*   Expected gm = {design['gm_required']*1e6:.3f} uS

.param W_DESIGN = {design['w_required']:.6e}
.param L_DESIGN = {design['L']:.6e}
.param VGS_OP = {design['VGS']:.4f}
.param VDS_OP = {DesignSpecs.VDS_OP:.2f}

* Include IHP SG13G2 PDK models
* PDK_ROOT: {pdk_root}
.lib '{lib_path}' mos_tt

* Voltage sources
VGS gate 0 DC={{VGS_OP}}
VDS drain 0 DC={{VDS_OP}}

* NMOS under test
* Terminal order: drain gate source bulk
X1 drain gate 0 0 sg13_lv_nmos L={{L_DESIGN}} W={{W_DESIGN}} ng=1 m=1

* Operating point analysis
.op

.control
op
echo "======================================"
echo "Operating Point Results"
echo "======================================"
echo ""
print @n.x1.nsg13_lv_nmos[id]
print @n.x1.nsg13_lv_nmos[gm]
print @n.x1.nsg13_lv_nmos[gds]
print @n.x1.nsg13_lv_nmos[vth]
print @n.x1.nsg13_lv_nmos[vdsat]
echo ""
echo "Expected from gm/ID tables:"
echo "  ID = {design['id_required']*1e6:.4f} uA"
echo "  gm = {design['gm_required']*1e6:.4f} uS"
echo "  gm/ID = {design['gm_required']/design['id_required']:.2f} S/A"
echo "  Av (gm/gds) = {design['expected_gain']:.2f} V/V ({design['expected_gain_db']:.1f} dB)"
echo "======================================"
.endc

.end
"""

    with open(output_path, 'w') as f:
        f.write(netlist)

    return output_path


# =============================================================================
# Main Design Flow
# =============================================================================

def run_design(data_dir: str, output_dir: str, target_gmid: float = 10.0) -> dict:
    """
    Execute the complete gm/ID design flow.

    Args:
        data_dir: Directory containing lookup tables
        output_dir: Directory for output files
        target_gmid: Target gm/ID operating point

    Returns:
        dict: Complete design results
    """
    setup_colorblind_style()
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("IHP SG13G2 CS Amplifier Design using gm/ID Methodology")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/6] Loading NMOS lookup table...")
    nmos, lt = load_nmos_data(data_dir)
    raw_data = get_raw_data(lt)
    print(f"  Lengths available: {[f'{L*1e6:.2f}um' for L in nmos.length]}")
    print(f"  VDS operating point: {DesignSpecs.VDS_OP}V")

    # Step 2: Select optimal length
    print(f"\n[2/6] Selecting optimal channel length (target gain > {DesignSpecs.AV_MIN} V/V)...")
    L_opt, L_idx, justification = select_optimal_length(nmos, DesignSpecs.AV_MIN)
    print(f"  {justification}")

    # Step 3: Find operating point
    print(f"\n[3/6] Finding operating point at gm/ID = {target_gmid} S/A...")
    op = find_operating_point(nmos, L_idx, target_gmid)
    print(f"  L = {op['L']*1e6:.2f} um")
    print(f"  VGS = {op['VGS']:.3f} V")
    print(f"  gm/ID = {op['gmid']:.2f} S/A")
    print(f"  gm/gds (gain) = {op['gain']:.1f} V/V ({20*np.log10(op['gain']):.1f} dB)")
    print(f"  fT = {op['ft']/1e9:.1f} GHz")
    print(f"  ID/W = {op['id_w']:.2f} A/m")

    # Step 4: Calculate dimensions
    print("\n[4/6] Calculating transistor dimensions...")
    specs = DesignSpecs()
    design = calculate_dimensions(specs, op)
    print(f"  Required gm = {design['gm_required']*1e6:.2f} uS (for BW = {specs.BW_MIN/1e6:.0f} MHz)")
    print(f"  Required ID = {design['id_required']*1e6:.2f} uA")
    print(f"  Required W = {design['w_required']*1e6:.2f} um")
    print(f"  fT margin = {design['ft_margin']:.1f}x (fT/BW)")

    # Step 5: Generate plots
    print("\n[5/6] Generating design space plots (color-blind friendly)...")
    plots = {}
    plots['gain_gmid'] = plot_gain_vs_gmid_design(nmos, op, output_dir)
    print(f"  {os.path.basename(plots['gain_gmid'])}")

    plots['ft_gmid'] = plot_ft_vs_gmid_design(nmos, op, output_dir)
    print(f"  {os.path.basename(plots['ft_gmid'])}")

    plots['id_w_gmid'] = plot_id_w_vs_gmid_design(nmos, op, output_dir)
    print(f"  {os.path.basename(plots['id_w_gmid'])}")

    plots['id_vgs'] = plot_id_vs_vgs(raw_data, design, output_dir)
    print(f"  {os.path.basename(plots['id_vgs'])}")

    plots['id_vds'] = plot_id_vs_vds(raw_data, design, output_dir)
    print(f"  {os.path.basename(plots['id_vds'])}")

    # Step 6: Generate netlist
    print("\n[6/6] Generating ngspice netlist...")
    netlist_path = os.path.join(os.path.dirname(output_dir), "cs_amp_op.cir")
    generate_ngspice_netlist(design, netlist_path)
    print(f"  {os.path.basename(netlist_path)}")

    # Summary
    print("\n" + "=" * 60)
    print("DESIGN SUMMARY")
    print("=" * 60)
    print(f"\n  Transistor: sg13_lv_nmos")
    print(f"  L = {design['L']*1e6:.3f} um")
    print(f"  W = {design['w_required']*1e6:.3f} um")
    print(f"  VGS = {design['VGS']:.4f} V")
    print(f"  VDS = {DesignSpecs.VDS_OP:.2f} V")
    print(f"  ID = {design['id_required']*1e6:.3f} uA")
    print(f"  gm = {design['gm_required']*1e6:.3f} uS")
    print(f"  gm/ID = {op['gmid']:.2f} S/A")
    print(f"  Expected Av = {design['expected_gain']:.1f} V/V ({design['expected_gain_db']:.1f} dB)")
    print(f"\n  Palette used: Tol Bright (color-blind friendly)")
    print(f"  Output directory: {output_dir}")
    print("=" * 60)

    return {
        'operating_point': op,
        'design': design,
        'plots': plots,
        'netlist': netlist_path
    }


def main():
    parser = argparse.ArgumentParser(
        description="IHP SG13G2 CS Amplifier Design using gm/ID methodology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python design_script.py
  python design_script.py --gmid 12
  python design_script.py --data-dir ../../data --output-dir ./plots
        """
    )
    parser.add_argument(
        "--data-dir", type=str, default="../../data",
        help="Directory containing .npz lookup tables (default: ../../data)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./plots",
        help="Output directory for plots (default: ./plots)"
    )
    parser.add_argument(
        "--gmid", type=float, default=10.0,
        help="Target gm/ID operating point in S/A (default: 10.0)"
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent
    data_dir = script_dir / args.data_dir if not os.path.isabs(args.data_dir) else Path(args.data_dir)
    output_dir = script_dir / args.output_dir if not os.path.isabs(args.output_dir) else Path(args.output_dir)

    try:
        results = run_design(str(data_dir), str(output_dir), args.gmid)
        print("\nDesign completed successfully!")
        print(f"\nTo verify with ngspice, run:")
        print(f"  ngspice {results['netlist']}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during design: {e}")
        raise


if __name__ == "__main__":
    main()
