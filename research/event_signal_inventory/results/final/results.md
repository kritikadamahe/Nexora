Seeds: [0, 1, 2, 3, 4] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 296s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 16273 ± 3110 | 10592 ± 2608 | 710 ± 150 | 4971 ± 394 | 10592 ± 2608 | 1183 ± 250 | 0.898 ± 0.013 | 0.276 ± 0.014 | 0.126 ± 0.009 | 0.800 ± 0.000 |
| clean | B_clean_trained | 11116 ± 1501 | 4658 ± 685 | 1162 ± 369 | 5296 ± 515 | 4658 ± 685 | 1936 ± 614 | 0.955 ± 0.003 | 0.226 ± 0.003 | 0.059 ± 0.001 | 0.900 ± 0.000 |
| clean | C_asavailable_trained | 11116 ± 1501 | 4658 ± 685 | 1162 ± 369 | 5296 ± 515 | 4658 ± 685 | 1936 ± 614 | 0.955 ± 0.003 | 0.226 ± 0.003 | 0.059 ± 0.001 | 0.900 ± 0.000 |
| false_alarm | A_blind | 16273 ± 3110 | 10592 ± 2608 | 710 ± 150 | 4971 ± 394 | 10592 ± 2608 | 1183 ± 250 | 0.898 ± 0.013 | 0.276 ± 0.014 | 0.126 ± 0.009 | 0.800 ± 0.000 |
| false_alarm | B_clean_trained | 20519 ± 2541 | 6401 ± 769 | 6885 ± 1555 | 7234 ± 1336 | 6401 ± 769 | 11475 ± 2592 | 0.937 ± 0.013 | 0.357 ± 0.029 | 0.117 ± 0.024 | 0.820 ± 0.045 |
| false_alarm | C_asavailable_trained | 17099 ± 2240 | 7907 ± 2152 | 3400 ± 1248 | 5792 ± 674 | 7907 ± 2152 | 5666 ± 2080 | 0.924 ± 0.014 | 0.269 ± 0.016 | 0.106 ± 0.017 | 0.820 ± 0.045 |
| imperfect | A_blind | 16273 ± 3110 | 10592 ± 2608 | 710 ± 150 | 4971 ± 394 | 10592 ± 2608 | 1183 ± 250 | 0.898 ± 0.013 | 0.276 ± 0.014 | 0.126 ± 0.009 | 0.800 ± 0.000 |
| imperfect | B_clean_trained | 17153 ± 6233 | 7499 ± 3766 | 3603 ± 2194 | 6050 ± 1340 | 7499 ± 3766 | 6005 ± 3656 | 0.929 ± 0.029 | 0.285 ± 0.029 | 0.088 ± 0.022 | 0.880 ± 0.045 |
| imperfect | C_asavailable_trained | 15786 ± 4285 | 8921 ± 4238 | 1582 ± 735 | 5282 ± 880 | 8921 ± 4238 | 2637 ± 1225 | 0.915 ± 0.029 | 0.267 ± 0.018 | 0.108 ± 0.018 | 0.820 ± 0.045 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | -31.687% | [-33.966%, -29.418%] | 0.92 |
| clean | B_clean_trained vs A_blind | -31.687% | [-34.139%, -29.240%] | 0.92 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -16.667% | [-19.659%, -13.381%] | 0.78 |
| false_alarm | C_asavailable_trained vs A_blind | +5.081% | [+1.905%, +8.893%] | 0.43 |
| false_alarm | B_clean_trained vs A_blind | +26.097% | [+18.864%, +33.523%] | 0.23 |
| imperfect | C_asavailable_trained vs B_clean_trained | -7.971% | [-11.191%, -4.999%] | 0.64 |
| imperfect | C_asavailable_trained vs A_blind | -2.993% | [-5.384%, -0.485%] | 0.62 |
| imperfect | B_clean_trained vs A_blind | +5.410% | [+1.162%, +9.969%] | 0.52 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| clean | 0 | +0.0% | -31.7% |
| clean | 1 | +0.0% | -31.5% |
| clean | 2 | +0.0% | -30.9% |
| clean | 3 | +0.0% | -36.8% |
| clean | 4 | +0.0% | -25.0% |
| false_alarm | 0 | -20.5% | +2.1% |
| false_alarm | 1 | -25.1% | +6.4% |
| false_alarm | 2 | -8.9% | +0.9% |
| false_alarm | 3 | -11.7% | -7.0% |
| false_alarm | 4 | -16.1% | +29.6% |
| imperfect | 0 | -4.5% | -4.6% |
| imperfect | 1 | -4.1% | -3.3% |
| imperfect | 2 | -5.4% | -9.4% |
| imperfect | 3 | -17.1% | +7.2% |
| imperfect | 4 | +0.6% | -9.7% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 10.0, announcements 10.0
- false_alarm: true events 10.0, announcements 26.4
- imperfect: true events 10.0, announcements 13.2
