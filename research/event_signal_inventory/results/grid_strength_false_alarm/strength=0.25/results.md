Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 231s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spurious_rate=0 | A_blind | 9428 ± 1177 | 3593 ± 568 | 630 ± 103 | 5205 ± 616 | 3593 ± 568 | 1050 ± 172 | 0.960 ± 0.003 | 0.229 ± 0.004 | 0.060 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0 | B_clean_trained | 8856 ± 1143 | 3520 ± 714 | 517 ± 68 | 4819 ± 508 | 3520 ± 714 | 861 ± 113 | 0.961 ± 0.004 | 0.221 ± 0.002 | 0.056 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0 | C_asavailable_trained | 8878 ± 1130 | 3450 ± 671 | 537 ± 67 | 4891 ± 541 | 3450 ± 671 | 896 ± 112 | 0.962 ± 0.004 | 0.221 ± 0.002 | 0.056 ± 0.001 | 0.900 ± 0.000 |
| spurious_rate=0.04 | A_blind | 9428 ± 1177 | 3593 ± 568 | 630 ± 103 | 5205 ± 616 | 3593 ± 568 | 1050 ± 172 | 0.960 ± 0.003 | 0.229 ± 0.004 | 0.060 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.04 | B_clean_trained | 9098 ± 1213 | 3379 ± 737 | 698 ± 172 | 5022 ± 532 | 3379 ± 737 | 1163 ± 286 | 0.963 ± 0.004 | 0.227 ± 0.006 | 0.057 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.04 | C_asavailable_trained | 9068 ± 1208 | 3522 ± 736 | 600 ± 102 | 4946 ± 520 | 3522 ± 736 | 1000 ± 169 | 0.961 ± 0.004 | 0.224 ± 0.003 | 0.057 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.08 | A_blind | 9428 ± 1177 | 3593 ± 568 | 630 ± 103 | 5205 ± 616 | 3593 ± 568 | 1050 ± 172 | 0.960 ± 0.003 | 0.229 ± 0.004 | 0.060 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.08 | B_clean_trained | 9382 ± 1245 | 3314 ± 667 | 859 ± 230 | 5209 ± 584 | 3314 ± 667 | 1432 ± 384 | 0.964 ± 0.004 | 0.233 ± 0.006 | 0.058 ± 0.001 | 0.900 ± 0.000 |
| spurious_rate=0.08 | C_asavailable_trained | 9147 ± 1106 | 3492 ± 480 | 625 ± 142 | 5030 ± 628 | 3492 ± 480 | 1042 ± 237 | 0.961 ± 0.003 | 0.226 ± 0.004 | 0.058 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.16 | A_blind | 9428 ± 1177 | 3593 ± 568 | 630 ± 103 | 5205 ± 616 | 3593 ± 568 | 1050 ± 172 | 0.960 ± 0.003 | 0.229 ± 0.004 | 0.060 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.16 | B_clean_trained | 9748 ± 1304 | 3210 ± 693 | 1110 ± 315 | 5428 ± 580 | 3210 ± 693 | 1850 ± 525 | 0.965 ± 0.004 | 0.242 ± 0.012 | 0.059 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.16 | C_asavailable_trained | 9191 ± 1130 | 3594 ± 639 | 600 ± 98 | 4997 ± 548 | 3594 ± 639 | 1000 ± 164 | 0.960 ± 0.004 | 0.227 ± 0.004 | 0.058 ± 0.002 | 0.900 ± 0.000 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| spurious_rate=0 | C_asavailable_trained vs B_clean_trained | +0.249% | [-0.162%, +0.692%] | 0.45 |
| spurious_rate=0 | C_asavailable_trained vs A_blind | -5.839% | [-7.076%, -4.686%] | 0.69 |
| spurious_rate=0 | B_clean_trained vs A_blind | -6.073% | [-7.241%, -4.917%] | 0.71 |
| spurious_rate=0.04 | C_asavailable_trained vs B_clean_trained | -0.333% | [-0.841%, +0.168%] | 0.49 |
| spurious_rate=0.04 | C_asavailable_trained vs A_blind | -3.820% | [-4.925%, -2.621%] | 0.64 |
| spurious_rate=0.04 | B_clean_trained vs A_blind | -3.498% | [-4.670%, -2.212%] | 0.60 |
| spurious_rate=0.08 | C_asavailable_trained vs B_clean_trained | -2.512% | [-3.502%, -1.485%] | 0.58 |
| spurious_rate=0.08 | C_asavailable_trained vs A_blind | -2.984% | [-3.835%, -2.090%] | 0.60 |
| spurious_rate=0.08 | B_clean_trained vs A_blind | -0.484% | [-1.712%, +0.720%] | 0.49 |
| spurious_rate=0.16 | C_asavailable_trained vs B_clean_trained | -5.720% | [-7.029%, -4.460%] | 0.68 |
| spurious_rate=0.16 | C_asavailable_trained vs A_blind | -2.516% | [-3.398%, -1.592%] | 0.63 |
| spurious_rate=0.16 | B_clean_trained vs A_blind | +3.398% | [+1.798%, +4.911%] | 0.40 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| spurious_rate=0 | 0 | +0.4% | -5.6% |
| spurious_rate=0 | 1 | +0.2% | -5.5% |
| spurious_rate=0 | 2 | +0.7% | -4.4% |
| spurious_rate=0 | 3 | -0.6% | -3.6% |
| spurious_rate=0 | 4 | +1.2% | -1.6% |
| spurious_rate=0 | 5 | +0.2% | -8.3% |
| spurious_rate=0 | 6 | +1.3% | -8.7% |
| spurious_rate=0 | 7 | +0.3% | -5.7% |
| spurious_rate=0 | 8 | -0.4% | -4.8% |
| spurious_rate=0 | 9 | -0.5% | -10.1% |
| spurious_rate=0.04 | 0 | -1.4% | -4.5% |
| spurious_rate=0.04 | 1 | +0.0% | -4.0% |
| spurious_rate=0.04 | 2 | -1.5% | -4.6% |
| spurious_rate=0.04 | 3 | -0.9% | -0.4% |
| spurious_rate=0.04 | 4 | +1.3% | -0.9% |
| spurious_rate=0.04 | 5 | -0.8% | -3.5% |
| spurious_rate=0.04 | 6 | -0.2% | -5.0% |
| spurious_rate=0.04 | 7 | -0.2% | -5.7% |
| spurious_rate=0.04 | 8 | +0.1% | -4.6% |
| spurious_rate=0.04 | 9 | +0.4% | -5.7% |
| spurious_rate=0.08 | 0 | -2.2% | -5.2% |
| spurious_rate=0.08 | 1 | -4.1% | -3.6% |
| spurious_rate=0.08 | 2 | -1.4% | -3.3% |
| spurious_rate=0.08 | 3 | -5.3% | -2.7% |
| spurious_rate=0.08 | 4 | -2.3% | +0.4% |
| spurious_rate=0.08 | 5 | -0.6% | -1.7% |
| spurious_rate=0.08 | 6 | -4.6% | -3.6% |
| spurious_rate=0.08 | 7 | -1.3% | -1.0% |
| spurious_rate=0.08 | 8 | -1.5% | -4.1% |
| spurious_rate=0.08 | 9 | -0.6% | -4.5% |
| spurious_rate=0.16 | 0 | -3.9% | -4.1% |
| spurious_rate=0.16 | 1 | -4.0% | -3.3% |
| spurious_rate=0.16 | 2 | -6.9% | -2.1% |
| spurious_rate=0.16 | 3 | -6.9% | -1.0% |
| spurious_rate=0.16 | 4 | -4.3% | +0.8% |
| spurious_rate=0.16 | 5 | -8.1% | -2.1% |
| spurious_rate=0.16 | 6 | -9.3% | -3.6% |
| spurious_rate=0.16 | 7 | -3.5% | -1.2% |
| spurious_rate=0.16 | 8 | -3.7% | -1.5% |
| spurious_rate=0.16 | 9 | -5.5% | -6.6% |

Mean event counts in the test period (announcements include spurious ones):

- spurious_rate=0: true events 10.1, announcements 9.5
- spurious_rate=0.04: true events 10.1, announcements 17.2
- spurious_rate=0.08: true events 10.1, announcements 25.0
- spurious_rate=0.16: true events 10.1, announcements 36.1
