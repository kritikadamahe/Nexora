# Item-clustered intervals for `results/m5`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

Clusters: item.

| condition | comparison | estimate | iid bootstrap (original) | cluster bootstrap | two-stage bootstrap | per-cluster t-interval | clusters first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/33 | 1.000 |
| clean | C_asavailable_trained vs A_blind | -5.3% | [-5.9%, -4.7%] | [-8.1%, -2.7%] | [-8.1%, -2.6%] | [-7.1%, -2.1%] | 24/33 | 0.000 |
| clean | B_clean_trained vs A_blind | -5.3% | [-5.9%, -4.7%] | [-8.2%, -2.6%] | [-8.3%, -2.6%] | [-7.1%, -2.1%] | 24/33 | 0.000 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -1.7% | [-2.0%, -1.4%] | [-2.4%, -1.1%] | [-2.4%, -1.1%] | [-2.4%, -1.1%] | 28/33 | 0.000 |
| false_alarm | C_asavailable_trained vs A_blind | -2.9% | [-3.3%, -2.5%] | [-4.5%, -1.4%] | [-4.5%, -1.3%] | [-3.9%, -1.0%] | 23/33 | 0.001 |
| false_alarm | B_clean_trained vs A_blind | -1.2% | [-1.7%, -0.7%] | [-3.0%, +0.5%] | [-3.1%, +0.5%] | [-2.3%, +0.9%] | 13/33 | 0.364 |
| imperfect | C_asavailable_trained vs B_clean_trained | -0.7% | [-1.1%, -0.3%] | [-1.5%, +0.2%] | [-1.6%, +0.2%] | [-1.2%, +0.4%] | 18/33 | 0.266 |
| imperfect | C_asavailable_trained vs A_blind | -0.7% | [-1.1%, -0.2%] | [-1.4%, +0.0%] | [-1.5%, +0.1%] | [-1.3%, -0.0%] | 20/33 | 0.047 |
| imperfect | B_clean_trained vs A_blind | +0.0% | [-0.4%, +0.5%] | [-1.0%, +1.2%] | [-1.1%, +1.3%] | [-1.2%, +0.9%] | 16/33 | 0.794 |
| clean | D_noise_injected vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/33 | 1.000 |
| clean | D_noise_injected vs A_blind | -5.3% | [-6.0%, -4.7%] | [-8.2%, -2.7%] | [-8.2%, -2.6%] | [-7.1%, -2.1%] | 24/33 | 0.000 |
| clean | D_noise_injected vs C_asavailable_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/33 | 1.000 |
| false_alarm | D_noise_injected vs B_clean_trained | -1.3% | [-1.6%, -1.0%] | [-1.8%, -0.9%] | [-1.9%, -0.8%] | [-1.8%, -0.9%] | 27/33 | 0.000 |
| false_alarm | D_noise_injected vs A_blind | -2.5% | [-3.0%, -2.0%] | [-4.2%, -1.0%] | [-4.2%, -1.0%] | [-3.5%, -0.7%] | 21/33 | 0.004 |
| false_alarm | D_noise_injected vs C_asavailable_trained | +0.4% | [+0.1%, +0.7%] | [+0.0%, +0.7%] | [-0.1%, +0.9%] | [+0.0%, +0.8%] | 12/33 | 0.028 |
| imperfect | D_noise_injected vs B_clean_trained | -1.3% | [-1.6%, -0.9%] | [-2.1%, -0.4%] | [-2.2%, -0.3%] | [-1.7%, -0.1%] | 19/33 | 0.037 |
| imperfect | D_noise_injected vs A_blind | -1.2% | [-1.6%, -0.8%] | [-2.0%, -0.5%] | [-2.1%, -0.4%] | [-1.7%, -0.4%] | 21/33 | 0.002 |
| imperfect | D_noise_injected vs C_asavailable_trained | -0.6% | [-0.9%, -0.2%] | [-0.9%, -0.3%] | [-1.0%, -0.1%] | [-0.7%, -0.2%] | 24/33 | 0.003 |

With 33 clusters the smallest attainable two-sided sign-flip p-value (Monte Carlo, 200,000 draws) is 5e-06. A cluster bootstrap with only 33 clusters also tends to understate uncertainty, so the per-cluster t-interval is the more conservative summary.
