# Item-clustered intervals for `results/favorita_planned`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

Clusters: item.

| condition | comparison | estimate | iid bootstrap (original) | cluster bootstrap | two-stage bootstrap | per-cluster t-interval | clusters first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/20 | 1.000 |
| clean | C_asavailable_trained vs A_blind | +0.6% | [+0.3%, +0.8%] | [-0.4%, +1.7%] | [-0.5%, +1.8%] | [-0.5%, +1.0%] | 9/20 | 0.518 |
| clean | B_clean_trained vs A_blind | +0.6% | [+0.3%, +0.8%] | [-0.4%, +1.7%] | [-0.5%, +1.7%] | [-0.5%, +1.0%] | 9/20 | 0.518 |
| planned_calendar | C_asavailable_trained vs B_clean_trained | -0.5% | [-0.6%, -0.3%] | [-0.8%, -0.2%] | [-0.9%, -0.1%] | [-0.7%, -0.1%] | 13/20 | 0.011 |
| planned_calendar | C_asavailable_trained vs A_blind | +0.2% | [+0.0%, +0.4%] | [-0.7%, +1.2%] | [-0.7%, +1.2%] | [-0.7%, +0.7%] | 9/20 | 0.967 |
| planned_calendar | B_clean_trained vs A_blind | +0.7% | [+0.5%, +1.0%] | [-0.3%, +2.0%] | [-0.4%, +2.0%] | [-0.4%, +1.2%] | 7/20 | 0.309 |

With 20 clusters the smallest attainable two-sided sign-flip p-value (exact) is 1.9e-06. A cluster bootstrap with only 20 clusters also tends to understate uncertainty, so the per-cluster t-interval is the more conservative summary.
