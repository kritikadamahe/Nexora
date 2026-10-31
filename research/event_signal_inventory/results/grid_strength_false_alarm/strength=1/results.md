Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 235s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spurious_rate=0 | A_blind | 17203 ± 2693 | 11674 ± 2299 | 705 ± 143 | 4825 ± 589 | 11674 ± 2299 | 1174 ± 239 | 0.883 ± 0.021 | 0.289 ± 0.019 | 0.135 ± 0.013 | 0.800 ± 0.000 |
| spurious_rate=0 | B_clean_trained | 11207 ± 1664 | 4724 ± 1179 | 1239 ± 389 | 5244 ± 546 | 4724 ± 1179 | 2064 ± 649 | 0.953 ± 0.007 | 0.231 ± 0.004 | 0.061 ± 0.004 | 0.900 ± 0.000 |
| spurious_rate=0 | C_asavailable_trained | 11581 ± 1856 | 4970 ± 1768 | 1282 ± 676 | 5330 ± 1041 | 4970 ± 1768 | 2136 ± 1127 | 0.951 ± 0.015 | 0.232 ± 0.003 | 0.067 ± 0.013 | 0.880 ± 0.042 |
| spurious_rate=0.04 | A_blind | 17203 ± 2693 | 11674 ± 2299 | 705 ± 143 | 4825 ± 589 | 11674 ± 2299 | 1174 ± 239 | 0.883 ± 0.021 | 0.289 ± 0.019 | 0.135 ± 0.013 | 0.800 ± 0.000 |
| spurious_rate=0.04 | B_clean_trained | 15591 ± 2676 | 5767 ± 2088 | 3892 ± 984 | 5932 ± 735 | 5767 ± 2088 | 6486 ± 1640 | 0.943 ± 0.016 | 0.289 ± 0.023 | 0.091 ± 0.022 | 0.840 ± 0.052 |
| spurious_rate=0.04 | C_asavailable_trained | 14519 ± 2647 | 6471 ± 2697 | 2495 ± 808 | 5554 ± 939 | 6471 ± 2697 | 4158 ± 1347 | 0.936 ± 0.021 | 0.261 ± 0.014 | 0.088 ± 0.021 | 0.850 ± 0.053 |
| spurious_rate=0.08 | A_blind | 17203 ± 2693 | 11674 ± 2299 | 705 ± 143 | 4825 ± 589 | 11674 ± 2299 | 1174 ± 239 | 0.883 ± 0.021 | 0.289 ± 0.019 | 0.135 ± 0.013 | 0.800 ± 0.000 |
| spurious_rate=0.08 | B_clean_trained | 20445 ± 3107 | 7258 ± 2309 | 6483 ± 2095 | 6704 ± 1558 | 7258 ± 2309 | 10805 ± 3492 | 0.927 ± 0.023 | 0.365 ± 0.034 | 0.131 ± 0.030 | 0.780 ± 0.075 |
| spurious_rate=0.08 | C_asavailable_trained | 17045 ± 2098 | 9563 ± 2675 | 2405 ± 1392 | 5077 ± 955 | 9563 ± 2675 | 4009 ± 2319 | 0.904 ± 0.026 | 0.279 ± 0.019 | 0.118 ± 0.020 | 0.795 ± 0.060 |
| spurious_rate=0.16 | A_blind | 17203 ± 2693 | 11674 ± 2299 | 705 ± 143 | 4825 ± 589 | 11674 ± 2299 | 1174 ± 239 | 0.883 ± 0.021 | 0.289 ± 0.019 | 0.135 ± 0.013 | 0.800 ± 0.000 |
| spurious_rate=0.16 | B_clean_trained | 23904 ± 2970 | 10137 ± 2346 | 7255 ± 2124 | 6512 ± 1051 | 10137 ± 2346 | 12092 ± 3540 | 0.899 ± 0.022 | 0.446 ± 0.037 | 0.204 ± 0.018 | 0.620 ± 0.063 |
| spurious_rate=0.16 | C_asavailable_trained | 16832 ± 2537 | 10368 ± 2925 | 1713 ± 935 | 4752 ± 960 | 10368 ± 2925 | 2855 ± 1558 | 0.895 ± 0.034 | 0.278 ± 0.020 | 0.121 ± 0.023 | 0.795 ± 0.060 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| spurious_rate=0 | C_asavailable_trained vs B_clean_trained | +3.338% | [+2.370%, +4.372%] | 0.40 |
| spurious_rate=0 | C_asavailable_trained vs A_blind | -32.680% | [-34.601%, -30.931%] | 0.92 |
| spurious_rate=0 | B_clean_trained vs A_blind | -34.855% | [-36.762%, -32.914%] | 0.92 |
| spurious_rate=0.04 | C_asavailable_trained vs B_clean_trained | -6.874% | [-8.203%, -5.549%] | 0.72 |
| spurious_rate=0.04 | C_asavailable_trained vs A_blind | -15.599% | [-17.875%, -13.328%] | 0.79 |
| spurious_rate=0.04 | B_clean_trained vs A_blind | -9.368% | [-11.651%, -7.229%] | 0.67 |
| spurious_rate=0.08 | C_asavailable_trained vs B_clean_trained | -16.630% | [-18.710%, -14.518%] | 0.78 |
| spurious_rate=0.08 | C_asavailable_trained vs A_blind | -0.918% | [-2.910%, +1.131%] | 0.55 |
| spurious_rate=0.08 | B_clean_trained vs A_blind | +18.846% | [+15.151%, +22.941%] | 0.29 |
| spurious_rate=0.16 | C_asavailable_trained vs B_clean_trained | -29.582% | [-31.499%, -27.725%] | 0.96 |
| spurious_rate=0.16 | C_asavailable_trained vs A_blind | -2.154% | [-4.100%, -0.269%] | 0.53 |
| spurious_rate=0.16 | B_clean_trained vs A_blind | +38.951% | [+35.055%, +42.815%] | 0.05 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| spurious_rate=0 | 0 | -1.5% | -32.1% |
| spurious_rate=0 | 1 | +9.3% | -25.1% |
| spurious_rate=0 | 2 | +1.9% | -27.4% |
| spurious_rate=0 | 3 | +0.6% | -30.9% |
| spurious_rate=0 | 4 | +0.6% | -23.4% |
| spurious_rate=0 | 5 | +1.5% | -41.5% |
| spurious_rate=0 | 6 | +10.7% | -35.1% |
| spurious_rate=0 | 7 | -0.2% | -42.3% |
| spurious_rate=0 | 8 | +9.9% | -27.1% |
| spurious_rate=0 | 9 | -0.3% | -39.1% |
| spurious_rate=0.04 | 0 | -9.0% | -10.7% |
| spurious_rate=0.04 | 1 | -7.6% | -15.6% |
| spurious_rate=0.04 | 2 | -7.5% | -9.5% |
| spurious_rate=0.04 | 3 | -2.6% | -5.7% |
| spurious_rate=0.04 | 4 | -5.2% | -14.1% |
| spurious_rate=0.04 | 5 | -7.6% | -9.6% |
| spurious_rate=0.04 | 6 | -9.2% | -17.5% |
| spurious_rate=0.04 | 7 | -7.2% | -28.8% |
| spurious_rate=0.04 | 8 | -7.7% | -17.3% |
| spurious_rate=0.04 | 9 | -6.2% | -26.5% |
| spurious_rate=0.08 | 0 | -20.9% | +3.2% |
| spurious_rate=0.08 | 1 | -25.6% | +5.6% |
| spurious_rate=0.08 | 2 | -10.1% | +0.3% |
| spurious_rate=0.08 | 3 | -11.6% | -6.3% |
| spurious_rate=0.08 | 4 | -16.5% | +29.5% |
| spurious_rate=0.08 | 5 | -11.1% | -1.5% |
| spurious_rate=0.08 | 6 | -20.0% | -3.6% |
| spurious_rate=0.08 | 7 | -8.4% | -7.2% |
| spurious_rate=0.08 | 8 | -11.6% | -12.2% |
| spurious_rate=0.08 | 9 | -25.0% | -7.4% |
| spurious_rate=0.16 | 0 | -36.6% | -9.0% |
| spurious_rate=0.16 | 1 | -34.3% | -8.2% |
| spurious_rate=0.16 | 2 | -30.8% | +5.3% |
| spurious_rate=0.16 | 3 | -25.1% | -4.8% |
| spurious_rate=0.16 | 4 | -36.0% | +5.5% |
| spurious_rate=0.16 | 5 | -29.8% | -1.7% |
| spurious_rate=0.16 | 6 | -40.2% | -14.9% |
| spurious_rate=0.16 | 7 | -12.2% | +12.9% |
| spurious_rate=0.16 | 8 | -18.9% | +11.7% |
| spurious_rate=0.16 | 9 | -30.0% | -13.4% |

Mean event counts in the test period (announcements include spurious ones):

- spurious_rate=0: true events 10.1, announcements 9.5
- spurious_rate=0.04: true events 10.1, announcements 17.2
- spurious_rate=0.08: true events 10.1, announcements 25.0
- spurious_rate=0.16: true events 10.1, announcements 36.1
