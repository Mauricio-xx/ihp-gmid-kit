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
"""

import sys
import os

# Prioritize vendorized mosplot over system installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vendor')))

from mosplot.lookup_table_generator import TransistorSweep

# NMOS sweep configuration
nmos_sweep = TransistorSweep(
    mos_type="nmos",
    length=[0.13e-6, 0.15e-6, 0.18e-6, 0.25e-6, 0.5e-6, 1.0e-6, 2.0e-6],
    vgs=(0, 1.5, 0.01),      # 0V to 1.5V, 10mV steps -> 151 points
    vds=(0, 1.5, 0.05),      # 0V to 1.5V, 50mV steps -> 31 points
    vbs=(0, -1.2, -0.3)      # 0V to -1.2V, -300mV steps -> 5 points
)

# PMOS sweep configuration
pmos_sweep = TransistorSweep(
    mos_type="pmos",
    length=[0.13e-6, 0.15e-6, 0.18e-6, 0.25e-6, 0.5e-6, 1.0e-6, 2.0e-6],
    vgs=(0, -1.5, -0.01),    # 0V to -1.5V, -10mV steps -> 151 points
    vds=(0, -1.5, -0.05),    # 0V to -1.5V, -50mV steps -> 31 points
    vbs=(0, 1.2, 0.3)        # 0V to 1.2V, 300mV steps -> 5 points
)
