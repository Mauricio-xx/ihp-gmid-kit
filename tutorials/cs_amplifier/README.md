# Tutorial: Common Source Amplifier Design with gm/ID Methodology

## IHP SG13G2 130nm PDK

This tutorial demonstrates the **gm/ID design methodology** for analog circuit design using pre-characterized lookup tables from the IHP SG13G2 130nm BiCMOS process.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Design Specifications](#design-specifications)
3. [The gm/ID Methodology](#the-gmid-methodology)
4. [Design Process](#design-process)
5. [Running the Design Script](#running-the-design-script)
6. [Verification with Ngspice](#verification-with-ngspice)
7. [Results Interpretation](#results-interpretation)

---

## Introduction

The **gm/ID methodology** is a powerful approach for analog circuit design that:

- Provides a unified framework across all inversion regions (weak, moderate, strong)
- Enables systematic trade-offs between gain, speed, and power consumption
- Uses technology-specific lookup tables for accurate sizing

This tutorial designs a **Common Source (CS) amplifier** using NMOS transistors from the IHP SG13G2 process.

---

## Design Specifications

| Parameter | Symbol | Value | Notes |
|-----------|--------|-------|-------|
| Supply Voltage | V_DD | 1.2 V | |
| Voltage Gain | A_v | > 20 dB (10 V/V) | Intrinsic gain |
| Bandwidth | BW | > 100 MHz | Unity-gain bandwidth |
| Load Capacitance | C_L | 100 fF | Output load |
| Body Bias | V_BS | 0 V | No body effect |
| Transistor | - | sg13_lv_nmos | IHP LV NMOS |

---

## The gm/ID Methodology

### Key Concept

The gm/ID ratio (transconductance efficiency) is a **technology-independent** parameter that characterizes the transistor's operating region:

| gm/ID (S/A) | Inversion Region | Characteristics |
|-------------|------------------|-----------------|
| 5-10 | Strong | High speed, high power |
| 10-15 | Moderate | Balanced trade-off |
| 15-25 | Weak | Low power, lower speed |

### Design Charts

The methodology uses four fundamental charts:

1. **fT vs gm/ID**: Transit frequency shows speed capability
2. **gm/gds vs gm/ID**: Intrinsic gain determines amplification
3. **ID/W vs gm/ID**: Current density for sizing
4. **gm/W vs gm/ID**: Transconductance density

---

## Design Process

### Step 1: Calculate Required Transconductance

For a given bandwidth and load capacitance:

```
BW = gm / (2*pi*C_L)

gm_required = 2*pi * BW * C_L
            = 2*pi * 100MHz * 100fF
            = 62.8 uS
```

### Step 2: Select Channel Length (L)

**Goal**: Meet gain requirement (A_v > 10 V/V)

The intrinsic gain is:
```
A_v = gm/gds
```

From the **gm/gds vs gm/ID chart**, longer channels provide higher gain but lower speed. We analyze gain at gm/ID = 10 S/A for each length:

| L (um) | gm/gds @ gm/ID=10 | Meets Av>10? |
|--------|-------------------|--------------|
| 0.13 | ~5-8 | No |
| 0.15 | ~6-10 | Marginal |
| 0.18 | ~8-12 | Yes |
| 0.25 | ~12-18 | Yes |
| 0.50 | ~25-35 | Yes |
| 1.00 | ~40-60 | Yes |

**Selection**: Choose the **smallest L that meets the gain requirement** to maximize fT.

### Step 3: Select gm/ID Operating Point

**Trade-offs**:
- Lower gm/ID (5-10): Higher speed (fT), higher power
- Higher gm/ID (15-20): Lower power, lower speed

**Target**: gm/ID = 10-12 S/A (moderate inversion, good balance)

### Step 4: Calculate Drain Current (ID)

```
ID = gm / (gm/ID)
   = 62.8 uS / 10 S/A
   = 6.28 uA
```

### Step 5: Calculate Width (W)

From the **ID/W vs gm/ID chart**, extract current density at selected L and gm/ID:

```
W = ID / (ID/W)
```

### Step 6: Determine VGS

From the lookup tables, find VGS that gives the target gm/ID at the selected L.

---

## Running the Design Script

### Prerequisites

1. Lookup tables generated (see `ihp_lookup_generator.py`)
2. Python environment with mosplot installed

### Execution

```bash
# From tutorial_cs_amp directory
python design_script.py

# With custom gm/ID target
python design_script.py --gmid 12

# Specify data directory
python design_script.py --data-dir ../../data
```

### Output

The script generates:

1. **Design plots** in `./plots/`:
   - `gain_vs_gmid_design.png` - Gain design space with operating point
   - `ft_vs_gmid_design.png` - Speed design space
   - `id_w_vs_gmid_design.png` - Current density
   - `cs_amp_id_vgs.png` - Transfer characteristic
   - `cs_amp_id_vds.png` - Output characteristic

2. **Ngspice netlist**: `cs_amp_op.cir`

---

## Verification with Ngspice

### Running the Simulation

```bash
# Set PDK path (if not already set)
export PDK_ROOT=/path/to/IHP-Open-PDK

# Run operating point analysis
ngspice cs_amp_op.cir
```

### Expected Output

```
======================================
Operating Point Results
======================================

@n.x1.nsg13_lv_nmos[id] = X.XXXe-06
@n.x1.nsg13_lv_nmos[gm] = X.XXXe-05
@n.x1.nsg13_lv_nmos[gds] = X.XXXe-06
@n.x1.nsg13_lv_nmos[vth] = X.XXX

Expected from gm/ID tables:
  ID = X.XX uA
  gm = XX.X uS
  gm/ID = XX.X S/A
  Av (gm/gds) = XX.X V/V (XX.X dB)
======================================
```

### Verification Criteria

| Parameter | Tolerance | Notes |
|-----------|-----------|-------|
| I_D | < 10% | Current matching |
| g_m | < 10% | Transconductance |
| g_ds | < 15% | Output conductance |
| gm/ID | < 5% | Operating point |
| A_v | < 15% | Intrinsic gain |

---

## Results Interpretation

### Successful Design

A successful design should show:

1. **ID matches** (within 10%): Validates current density extraction
2. **gm matches** (within 10%): Confirms operating point
3. **Gain meets spec**: A_v > 10 V/V (20 dB)
4. **fT margin**: fT should be >> BW (typically 10-100x)

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| ID too high | W oversized | Reduce gm/ID target |
| Gain too low | L too short | Increase L |
| fT too low | L too long | Reduce L, accept lower gain |
| Poor matching | Lookup table interpolation | Check bias conditions |

---

## Accessibility Notes

All plots in this tutorial use:

- **Color-blind friendly palette**: Tol Bright colors
- **Distinct markers**: Different shapes for each curve
- **Varied linestyles**: Solid, dashed, dotted for additional distinction

This ensures the design charts are accessible to users with color vision deficiencies.

---

## Files in This Directory

| File | Description |
|------|-------------|
| `README.md` | This tutorial document |
| `design_script.py` | Main design and plotting script |
| `cs_amp_op.cir` | Generated ngspice netlist |
| `plots/` | Generated design charts |

---

## References

1. Murmann, B. "Systematic Design of Analog Circuits Using Pre-Computed Lookup Tables"
2. Jespers, P. & Murmann, B. "Systematic Design of Analog CMOS Circuits"
3. IHP SG13G2 PDK Documentation
