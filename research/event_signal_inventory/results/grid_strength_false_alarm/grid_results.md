# Event strength x spurious_rate

Base config `configs/seed20.json`, base condition `false_alarm`, seeds [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]. Runtime 932s.

Cells: mean per-seed relative test-cost difference (negative = first arm cheaper), then seeds where the first arm was cheaper and the exact sign-flip p (not multiplicity-corrected).

## C_asavailable_trained vs B_clean_trained

| strength | spurious_rate=0 | spurious_rate=0.04 | spurious_rate=0.08 | spurious_rate=0.16 |
|---|---|---|---|---|
| 0.1 | +0.4% (2/10, p=0.033) | +0.1% (6/10, p=0.531) | -0.5% (6/10, p=0.283) | -1.5% (8/10, p=0.018) |
| 0.25 | +0.3% (3/10, p=0.234) | -0.3% (6/10, p=0.266) | -2.4% (10/10, p=0.002) | -5.6% (10/10, p=0.002) |
| 0.5 | +0.9% (3/10, p=0.070) | -3.0% (10/10, p=0.002) | -7.9% (10/10, p=0.002) | -13.7% (10/10, p=0.002) |
| 1 | +3.2% (3/10, p=0.047) | -7.0% (10/10, p=0.002) | -16.1% (10/10, p=0.002) | -29.4% (10/10, p=0.002) |

## C_asavailable_trained vs A_blind

| strength | spurious_rate=0 | spurious_rate=0.04 | spurious_rate=0.08 | spurious_rate=0.16 |
|---|---|---|---|---|
| 0.1 | -3.0% (10/10, p=0.002) | -2.2% (10/10, p=0.002) | -1.5% (9/10, p=0.004) | -1.4% (10/10, p=0.002) |
| 0.25 | -5.8% (10/10, p=0.002) | -3.9% (10/10, p=0.002) | -2.9% (9/10, p=0.004) | -2.5% (9/10, p=0.004) |
| 0.5 | -14.2% (10/10, p=0.002) | -9.3% (10/10, p=0.002) | -2.8% (8/10, p=0.279) | -3.2% (7/10, p=0.084) |
| 1 | -32.4% (10/10, p=0.002) | -15.5% (10/10, p=0.002) | +0.0% (6/10, p=0.992) | -1.6% (6/10, p=0.611) |

## B_clean_trained vs A_blind

| strength | spurious_rate=0 | spurious_rate=0.04 | spurious_rate=0.08 | spurious_rate=0.16 |
|---|---|---|---|---|
| 0.1 | -3.4% (10/10, p=0.002) | -2.3% (10/10, p=0.002) | -1.0% (7/10, p=0.043) | +0.1% (3/10, p=0.938) |
| 0.25 | -6.1% (10/10, p=0.002) | -3.6% (9/10, p=0.004) | -0.5% (5/10, p=0.492) | +3.3% (2/10, p=0.012) |
| 0.5 | -14.9% (10/10, p=0.002) | -6.5% (10/10, p=0.002) | +5.7% (3/10, p=0.061) | +12.5% (0/10, p=0.002) |
| 1 | -34.5% (10/10, p=0.002) | -9.2% (10/10, p=0.002) | +20.0% (1/10, p=0.004) | +40.0% (0/10, p=0.002) |
