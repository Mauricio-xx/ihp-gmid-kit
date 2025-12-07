"""
IHP SG13G2 Sweep Configuration

Defines sweep parameters for NMOS and PMOS transistors in the IHP SG13G2 130nm PDK.

Device constraints (from PDK documentation):
- L (length): 0.13um - 10um
- W (width): 0.15um - 10um
- VDS max: 1.5V

Model names:
- NMOS: sg13_lv_nmos (subcircuit)
- PMOS: sg13_lv_pmos (subcircuit)

Sweep configuration:
- 76 length values from 130nm to 9.88um (130nm steps)
- VGS: 10mV resolution (finer than typical 100mV)
- VDS: 50mV resolution
- VBS: 100mV resolution (13 points)
- Includes capacitances (cgg, cgs, cgd) for fT calculation
"""

import sys
import os

# Prioritize vendorized mosplot over system installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vendor')))

from mosplot.lookup_table_generator import TransistorSweep

# Generate 76 length values from 130nm to 9.88um (130nm steps)
LENGTH_VALUES = [130e-9 + i * 130e-9 for i in range(76)]

# NMOS sweep configuration
nmos_sweep = TransistorSweep(
    mos_type="nmos",
    length=LENGTH_VALUES,
    vgs=(0, 1.5, 0.01),      # 0V to 1.5V, 10mV steps -> 151 points
    vds=(0, 1.5, 0.05),      # 0V to 1.5V, 50mV steps -> 31 points
    vbs=(0, -1.2, -0.1)      # 0V to -1.2V, 100mV steps -> 13 points
)

# PMOS sweep configuration
pmos_sweep = TransistorSweep(
    mos_type="pmos",
    length=LENGTH_VALUES,
    vgs=(0, -1.5, -0.01),    # 0V to -1.5V, -10mV steps -> 151 points
    vds=(0, -1.5, -0.05),    # 0V to -1.5V, -50mV steps -> 31 points
    vbs=(0, 1.2, 0.1)        # 0V to 1.2V, 100mV steps -> 13 points
)
