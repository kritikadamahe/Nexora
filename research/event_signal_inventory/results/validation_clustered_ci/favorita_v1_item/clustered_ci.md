# Item-clustered intervals for `results/favorita`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

Clusters: item.

| condition | comparison | estimate | iid bootstrap (original) | cluster bootstrap | two-stage bootstrap | per-cluster t-interval | clusters first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/20 | 1.000 |
| clean | C_asavailable_trained vs A_blind | +0.6% | [+0.3%, +0.8%] | [-0.4%, +1.7%] | [-0.5%, +1.8%] | [-0.5%, +1.0%] | 9/20 | 0.518 |
| clean | B_clean_trained vs A_blind | +0.6% | [+0.3%, +0.8%] | [-0.4%, +1.7%] | [-0.5%, +1.7%] | [-0.5%, +1.0%] | 9/20 | 0.518 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -0.1% | [-0.3%, +0.1%] | [-0.4%, +0.2%] | [-0.5%, +0.3%] | [-0.3%, +0.3%] | 11/20 | 0.856 |
| false_alarm | C_asavailable_trained vs A_blind | +0.7% | [+0.4%, +0.9%] | [-0.2%, +1.6%] | [-0.3%, +1.6%] | [-0.1%, +1.2%] | 7/20 | 0.099 |
| false_alarm | B_clean_trained vs A_blind | +0.8% | [+0.6%, +1.0%] | [-0.2%, +1.9%] | [-0.2%, +1.9%] | [-0.2%, +1.2%] | 6/20 | 0.158 |
| imperfect | C_asavailable_trained vs B_clean_trained | -0.7% | [-0.9%, -0.5%] | [-1.4%, -0.0%] | [-1.4%, +0.0%] | [-0.9%, +0.1%] | 11/20 | 0.125 |
| imperfect | C_asavailable_trained vs A_blind | +0.2% | [+0.0%, +0.4%] | [-0.3%, +0.7%] | [-0.3%, +0.8%] | [-0.2%, +0.6%] | 7/20 | 0.246 |
| imperfect | B_clean_trained vs A_blind | +0.9% | [+0.7%, +1.1%] | [-0.0%, +2.0%] | [-0.0%, +2.0%] | [-0.0%, +1.3%] | 6/20 | 0.038 |

With 20 clusters the smallest attainable two-sided sign-flip p-value is 0.0000. A cluster bootstrap with only 20 clusters also tends to understate uncertainty, so the per-cluster t-interval is the more conservative summary.
