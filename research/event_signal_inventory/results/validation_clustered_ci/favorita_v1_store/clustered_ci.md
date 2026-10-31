# Store-clustered intervals for `results/favorita`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

Clusters: store.

| condition | comparison | estimate | iid bootstrap (original) | cluster bootstrap | two-stage bootstrap | per-cluster t-interval | clusters first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/5 | 1.000 |
| clean | C_asavailable_trained vs A_blind | +0.6% | [+0.3%, +0.8%] | [-0.6%, +1.1%] | [-0.5%, +1.2%] | [-1.4%, +2.1%] | 1/5 | 0.688 |
| clean | B_clean_trained vs A_blind | +0.6% | [+0.3%, +0.8%] | [-0.6%, +1.1%] | [-0.6%, +1.2%] | [-1.4%, +2.1%] | 1/5 | 0.688 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -0.1% | [-0.3%, +0.1%] | [-0.4%, +0.2%] | [-0.5%, +0.2%] | [-0.5%, +0.3%] | 2/5 | 0.500 |
| false_alarm | C_asavailable_trained vs A_blind | +0.7% | [+0.4%, +0.9%] | [-0.3%, +1.2%] | [-0.3%, +1.3%] | [-1.0%, +1.9%] | 1/5 | 0.438 |
| false_alarm | B_clean_trained vs A_blind | +0.8% | [+0.6%, +1.0%] | [-0.1%, +1.2%] | [-0.1%, +1.3%] | [-0.9%, +2.1%] | 1/5 | 0.375 |
| imperfect | C_asavailable_trained vs B_clean_trained | -0.7% | [-0.9%, -0.5%] | [-1.1%, -0.2%] | [-1.2%, -0.1%] | [-1.4%, +0.2%] | 4/5 | 0.188 |
| imperfect | C_asavailable_trained vs A_blind | +0.2% | [+0.0%, +0.4%] | [-0.3%, +0.6%] | [-0.3%, +0.6%] | [-0.6%, +0.9%] | 2/5 | 0.750 |
| imperfect | B_clean_trained vs A_blind | +0.9% | [+0.7%, +1.1%] | [+0.2%, +1.3%] | [+0.1%, +1.4%] | [-0.5%, +2.0%] | 1/5 | 0.125 |

With 5 clusters the smallest attainable two-sided sign-flip p-value is 0.0625. A cluster bootstrap with only 5 clusters also tends to understate uncertainty, so the per-cluster t-interval is the more conservative summary.
