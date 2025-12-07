# Lookup Tables

Pre-generated MOSFET characterization lookup tables for IHP SG13G2 130nm PDK.

## Files

| File | Description | Size |
|------|-------------|------|
| `sg13_lv_nmos.npz` | Low-voltage NMOS characterization | ~3.5 MB |
| `sg13_lv_pmos.npz` | Low-voltage PMOS characterization | ~4.0 MB |

## Sweep Parameters

### NMOS
| Parameter | Range | Step | Points |
|-----------|-------|------|--------|
| VGS | 0 to 1.5V | 10mV | 151 |
| VDS | 0 to 1.5V | 50mV | 31 |
| VBS | 0 to -1.2V | -300mV | 5 |
| Length | 0.13, 0.15, 0.18, 0.25, 0.5, 1.0, 2.0 um | - | 7 |

### PMOS
| Parameter | Range | Step | Points |
|-----------|-------|------|--------|
| VGS | 0 to -1.5V | -10mV | 151 |
| VDS | 0 to -1.5V | -50mV | 31 |
| VBS | 0 to 1.2V | 300mV | 5 |
| Length | 0.13, 0.15, 0.18, 0.25, 0.5, 1.0, 2.0 um | - | 7 |

## Regenerating Tables

If you need to regenerate the tables (e.g., for different corners or sweep ranges):

```bash
# Requires PDK_ROOT environment variable and ngspice
export PDK_ROOT=/path/to/IHP-Open-PDK
python src/ihp_gmid/lookup_generator.py --output-dir ./data
```
