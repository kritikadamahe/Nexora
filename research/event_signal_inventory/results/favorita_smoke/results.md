Seeds: [0, 1] | SKUs: 10 | test days: 166 (first 7 excluded) | runtime 35s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 24907 ± 0 | 8890 ± 0 | 1115 ± 0 | 14902 ± 0 | 8890 ± 0 | 1859 ± 0 | 0.980 ± 0.000 | 0.132 ± 0.000 | 0.032 ± 0.000 | 0.900 ± 0.000 |
| clean | B_clean_trained | 25212 ± 0 | 9645 ± 0 | 1082 ± 0 | 14484 ± 0 | 9645 ± 0 | 1804 ± 0 | 0.979 ± 0.000 | 0.131 ± 0.000 | 0.033 ± 0.000 | 0.900 ± 0.000 |
| clean | C_asavailable_trained | 25212 ± 0 | 9645 ± 0 | 1082 ± 0 | 14484 ± 0 | 9645 ± 0 | 1804 ± 0 | 0.979 ± 0.000 | 0.131 ± 0.000 | 0.033 ± 0.000 | 0.900 ± 0.000 |
| false_alarm | A_blind | 24907 ± 0 | 8890 ± 0 | 1115 ± 0 | 14902 ± 0 | 8890 ± 0 | 1859 ± 0 | 0.980 ± 0.000 | 0.132 ± 0.000 | 0.032 ± 0.000 | 0.900 ± 0.000 |
| false_alarm | B_clean_trained | 25582 ± 554 | 9732 ± 301 | 1078 ± 0 | 14771 ± 253 | 9732 ± 301 | 1797 ± 0 | 0.979 ± 0.001 | 0.132 ± 0.001 | 0.033 ± 0.001 | 0.900 ± 0.000 |
| false_alarm | C_asavailable_trained | 26029 ± 1385 | 10259 ± 1428 | 1004 ± 34 | 14766 ± 10 | 10259 ± 1428 | 1674 ± 56 | 0.977 ± 0.003 | 0.133 ± 0.000 | 0.034 ± 0.002 | 0.900 ± 0.000 |
| imperfect | A_blind | 24907 ± 0 | 8890 ± 0 | 1115 ± 0 | 14902 ± 0 | 8890 ± 0 | 1859 ± 0 | 0.980 ± 0.000 | 0.132 ± 0.000 | 0.032 ± 0.000 | 0.900 ± 0.000 |
| imperfect | B_clean_trained | 25480 ± 279 | 9834 ± 313 | 1098 ± 22 | 14548 ± 12 | 9834 ± 313 | 1830 ± 37 | 0.978 ± 0.001 | 0.132 ± 0.000 | 0.033 ± 0.000 | 0.900 ± 0.000 |
| imperfect | C_asavailable_trained | 25479 ± 409 | 9424 ± 537 | 1036 ± 124 | 15018 ± 3 | 9424 ± 537 | 1728 ± 207 | 0.979 ± 0.001 | 0.133 ± 0.002 | 0.033 ± 0.001 | 0.900 ± 0.000 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | +1.224% | [-0.394%, +2.687%] | 0.50 |
| clean | B_clean_trained vs A_blind | +1.224% | [-0.393%, +2.673%] | 0.50 |
| false_alarm | C_asavailable_trained vs B_clean_trained | +1.748% | [-0.717%, +4.380%] | 0.45 |
| false_alarm | C_asavailable_trained vs A_blind | +4.504% | [+1.051%, +8.418%] | 0.35 |
| false_alarm | B_clean_trained vs A_blind | +2.708% | [+1.065%, +4.193%] | 0.35 |
| imperfect | C_asavailable_trained vs B_clean_trained | -0.006% | [-1.571%, +1.566%] | 0.45 |
| imperfect | C_asavailable_trained vs A_blind | +2.296% | [+0.636%, +4.204%] | 0.35 |
| imperfect | B_clean_trained vs A_blind | +2.302% | [+0.597%, +3.727%] | 0.35 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| clean | 0 | +0.0% | +1.2% |
| clean | 1 | +0.0% | +1.2% |
| false_alarm | 0 | -0.6% | +0.6% |
| false_alarm | 1 | +4.0% | +8.4% |
| imperfect | 0 | -0.4% | +1.1% |
| imperfect | 1 | +0.4% | +3.5% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 6.0, announcements 6.0
- false_alarm: true events 6.0, announcements 24.5
- imperfect: true events 6.0, announcements 8.5
