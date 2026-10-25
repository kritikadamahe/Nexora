# Seed-clustered intervals for `results/sensitivity_false_alarm`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

| condition | comparison | estimate | iid bootstrap (original) | seed-cluster bootstrap | two-stage bootstrap | per-seed t-interval | seeds first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| spurious_rate=0 | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/5 | 1.000 |
| spurious_rate=0 | C_asavailable_trained vs A_blind | -31.4% | [-33.8%, -29.0%] | [-34.9%, -27.2%] | [-35.3%, -26.6%] | [-36.2%, -25.5%] | 5/5 | 0.062 |
| spurious_rate=0 | B_clean_trained vs A_blind | -31.4% | [-33.7%, -28.9%] | [-34.8%, -27.4%] | [-35.2%, -26.7%] | [-36.2%, -25.5%] | 5/5 | 0.062 |
| spurious_rate=0.04 | C_asavailable_trained vs B_clean_trained | -4.4% | [-6.6%, -2.4%] | [-6.8%, -1.5%] | [-7.8%, -1.0%] | [-8.4%, +0.0%] | 4/5 | 0.125 |
| spurious_rate=0.04 | C_asavailable_trained vs A_blind | -22.6% | [-24.8%, -20.3%] | [-28.6%, -15.6%] | [-29.2%, -15.2%] | [-31.7%, -11.8%] | 5/5 | 0.062 |
| spurious_rate=0.04 | B_clean_trained vs A_blind | -19.1% | [-21.8%, -16.4%] | [-23.7%, -13.5%] | [-24.6%, -13.1%] | [-26.2%, -10.7%] | 5/5 | 0.062 |
| spurious_rate=0.08 | C_asavailable_trained vs B_clean_trained | -4.6% | [-6.1%, -3.2%] | [-7.2%, -1.5%] | [-7.9%, -1.3%] | [-9.4%, +0.8%] | 4/5 | 0.125 |
| spurious_rate=0.08 | C_asavailable_trained vs A_blind | -8.3% | [-10.8%, -5.7%] | [-13.7%, -2.3%] | [-14.0%, -1.4%] | [-16.9%, +1.6%] | 4/5 | 0.125 |
| spurious_rate=0.08 | B_clean_trained vs A_blind | -4.0% | [-7.1%, -0.8%] | [-9.7%, +2.5%] | [-10.2%, +2.8%] | [-12.9%, +6.1%] | 3/5 | 0.438 |
| spurious_rate=0.12 | C_asavailable_trained vs B_clean_trained | -7.1% | [-8.7%, -5.4%] | [-10.2%, -4.1%] | [-10.4%, -3.7%] | [-11.1%, -2.2%] | 5/5 | 0.062 |
| spurious_rate=0.12 | C_asavailable_trained vs A_blind | -4.5% | [-7.0%, -2.1%] | [-10.7%, +0.6%] | [-10.9%, +1.2%] | [-11.9%, +4.8%] | 4/5 | 0.312 |
| spurious_rate=0.12 | B_clean_trained vs A_blind | +2.7% | [+0.1%, +5.3%] | [-1.1%, +7.3%] | [-1.9%, +8.2%] | [-3.3%, +9.9%] | 2/5 | 0.312 |
| spurious_rate=0.2 | C_asavailable_trained vs B_clean_trained | -15.0% | [-16.7%, -13.5%] | [-18.9%, -10.5%] | [-19.2%, -10.4%] | [-21.4%, -8.0%] | 5/5 | 0.062 |
| spurious_rate=0.2 | C_asavailable_trained vs A_blind | +6.8% | [+3.1%, +10.8%] | [-2.5%, +17.0%] | [-2.3%, +17.3%] | [-5.5%, +22.1%] | 1/5 | 0.188 |
| spurious_rate=0.2 | B_clean_trained vs A_blind | +25.8% | [+21.3%, +30.5%] | [+17.6%, +35.2%] | [+17.1%, +36.4%] | [+14.4%, +39.6%] | 0/5 | 0.062 |

With 5 seeds the smallest attainable two-sided sign-flip p-value is 0.0625. A seed-cluster bootstrap with only 5 clusters also tends to understate uncertainty, so the per-seed t-interval is the more conservative summary.
