# When Do Event Signals Pay Off? Signal Quality, Event Strength and Perishable Replenishment

*Working draft v0. Items marked **[TODO]** are missing results or citations. Every number below is copied from a saved result file in `results/`, and the source is given in brackets.*

## Abstract

Demand forecasters for perishable goods are usually given event information (holidays, festivals, promotions) taken from a clean, after-the-fact calendar. At ordering time that information can be missing, late, false or mislabelled. We study when event signals reduce inventory cost and when imperfect signals do more harm than good. We compare three forecasters that share one replenishment policy: one that ignores events (A), one trained on the true calendar (B), and one trained on the signals as they would have been available at ordering time (C). In a simulation with strong events and clean signals, event-aware forecasting cuts cost by 36.9% (20/20 seeds). Clean-calendar training with false-alarm-heavy signals costs 15.6% more than ignoring events, and as-available training (C) removes most of that harm (16.6% cheaper than B). A sweep over event strength and false-alarm rate shows that these effects scale with event strength: at the strength level matching real Favorita grocery data, all differences shrink to 3.4% or less. On Favorita, with 100 perishable series, event signals made no statistically distinguishable difference in cost (all intervals include 0). **[TODO: one sentence on M5 / Wisconsin SNAP days once the experiment has run.]** Event signals, and protection against their errors, matter in proportion to how strongly events move demand.

## 1. Introduction

Perishable retail has a narrow margin for error. Over-ordering turns into waste, and under-ordering turns into lost sales. Event information is a natural input to demand forecasts, but the literature and practice usually build event features from a clean calendar that is known with certainty after the fact. In deployment the signal is different. Events are announced late, some never get announced, some announcements turn out to be false, and labels can be wrong. A model that learned to trust a clean calendar may react strongly to a signal that is wrong.

This paper asks two questions:

1. **Does training on signals as they were actually available (C) reduce the cost harm of imperfect signals, compared with training on the clean calendar (B)?**
2. **How does the answer depend on how strongly events move demand?** When events barely matter, is any of this worth doing?

**Contributions.**

1. A controlled simulation of perishable replenishment (fixed shelf life, lead time, FIFO stock) in which signal quality (misses, late announcements, false alarms, mislabelling) is a tunable input, and in which models are evaluated on inventory cost rather than forecast error alone.
2. A map of where event signals help, where they do nothing and where they hurt, over event strength and false-alarm rate.
3. A real-data check on Favorita grocery sales, where events are weak, together with a matched analysis whose confidence intervals account for the shared demand across seeds.
4. **[TODO]** A real-data case with strong, scheduled events (M5 / Walmart SNAP days).

**Scope.** The claims are about operational cost under one heuristic replenishment policy. We make no claim of novelty beyond what the related-work section supports, and no claim about deployed systems.

## 2. Related work

**[TODO: no systematic literature review has been done for this study, and none is claimed. Adding cited related work is required before submission. Suggested threads, not yet verified:**
- event and calendar features in retail demand forecasting;
- the effect of forecast-input errors on inventory decisions;
- perishable inventory models with fixed shelf life (the outdating-corrected order-up-to rule);
- training on noisy or as-available inputs versus clean inputs (train-test input mismatch);
- quantile forecasting in newsvendor-style decisions.**

*Existing repository material (`literature_review_and_gap_analysis.md`) covers the wider RetailEdge system and does not review this specific question.*

## 3. Problem setting and methods

### 3.1 Replenishment problem

One SKU is managed on a daily basis with lead time *L* = 2 days and shelf life *m* = 4 days. Stock is sold first-in-first-out, unmet demand is lost, and units that reach the end of their shelf life expire. Costs are holding 0.05 per unit-day, shortage 1.0 per lost unit and waste 0.6 per expired unit. Orders follow an outdating-corrected order-up-to rule, `q = max(0, S − (inventory position − projected FIFO expiry over L+1 days))`, with *S* set from a quantile τ of the forecast of demand over the next *L*+1 days. The rule is a heuristic and is not claimed to be optimal. All arms share it.

### 3.2 Event signals

Each announcement is `(announce_day, start, duration, type)`. At ordering day *t* a forecaster sees only announcements with `announce_day ≤ t`. The error process has four parts: missed events (`p_miss`), announcements that arrive on the event's start day instead of 14 days earlier (`p_late`), spurious events at rate `spurious_rate` per day, and spurious events labelled as the highest-uplift type (`p_misleading`).

Three signal conditions are used:

| Condition | p_miss | p_late | spurious per day | p_misleading |
|---|---|---|---|---|
| clean | 0 | 0 | 0 | 0 |
| imperfect | 0.3 | 0.3 | 0.04 | 0.5 |
| false_alarm | 0.1 | 0 | 0.08 | 0.8 |

### 3.3 Forecasters (arms)

All arms use pooled gradient-boosted quantile regression (scikit-learn `HistGradientBoostingRegressor`, quantile loss), one model per quantile level, predicting cumulative demand over days *t*…*t*+*L*. Features use only demand before *t*, scaled by the trailing 28-day mean, plus per-type counts of signalled event days in the window for the event arms.

- **A (blind):** no event features.
- **B (clean-trained):** trained on the true event calendar, with every event announced 14 days ahead, then served the imperfect signal.
- **C (as-available-trained):** trained on the training-period part of the same signal realisation it is served with.

Under clean signals, B and C see identical features and must produce identical results; this is used as a built-in consistency check. The quantile τ is chosen separately for each arm and condition by validation-period simulated cost, and the test period is evaluated once.

### 3.4 Synthetic demand and real demand

*Synthetic.* Negative-binomial daily demand, equal to a SKU base level times a weekday profile, a linear trend and an event multiplier. Event uplifts vary by type and by SKU, and 20% of SKUs do not respond to events. Each seed is an independent world.

*Real, Favorita.* 5 Quito stores × 20 perishable items (100 series; 80 produce, 10 meats, 5 dairy, 5 poultry), 742 days (2015-08-01 to 2017-08-15), 166 test days after a 7-day warm-up. Events come from the holiday calendar: national holidays (21 occurrences, 5 in the test period), national events (6 occurrences, 1 in test) and local holidays (2 occurrences, 0 in test). The April 2016 earthquake is excluded because it could not have been announced. Demand is fixed real sales, so seeds vary only the signal errors and the model fits. Recorded sales are censored by stockouts. Zero-sale days are 0.4% of the panel and the same share is flagged as suspected stockouts, so the bias is small but not zero. [`results/favorita_v2_stdout.log`]

*Real, M5.* **[TODO: Walmart M5, Wisconsin stores, top food products; scheduled SNAP days plus named events as event types. On SNAP days, store-level food sales are higher by about +12% (CA), +17% (TX) and +32% (WI) compared with other days on the same weekday in the same month.]**

### 3.5 Statistics

Each seed in the synthetic experiments is an independent world, so the unit of analysis is the seed. The primary evidence is the per-seed 95% t-interval (19 degrees of freedom for 20 seeds) and the exact two-sided sign-flip test on per-seed relative cost differences. A comparison is called supported only when the interval excludes 0 and *p* < 0.05, and Holm's correction is applied across the eight non-trivial comparisons at family-wise α = 0.05. Bootstrap intervals over (seed, SKU) units are reported for reference only, because they ignore dependence and are too narrow.

On real data every seed shares the same demand, so seeds are not independent. There we resample products (20 clusters) or stores (5 clusters) instead and treat the per-cluster t-interval as the conservative summary.

## 4. Results

### 4.1 Synthetic: strong events, three signal conditions (20 seeds)

Costs are summed over 40 SKUs over 161 evaluated test days, mean over seeds. [`results/rerun/results.md`, `results/validation_clustered_ci/rerun/clustered_ci.csv`]

| Condition | A (blind) | B (clean-trained) | C (as-available) |
|---|---|---|---|
| clean | 17,748 | 11,208 | 11,208 |
| imperfect | 17,748 | 17,992 | 17,134 |
| false_alarm | 17,748 | 20,521 | 17,121 |

| Condition | Comparison | Pooled estimate | Per-seed t-interval | Sign-flip *p* | Seeds first cheaper | Holm-adjusted *p* | Supported |
|---|---|---|---|---|---|---|---|
| clean | C vs A | −36.9% | [−38.68%, −33.75%] | 1.9 × 10⁻⁶ | 20/20 | 1.5 × 10⁻⁵ | Yes |
| clean | B vs A | −36.9% | [−38.68%, −33.75%] | 1.9 × 10⁻⁶ | 20/20 | 1.5 × 10⁻⁵ | Yes |
| false_alarm | C vs B | −16.6% | [−19.63%, −12.64%] | 1.9 × 10⁻⁶ | 20/20 | 1.5 × 10⁻⁵ | Yes |
| false_alarm | B vs A | +15.6% | [+8.21%, +25.60%] | 1.5 × 10⁻⁴ | 2/20 | 7.6 × 10⁻⁴ | Yes (B worse than A) |
| imperfect | C vs B | −4.8% | [−8.09%, −0.08%] | 0.047 | 15/20 | 0.188 | Marginal, fails Holm |
| imperfect | C vs A | −3.5% | [−7.73%, +0.27%] | 0.063 | 15/20 | 0.189 | No |
| false_alarm | C vs A | −3.5% | [−8.25%, +2.55%] | 0.287 | 15/20 | 0.574 | No |
| imperfect | B vs A | +1.4% | [−4.38%, +6.29%] | 0.716 | 11/20 | 0.716 | No |

Holm is adjusted over the eight comparisons shown. Clean C vs B is omitted because the two arms are identical by design, so clean B vs A equals clean C vs A; keeping it as a separate hypothesis makes the correction slightly conservative.

Findings:

1. **Accurate signals pay off strongly** (clean C vs A, −36.9%).
2. **Clean-calendar training with false-alarm-heavy signals is worse than ignoring events** (+15.6%). As-available training removes most of that harm (−16.6% vs B).
3. **With mixed, moderate errors the advantage of C over B is small** and does not survive multiplicity correction.
4. **Neither imperfect condition shows that using imperfect signals beats ignoring them** (C vs A is not supported in either).

### 4.2 Synthetic: event strength × false-alarm rate (10 seeds)

Event strength scales the generator's event log-uplifts, where 1.0 is the original simulation and 0.1 is roughly the level measured in the Favorita panel. False-alarm rate is `spurious_rate`, with `p_miss` = 0.1 and `p_misleading` = 0.8. Cells show the mean per-seed relative cost difference. [`results/grid_strength_false_alarm/grid_results.md`; 10 seeds, sign-flip *p* not corrected for multiplicity]

*C vs A (negative = using events as-available is cheaper than ignoring them):*

| strength | spurious=0 | 0.04 | 0.08 | 0.16 |
|---|---|---|---|---|
| 0.1 | −3.0% | −2.2% | −1.5% | −1.4% |
| 0.25 | −5.8% | −3.9% | −2.9% | −2.5% |
| 0.5 | −14.2% | −9.3% | −2.8% | −3.2% |
| 1.0 | −32.4% | −15.5% | +0.0% | −1.6% |

*B vs A (clean-trained vs ignoring events):*

| strength | spurious=0 | 0.04 | 0.08 | 0.16 |
|---|---|---|---|---|
| 0.1 | −3.4% | −2.3% | −1.0% | +0.1% |
| 0.25 | −6.1% | −3.6% | −0.5% | +3.3% |
| 0.5 | −14.9% | −6.5% | +5.7% | +12.5% |
| 1.0 | −34.5% | −9.2% | +20.0% | +40.0% |

*C vs B (protection from as-available training):*

| strength | spurious=0 | 0.04 | 0.08 | 0.16 |
|---|---|---|---|---|
| 0.1 | +0.4% | +0.1% | −0.5% | −1.5% |
| 0.25 | +0.3% | −0.3% | −2.4% | −5.6% |
| 0.5 | +0.9% | −3.0% | −7.9% | −13.7% |
| 1.0 | +3.2% | −7.0% | −16.1% | −29.4% |

Reading the map:

- **Benefit of events grows with strength**, from about −3% to about −32% at zero false alarms.
- **Harm from false alarms grows with strength**: at strength 1.0 and 0.16 false alarms per day, clean-trained B costs 40% more than ignoring events.
- **The protection of as-available training (C vs B) grows with both** strength and false-alarm rate, and is near zero or slightly adverse (+0.3% to +3.2%, so C is slightly worse than B) when there are no false alarms (these cells still have 10% missed events).
- **At strength 0.1 everything is within 3.4%.** This is the regime that matches Favorita.

### 4.3 Real data: Favorita (100 series, 20 seeds)

Test-period cost summed over 100 series, mean over seeds. [`results/favorita_v2/results.md`]

| Condition | A (blind) | B (clean-trained) | C (as-available) |
|---|---|---|---|
| clean | 127,203 | 127,909 | 127,909 |
| imperfect | 127,203 | 128,359 | 127,467 |
| false_alarm | 127,203 | 128,203 | 128,042 |

Relative cost differences with 95% intervals clustered by item (20 clusters). [`results/validation_clustered_ci/favorita_v2_item/`]

| Condition | Comparison | Estimate | Cluster bootstrap | Per-cluster t-interval |
|---|---|---|---|---|
| clean | B/C vs A | +0.6% | [−0.4%, +1.7%] | [−0.5%, +1.0%] |
| false_alarm | C vs A | +0.7% | [−0.2%, +1.6%] | [−0.1%, +1.2%] |
| false_alarm | B vs A | +0.8% | [−0.2%, +1.9%] | [−0.2%, +1.2%] |
| imperfect | C vs A | +0.2% | [−0.3%, +0.7%] | [−0.2%, +0.6%] |
| imperfect | B vs A | +0.9% | [−0.0%, +2.0%] | [−0.5%, +1.3%] |
| imperfect | C vs B | −0.7% | [−1.4%, −0.0%] | [−0.9%, +0.1%] |

Findings:

1. **Event signals did not measurably change cost.** Every item-clustered interval for events vs ignoring them includes 0. The point estimates are slightly positive, meaning events are slightly worse.
2. **The ordering from the simulation shows up in miniature.** Under imperfect signals C is slightly cheaper than B (−0.7%), but with store clustering (5 clusters) the cluster bootstrap is [−1.1%, −0.2%] and the t-interval [−1.4%, +0.2%], so this is weak evidence at best.
3. **Why so little:** national holidays raise sales by only about 9% (training log-uplift +0.087), national events by about 0% (−0.008), the test period has only 6 events, and the 80% produce share is demand that is steady across the calendar. With clean signals, cost within event windows fell by 0.75% against A, but the extra features made the model slightly noisier on the other days (+0.95%), which carry 77% of the cost. [`results/favorita_v2/event_window_split.csv`, from `python -m esi.event_windows --results results/favorita_v2`]
4. **The quantile grid is not the constraint.** After widening the grid to include 0.95 and 0.975, all arms still select τ = 0.90.

### 4.4 Real data with strong events: M5 (Walmart)

**[TODO: run the M5 loader and the three-arm experiment on Wisconsin food products with SNAP days plus named events. Expected role: a real-data case at event strength roughly 0.25–0.5 on the grid in Section 4.2, where the simulation predicts events matter and false alarms start to hurt. Report whether the observed real-data differences fall inside the range the grid predicts for that strength.]**

## 5. Discussion

**Answer to the questions.**

1. Training on as-available signals reduces the cost of imperfect signals, and the benefit grows with the false-alarm rate. It is strongly supported in simulation when false alarms are common (−16.6% vs B), weak when errors are mixed and moderate, and not distinguishable from zero on Favorita.
2. The size of all effects is governed by event strength. When events move demand a lot, accurate signals are worth tens of percent and false alarms can cost as much. When events move demand by under about 10%, the cost of the whole question is a few percent at most.

**Practical reading.** Before investing in event features or in the quality of event feeds, estimate how much events move demand for the product in question. If the uplift is small, a blind forecaster is as good. If it is large, clean signals are valuable, and training the forecaster on realistic signals is a cheap way to avoid being worse than blind when signals are unreliable.

**Where this does not apply.** The "events don't help" result on Favorita is about everyday perishables, mostly produce, under national and local holidays. It should not be read as "events never help in real retail."

## 6. Limitations

1. **Partly favourable design for C.** C is trained and evaluated on the same error process. Its advantage under a shift in that process has not been tested.
2. **One policy, one cost structure.** All arms share one heuristic order-up-to rule. Lead time 2, shelf life 4 and the cost ratios are fixed. A different policy or cost ratio could change the sizes of the differences.
3. **Simplified operations.** Single SKU, single echelon, no capacity limits, ordering costs, substitution or supplier variability.
4. **Censored demand.** Real sales understate demand during stockouts. The suspected-stockout share in Favorita is 0.4% of series-days.
5. **Few clusters.** 20 seeds is a modest number, and store-level clustering on Favorita has only 5 stores. The smallest attainable sign-flip *p* with 5 clusters is 0.0625.
6. **Panel composition.** 80 of the 100 Favorita series are produce, from one city.
7. **Grid sweep size.** The strength × false-alarm grid uses 10 seeds, and its sign-flip *p*-values are not corrected for multiplicity.
8. **Library-version sensitivity.** Results are deterministic in a fixed environment, but the gradient-boosting fits change with the scikit-learn version. The earlier 5-seed run (scikit-learn 1.9.1) differs from seeds 0–4 of the 20-seed run (1.8.0) by up to 10% per seed and arm. A 5-seed run under 1.8.0 matches the 20-seed run exactly. All reported results use one pinned environment, recorded with each run (`results/reproducibility_check.md`).
9. **No pre-registration.** The hypotheses were set during prototype design and were not pre-registered.

## 7. Conclusion

Event signals are worth exactly as much as events move demand, and imperfect signals can destroy that value. In simulation, accurate event information cut inventory cost by 37% and false-alarm-heavy signals made a clean-trained model 16% worse than ignoring events, while a model trained on realistic signals recovered most of that. On real Favorita perishables, where events move demand by under 10%, none of it mattered. A map over event strength and false-alarm rate tells practitioners which regime they are in. **[TODO: finish after M5.]**

## 8. Reproducibility

Code, configs and saved results are public at https://github.com/kritikadamahe/Nexora/tree/main/research/event_signal_inventory. Exact reproduction needs the environment recorded in each run's `environment.json` (Python 3.11.9, numpy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0; see `results/reproducibility_check.md`). Real data are downloaded separately from Kaggle and are never committed. Synthetic experiments: `configs/seed20.json` (20 seeds) via `python -m esi.experiment`. Grid: `configs/grid_strength_false_alarm.json` via `python -m esi.grid`. Favorita: `configs/favorita.json`. Clustered intervals: `python -m esi.clustered_ci --cluster item|store`. The test suite is in `tests/`.

## References

**[TODO]** None cited yet.
