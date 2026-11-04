Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] | SKUs: 99 | test days: 177 (first 7 excluded) | runtime 1588s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 25747 ± 611 | 11228 ± 3465 | 4293 ± 1042 | 10226 ± 1816 | 11228 ± 3465 | 7156 ± 1736 | 0.946 ± 0.017 | 0.246 ± 0.000 | 0.077 ± 0.016 | 0.850 ± 0.051 |
| clean | B_clean_trained | 24370 ± 71 | 7965 ± 82 | 4919 ± 33 | 11486 ± 40 | 7965 ± 82 | 8199 ± 55 | 0.962 ± 0.000 | 0.235 ± 0.000 | 0.060 ± 0.000 | 0.900 ± 0.000 |
| clean | C_asavailable_trained | 24370 ± 71 | 7965 ± 82 | 4919 ± 33 | 11486 ± 40 | 7965 ± 82 | 8199 ± 55 | 0.962 ± 0.000 | 0.235 ± 0.000 | 0.060 ± 0.000 | 0.900 ± 0.000 |
| clean | D_noise_injected | 24370 ± 71 | 7965 ± 82 | 4919 ± 33 | 11486 ± 40 | 7965 ± 82 | 8199 ± 55 | 0.962 ± 0.000 | 0.235 ± 0.000 | 0.060 ± 0.000 | 0.900 ± 0.000 |
| false_alarm | A_blind | 25747 ± 611 | 11228 ± 3465 | 4293 ± 1042 | 10226 ± 1816 | 11228 ± 3465 | 7156 ± 1736 | 0.946 ± 0.017 | 0.246 ± 0.000 | 0.077 ± 0.016 | 0.850 ± 0.051 |
| false_alarm | B_clean_trained | 25438 ± 637 | 10745 ± 3093 | 4378 ± 956 | 10315 ± 1639 | 10745 ± 3093 | 7297 ± 1594 | 0.949 ± 0.015 | 0.239 ± 0.003 | 0.074 ± 0.015 | 0.855 ± 0.051 |
| false_alarm | C_asavailable_trained | 24997 ± 444 | 9265 ± 2438 | 4721 ± 767 | 11011 ± 1338 | 9265 ± 2438 | 7869 ± 1279 | 0.956 ± 0.012 | 0.239 ± 0.002 | 0.067 ± 0.012 | 0.880 ± 0.041 |
| false_alarm | D_noise_injected | 25096 ± 590 | 9933 ± 2902 | 4506 ± 861 | 10658 ± 1520 | 9933 ± 2902 | 7509 ± 1435 | 0.953 ± 0.014 | 0.239 ± 0.002 | 0.070 ± 0.014 | 0.870 ± 0.047 |
| imperfect | A_blind | 25747 ± 611 | 11228 ± 3465 | 4293 ± 1042 | 10226 ± 1816 | 11228 ± 3465 | 7156 ± 1736 | 0.946 ± 0.017 | 0.246 ± 0.000 | 0.077 ± 0.016 | 0.850 ± 0.051 |
| imperfect | B_clean_trained | 25757 ± 281 | 10213 ± 464 | 4722 ± 163 | 10822 ± 201 | 10213 ± 464 | 7870 ± 272 | 0.951 ± 0.002 | 0.246 ± 0.002 | 0.064 ± 0.001 | 0.900 ± 0.000 |
| imperfect | C_asavailable_trained | 25577 ± 693 | 10435 ± 3218 | 4507 ± 921 | 10636 ± 1647 | 10435 ± 3218 | 7511 ± 1535 | 0.950 ± 0.015 | 0.243 ± 0.001 | 0.072 ± 0.015 | 0.865 ± 0.049 |
| imperfect | D_noise_injected | 25433 ± 578 | 9781 ± 2870 | 4712 ± 840 | 10941 ± 1468 | 9781 ± 2870 | 7852 ± 1401 | 0.953 ± 0.014 | 0.243 ± 0.002 | 0.069 ± 0.014 | 0.875 ± 0.044 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | -5.347% | [-5.951%, -4.761%] | 0.59 |
| clean | B_clean_trained vs A_blind | -5.347% | [-5.974%, -4.732%] | 0.59 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -1.731% | [-2.036%, -1.438%] | 0.60 |
| false_alarm | C_asavailable_trained vs A_blind | -2.911% | [-3.331%, -2.471%] | 0.57 |
| false_alarm | B_clean_trained vs A_blind | -1.201% | [-1.709%, -0.668%] | 0.49 |
| imperfect | C_asavailable_trained vs B_clean_trained | -0.697% | [-1.094%, -0.306%] | 0.54 |
| imperfect | C_asavailable_trained vs A_blind | -0.659% | [-1.058%, -0.261%] | 0.51 |
| imperfect | B_clean_trained vs A_blind | +0.038% | [-0.409%, +0.503%] | 0.49 |
| clean | D_noise_injected vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | D_noise_injected vs A_blind | -5.347% | [-5.949%, -4.747%] | 0.59 |
| clean | D_noise_injected vs C_asavailable_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| false_alarm | D_noise_injected vs B_clean_trained | -1.343% | [-1.679%, -1.019%] | 0.59 |
| false_alarm | D_noise_injected vs A_blind | -2.528% | [-3.052%, -2.035%] | 0.55 |
| false_alarm | D_noise_injected vs C_asavailable_trained | +0.395% | [+0.073%, +0.727%] | 0.48 |
| imperfect | D_noise_injected vs B_clean_trained | -1.257% | [-1.611%, -0.904%] | 0.55 |
| imperfect | D_noise_injected vs A_blind | -1.219% | [-1.604%, -0.815%] | 0.54 |
| imperfect | D_noise_injected vs C_asavailable_trained | -0.564% | [-0.866%, -0.269%] | 0.53 |

Per-seed relative test cost (cluster-level check; seeds share the same real demand and differ only in signal errors and model fits; use esi.clustered_ci --cluster item for inference):

| condition | seed | C vs B | C vs A | D vs B | D vs C |
|---|---|---|---|---|---|
| clean | 0 | +0.0% | -3.7% | +0.0% | +0.0% |
| clean | 1 | +0.0% | -3.0% | +0.0% | +0.0% |
| clean | 2 | +0.0% | -7.4% | +0.0% | +0.0% |
| clean | 3 | +0.0% | -7.2% | +0.0% | +0.0% |
| clean | 4 | +0.0% | -3.1% | +0.0% | +0.0% |
| clean | 5 | +0.0% | -7.8% | +0.0% | +0.0% |
| clean | 6 | +0.0% | -7.6% | +0.0% | +0.0% |
| clean | 7 | +0.0% | -3.2% | +0.0% | +0.0% |
| clean | 8 | +0.0% | -3.0% | +0.0% | +0.0% |
| clean | 9 | +0.0% | -7.1% | +0.0% | +0.0% |
| clean | 10 | +0.0% | -2.9% | +0.0% | +0.0% |
| clean | 11 | +0.0% | -7.3% | +0.0% | +0.0% |
| clean | 12 | +0.0% | -3.4% | +0.0% | +0.0% |
| clean | 13 | +0.0% | -2.8% | +0.0% | +0.0% |
| clean | 14 | +0.0% | -8.4% | +0.0% | +0.0% |
| clean | 15 | +0.0% | -7.3% | +0.0% | +0.0% |
| clean | 16 | +0.0% | -7.7% | +0.0% | +0.0% |
| clean | 17 | +0.0% | -3.3% | +0.0% | +0.0% |
| clean | 18 | +0.0% | -7.2% | +0.0% | +0.0% |
| clean | 19 | +0.0% | -2.6% | +0.0% | +0.0% |
| false_alarm | 0 | -0.5% | -3.4% | +0.1% | +0.6% |
| false_alarm | 1 | -1.0% | -1.5% | +3.8% | +4.8% |
| false_alarm | 2 | +0.1% | -5.6% | -0.7% | -0.7% |
| false_alarm | 3 | -5.2% | -7.3% | -4.5% | +0.8% |
| false_alarm | 4 | -0.3% | -2.0% | -0.3% | -0.0% |
| false_alarm | 5 | -0.5% | -6.4% | -0.7% | -0.2% |
| false_alarm | 6 | +0.7% | -2.1% | -4.1% | -4.8% |
| false_alarm | 7 | -5.4% | -1.2% | -0.4% | +5.3% |
| false_alarm | 8 | -3.9% | -0.9% | -0.3% | +3.8% |
| false_alarm | 9 | -0.5% | -1.9% | -4.5% | -4.0% |
| false_alarm | 10 | -0.3% | -0.6% | -1.5% | -1.2% |
| false_alarm | 11 | -4.6% | -4.9% | -4.8% | -0.2% |
| false_alarm | 12 | -0.5% | -1.5% | +0.4% | +0.9% |
| false_alarm | 13 | -1.1% | -1.6% | -1.3% | -0.2% |
| false_alarm | 14 | -0.9% | -2.0% | -1.3% | -0.4% |
| false_alarm | 15 | -6.0% | -4.9% | -1.9% | +4.3% |
| false_alarm | 16 | +0.0% | -5.2% | -0.7% | -0.7% |
| false_alarm | 17 | -1.8% | +1.5% | -2.1% | -0.3% |
| false_alarm | 18 | -0.3% | -4.9% | +0.4% | +0.7% |
| false_alarm | 19 | -1.8% | -1.2% | -1.9% | -0.1% |
| imperfect | 0 | -4.1% | -0.2% | -3.2% | +1.0% |
| imperfect | 1 | -1.7% | -0.6% | -1.9% | -0.2% |
| imperfect | 2 | +1.5% | +0.3% | +2.6% | +1.1% |
| imperfect | 3 | -3.1% | -5.0% | -2.5% | +0.5% |
| imperfect | 4 | -2.9% | -0.6% | -3.1% | -0.2% |
| imperfect | 5 | +2.8% | -0.1% | -1.8% | -4.5% |
| imperfect | 6 | +1.9% | +1.5% | +0.7% | -1.2% |
| imperfect | 7 | -2.8% | -0.6% | -2.9% | -0.1% |
| imperfect | 8 | +4.2% | +7.1% | -2.6% | -6.5% |
| imperfect | 9 | -1.3% | -3.6% | -2.0% | -0.7% |
| imperfect | 10 | +2.0% | +5.4% | +0.4% | -1.5% |
| imperfect | 11 | -2.5% | -4.1% | -2.7% | -0.1% |
| imperfect | 12 | -0.8% | +0.2% | +3.3% | +4.1% |
| imperfect | 13 | -2.4% | +0.3% | -1.9% | +0.5% |
| imperfect | 14 | -2.3% | -5.2% | +2.6% | +5.0% |
| imperfect | 15 | -2.8% | -4.8% | -2.9% | -0.1% |
| imperfect | 16 | -0.9% | -3.0% | -2.6% | -1.7% |
| imperfect | 17 | +3.2% | +3.0% | -0.5% | -3.6% |
| imperfect | 18 | +1.1% | -0.7% | -2.4% | -3.5% |
| imperfect | 19 | -3.0% | -1.7% | -1.9% | +1.2% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 42.0, announcements 42.0
- false_alarm: true events 42.0, announcements 51.5
- imperfect: true events 42.0, announcements 35.9
