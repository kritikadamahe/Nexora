Seeds: [0, 1, 2, 3, 4] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 171s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spurious_rate=0 | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| spurious_rate=0 | B_clean_trained | 11142 ± 1503 | 4648 ± 669 | 1186 ± 380 | 5308 ± 505 | 4648 ± 669 | 1977 ± 634 | 0.955 ± 0.003 | 0.226 ± 0.003 | 0.059 ± 0.001 | 0.900 ± 0.000 |
| spurious_rate=0 | C_asavailable_trained | 11142 ± 1503 | 4648 ± 669 | 1186 ± 380 | 5308 ± 505 | 4648 ± 669 | 1977 ± 634 | 0.955 ± 0.003 | 0.226 ± 0.003 | 0.059 ± 0.001 | 0.900 ± 0.000 |
| spurious_rate=0.04 | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| spurious_rate=0.04 | B_clean_trained | 13139 ± 1834 | 7449 ± 1064 | 1309 ± 700 | 4381 ± 450 | 7449 ± 1064 | 2182 ± 1166 | 0.928 ± 0.002 | 0.241 ± 0.016 | 0.091 ± 0.004 | 0.800 ± 0.000 |
| spurious_rate=0.04 | C_asavailable_trained | 12566 ± 1563 | 5607 ± 1413 | 1597 ± 904 | 5362 ± 948 | 5607 ± 1413 | 2662 ± 1506 | 0.945 ± 0.014 | 0.246 ± 0.013 | 0.069 ± 0.012 | 0.880 ± 0.045 |
| spurious_rate=0.08 | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| spurious_rate=0.08 | B_clean_trained | 15596 ± 2476 | 6013 ± 554 | 3704 ± 1669 | 5879 ± 1396 | 6013 ± 554 | 6173 ± 2781 | 0.941 ± 0.010 | 0.287 ± 0.025 | 0.097 ± 0.017 | 0.820 ± 0.045 |
| spurious_rate=0.08 | C_asavailable_trained | 14885 ± 2151 | 6071 ± 1681 | 2941 ± 1341 | 5873 ± 1280 | 6071 ± 1681 | 4901 ± 2236 | 0.941 ± 0.017 | 0.267 ± 0.015 | 0.083 ± 0.017 | 0.860 ± 0.055 |
| spurious_rate=0.12 | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| spurious_rate=0.12 | B_clean_trained | 16678 ± 2538 | 6504 ± 1264 | 4163 ± 758 | 6011 ± 679 | 6504 ± 1264 | 6938 ± 1264 | 0.937 ± 0.006 | 0.303 ± 0.008 | 0.109 ± 0.002 | 0.800 ± 0.000 |
| spurious_rate=0.12 | C_asavailable_trained | 15502 ± 1731 | 5945 ± 1758 | 3275 ± 883 | 6282 ± 1057 | 5945 ± 1758 | 5458 ± 1471 | 0.942 ± 0.017 | 0.267 ± 0.008 | 0.080 ± 0.015 | 0.880 ± 0.045 |
| spurious_rate=0.2 | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| spurious_rate=0.2 | B_clean_trained | 20425 ± 2583 | 6984 ± 2740 | 6377 ± 1467 | 7064 ± 1087 | 6984 ± 2740 | 10628 ± 2445 | 0.933 ± 0.021 | 0.382 ± 0.036 | 0.147 ± 0.022 | 0.740 ± 0.082 |
| spurious_rate=0.2 | C_asavailable_trained | 17351 ± 1711 | 7095 ± 2797 | 3805 ± 1371 | 6451 ± 823 | 7095 ± 2797 | 6342 ± 2285 | 0.932 ± 0.019 | 0.276 ± 0.009 | 0.094 ± 0.017 | 0.860 ± 0.055 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| spurious_rate=0 | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| spurious_rate=0 | C_asavailable_trained vs A_blind | -31.388% | [-33.613%, -29.110%] | 0.91 |
| spurious_rate=0 | B_clean_trained vs A_blind | -31.388% | [-33.765%, -29.003%] | 0.91 |
| spurious_rate=0.04 | C_asavailable_trained vs B_clean_trained | -4.362% | [-6.679%, -2.274%] | 0.61 |
| spurious_rate=0.04 | C_asavailable_trained vs A_blind | -22.621% | [-24.792%, -20.260%] | 0.86 |
| spurious_rate=0.04 | B_clean_trained vs A_blind | -19.092% | [-21.844%, -16.314%] | 0.74 |
| spurious_rate=0.08 | C_asavailable_trained vs B_clean_trained | -4.555% | [-6.039%, -3.171%] | 0.69 |
| spurious_rate=0.08 | C_asavailable_trained vs A_blind | -8.339% | [-10.822%, -5.618%] | 0.67 |
| spurious_rate=0.08 | B_clean_trained vs A_blind | -3.964% | [-7.065%, -0.772%] | 0.55 |
| spurious_rate=0.12 | C_asavailable_trained vs B_clean_trained | -7.051% | [-8.703%, -5.402%] | 0.65 |
| spurious_rate=0.12 | C_asavailable_trained vs A_blind | -4.540% | [-7.040%, -2.037%] | 0.60 |
| spurious_rate=0.12 | B_clean_trained vs A_blind | +2.701% | [+0.064%, +5.534%] | 0.42 |
| spurious_rate=0.2 | C_asavailable_trained vs B_clean_trained | -15.048% | [-16.759%, -13.497%] | 0.92 |
| spurious_rate=0.2 | C_asavailable_trained vs A_blind | +6.847% | [+3.237%, +10.888%] | 0.41 |
| spurious_rate=0.2 | B_clean_trained vs A_blind | +25.774% | [+21.446%, +30.531%] | 0.17 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| spurious_rate=0 | 0 | +0.0% | -31.1% |
| spurious_rate=0 | 1 | +0.0% | -31.4% |
| spurious_rate=0 | 2 | +0.0% | -30.3% |
| spurious_rate=0 | 3 | +0.0% | -36.7% |
| spurious_rate=0 | 4 | +0.0% | -24.7% |
| spurious_rate=0.04 | 0 | -4.5% | -15.3% |
| spurious_rate=0.04 | 1 | -7.2% | -26.9% |
| spurious_rate=0.04 | 2 | -2.1% | -22.4% |
| spurious_rate=0.04 | 3 | -7.6% | -31.8% |
| spurious_rate=0.04 | 4 | +0.5% | -12.4% |
| spurious_rate=0.08 | 0 | -9.4% | -10.3% |
| spurious_rate=0.08 | 1 | -1.3% | +3.3% |
| spurious_rate=0.08 | 2 | -6.0% | -3.9% |
| spurious_rate=0.08 | 3 | -5.8% | -15.6% |
| spurious_rate=0.08 | 4 | +0.9% | -11.7% |
| spurious_rate=0.12 | 0 | -2.5% | -3.5% |
| spurious_rate=0.12 | 1 | -6.3% | -0.5% |
| spurious_rate=0.12 | 2 | -5.5% | -2.2% |
| spurious_rate=0.12 | 3 | -12.3% | -14.7% |
| spurious_rate=0.12 | 4 | -6.6% | +3.1% |
| spurious_rate=0.2 | 0 | -21.6% | +8.4% |
| spurious_rate=0.2 | 1 | -10.6% | +10.4% |
| spurious_rate=0.2 | 2 | -15.1% | +6.7% |
| spurious_rate=0.2 | 3 | -18.0% | -7.7% |
| spurious_rate=0.2 | 4 | -8.3% | +23.6% |

Mean event counts in the test period (announcements include spurious ones):

- spurious_rate=0: true events 10.0, announcements 10.0
- spurious_rate=0.04: true events 10.0, announcements 14.0
- spurious_rate=0.08: true events 10.0, announcements 22.6
- spurious_rate=0.12: true events 10.0, announcements 28.2
- spurious_rate=0.2: true events 10.0, announcements 46.8
