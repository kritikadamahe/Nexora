Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] | SKUs: 100 | test days: 166 (first 7 excluded) | runtime 1301s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 127203 ± 720 | 38006 ± 601 | 9052 ± 255 | 80144 ± 506 | 38006 ± 601 | 15087 ± 425 | 0.982 ± 0.000 | 0.146 ± 0.000 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| clean | B_clean_trained | 127909 ± 669 | 39679 ± 576 | 8936 ± 182 | 79294 ± 478 | 39679 ± 576 | 14894 ± 304 | 0.981 ± 0.000 | 0.146 ± 0.000 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| clean | C_asavailable_trained | 127909 ± 669 | 39679 ± 576 | 8936 ± 182 | 79294 ± 478 | 39679 ± 576 | 14894 ± 304 | 0.981 ± 0.000 | 0.146 ± 0.000 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| false_alarm | A_blind | 127203 ± 720 | 38006 ± 601 | 9052 ± 255 | 80144 ± 506 | 38006 ± 601 | 15087 ± 425 | 0.982 ± 0.000 | 0.146 ± 0.000 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| false_alarm | B_clean_trained | 128203 ± 981 | 39775 ± 763 | 8976 ± 197 | 79452 ± 844 | 39775 ± 763 | 14960 ± 328 | 0.981 ± 0.000 | 0.146 ± 0.000 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| false_alarm | C_asavailable_trained | 128042 ± 1309 | 40506 ± 1479 | 8833 ± 292 | 78703 ± 1061 | 40506 ± 1479 | 14721 ± 486 | 0.980 ± 0.001 | 0.145 ± 0.001 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| imperfect | A_blind | 127203 ± 720 | 38006 ± 601 | 9052 ± 255 | 80144 ± 506 | 38006 ± 601 | 15087 ± 425 | 0.982 ± 0.000 | 0.146 ± 0.000 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| imperfect | B_clean_trained | 128359 ± 1089 | 40381 ± 1075 | 8962 ± 187 | 79017 ± 794 | 40381 ± 1075 | 14936 ± 311 | 0.980 ± 0.001 | 0.145 ± 0.001 | 0.036 ± 0.000 | 0.900 ± 0.000 |
| imperfect | C_asavailable_trained | 127467 ± 1145 | 39182 ± 1191 | 8924 ± 323 | 79360 ± 640 | 39182 ± 1191 | 14874 ± 538 | 0.981 ± 0.001 | 0.146 ± 0.001 | 0.036 ± 0.000 | 0.900 ± 0.000 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | +0.556% | [+0.337%, +0.801%] | 0.46 |
| clean | B_clean_trained vs A_blind | +0.556% | [+0.327%, +0.791%] | 0.46 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -0.126% | [-0.319%, +0.065%] | 0.51 |
| false_alarm | C_asavailable_trained vs A_blind | +0.660% | [+0.418%, +0.901%] | 0.45 |
| false_alarm | B_clean_trained vs A_blind | +0.786% | [+0.559%, +1.018%] | 0.45 |
| imperfect | C_asavailable_trained vs B_clean_trained | -0.695% | [-0.924%, -0.470%] | 0.53 |
| imperfect | C_asavailable_trained vs A_blind | +0.208% | [-0.003%, +0.411%] | 0.47 |
| imperfect | B_clean_trained vs A_blind | +0.909% | [+0.688%, +1.140%] | 0.44 |

Per-seed relative test cost (cluster-level check; seeds share the same real demand and differ only in signal errors and model fits; use esi.clustered_ci --cluster item for inference):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| clean | 0 | +0.0% | +0.9% |
| clean | 1 | +0.0% | -0.6% |
| clean | 2 | +0.0% | +0.3% |
| clean | 3 | +0.0% | +0.3% |
| clean | 4 | +0.0% | +2.6% |
| clean | 5 | +0.0% | +0.2% |
| clean | 6 | +0.0% | +0.8% |
| clean | 7 | +0.0% | +1.0% |
| clean | 8 | +0.0% | -0.4% |
| clean | 9 | +0.0% | +0.6% |
| clean | 10 | +0.0% | +1.3% |
| clean | 11 | +0.0% | +0.2% |
| clean | 12 | +0.0% | -0.1% |
| clean | 13 | +0.0% | +0.4% |
| clean | 14 | +0.0% | +0.6% |
| clean | 15 | +0.0% | +0.2% |
| clean | 16 | +0.0% | +1.1% |
| clean | 17 | +0.0% | +0.7% |
| clean | 18 | +0.0% | +0.5% |
| clean | 19 | +0.0% | +0.9% |
| false_alarm | 0 | -0.9% | +0.3% |
| false_alarm | 1 | +0.6% | +1.6% |
| false_alarm | 2 | +0.0% | +0.1% |
| false_alarm | 3 | -0.2% | -0.0% |
| false_alarm | 4 | -0.5% | +1.9% |
| false_alarm | 5 | +2.2% | +2.3% |
| false_alarm | 6 | +0.5% | +1.6% |
| false_alarm | 7 | -0.6% | +0.7% |
| false_alarm | 8 | -0.5% | -0.1% |
| false_alarm | 9 | +1.1% | +1.9% |
| false_alarm | 10 | -0.0% | +1.3% |
| false_alarm | 11 | -0.3% | -0.1% |
| false_alarm | 12 | +1.4% | +0.1% |
| false_alarm | 13 | -1.1% | -0.0% |
| false_alarm | 14 | -1.2% | -0.1% |
| false_alarm | 15 | -1.5% | -1.4% |
| false_alarm | 16 | -0.9% | +0.8% |
| false_alarm | 17 | +0.2% | +1.2% |
| false_alarm | 18 | -0.4% | +0.4% |
| false_alarm | 19 | -0.4% | +0.7% |
| imperfect | 0 | -1.0% | -0.0% |
| imperfect | 1 | -0.7% | -0.8% |
| imperfect | 2 | -0.3% | +0.5% |
| imperfect | 3 | -1.1% | +0.4% |
| imperfect | 4 | -0.9% | +2.3% |
| imperfect | 5 | +0.1% | +0.8% |
| imperfect | 6 | -0.7% | -0.1% |
| imperfect | 7 | -1.1% | +0.5% |
| imperfect | 8 | -1.6% | -1.4% |
| imperfect | 9 | +0.3% | +0.6% |
| imperfect | 10 | -0.9% | +0.9% |
| imperfect | 11 | +2.7% | +2.6% |
| imperfect | 12 | +0.7% | +0.6% |
| imperfect | 13 | -0.5% | +0.3% |
| imperfect | 14 | -2.3% | -1.0% |
| imperfect | 15 | -1.0% | -0.1% |
| imperfect | 16 | -2.0% | -0.2% |
| imperfect | 17 | -1.3% | -0.8% |
| imperfect | 18 | -0.3% | -0.3% |
| imperfect | 19 | -1.8% | -0.6% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 6.0, announcements 6.0
- false_alarm: true events 6.0, announcements 21.1
- imperfect: true events 6.0, announcements 10.1
