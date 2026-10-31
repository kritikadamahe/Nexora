Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 241s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spurious_rate=0 | A_blind | 10941 ± 1499 | 4350 ± 772 | 902 ± 242 | 5689 ± 653 | 4350 ± 772 | 1504 ± 404 | 0.953 ± 0.006 | 0.241 ± 0.010 | 0.068 ± 0.005 | 0.900 ± 0.000 |
| spurious_rate=0 | B_clean_trained | 9310 ± 1286 | 3804 ± 760 | 600 ± 136 | 4906 ± 542 | 3804 ± 760 | 1000 ± 226 | 0.959 ± 0.004 | 0.222 ± 0.005 | 0.056 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0 | C_asavailable_trained | 9395 ± 1342 | 3646 ± 730 | 667 ± 200 | 5082 ± 616 | 3646 ± 730 | 1112 ± 333 | 0.961 ± 0.004 | 0.223 ± 0.005 | 0.057 ± 0.002 | 0.900 ± 0.000 |
| spurious_rate=0.04 | A_blind | 10941 ± 1499 | 4350 ± 772 | 902 ± 242 | 5689 ± 653 | 4350 ± 772 | 1504 ± 404 | 0.953 ± 0.006 | 0.241 ± 0.010 | 0.068 ± 0.005 | 0.900 ± 0.000 |
| spurious_rate=0.04 | B_clean_trained | 10233 ± 1438 | 3490 ± 815 | 1300 ± 421 | 5443 ± 604 | 3490 ± 815 | 2166 ± 702 | 0.963 ± 0.005 | 0.237 ± 0.010 | 0.059 ± 0.003 | 0.900 ± 0.000 |
| spurious_rate=0.04 | C_asavailable_trained | 9924 ± 1418 | 3769 ± 877 | 904 ± 238 | 5251 ± 558 | 3769 ± 877 | 1506 ± 397 | 0.960 ± 0.005 | 0.231 ± 0.008 | 0.059 ± 0.003 | 0.900 ± 0.000 |
| spurious_rate=0.08 | A_blind | 10941 ± 1499 | 4350 ± 772 | 902 ± 242 | 5689 ± 653 | 4350 ± 772 | 1504 ± 404 | 0.953 ± 0.006 | 0.241 ± 0.010 | 0.068 ± 0.005 | 0.900 ± 0.000 |
| spurious_rate=0.08 | B_clean_trained | 11543 ± 1684 | 3878 ± 1164 | 1946 ± 843 | 5720 ± 972 | 3878 ± 1164 | 3243 ± 1405 | 0.958 ± 0.011 | 0.259 ± 0.015 | 0.070 ± 0.015 | 0.880 ± 0.042 |
| spurious_rate=0.08 | C_asavailable_trained | 10631 ± 1621 | 4006 ± 705 | 1165 ± 676 | 5460 ± 794 | 4006 ± 705 | 1942 ± 1126 | 0.957 ± 0.006 | 0.236 ± 0.010 | 0.063 ± 0.003 | 0.900 ± 0.000 |
| spurious_rate=0.16 | A_blind | 10941 ± 1499 | 4350 ± 772 | 902 ± 242 | 5689 ± 653 | 4350 ± 772 | 1504 ± 404 | 0.953 ± 0.006 | 0.241 ± 0.010 | 0.068 ± 0.005 | 0.900 ± 0.000 |
| spurious_rate=0.16 | B_clean_trained | 12255 ± 1413 | 5059 ± 759 | 1914 ± 582 | 5282 ± 765 | 5059 ± 759 | 3190 ± 970 | 0.945 ± 0.007 | 0.280 ± 0.019 | 0.099 ± 0.014 | 0.810 ± 0.032 |
| spurious_rate=0.16 | C_asavailable_trained | 10568 ± 1344 | 4400 ± 1043 | 921 ± 319 | 5247 ± 867 | 4400 ± 1043 | 1535 ± 531 | 0.952 ± 0.014 | 0.236 ± 0.008 | 0.067 ± 0.012 | 0.890 ± 0.032 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| spurious_rate=0 | C_asavailable_trained vs B_clean_trained | +0.922% | [+0.367%, +1.516%] | 0.43 |
| spurious_rate=0 | C_asavailable_trained vs A_blind | -14.127% | [-16.072%, -12.334%] | 0.80 |
| spurious_rate=0 | B_clean_trained vs A_blind | -14.912% | [-16.819%, -13.067%] | 0.81 |
| spurious_rate=0.04 | C_asavailable_trained vs B_clean_trained | -3.018% | [-3.986%, -2.097%] | 0.64 |
| spurious_rate=0.04 | C_asavailable_trained vs A_blind | -9.294% | [-11.021%, -7.684%] | 0.71 |
| spurious_rate=0.04 | B_clean_trained vs A_blind | -6.472% | [-8.195%, -4.875%] | 0.63 |
| spurious_rate=0.08 | C_asavailable_trained vs B_clean_trained | -7.904% | [-9.327%, -6.408%] | 0.70 |
| spurious_rate=0.08 | C_asavailable_trained vs A_blind | -2.834% | [-4.662%, -0.805%] | 0.61 |
| spurious_rate=0.08 | B_clean_trained vs A_blind | +5.505% | [+2.795%, +8.404%] | 0.42 |
| spurious_rate=0.16 | C_asavailable_trained vs B_clean_trained | -13.765% | [-15.694%, -11.644%] | 0.79 |
| spurious_rate=0.16 | C_asavailable_trained vs A_blind | -3.412% | [-4.849%, -1.966%] | 0.59 |
| spurious_rate=0.16 | B_clean_trained vs A_blind | +12.005% | [+9.515%, +14.645%] | 0.28 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| spurious_rate=0 | 0 | -0.3% | -15.2% |
| spurious_rate=0 | 1 | +1.9% | -13.3% |
| spurious_rate=0 | 2 | +0.6% | -12.5% |
| spurious_rate=0 | 3 | +0.2% | -12.4% |
| spurious_rate=0 | 4 | +0.1% | -7.7% |
| spurious_rate=0 | 5 | -0.3% | -17.1% |
| spurious_rate=0 | 6 | +4.7% | -17.0% |
| spurious_rate=0 | 7 | +1.0% | -20.0% |
| spurious_rate=0 | 8 | +1.2% | -11.9% |
| spurious_rate=0 | 9 | -0.3% | -14.6% |
| spurious_rate=0.04 | 0 | -2.4% | -6.3% |
| spurious_rate=0.04 | 1 | -2.2% | -11.5% |
| spurious_rate=0.04 | 2 | -0.1% | -7.0% |
| spurious_rate=0.04 | 3 | -0.5% | -5.8% |
| spurious_rate=0.04 | 4 | -3.4% | -6.2% |
| spurious_rate=0.04 | 5 | -5.9% | -6.8% |
| spurious_rate=0.04 | 6 | -5.5% | -13.1% |
| spurious_rate=0.04 | 7 | -3.0% | -16.3% |
| spurious_rate=0.04 | 8 | -2.9% | -8.8% |
| spurious_rate=0.04 | 9 | -4.4% | -11.2% |
| spurious_rate=0.08 | 0 | -12.4% | -6.0% |
| spurious_rate=0.08 | 1 | -11.3% | -5.3% |
| spurious_rate=0.08 | 2 | -2.3% | -4.4% |
| spurious_rate=0.08 | 3 | -0.5% | -4.0% |
| spurious_rate=0.08 | 4 | -8.3% | +17.4% |
| spurious_rate=0.08 | 5 | -9.3% | -3.8% |
| spurious_rate=0.08 | 6 | -7.6% | +0.3% |
| spurious_rate=0.08 | 7 | -7.7% | -6.6% |
| spurious_rate=0.08 | 8 | -5.0% | -9.5% |
| spurious_rate=0.08 | 9 | -14.2% | -5.9% |
| spurious_rate=0.16 | 0 | -16.4% | -7.8% |
| spurious_rate=0.16 | 1 | -14.3% | -9.4% |
| spurious_rate=0.16 | 2 | -14.6% | -3.5% |
| spurious_rate=0.16 | 3 | -4.1% | -2.9% |
| spurious_rate=0.16 | 4 | -23.5% | +0.7% |
| spurious_rate=0.16 | 5 | -18.3% | -5.0% |
| spurious_rate=0.16 | 6 | -16.0% | -6.5% |
| spurious_rate=0.16 | 7 | -4.1% | +8.0% |
| spurious_rate=0.16 | 8 | -12.1% | +0.5% |
| spurious_rate=0.16 | 9 | -13.5% | -6.1% |

Mean event counts in the test period (announcements include spurious ones):

- spurious_rate=0: true events 10.1, announcements 9.5
- spurious_rate=0.04: true events 10.1, announcements 17.2
- spurious_rate=0.08: true events 10.1, announcements 25.0
- spurious_rate=0.16: true events 10.1, announcements 36.1
