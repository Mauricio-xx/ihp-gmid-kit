# Lookup Tables

MOSFET characterization lookup tables for IHP SG13G2 130nm PDK.

**Note:** LUT files are not included in this repository due to size (~200 MB total). You must generate them locally using the provided scripts.

## Generating Lookup Tables

Requirements:
- IHP-Open-PDK installed
- ngspice in PATH
- PDK_ROOT environment variable set

```bash
export PDK_ROOT=/path/to/IHP-Open-PDK

cd src/ihp_gmid
python lookup_generator.py --output-dir ../../data --n-process 4
```

Generation takes approximately 10-15 minutes with 4 parallel processes.

## Output Files

| File | Description | Size |
|------|-------------|------|
| `sg13_lv_nmos.npz` | Low-voltage NMOS characterization | ~97 MB |
| `sg13_lv_pmos.npz` | Low-voltage PMOS characterization | ~102 MB |

## Sweep Parameters

| Parameter | Range | Step | Points |
|-----------|-------|------|--------|
| VGS | 0 to 1.5V | 10mV | 151 |
| VDS | 0 to 1.5V | 50mV | 31 |
| VBS | 0 to 1.2V | 100mV | 13 |
| Length | 0.13 to 9.88 um | 130nm | 76 |

## Saved Parameters

- id (drain current)
- gm (transconductance)
- gds (output conductance)
- vth (threshold voltage)
- vdsat (saturation voltage)
- cgg, cgs, cgd (gate capacitances for fT calculation)
