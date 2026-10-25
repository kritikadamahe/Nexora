# Seed-clustered intervals for `results/small`

Relative total-cost difference (negative = first arm cheaper). 95% intervals.

| condition | comparison | estimate | iid bootstrap (original) | seed-cluster bootstrap | two-stage bootstrap | per-seed t-interval | seeds first cheaper | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/5 | 1.000 |
| clean | C_asavailable_trained vs A_blind | -31.4% | [-33.8%, -29.0%] | [-34.9%, -27.2%] | [-35.3%, -26.6%] | [-36.2%, -25.5%] | 5/5 | 0.062 |
| clean | B_clean_trained vs A_blind | -31.4% | [-33.7%, -28.9%] | [-34.8%, -27.4%] | [-35.2%, -26.7%] | [-36.2%, -25.5%] | 5/5 | 0.062 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -17.1% | [-20.2%, -13.6%] | [-22.1%, -12.2%] | [-22.9%, -11.0%] | [-25.0%, -8.9%] | 5/5 | 0.062 |
| false_alarm | C_asavailable_trained vs A_blind | +5.2% | [+1.9%, +8.9%] | [-3.4%, +18.7%] | [-3.4%, +18.3%] | [-10.5%, +23.3%] | 1/5 | 0.438 |
| false_alarm | B_clean_trained vs A_blind | +26.9% | [+19.8%, +34.4%] | [+12.1%, +44.6%] | [+10.4%, +46.6%] | [+3.5%, +54.4%] | 0/5 | 0.062 |
| imperfect | C_asavailable_trained vs B_clean_trained | -8.8% | [-11.9%, -5.9%] | [-14.2%, -3.4%] | [-15.3%, -2.8%] | [-14.7%, +0.5%] | 5/5 | 0.062 |
| imperfect | C_asavailable_trained vs A_blind | -3.3% | [-5.7%, -1.0%] | [-8.8%, +2.6%] | [-9.3%, +3.2%] | [-12.8%, +4.2%] | 4/5 | 0.250 |
| imperfect | B_clean_trained vs A_blind | +6.0% | [+1.8%, +10.3%] | [-5.3%, +19.7%] | [-5.9%, +19.9%] | [-14.7%, +22.2%] | 2/5 | 0.812 |

With 5 seeds the smallest attainable two-sided sign-flip p-value is 0.0625. A seed-cluster bootstrap with only 5 clusters also tends to understate uncertainty, so the per-seed t-interval is the more conservative summary.
