Seeds: [0] | SKUs: 6 | test days: 58 (first 7 excluded) | runtime 1s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 795 ± nan | 315 ± nan | 127 ± nan | 354 ± nan | 315 ± nan | 211 ± nan | 0.932 ± nan | 0.276 ± nan | 0.149 ± nan | 0.800 ± nan |
| clean | B_clean_trained | 630 ± nan | 438 ± nan | 5 ± nan | 186 ± nan | 438 ± nan | 9 ± nan | 0.906 ± nan | 0.231 ± nan | 0.098 ± nan | 0.800 ± nan |
| clean | C_asavailable_trained | 630 ± nan | 438 ± nan | 5 ± nan | 186 ± nan | 438 ± nan | 9 ± nan | 0.906 ± nan | 0.231 ± nan | 0.098 ± nan | 0.800 ± nan |
| false_alarm | A_blind | 795 ± nan | 315 ± nan | 127 ± nan | 354 ± nan | 315 ± nan | 211 ± nan | 0.932 ± nan | 0.276 ± nan | 0.149 ± nan | 0.800 ± nan |
| false_alarm | B_clean_trained | 1280 ± nan | 258 ± nan | 601 ± nan | 421 ± nan | 258 ± nan | 1002 ± nan | 0.944 ± nan | 0.398 ± nan | 0.139 ± nan | 0.800 ± nan |
| false_alarm | C_asavailable_trained | 888 ± nan | 345 ± nan | 242 ± nan | 301 ± nan | 345 ± nan | 404 ± nan | 0.926 ± nan | 0.268 ± nan | 0.122 ± nan | 0.800 ± nan |
| imperfect | A_blind | 795 ± nan | 315 ± nan | 127 ± nan | 354 ± nan | 315 ± nan | 211 ± nan | 0.932 ± nan | 0.276 ± nan | 0.149 ± nan | 0.800 ± nan |
| imperfect | B_clean_trained | 675 ± nan | 403 ± nan | 62 ± nan | 210 ± nan | 403 ± nan | 103 ± nan | 0.913 ± nan | 0.252 ± nan | 0.101 ± nan | 0.800 ± nan |
| imperfect | C_asavailable_trained | 728 ± nan | 341 ± nan | 91 ± nan | 296 ± nan | 341 ± nan | 151 ± nan | 0.926 ± nan | 0.269 ± nan | 0.132 ± nan | 0.800 ± nan |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | -20.821% | [-38.762%, +0.065%] | 0.67 |
| clean | B_clean_trained vs A_blind | -20.821% | [-38.765%, +0.425%] | 0.67 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -30.591% | [-34.069%, -26.865%] | 1.00 |
| false_alarm | C_asavailable_trained vs A_blind | +11.722% | [-11.074%, +30.046%] | 0.33 |
| false_alarm | B_clean_trained vs A_blind | +60.961% | [+30.199%, +87.207%] | 0.00 |
| imperfect | C_asavailable_trained vs B_clean_trained | +7.768% | [-4.193%, +25.966%] | 0.50 |
| imperfect | C_asavailable_trained vs A_blind | -8.483% | [-22.462%, +1.926%] | 0.83 |
| imperfect | B_clean_trained vs A_blind | -15.080% | [-32.798%, +2.991%] | 0.83 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| clean | 0 | +0.0% | -20.8% |
| false_alarm | 0 | -30.6% | +11.7% |
| imperfect | 0 | +7.8% | -8.5% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 4.0, announcements 4.0
- false_alarm: true events 4.0, announcements 8.0
- imperfect: true events 4.0, announcements 6.0
