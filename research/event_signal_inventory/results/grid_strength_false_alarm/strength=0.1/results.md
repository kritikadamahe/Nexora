Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 224s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spurious_rate=0 | A_blind | 8765 ± 890 | 3215 ± 446 | 540 ± 43 | 5010 ± 533 | 3215 ± 446 | 900 ± 71 | 0.964 ± 0.003 | 0.224 ± 0.008 | 0.057 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0 | B_clean_trained | 8467 ± 826 | 3190 ± 391 | 474 ± 51 | 4803 ± 533 | 3190 ± 391 | 791 ± 85 | 0.964 ± 0.004 | 0.220 ± 0.007 | 0.055 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0 | C_asavailable_trained | 8501 ± 835 | 3192 ± 383 | 480 ± 56 | 4829 ± 543 | 3192 ± 383 | 799 ± 93 | 0.964 ± 0.004 | 0.220 ± 0.007 | 0.055 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.04 | A_blind | 8765 ± 890 | 3215 ± 446 | 540 ± 43 | 5010 ± 533 | 3215 ± 446 | 900 ± 71 | 0.964 ± 0.003 | 0.224 ± 0.008 | 0.057 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.04 | B_clean_trained | 8560 ± 846 | 3150 ± 404 | 533 ± 90 | 4876 ± 535 | 3150 ± 404 | 888 ± 150 | 0.964 ± 0.003 | 0.222 ± 0.007 | 0.055 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.04 | C_asavailable_trained | 8570 ± 862 | 3228 ± 431 | 496 ± 60 | 4846 ± 500 | 3228 ± 431 | 827 ± 101 | 0.964 ± 0.003 | 0.221 ± 0.008 | 0.055 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.08 | A_blind | 8765 ± 890 | 3215 ± 446 | 540 ± 43 | 5010 ± 533 | 3215 ± 446 | 900 ± 71 | 0.964 ± 0.003 | 0.224 ± 0.008 | 0.057 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.08 | B_clean_trained | 8673 ± 864 | 3127 ± 379 | 589 ± 119 | 4956 ± 557 | 3127 ± 379 | 982 ± 198 | 0.965 ± 0.004 | 0.224 ± 0.008 | 0.056 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.08 | C_asavailable_trained | 8630 ± 847 | 3206 ± 372 | 520 ± 71 | 4903 ± 581 | 3206 ± 372 | 867 ± 118 | 0.964 ± 0.004 | 0.222 ± 0.008 | 0.056 ± 0.003 | 0.900 ± 0.000 |
| spurious_rate=0.16 | A_blind | 8765 ± 890 | 3215 ± 446 | 540 ± 43 | 5010 ± 533 | 3215 ± 446 | 900 ± 71 | 0.964 ± 0.003 | 0.224 ± 0.008 | 0.057 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.16 | B_clean_trained | 8767 ± 894 | 3075 ± 453 | 653 ± 133 | 5038 ± 546 | 3075 ± 453 | 1089 ± 222 | 0.965 ± 0.004 | 0.226 ± 0.008 | 0.056 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.16 | C_asavailable_trained | 8638 ± 878 | 3270 ± 418 | 503 ± 45 | 4865 ± 518 | 3270 ± 418 | 838 ± 74 | 0.963 ± 0.003 | 0.222 ± 0.007 | 0.056 ± 0.002 | 0.900 ± 0.000 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| spurious_rate=0 | C_asavailable_trained vs B_clean_trained | +0.400% | [+0.059%, +0.755%] | 0.44 |
| spurious_rate=0 | C_asavailable_trained vs A_blind | -3.010% | [-3.780%, -2.250%] | 0.63 |
| spurious_rate=0 | B_clean_trained vs A_blind | -3.396% | [-4.241%, -2.624%] | 0.67 |
| spurious_rate=0.04 | C_asavailable_trained vs B_clean_trained | +0.120% | [-0.320%, +0.554%] | 0.53 |
| spurious_rate=0.04 | C_asavailable_trained vs A_blind | -2.226% | [-2.893%, -1.586%] | 0.63 |
| spurious_rate=0.04 | B_clean_trained vs A_blind | -2.343% | [-3.150%, -1.607%] | 0.62 |
| spurious_rate=0.08 | C_asavailable_trained vs B_clean_trained | -0.493% | [-1.012%, +0.020%] | 0.56 |
| spurious_rate=0.08 | C_asavailable_trained vs A_blind | -1.539% | [-2.205%, -0.870%] | 0.59 |
| spurious_rate=0.08 | B_clean_trained vs A_blind | -1.051% | [-1.739%, -0.400%] | 0.56 |
| spurious_rate=0.16 | C_asavailable_trained vs B_clean_trained | -1.479% | [-2.155%, -0.801%] | 0.57 |
| spurious_rate=0.16 | C_asavailable_trained vs A_blind | -1.453% | [-2.051%, -0.879%] | 0.58 |
| spurious_rate=0.16 | B_clean_trained vs A_blind | +0.026% | [-0.860%, +0.843%] | 0.51 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| spurious_rate=0 | 0 | +0.2% | -3.0% |
| spurious_rate=0 | 1 | +1.4% | -4.1% |
| spurious_rate=0 | 2 | -0.2% | -2.0% |
| spurious_rate=0 | 3 | +0.6% | -3.4% |
| spurious_rate=0 | 4 | +1.1% | -0.6% |
| spurious_rate=0 | 5 | +0.5% | -2.3% |
| spurious_rate=0 | 6 | +0.1% | -5.0% |
| spurious_rate=0 | 7 | -0.1% | -3.3% |
| spurious_rate=0 | 8 | +0.1% | -2.1% |
| spurious_rate=0 | 9 | +0.4% | -4.0% |
| spurious_rate=0.04 | 0 | -0.0% | -1.9% |
| spurious_rate=0.04 | 1 | +0.5% | -4.3% |
| spurious_rate=0.04 | 2 | -0.2% | -1.9% |
| spurious_rate=0.04 | 3 | +0.6% | -1.4% |
| spurious_rate=0.04 | 4 | +0.3% | -1.2% |
| spurious_rate=0.04 | 5 | -0.6% | -1.1% |
| spurious_rate=0.04 | 6 | -0.3% | -3.5% |
| spurious_rate=0.04 | 7 | -0.1% | -2.2% |
| spurious_rate=0.04 | 8 | -0.1% | -2.1% |
| spurious_rate=0.04 | 9 | +1.1% | -2.5% |
| spurious_rate=0.08 | 0 | -0.7% | -1.9% |
| spurious_rate=0.08 | 1 | -1.3% | -4.5% |
| spurious_rate=0.08 | 2 | -0.3% | -1.7% |
| spurious_rate=0.08 | 3 | +0.4% | -1.3% |
| spurious_rate=0.08 | 4 | -1.6% | -0.6% |
| spurious_rate=0.08 | 5 | -0.6% | -0.6% |
| spurious_rate=0.08 | 6 | -3.0% | -2.5% |
| spurious_rate=0.08 | 7 | +0.3% | +0.2% |
| spurious_rate=0.08 | 8 | +1.1% | -1.0% |
| spurious_rate=0.08 | 9 | +1.1% | -1.0% |
| spurious_rate=0.16 | 0 | -1.8% | -2.4% |
| spurious_rate=0.16 | 1 | +1.2% | -3.2% |
| spurious_rate=0.16 | 2 | -0.8% | -0.2% |
| spurious_rate=0.16 | 3 | -1.2% | -0.4% |
| spurious_rate=0.16 | 4 | -1.3% | -0.1% |
| spurious_rate=0.16 | 5 | -2.1% | -1.8% |
| spurious_rate=0.16 | 6 | -4.2% | -2.9% |
| spurious_rate=0.16 | 7 | -3.1% | -0.6% |
| spurious_rate=0.16 | 8 | -1.8% | -1.0% |
| spurious_rate=0.16 | 9 | +0.3% | -1.8% |

Mean event counts in the test period (announcements include spurious ones):

- spurious_rate=0: true events 10.1, announcements 9.5
- spurious_rate=0.04: true events 10.1, announcements 17.2
- spurious_rate=0.08: true events 10.1, announcements 25.0
- spurious_rate=0.16: true events 10.1, announcements 36.1
