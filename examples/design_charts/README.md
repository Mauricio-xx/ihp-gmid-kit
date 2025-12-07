# IHP SG13G2 Design Charts

Pre-generated gm/ID design charts at 300 dpi. VDS = 0.6V (NMOS) / -0.6V (PMOS), VBS = 0V.

## Charts

| File | Description |
|------|-------------|
| `nmos_ft_vs_gmid.png` | NMOS Transit Frequency vs gm/ID |
| `nmos_gain_vs_gmid.png` | NMOS Intrinsic Gain (gm/gds) vs gm/ID |
| `nmos_id_w_vs_gmid.png` | NMOS Current Density (ID/W) vs gm/ID |
| `nmos_gm_w_vs_gmid.png` | NMOS Transconductance Density (gm/W) vs gm/ID |
| `pmos_ft_vs_gmid.png` | PMOS Transit Frequency vs gm/ID |
| `pmos_gain_vs_gmid.png` | PMOS Intrinsic Gain (gm/gds) vs gm/ID |
| `pmos_id_w_vs_gmid.png` | PMOS Current Density (ID/W) vs gm/ID |
| `pmos_gm_w_vs_gmid.png` | PMOS Transconductance Density (gm/W) vs gm/ID |

## Regenerate

```bash
python ../generate_design_charts.py
```
