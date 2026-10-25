# Seed-clustered intervals for `results/rerun`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

| condition | comparison | estimate | iid bootstrap (original) | seed-cluster bootstrap | two-stage bootstrap | per-seed t-interval | seeds first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/20 | 1.000 |
| clean | C_asavailable_trained vs A_blind | -36.9% | [-38.2%, -35.5%] | [-38.8%, -34.6%] | [-39.2%, -34.2%] | [-38.7%, -33.8%] | 20/20 | 0.000 |
| clean | B_clean_trained vs A_blind | -36.9% | [-38.2%, -35.5%] | [-38.8%, -34.7%] | [-39.1%, -34.4%] | [-38.7%, -33.8%] | 20/20 | 0.000 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -16.6% | [-17.9%, -15.1%] | [-20.2%, -13.5%] | [-20.5%, -13.3%] | [-19.6%, -12.6%] | 20/20 | 0.000 |
| false_alarm | C_asavailable_trained vs A_blind | -3.5% | [-4.9%, -2.1%] | [-7.6%, +1.5%] | [-7.7%, +1.9%] | [-8.3%, +2.6%] | 15/20 | 0.287 |
| false_alarm | B_clean_trained vs A_blind | +15.6% | [+13.1%, +18.2%] | [+8.2%, +23.6%] | [+8.2%, +23.8%] | [+8.2%, +25.6%] | 2/20 | 0.000 |
| imperfect | C_asavailable_trained vs B_clean_trained | -4.8% | [-6.0%, -3.4%] | [-8.3%, -0.9%] | [-8.5%, -0.8%] | [-8.1%, -0.1%] | 15/20 | 0.047 |
| imperfect | C_asavailable_trained vs A_blind | -3.5% | [-4.8%, -2.2%] | [-7.5%, +0.4%] | [-7.7%, +0.5%] | [-7.7%, +0.3%] | 15/20 | 0.063 |
| imperfect | B_clean_trained vs A_blind | +1.4% | [-0.4%, +3.1%] | [-3.9%, +6.8%] | [-4.0%, +7.1%] | [-4.4%, +6.3%] | 11/20 | 0.716 |

With 20 seeds the smallest attainable two-sided sign-flip p-value is 0.0000. A seed-cluster bootstrap with only 20 clusters also tends to understate uncertainty, so the per-seed t-interval is the more conservative summary.
