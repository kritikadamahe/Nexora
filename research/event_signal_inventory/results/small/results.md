Seeds: [0, 1, 2, 3, 4] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 207s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 16588 ± 2997 | 9745 ± 3649 | 1229 ± 1040 | 5613 ± 1337 | 9745 ± 3649 | 2049 ± 1734 | 0.906 ± 0.027 | 0.276 ± 0.014 | 0.120 ± 0.018 | 0.820 ± 0.045 |
| clean | B_clean_trained | 11069 ± 1439 | 4603 ± 656 | 1169 ± 362 | 5296 ± 495 | 4603 ± 656 | 1949 ± 604 | 0.955 ± 0.003 | 0.227 ± 0.002 | 0.058 ± 0.001 | 0.900 ± 0.000 |
| clean | C_asavailable_trained | 11069 ± 1439 | 4603 ± 656 | 1169 ± 362 | 5296 ± 495 | 4603 ± 656 | 1949 ± 604 | 0.955 ± 0.003 | 0.227 ± 0.002 | 0.058 ± 0.001 | 0.900 ± 0.000 |
| false_alarm | A_blind | 16588 ± 2997 | 9745 ± 3649 | 1229 ± 1040 | 5613 ± 1337 | 9745 ± 3649 | 2049 ± 1734 | 0.906 ± 0.027 | 0.276 ± 0.014 | 0.120 ± 0.018 | 0.820 ± 0.045 |
| false_alarm | B_clean_trained | 20668 ± 2503 | 7121 ± 2081 | 6583 ± 1749 | 6965 ± 1519 | 7121 ± 2081 | 10972 ± 2915 | 0.929 ± 0.024 | 0.358 ± 0.029 | 0.125 ± 0.036 | 0.790 ± 0.089 |
| false_alarm | C_asavailable_trained | 17199 ± 2248 | 7097 ± 1177 | 3875 ± 1440 | 6227 ± 1207 | 7097 ± 1177 | 6459 ± 2400 | 0.930 ± 0.013 | 0.270 ± 0.015 | 0.099 ± 0.020 | 0.840 ± 0.055 |
| imperfect | A_blind | 16588 ± 2997 | 9745 ± 3649 | 1229 ± 1040 | 5613 ± 1337 | 9745 ± 3649 | 2049 ± 1734 | 0.906 ± 0.027 | 0.276 ± 0.014 | 0.120 ± 0.018 | 0.820 ± 0.045 |
| imperfect | B_clean_trained | 17200 ± 6232 | 7498 ± 3728 | 3648 ± 2221 | 6055 ± 1347 | 7498 ± 3728 | 6079 ± 3702 | 0.929 ± 0.029 | 0.285 ± 0.029 | 0.088 ± 0.022 | 0.880 ± 0.045 |
| imperfect | C_asavailable_trained | 15630 ± 4247 | 8821 ± 4164 | 1525 ± 715 | 5284 ± 916 | 8821 ± 4164 | 2542 ± 1192 | 0.916 ± 0.028 | 0.267 ± 0.018 | 0.107 ± 0.017 | 0.820 ± 0.045 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | -33.271% | [-35.843%, -30.573%] | 0.92 |
| clean | B_clean_trained vs A_blind | -33.271% | [-35.875%, -30.476%] | 0.92 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -16.786% | [-19.135%, -14.175%] | 0.80 |
| false_alarm | C_asavailable_trained vs A_blind | +3.684% | [-0.223%, +8.187%] | 0.41 |
| false_alarm | B_clean_trained vs A_blind | +24.599% | [+17.418%, +31.836%] | 0.24 |
| imperfect | C_asavailable_trained vs B_clean_trained | -9.128% | [-12.074%, -6.259%] | 0.64 |
| imperfect | C_asavailable_trained vs A_blind | -5.772% | [-8.398%, -3.208%] | 0.62 |
| imperfect | B_clean_trained vs A_blind | +3.693% | [-0.973%, +8.682%] | 0.56 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| clean | 0 | +0.0% | -31.8% |
| clean | 1 | +0.0% | -38.1% |
| clean | 2 | +0.0% | -31.2% |
| clean | 3 | +0.0% | -37.7% |
| clean | 4 | +0.0% | -24.8% |
| false_alarm | 0 | -20.8% | +2.5% |
| false_alarm | 1 | -26.0% | -2.3% |
| false_alarm | 2 | -9.4% | +1.0% |
| false_alarm | 3 | -11.8% | -7.0% |
| false_alarm | 4 | -15.0% | +30.7% |
| imperfect | 0 | -5.5% | -5.2% |
| imperfect | 1 | -4.6% | -12.6% |
| imperfect | 2 | -7.4% | -11.0% |
| imperfect | 3 | -18.1% | +6.0% |
| imperfect | 4 | -1.2% | -11.0% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 10.0, announcements 10.0
- false_alarm: true events 10.0, announcements 26.4
- imperfect: true events 10.0, announcements 13.2
