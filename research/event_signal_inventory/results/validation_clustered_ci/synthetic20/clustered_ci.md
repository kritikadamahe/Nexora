# Seed-clustered intervals for `results/synthetic20`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

Clusters: seed.

| condition | comparison | estimate | iid bootstrap (original) | cluster bootstrap | two-stage bootstrap | per-cluster t-interval | clusters first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/20 | 1.000 |
| clean | C_asavailable_trained vs A_blind | -36.8% | [-38.1%, -35.4%] | [-38.8%, -34.4%] | [-39.2%, -34.0%] | [-38.7%, -33.5%] | 20/20 | 0.000 |
| clean | B_clean_trained vs A_blind | -36.8% | [-38.1%, -35.4%] | [-38.8%, -34.5%] | [-39.1%, -34.2%] | [-38.7%, -33.5%] | 20/20 | 0.000 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -17.0% | [-18.4%, -15.5%] | [-20.6%, -13.8%] | [-20.9%, -13.6%] | [-20.1%, -12.9%] | 20/20 | 0.000 |
| false_alarm | C_asavailable_trained vs A_blind | -3.6% | [-5.1%, -2.1%] | [-7.8%, +1.5%] | [-8.0%, +1.8%] | [-8.3%, +2.6%] | 14/20 | 0.286 |
| false_alarm | B_clean_trained vs A_blind | +16.1% | [+13.5%, +18.7%] | [+8.5%, +24.1%] | [+8.3%, +24.3%] | [+8.7%, +26.4%] | 2/20 | 0.000 |
| imperfect | C_asavailable_trained vs B_clean_trained | -5.2% | [-6.5%, -3.9%] | [-8.6%, -1.5%] | [-8.9%, -1.4%] | [-8.3%, -0.9%] | 16/20 | 0.019 |
| imperfect | C_asavailable_trained vs A_blind | -3.8% | [-5.2%, -2.6%] | [-8.1%, +0.2%] | [-8.3%, +0.3%] | [-8.1%, +0.1%] | 15/20 | 0.053 |
| imperfect | B_clean_trained vs A_blind | +1.5% | [-0.3%, +3.2%] | [-3.8%, +6.8%] | [-4.0%, +7.1%] | [-4.2%, +6.5%] | 9/20 | 0.665 |
| clean | D_noise_injected vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/20 | 1.000 |
| clean | D_noise_injected vs A_blind | -36.8% | [-38.2%, -35.3%] | [-38.8%, -34.5%] | [-39.3%, -33.9%] | [-38.7%, -33.5%] | 20/20 | 0.000 |
| clean | D_noise_injected vs C_asavailable_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/20 | 1.000 |
| false_alarm | D_noise_injected vs B_clean_trained | -18.1% | [-19.5%, -16.7%] | [-21.5%, -15.1%] | [-21.7%, -14.8%] | [-21.2%, -14.1%] | 20/20 | 0.000 |
| false_alarm | D_noise_injected vs A_blind | -4.9% | [-6.3%, -3.3%] | [-8.7%, +0.0%] | [-9.0%, +0.2%] | [-9.4%, +1.1%] | 16/20 | 0.113 |
| false_alarm | D_noise_injected vs C_asavailable_trained | -1.3% | [-2.2%, -0.5%] | [-3.4%, +0.8%] | [-3.6%, +0.9%] | [-3.6%, +1.3%] | 13/20 | 0.329 |
| imperfect | D_noise_injected vs B_clean_trained | -5.5% | [-6.4%, -4.6%] | [-7.3%, -3.5%] | [-7.5%, -3.3%] | [-7.2%, -2.9%] | 18/20 | 0.000 |
| imperfect | D_noise_injected vs A_blind | -4.1% | [-5.5%, -2.8%] | [-8.0%, +0.1%] | [-8.1%, +0.1%] | [-8.4%, -0.2%] | 15/20 | 0.043 |
| imperfect | D_noise_injected vs C_asavailable_trained | -0.3% | [-1.4%, +0.8%] | [-2.9%, +2.1%] | [-3.1%, +2.4%] | [-2.6%, +2.5%] | 9/20 | 0.947 |

With 20 clusters the smallest attainable two-sided sign-flip p-value (exact) is 1.9e-06. A cluster bootstrap with only 20 clusters also tends to understate uncertainty, so the per-cluster t-interval is the more conservative summary.
