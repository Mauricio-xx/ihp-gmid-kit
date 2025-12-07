# IHP gm/ID Design Kit

Analog IC design toolkit using the gm/ID methodology for the **IHP SG13G2 130nm BiCMOS PDK**.

## Features

- **Lookup table generator** with comprehensive sweep coverage (76 lengths, 13 VBS points)
- **Design charts generator** for the 4 fundamental gm/ID plots
- **Interactive tutorials** (Jupyter notebooks in English and Spanish)
- **Portable & self-contained** - includes vendorized mosplot library
- **Color-blind friendly** plots using Tol Bright palette

## Quick Start

### Prerequisites

1. **Python 3.9+** with numpy, scipy, matplotlib
2. **ngspice** installed and in PATH
3. **IHP-Open-PDK** with PDK_ROOT environment variable set

### Installation

```bash
git clone https://github.com/Mauricio-xx/ihp-gmid-kit.git
cd ihp-gmid-kit
pip install -r requirements.txt
```

### Generate Lookup Tables

LUT files are not included due to size (~200 MB). Generate them locally:

```bash
export PDK_ROOT=/path/to/IHP-Open-PDK

cd src/ihp_gmid
python lookup_generator.py --output-dir ../../data --n-process 4
```

Generation takes approximately 10-15 minutes.

### Using the Lookup Tables

```python
import sys
import os

# Add vendor to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))

from mosplot.plot import load_lookup_table, Mosfet

# Load NMOS lookup table
lookup_table = load_lookup_table("./data/sg13_lv_nmos.npz")

# Create Mosfet instance
nmos = Mosfet(
    lookup_table=lookup_table,
    mos="sg13_lv_nmos",
    vbs=0.0,
    vds=0.6,
    vgs=(0.3, 1.2)
)

# Plot gm/ID vs fT
nmos.plot_by_expression(
    x_expression=nmos.gmid_expression,
    y_expression=nmos.transist_frequency_expression,
    filtered_values=nmos.length,
    y_scale="log"
)
```

### Running the Tutorials

```bash
cd tutorials/cs_amplifier
jupyter notebook tutorial_en.ipynb  # English
jupyter notebook tutorial_es.ipynb  # Spanish
```

## Repository Structure

```
ihp-gmid-kit/
├── data/                      # Lookup tables (generated locally)
├── src/ihp_gmid/              # Main package
│   ├── design_charts.py       # Design charts generator
│   ├── lookup_generator.py    # Lookup table generator
│   └── sweep_config.py        # Sweep parameters
├── tutorials/cs_amplifier/    # CS amplifier tutorial
│   ├── tutorial_en.ipynb      # English notebook
│   ├── tutorial_es.ipynb      # Spanish notebook
│   └── design_script.py       # Automated design script
├── vendor/mosplot/            # Vendorized mosplot library
└── examples/                  # Usage examples
```

## Generating Design Charts

```bash
cd examples
python generate_design_charts.py
```

This generates the 4 fundamental gm/ID charts:
- fT vs gm/ID
- Intrinsic Gain (gm/gds) vs gm/ID
- Current Density (ID/W) vs gm/ID
- Transconductance Density (gm/W) vs gm/ID

## Lookup Table Coverage

| Parameter | Range | Step | Points |
|-----------|-------|------|--------|
| VGS | 0 to 1.5V | 10mV | 151 |
| VDS | 0 to 1.5V | 50mV | 31 |
| VBS | 0 to 1.2V | 100mV | 13 |
| Length | 0.13 to 9.88 um | 130nm | 76 |

Saved parameters: id, gm, gds, vth, vdsat, cgg, cgs, cgd (enables fT calculation).

## IHP SG13G2 PDK Notes

| Parameter | NMOS | PMOS |
|-----------|------|------|
| Model | sg13_lv_nmos | sg13_lv_pmos |
| L range | 0.13 - 10 um | 0.13 - 10 um |
| W range | 0.15 - 10 um | 0.15 - 10 um |
| VDS max | 1.5V | -1.5V |

## License

Apache License 2.0 - See [LICENSE](LICENSE)

This project includes [mosplot](https://github.com/medwatt/gmid) (Apache 2.0) - See [NOTICE](NOTICE)
