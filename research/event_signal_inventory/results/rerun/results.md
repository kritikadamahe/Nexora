Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 947s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 17748 ± 3065 | 11397 ± 2781 | 1026 ± 721 | 5325 ± 1113 | 11397 ± 2781 | 1709 ± 1202 | 0.889 ± 0.025 | 0.289 ± 0.022 | 0.131 ± 0.018 | 0.815 ± 0.037 |
| clean | B_clean_trained | 11208 ± 1402 | 4411 ± 833 | 1358 ± 519 | 5438 ± 673 | 4411 ± 833 | 2264 ± 865 | 0.957 ± 0.006 | 0.228 ± 0.006 | 0.060 ± 0.007 | 0.895 ± 0.022 |
| clean | C_asavailable_trained | 11208 ± 1402 | 4411 ± 833 | 1358 ± 519 | 5438 ± 673 | 4411 ± 833 | 2264 ± 865 | 0.957 ± 0.006 | 0.228 ± 0.006 | 0.060 ± 0.007 | 0.895 ± 0.022 |
| false_alarm | A_blind | 17748 ± 3065 | 11397 ± 2781 | 1026 ± 721 | 5325 ± 1113 | 11397 ± 2781 | 1709 ± 1202 | 0.889 ± 0.025 | 0.289 ± 0.022 | 0.131 ± 0.018 | 0.815 ± 0.037 |
| false_alarm | B_clean_trained | 20521 ± 3499 | 6955 ± 2163 | 6687 ± 2353 | 6880 ± 1501 | 6955 ± 2163 | 11144 ± 3922 | 0.932 ± 0.019 | 0.357 ± 0.042 | 0.126 ± 0.031 | 0.785 ± 0.078 |
| false_alarm | C_asavailable_trained | 17121 ± 2797 | 9176 ± 3040 | 2542 ± 1475 | 5403 ± 1234 | 9176 ± 3040 | 4237 ± 2458 | 0.911 ± 0.028 | 0.278 ± 0.021 | 0.112 ± 0.022 | 0.813 ± 0.056 |
| imperfect | A_blind | 17748 ± 3065 | 11397 ± 2781 | 1026 ± 721 | 5325 ± 1113 | 11397 ± 2781 | 1709 ± 1202 | 0.889 ± 0.025 | 0.289 ± 0.022 | 0.131 ± 0.018 | 0.815 ± 0.037 |
| imperfect | B_clean_trained | 17992 ± 4218 | 8305 ± 3442 | 3777 ± 1514 | 5910 ± 1197 | 8305 ± 3442 | 6295 ± 2523 | 0.919 ± 0.034 | 0.296 ± 0.026 | 0.100 ± 0.028 | 0.855 ± 0.051 |
| imperfect | C_asavailable_trained | 17134 ± 3618 | 9598 ± 3979 | 2092 ± 1027 | 5444 ± 1080 | 9598 ± 3979 | 3487 ± 1711 | 0.908 ± 0.033 | 0.280 ± 0.023 | 0.112 ± 0.024 | 0.823 ± 0.062 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | -36.852% | [-38.168%, -35.492%] | 0.90 |
| clean | B_clean_trained vs A_blind | -36.852% | [-38.222%, -35.483%] | 0.90 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -16.567% | [-17.947%, -15.141%] | 0.80 |
| false_alarm | C_asavailable_trained vs A_blind | -3.533% | [-4.982%, -2.085%] | 0.60 |
| false_alarm | B_clean_trained vs A_blind | +15.623% | [+13.066%, +18.303%] | 0.30 |
| imperfect | C_asavailable_trained vs B_clean_trained | -4.764% | [-6.040%, -3.458%] | 0.61 |
| imperfect | C_asavailable_trained vs A_blind | -3.460% | [-4.841%, -2.162%] | 0.58 |
| imperfect | B_clean_trained vs A_blind | +1.370% | [-0.292%, +3.101%] | 0.50 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| clean | 0 | +0.0% | -31.7% |
| clean | 1 | +0.0% | -31.5% |
| clean | 2 | +0.0% | -30.9% |
| clean | 3 | +0.0% | -36.8% |
| clean | 4 | +0.0% | -25.0% |
| clean | 5 | +0.0% | -41.6% |
| clean | 6 | +0.0% | -40.6% |
| clean | 7 | +0.0% | -42.4% |
| clean | 8 | +0.0% | -38.9% |
| clean | 9 | +0.0% | -38.9% |
| clean | 10 | +0.0% | -30.6% |
| clean | 11 | +0.0% | -41.3% |
| clean | 12 | +0.0% | -27.5% |
| clean | 13 | +0.0% | -38.1% |
| clean | 14 | +0.0% | -35.1% |
| clean | 15 | +0.0% | -42.7% |
| clean | 16 | +0.0% | -35.3% |
| clean | 17 | +0.0% | -37.0% |
| clean | 18 | +0.0% | -35.6% |
| clean | 19 | +0.0% | -42.9% |
| false_alarm | 0 | -20.5% | +2.1% |
| false_alarm | 1 | -25.1% | +6.4% |
| false_alarm | 2 | -8.9% | +0.9% |
| false_alarm | 3 | -11.7% | -7.0% |
| false_alarm | 4 | -16.1% | +29.6% |
| false_alarm | 5 | -11.4% | -0.9% |
| false_alarm | 6 | -20.0% | -3.1% |
| false_alarm | 7 | -8.0% | -7.0% |
| false_alarm | 8 | -11.5% | -11.9% |
| false_alarm | 9 | -20.0% | -7.3% |
| false_alarm | 10 | -30.4% | -11.3% |
| false_alarm | 11 | -17.6% | -10.8% |
| false_alarm | 12 | -7.9% | -2.7% |
| false_alarm | 13 | -10.8% | -7.2% |
| false_alarm | 14 | -18.5% | +20.4% |
| false_alarm | 15 | -12.6% | -11.4% |
| false_alarm | 16 | -35.2% | -4.1% |
| false_alarm | 17 | -14.6% | -23.3% |
| false_alarm | 18 | -12.6% | -1.2% |
| false_alarm | 19 | -9.4% | -7.1% |
| imperfect | 0 | -4.5% | -4.6% |
| imperfect | 1 | -4.1% | -3.3% |
| imperfect | 2 | -5.4% | -9.4% |
| imperfect | 3 | -17.1% | +7.2% |
| imperfect | 4 | +0.6% | -9.7% |
| imperfect | 5 | -11.9% | -12.0% |
| imperfect | 6 | -15.7% | -25.6% |
| imperfect | 7 | -1.4% | -7.9% |
| imperfect | 8 | +15.4% | -12.5% |
| imperfect | 9 | -5.1% | -5.6% |
| imperfect | 10 | -7.9% | -7.3% |
| imperfect | 11 | -5.5% | +7.4% |
| imperfect | 12 | -10.8% | -4.1% |
| imperfect | 13 | +2.3% | -2.4% |
| imperfect | 14 | -2.8% | +7.5% |
| imperfect | 15 | +0.1% | -0.9% |
| imperfect | 16 | -9.6% | -5.8% |
| imperfect | 17 | +15.5% | +6.2% |
| imperfect | 18 | -1.2% | +9.5% |
| imperfect | 19 | -12.5% | -1.2% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 10.4, announcements 10.4
- false_alarm: true events 10.4, announcements 23.6
- imperfect: true events 10.4, announcements 13.8
