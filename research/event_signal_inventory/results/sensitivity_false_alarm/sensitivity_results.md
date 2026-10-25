# Sensitivity: `spurious_rate` ∈ [0.0, 0.04, 0.08, 0.12, 0.2]

Base condition: `clean` of `configs/small.json`. Seeds: [0, 1, 2, 3, 4] (same as baseline; no additional seeds). Runtime 171s.

## Test-period metrics (mean ± sd across seeds; summed over SKUs)

| condition | arm | total_cost | holding_cost | shortage_cost | waste_cost | lost_units | waste_units | fill_rate |
|---|---|---|---|---|---|---|---|---|
| spurious_rate=0 | A_blind | 16239 ± 3119 | 4978 ± 402 | 10554 ± 2625 | 707 ± 150 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 |
| spurious_rate=0 | B_clean_trained | 11142 ± 1503 | 5308 ± 505 | 4648 ± 669 | 1186 ± 380 | 4648 ± 669 | 1977 ± 634 | 0.955 ± 0.003 |
| spurious_rate=0 | C_asavailable_trained | 11142 ± 1503 | 5308 ± 505 | 4648 ± 669 | 1186 ± 380 | 4648 ± 669 | 1977 ± 634 | 0.955 ± 0.003 |
| spurious_rate=0.04 | A_blind | 16239 ± 3119 | 4978 ± 402 | 10554 ± 2625 | 707 ± 150 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 |
| spurious_rate=0.04 | B_clean_trained | 13139 ± 1834 | 4381 ± 450 | 7449 ± 1064 | 1309 ± 700 | 7449 ± 1064 | 2182 ± 1166 | 0.928 ± 0.002 |
| spurious_rate=0.04 | C_asavailable_trained | 12566 ± 1563 | 5362 ± 948 | 5607 ± 1413 | 1597 ± 904 | 5607 ± 1413 | 2662 ± 1506 | 0.945 ± 0.014 |
| spurious_rate=0.08 | A_blind | 16239 ± 3119 | 4978 ± 402 | 10554 ± 2625 | 707 ± 150 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 |
| spurious_rate=0.08 | B_clean_trained | 15596 ± 2476 | 5879 ± 1396 | 6013 ± 554 | 3704 ± 1669 | 6013 ± 554 | 6173 ± 2781 | 0.941 ± 0.010 |
| spurious_rate=0.08 | C_asavailable_trained | 14885 ± 2151 | 5873 ± 1280 | 6071 ± 1681 | 2941 ± 1341 | 6071 ± 1681 | 4901 ± 2236 | 0.941 ± 0.017 |
| spurious_rate=0.12 | A_blind | 16239 ± 3119 | 4978 ± 402 | 10554 ± 2625 | 707 ± 150 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 |
| spurious_rate=0.12 | B_clean_trained | 16678 ± 2538 | 6011 ± 679 | 6504 ± 1264 | 4163 ± 758 | 6504 ± 1264 | 6938 ± 1264 | 0.937 ± 0.006 |
| spurious_rate=0.12 | C_asavailable_trained | 15502 ± 1731 | 6282 ± 1057 | 5945 ± 1758 | 3275 ± 883 | 5945 ± 1758 | 5458 ± 1471 | 0.942 ± 0.017 |
| spurious_rate=0.2 | A_blind | 16239 ± 3119 | 4978 ± 402 | 10554 ± 2625 | 707 ± 150 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 |
| spurious_rate=0.2 | B_clean_trained | 20425 ± 2583 | 7064 ± 1087 | 6984 ± 2740 | 6377 ± 1467 | 6984 ± 2740 | 10628 ± 2445 | 0.933 ± 0.021 |
| spurious_rate=0.2 | C_asavailable_trained | 17351 ± 1711 | 6451 ± 823 | 7095 ± 2797 | 3805 ± 1371 | 7095 ± 2797 | 6342 ± 2285 | 0.932 ± 0.019 |

## Paired relative total-cost differences (negative = C cheaper)

95% bootstrap CI over (seed, SKU) units; seed count = seeds where C is cheaper.

| condition | C vs A | 95% CI | seeds C<A | C vs B | 95% CI | seeds C<B |
|---|---|---|---|---|---|---|
| spurious_rate=0 | -31.4% | [-33.6%, -29.1%] | 5/5 | +0.0% | [+0.0%, +0.0%] | 0/5 |
| spurious_rate=0.04 | -22.6% | [-24.8%, -20.3%] | 5/5 | -4.4% | [-6.7%, -2.3%] | 4/5 |
| spurious_rate=0.08 | -8.3% | [-10.8%, -5.6%] | 4/5 | -4.6% | [-6.0%, -3.2%] | 4/5 |
| spurious_rate=0.12 | -4.5% | [-7.0%, -2.0%] | 4/5 | -7.1% | [-8.7%, -5.4%] | 5/5 |
| spurious_rate=0.2 | +6.8% | [+3.2%, +10.9%] | 1/5 | -15.0% | [-16.8%, -13.5%] | 5/5 |

## Per-seed relative total cost

| condition | seed | cost A | cost B | cost C | C vs A | C vs B |
|---|---|---|---|---|---|---|
| spurious_rate=0 | 0 | 15435 | 10637 | 10637 | -31.1% | +0.0% |
| spurious_rate=0 | 1 | 14771 | 10127 | 10127 | -31.4% | +0.0% |
| spurious_rate=0 | 2 | 14785 | 10299 | 10299 | -30.3% | +0.0% |
| spurious_rate=0 | 3 | 21781 | 13782 | 13782 | -36.7% | +0.0% |
| spurious_rate=0 | 4 | 14425 | 10866 | 10866 | -24.7% | +0.0% |
| spurious_rate=0.04 | 0 | 15435 | 13697 | 13077 | -15.3% | -4.5% |
| spurious_rate=0.04 | 1 | 14771 | 11634 | 10803 | -26.9% | -7.2% |
| spurious_rate=0.04 | 2 | 14785 | 11724 | 11473 | -22.4% | -2.1% |
| spurious_rate=0.04 | 3 | 21781 | 16065 | 14846 | -31.8% | -7.6% |
| spurious_rate=0.04 | 4 | 14425 | 12574 | 12631 | -12.4% | +0.5% |
| spurious_rate=0.08 | 0 | 15435 | 15277 | 13843 | -10.3% | -9.4% |
| spurious_rate=0.08 | 1 | 14771 | 15454 | 15258 | +3.3% | -1.3% |
| spurious_rate=0.08 | 2 | 14785 | 15110 | 14207 | -3.9% | -6.0% |
| spurious_rate=0.08 | 3 | 21781 | 19512 | 18379 | -15.6% | -5.8% |
| spurious_rate=0.08 | 4 | 14425 | 12625 | 12738 | -11.7% | +0.9% |
| spurious_rate=0.12 | 0 | 15435 | 15283 | 14900 | -3.5% | -2.5% |
| spurious_rate=0.12 | 1 | 14771 | 15696 | 14701 | -0.5% | -6.3% |
| spurious_rate=0.12 | 2 | 14785 | 15293 | 14456 | -2.2% | -5.5% |
| spurious_rate=0.12 | 3 | 21781 | 21192 | 18583 | -14.7% | -12.3% |
| spurious_rate=0.12 | 4 | 14425 | 15926 | 14871 | +3.1% | -6.6% |
| spurious_rate=0.2 | 0 | 15435 | 21358 | 16739 | +8.4% | -21.6% |
| spurious_rate=0.2 | 1 | 14771 | 18246 | 16311 | +10.4% | -10.6% |
| spurious_rate=0.2 | 2 | 14785 | 18579 | 15781 | +6.7% | -15.1% |
| spurious_rate=0.2 | 3 | 21781 | 24509 | 20101 | -7.7% | -18.0% |
| spurious_rate=0.2 | 4 | 14425 | 19432 | 17825 | +23.6% | -8.3% |

## Baseline cross-check: `spurious_rate=0` vs `clean` in `results/small/metrics_by_seed.csv`

All compared metrics identical for every seed and arm: **True**

| metric | max abs difference |
|---|---|
| tau_selected | 0 |
| val_cost | 0 |
| total_cost | 0 |
| holding_cost | 0 |
| shortage_cost | 0 |
| waste_cost | 0 |
| lost_units | 0 |
| waste_units | 0 |
| fill_rate | 0 |
| waste_rate | 0 |
| wape_median | 0 |
| pinball_tau_norm | 0 |
