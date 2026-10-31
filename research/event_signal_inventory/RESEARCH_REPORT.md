# Event-Signal Quality and Perishable Replenishment: Research Report

*Research module:* `research/event_signal_inventory/` (Nexora / RetailEdge AI)
*Status:* simulation study. **Primary results: the 20-seed run** (Section 6). The earlier 5-seed run (Appendix A) and the 5-seed false-alarm sensitivity sweep (Appendix B) are reported separately and are descriptive only.

---

## Report status and verification

Every statement about the design in Sections 1–5 was checked against the code (`esi/*.py`) and `configs/small.json`. Numbers in Appendices A and B were generated directly from saved result files.

**Sources for the 20-seed results (Section 6).** These come from three files in the project owner's repository:

- `results/rerun/results.md` (provided as text): operational metrics, the original unit-level intervals, and the per-seed table;
- `results/validation_clustered_ci/rerun/clustered_ci.md` (provided as text);
- `results/validation_clustered_ci/rerun/clustered_ci.csv` (provided as the file): **all statistics in Sections 6.2 and 6.3** are taken from this file at full precision.

All nine rows of `clustered_ci.csv` were checked against the report. This covers the estimates, the per-seed t-intervals, the seed-cluster and two-stage bootstrap intervals, the seed counts, and the exact sign-flip p-values. All values rounded to one decimal agree with `clustered_ci.md`, and the Holm correction in Section 6.3 was computed from the CSV p-values.

Values from `results.md` carry that file's rounding. `metrics_by_seed.csv`, `paired_differences.csv`, `config.json` and `environment.json` from the 20-seed run were **not** available.

The sources were also cross-checked against each other:
- the pooled estimates agree;
- the per-seed counts of "first arm cheaper" agree with the per-seed table in `results.md`;
- cost components sum to the reported totals to within ±1 (rounding).

Discrepancies are listed in Section 9.

---

## 1. Research question and motivation

**Research question.** Does training a demand forecaster on event information *as it would actually be available at ordering time* reduce the inventory-cost harm caused by imperfect event signals?

**Motivation.** Retail demand forecasters often use calendar or event features (holidays, festivals, promotions, local events). These features are commonly built from a clean, after-the-fact event calendar. At ordering time, however, event information can be missing, late, false, or mislabelled.

A model fitted on clean calendars may trust event features fully and then react strongly to signals that turn out to be wrong. For perishable products, over-ordering on a false signal becomes waste, and under-reacting to a missed event becomes lost sales. The study asks whether training on signals with realistic errors reduces that harm when forecasts are turned into orders.

The study measures **operational outcomes** (inventory cost, lost sales, waste), not only forecast accuracy.

**Scope of claims.** This is a controlled simulation. No claim is made about novelty relative to prior literature, about real-world effectiveness, or about patentability. The related literature has not been systematically verified for this module.

## 2. Hypotheses

These working hypotheses were set while the prototype was designed. They were **not formally pre-registered**.

- **H1 (clean information):** with accurate event signals, event-aware forecasting (arms B and C, which are identical in this condition) has lower total cost than event-blind forecasting (arm A).
- **H2 (imperfect information):** with imperfect signals, the arm trained on as-available signals (C) has lower total cost than the arm trained on the true calendar and served imperfect signals (B).
- **H3 (exploratory):** with imperfect signals, C has lower total cost than ignoring events altogether (A). The design does not guarantee this. It depends on how unreliable the signal is.

## 3. Experimental design

### 3.1 Synthetic demand (`esi/generator.py`)

Each simulated "world" contains 40 SKUs observed over 730 days. Daily demand follows a negative-binomial distribution with mean

μ(i, t) = base(i) × weekday(i, t mod 7) × trend(i, t) × exp(uplift(i, k(t)))

where k(t) is the event type active on day t (0 means no event).

Parameters from `configs/small.json`:

| Component | Setting |
|---|---|
| Base mean | log-normal, median 12, log-sd 0.6 |
| Weekday profile | log-sd 0.15, normalised to mean 1 |
| Linear trend | relative slope sd 0.2, floored at 0.3 |
| Negative-binomial dispersion | 8 |
| Event types | 3, with mean log-uplifts 0.4, 0.8, 1.2 (about ×1.49, ×2.23, ×3.32 before SKU-level variation) |
| SKU-level uplift deviation | sd 0.3 |
| SKUs that don't respond to events | 20% |
| True events | non-overlapping, 1–3 days long, 7–21 days apart |

Demand is fully observed. There is no censoring by stockouts in the training data.

### 3.2 Event signals (`esi/signals.py`)

A signal is an announcement `(announce_day, start_day, duration, type)`. At forecast origin *t*, an announcement is usable only if `announce_day ≤ t`. This single rule prevents signal information from leaking backwards in time.

The error process for each condition (`configs/small.json`):

| Condition | Missed events (`p_miss`) | Late announcements (`p_late`) | False events per day (`spurious_rate`) | False events labelled as highest-uplift type (`p_misleading`) |
|---|---|---|---|---|
| clean | 0 | 0 | 0 | 0 |
| imperfect | 0.3 | 0.3 | 0.04 | 0.5 |
| false_alarm | 0.1 | 0 | 0.08 | 0.8 |

On-time announcements arrive 14 days before the event. Late announcements arrive on the event's start day. With lead time L = 2, a late signal can only help on the later days of a multi-day event.

False events start on uniformly random days, last 1–2 days (hard-coded), and are announced 14 days ahead. Non-misleading false events get a uniformly random type.

One signal realisation per seed and condition covers the training, validation and test periods. In the 5-seed run, the test period contained on average 10.0 true events and 10.0 / 13.2 / 26.4 announcements under clean / imperfect / false_alarm (`results/small/signal_counts.csv`).

### 3.3 Forecasting arms (`esi/forecasting.py`, `esi/experiment.py`)

All arms use the same model class, the same non-event features, the same quantile grid, and the same replenishment policy.

- **A, event-blind (`A_blind`):** no event features.
- **B, clean-trained (`B_clean_trained`):** trained with event features from the true calendar (every event announced 14 days ahead), then served the condition's imperfect signal on validation and test.
- **C, as-available-trained (`C_asavailable_trained`):** trained with event features from the training-period part of the same signal realisation it is served on validation and test.

Under the clean condition, B and C receive identical features. Their results must therefore be identical, which serves as an internal consistency check.

**Model.** The forecaster is scikit-learn's `HistGradientBoostingRegressor` with quantile loss. One model is fitted per quantile in {0.5, 0.65, 0.8, 0.9}, with `max_iter` 150, learning rate 0.08, `max_leaf_nodes` 15, and `min_samples_leaf` 40. A single model is pooled across SKUs, with the SKU id as a categorical feature.

**Target.** Cumulative demand over the protection window, days t to t+L (3 days), divided by the SKU's trailing 28-day mean plus 1.

**Features.** All demand features use only days before *t*:
- SKU id;
- weekday of the origin;
- 7-day and 28-day mean demand;
- a seasonal-naive window (same weekdays over the previous 4 weeks);
- the 28-day standard deviation;
- for B and C only, per-type counts of signalled days in the window that are visible at *t*.

The code rejects lead times L ≥ 7, because the seasonal-naive feature would otherwise reach day *t* or later.

### 3.4 Replenishment policy (`esi/inventory.py`)

All arms use one policy: an outdating-corrected order-up-to rule.

q_t = max(0, round(S_t − (IP_t − Ê_t)))

- **S_t:** the forecast τ-quantile of cumulative demand over days t to t+L.
- **IP_t:** on-hand stock plus orders in transit.
- **Ê_t:** the number of units projected to expire within the next L+1 days. It is computed by a FIFO projection that assumes daily demand equals the median forecast divided by L+1.

This is a heuristic policy. **It is not claimed to be optimal.**

### 3.5 Inventory simulation and costs

Each SKU is simulated separately, one day at a time, with lead time L = 2 days and shelf life m = 4 days. The daily sequence is:

1. Receive the order placed on day t−L. Received units can be sold on days t to t+3.
2. Place the order q_t.
3. Serve demand oldest-stock-first (FIFO). Unmet demand is lost; there are no backorders.
4. Unsold units on their last sellable day expire as waste.
5. All remaining stock ages by one day.

The daily cost is

C_t = 0.05 × (end-of-day on-hand units) + 1.0 × (lost units) + 0.6 × (expired units).

These are holding, shortage and waste costs. They are relative cost units chosen for the simulation, not monetary estimates. There is no ordering cost, no capacity or budget constraint, no substitution between SKUs, and no supplier uncertainty.

Initial stock at the start of each simulated period is the 28-day mean demand before that period times L, rounded.

### 3.6 Data split and model selection

| Period | Days | Use |
|---|---|---|
| Training | forecast origins 28–417 (390 origins per SKU); every target window ends by day 419 | Model fitting only |
| Validation | days 420–559 (140 days) | Choosing τ only |
| Test | days 560–727 (168 days; the first 7 are excluded as warm-up, leaving 161 evaluated days) | Evaluated once with the chosen τ |

τ is chosen separately for each arm, condition and seed. It is the grid value that minimises total simulated validation cost over all SKUs, after excluding the first 7 validation days.

Models are not refitted on training plus validation data. The test period is never used for fitting or selection. A test confirms that corrupting test-period demand leaves τ and validation cost unchanged.

### 3.7 Metrics

**Operational metrics** (test period, summed over SKUs):
- total cost and its holding, shortage and waste components;
- lost units and expired (waste) units;
- fill rate (units sold ÷ units demanded);
- waste rate (expired ÷ received);
- cost on days near true events versus other days.

**Forecast metrics:**
- WAPE of the median window forecast;
- pinball loss at the selected τ, divided by mean window demand.

Forecast metrics are diagnostic only. The primary outcome is **total test-period cost**.

### 3.8 Statistical analysis

**Paired comparisons.** For each condition, three comparisons are made: C vs B, C vs A, and B vs A. Each is summarised by the relative difference in summed test cost:

(Σ cost_first − Σ cost_second) / Σ cost_second

A negative value means the first arm is cheaper.

**Original intervals** (`experiment.paired_differences`, reported in each run's `paired_differences.csv` and `results.md`). These come from a percentile bootstrap (2,000 replicates, seed 12345) that resamples (seed, SKU) units independently.

This method **ignores dependence within a seed**. All SKUs in one seed share the same demand world, event calendar and signal realisation, so their cost differences are correlated. Because the intervals treat 40 × n_seeds correlated units as independent, they are too narrow.

**Primary uncertainty assessment** (`esi/clustered_ci.py`, which re-analyses a run's `metrics_by_sku.csv` without re-running the simulation). It reports:

1. a bootstrap that resamples whole seeds;
2. a two-stage bootstrap that resamples seeds and then SKUs within each drawn seed;
3. a 95% t-interval of the per-seed relative differences, with n_seeds − 1 degrees of freedom;
4. the number of seeds in which the first arm is cheaper;
5. an exact two-sided sign-flip test on the per-seed relative differences.

Seeds are the independent replications, so this report treats the **seed-level analysis as primary**. Specifically, the per-seed t-interval and sign-flip test are primary, and the two-stage bootstrap is secondary.

The per-seed t-interval is centred on the **mean of the per-seed relative differences** (`seed_mean` in `clustered_ci.csv`). The headline estimate is the **pooled** relative difference in summed cost (`rel_cost_diff`). The two differ because seeds with higher total cost weigh more in the pooled figure, so Section 6.2 reports both.

**Decision rule.** A comparison is called *statistically supported* only if the per-seed 95% t-interval excludes 0 **and** the sign-flip p-value is below 0.05. A pooled cost difference that doesn't meet this rule is reported as *descriptive only*.

The rule's reachability depends on the number of seeds:
- With 5 seeds, the smallest attainable sign-flip p-value is 2/2⁵ = 0.0625, so no 5-seed comparison can meet the rule.
- With 20 seeds, the minimum is 2/2²⁰ ≈ 1.9 × 10⁻⁶.

---

## 4. Implementation checks relevant to validity

The test suite (`tests/`) covers:
- inventory balance;
- lead-time arrival;
- exact expiry timing;
- FIFO versus LIFO (confirmed by a mutation check);
- lost sales;
- announcement-time visibility and late-signal timing;
- feature invariance to same-day and future demand;
- order invariance to same-day and future demand;
- training targets staying inside the training period;
- τ selection being unaffected by changes to test-period demand;
- empirical signal error rates matching the configuration;
- identical test demand across arms, and B equal to C under clean signals;
- reproducibility of runs;
- the clustered-interval calculations.

According to the project owner, all 32 tests pass. That was not re-run for this report.

## 5. Conditions: what each one tests

- **Clean:** whether event information is worth using at all when it is accurate. This is H1, and also a sanity check, since B must equal C.
- **Imperfect:** a mix of all four error types (missed, late, false, misleading). It tests H2 and H3 under moderate signal degradation.
- **False alarm:** a condition dominated by false events, most of them labelled as the highest-uplift type. It tests how strongly B over-reacts and whether C limits the harm. It is **not** a pure false-alarm condition, because it also has 10% missed events and 80% misleading labels.

---

## 6. Results: 20-seed run (`results/rerun`, seeds 0–19; primary)

40 SKUs per seed. 168 test days, of which the first 7 are excluded as warm-up. Recorded runtime 947 s. Costs are summed over SKUs; values are mean ± standard deviation across the 20 seeds.

Source: `results/rerun/results.md`.

### 6.1 Operational and forecast metrics

| Condition | Arm | Total cost | Shortage | Waste | Holding | Lost units | Waste units | Fill rate | WAPE (median) | Pinball (norm.) | Selected τ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 17748 ± 3065 | 11397 ± 2781 | 1026 ± 721 | 5325 ± 1113 | 11397 ± 2781 | 1709 ± 1202 | 0.889 ± 0.025 | 0.289 ± 0.022 | 0.131 ± 0.018 | 0.815 ± 0.037 |
| clean | B_clean_trained | 11208 ± 1402 | 4411 ± 833 | 1358 ± 519 | 5438 ± 673 | 4411 ± 833 | 2264 ± 865 | 0.957 ± 0.006 | 0.228 ± 0.006 | 0.060 ± 0.007 | 0.895 ± 0.022 |
| clean | C_asavailable_trained | 11208 ± 1402 | 4411 ± 833 | 1358 ± 519 | 5438 ± 673 | 4411 ± 833 | 2264 ± 865 | 0.957 ± 0.006 | 0.228 ± 0.006 | 0.060 ± 0.007 | 0.895 ± 0.022 |
| imperfect | A_blind | 17748 ± 3065 | 11397 ± 2781 | 1026 ± 721 | 5325 ± 1113 | 11397 ± 2781 | 1709 ± 1202 | 0.889 ± 0.025 | 0.289 ± 0.022 | 0.131 ± 0.018 | 0.815 ± 0.037 |
| imperfect | B_clean_trained | 17992 ± 4218 | 8305 ± 3442 | 3777 ± 1514 | 5910 ± 1197 | 8305 ± 3442 | 6295 ± 2523 | 0.919 ± 0.034 | 0.296 ± 0.026 | 0.100 ± 0.028 | 0.855 ± 0.051 |
| imperfect | C_asavailable_trained | 17134 ± 3618 | 9598 ± 3979 | 2092 ± 1027 | 5444 ± 1080 | 9598 ± 3979 | 3487 ± 1711 | 0.908 ± 0.033 | 0.280 ± 0.023 | 0.112 ± 0.024 | 0.823 ± 0.062 |
| false_alarm | A_blind | 17748 ± 3065 | 11397 ± 2781 | 1026 ± 721 | 5325 ± 1113 | 11397 ± 2781 | 1709 ± 1202 | 0.889 ± 0.025 | 0.289 ± 0.022 | 0.131 ± 0.018 | 0.815 ± 0.037 |
| false_alarm | B_clean_trained | 20521 ± 3499 | 6955 ± 2163 | 6687 ± 2353 | 6880 ± 1501 | 6955 ± 2163 | 11144 ± 3922 | 0.932 ± 0.019 | 0.357 ± 0.042 | 0.126 ± 0.031 | 0.785 ± 0.078 |
| false_alarm | C_asavailable_trained | 17121 ± 2797 | 9176 ± 3040 | 2542 ± 1475 | 5403 ± 1234 | 9176 ± 3040 | 4237 ± 2458 | 0.911 ± 0.028 | 0.278 ± 0.021 | 0.112 ± 0.022 | 0.813 ± 0.056 |

Arm A uses no event signals, so its results are the same in every condition. Under the clean condition B and C are identical by design.

Mean event counts in the test period were 10.4 true events, with 10.4 / 13.8 / 23.6 announcements under clean / imperfect / false_alarm. Announcements include false events.

### 6.2 Paired comparisons

The pooled estimate is the relative difference in summed test cost; negative means the first arm is cheaper. The mean per-seed difference is the centre of the per-seed t-interval (Section 3.8).

- **Primary evidence:** the per-seed 95% t-interval (19 degrees of freedom) and the exact sign-flip p-value, both from `results/validation_clustered_ci/rerun/clustered_ci.csv`.
- **Secondary:** the two-stage bootstrap, from the same file.
- **Original method, for reference only:** the unit-level bootstrap from `results/rerun/results.md` (`paired_differences`), as displayed there.

"Supported" means the Section 3.8 rule is met: the t-interval excludes 0 **and** p < 0.05. Sign-flip p-values are multiples of 1/2²⁰ and are given exactly where they fall below 0.001.

| Condition | Comparison | Pooled estimate | Mean per-seed difference | Per-seed t-interval | Sign-flip p | Seeds first cheaper | Two-stage bootstrap | Original unit-level CI | Supported? |
|---|---|---|---|---|---|---|---|---|---|
| clean | C vs B | +0.0% | +0.00% | [+0.00%, +0.00%] | 1.000 | 0/20 | [+0.0%, +0.0%] | [+0.000%, +0.000%] | Consistency check, not a finding |
| clean | C vs A | −36.9% | −36.21% | [−38.68%, −33.75%] | 1.9 × 10⁻⁶ (= 2/2²⁰) | 20/20 | [−39.2%, −34.2%] | [−38.168%, −35.492%] | **Yes** |
| clean | B vs A | −36.9% | −36.21% | [−38.68%, −33.75%] | 1.9 × 10⁻⁶ (= 2/2²⁰) | 20/20 | [−39.1%, −34.4%] | [−38.222%, −35.483%] | **Yes** |
| imperfect | C vs B | −4.8% | −4.09% | [−8.09%, −0.08%] | 0.047 | 15/20 | [−8.5%, −0.8%] | [−6.040%, −3.458%] | **Yes, marginally**; not after Holm (6.3) |
| imperfect | C vs A | −3.5% | −3.73% | [−7.73%, +0.27%] | 0.063 | 15/20 | [−7.7%, +0.5%] | [−4.841%, −2.162%] | **No** |
| imperfect | B vs A | +1.4% | +0.95% | [−4.38%, +6.29%] | 0.716 | 11/20 | [−4.0%, +7.1%] | [−0.292%, +3.101%] | No |
| false_alarm | C vs B | −16.6% | −16.13% | [−19.63%, −12.64%] | 1.9 × 10⁻⁶ (= 2/2²⁰) | 20/20 | [−20.5%, −13.3%] | [−17.947%, −15.141%] | **Yes** |
| false_alarm | C vs A | −3.5% | −2.85% | [−8.25%, +2.55%] | 0.287 | 15/20 | [−7.7%, +1.9%] | [−4.982%, −2.085%] | **No** |
| false_alarm | B vs A | +15.6% | +16.91% | [+8.21%, +25.60%] | 1.5 × 10⁻⁴ (= 160/2²⁰) | 2/20 | [+8.2%, +23.8%] | [+13.066%, +18.303%] | **Yes** (B costs more than A) |

The three p-values of 2/2²⁰ ≈ 1.9 × 10⁻⁶ are the smallest attainable with 20 seeds. They occur because all 20 per-seed differences have the same sign. False-alarm B vs A has p = 160/2²⁰ ≈ 1.5 × 10⁻⁴, with B cheaper than A in only 2 of 20 seeds.

### 6.3 Statistical conclusions

**Supported** by the decision rule:
- **Clean signals:** event-aware forecasting (B = C) cost less than event-blind forecasting (A): −36.9%, cheaper in 20 of 20 seeds. This supports H1.
- **False-alarm signals:**
  - C cost less than B: −16.6%, cheaper in 20 of 20 seeds. This supports H2 for this condition.
  - B cost more than A: +15.6%, B cheaper in only 2 of 20 seeds. Clean-calendar training combined with false-alarm-heavy signals was worse than ignoring events.

**Marginal:**
- **Imperfect signals, C vs B:** −4.8%, cheaper in 15 of 20 seeds. It meets the decision rule only narrowly: the t-interval is [−8.09%, −0.08%] and the exact p is 0.0470.
- The decision rule does not adjust for multiple comparisons. The table below applies Holm's step-down correction (family-wise α = 0.05) to the eight non-trivial comparisons, using the exact p-values from `clustered_ci.csv`. Clean C vs B is excluded because the two arms are identical by design.

| Holm rank | Comparison | Exact sign-flip p | Holm threshold 0.05 / (8 − rank + 1) | Holm-adjusted p | Decision |
|---|---|---|---|---|---|
| 1 | clean C vs A | 1.9 × 10⁻⁶ (= 2/2²⁰) | 0.00625 | 1.5 × 10⁻⁵ | Reject |
| 2 | clean B vs A | 1.9 × 10⁻⁶ (= 2/2²⁰) | 0.00714 | 1.5 × 10⁻⁵ | Reject |
| 3 | false_alarm C vs B | 1.9 × 10⁻⁶ (= 2/2²⁰) | 0.00833 | 1.5 × 10⁻⁵ | Reject |
| 4 | false_alarm B vs A | 1.5 × 10⁻⁴ (= 160/2²⁰) | 0.01000 | 7.6 × 10⁻⁴ | Reject |
| 5 | imperfect C vs B | 0.047 | 0.01250 | 0.188 | **Not rejected; the procedure stops here** |
| 6 | imperfect C vs A | 0.063 | 0.01667 | 0.189 | Not rejected |
| 7 | false_alarm C vs A | 0.287 | 0.02500 | 0.574 | Not rejected |
| 8 | imperfect B vs A | 0.716 | 0.05000 | 0.716 | Not rejected |

- Holm's procedure (family-wise α = 0.05), applied to the exact p-values from `clustered_ci.csv`, rejects the null hypothesis for exactly four comparisons: clean C vs A, clean B vs A, false-alarm C vs B, and false-alarm B vs A.
- Imperfect C vs B is the first comparison not rejected. Its exact p = 0.0470 exceeds its threshold of 0.0125, and its Holm-adjusted p is 0.188.
- Clean C vs A and clean B vs A are the same comparison here, so including both makes the correction slightly more conservative.
- Imperfect C vs B should therefore be called *weak evidence* for H2 under imperfect signals, not a firm result.

**Not supported:**
- **C vs A under imperfect signals:** −3.5% pooled and cheaper in 15 of 20 seeds, but the t-interval [−7.73%, +0.27%] includes 0 and p = 0.063. C cost more than A in 5 of 20 seeds. **The results do not show that C consistently beats A under imperfect signals.** H3 is not supported.
- **C vs A under false-alarm signals:** −3.5% pooled, t-interval [−8.25%, +2.55%], p = 0.287. Not supported.
- **B vs A under imperfect signals:** +1.4%, p = 0.716. No difference supported.

**Original intervals overstated certainty.** For all three C vs A and B vs A comparisons under imperfect and false-alarm signals, the unit-level bootstrap intervals (`results.md`) excluded 0 or nearly did, while the seed-level intervals include 0. This happens because those intervals treat 800 correlated seed–SKU units as independent.

### 6.4 Descriptive patterns

The cost components show how the arms differ:
- Under clean signals, event awareness cut shortage cost from 11,397 to 4,411 at the price of more waste (1,026 → 1,358).
- Under imperfect and false-alarm signals, C's advantage over B came from much lower waste cost (2,092 vs 3,777 imperfect; 2,542 vs 6,687 false alarm) and lower holding cost. This was partly offset by higher shortage cost (9,598 vs 8,305; 9,176 vs 6,955).
- This pattern is consistent with B over-ordering on false announcements and C learning to discount them. It is a descriptive interpretation, not a tested mechanism.
- Forecast accuracy followed the same ordering. B's median-forecast WAPE under false alarms (0.357) was worse than A's (0.289).

---

## 7. Discussion

**Main findings (20 seeds; Section 6).**

1. Accurate event information was clearly valuable in this simulation.
2. When signals contained many false alarms, a forecaster trained on the clean calendar did worse than ignoring events. A forecaster trained on as-available signals avoided most of that harm.
3. With moderate, mixed signal errors (the imperfect condition), the advantage of as-available training over clean-calendar training was small, and its statistical support is marginal.
4. In neither imperfect condition did as-available training produce a statistically supported improvement over ignoring events. The answer to the research question is therefore qualified:
   - training on as-available signals **reduced the cost harm of imperfect signals relative to clean-calendar training**, firmly so for false-alarm-heavy signals and weakly for mixed errors;
   - it was **not shown to make imperfect signals worth using** compared with an event-blind forecaster.

**Relationship to the earlier 5-seed results** (Appendix A; descriptive only). The 5-seed run pointed in the same direction for clean C vs A (−31.4%), false-alarm C vs B (−17.1%) and imperfect C vs B (−8.8%). For false-alarm C vs A, however, its pooled estimate was +5.2%, whereas the 20-seed estimate is −3.5%; neither is statistically supported. The sign change shows how unstable that comparison is at small seed counts.

The 20-seed values for seeds 0–4 are not identical to the 5-seed run because the two runs used different scikit-learn versions (Section 9, item 3), so the 5-seed run is not an exact subset of the 20-seed run.

**False-alarm sensitivity sweep** (Appendix B; 5 seeds, descriptive only). As the false-alarm rate rose from 0 to 0.20, C's pooled advantage over A shrank and then reversed, while its advantage over B grew. This sweep was not repeated with 20 seeds, so these patterns remain hypotheses.

## 8. Limitations and threats to validity

1. **Synthetic data only.** Demand, events and signal errors come from a generator written for this study. Effect sizes reflect its assumptions, such as negative-binomial noise, multiplicative event effects, and uniformly placed false events.
2. **Selected simulation parameters.** The results cover one lead time (2 days), one shelf life (4 days), one cost structure (0.05 / 1.0 / 0.6), one SKU count, and three hand-chosen signal conditions. Only the false-alarm rate was varied, and only with 5 seeds.
3. **Partly favourable design for C.** C is trained and evaluated on the same signal-error process. Its advantage under a *shift* in that process (training errors differing from deployment errors) has not been tested.
4. **Number of replications.** Twenty independent seeds is still a modest number of clusters. Seed-cluster bootstraps with few clusters can understate uncertainty, which is why the per-seed t-interval is primary.
5. **Shared heuristic policy.** All arms use one outdating-corrected order-up-to rule, with τ chosen from a coarse 4-point grid. In the 5-seed run, 17 of 45 arm–condition–seed selections were at the top of the grid (0.9). In the 20-seed run, the mean selected τ for B and C under clean signals was 0.895, close to the top of the grid. Comparisons among forecasting arms are conditional on this policy; a different or optimised policy could change the size or direction of the differences.
6. **Simplified operations.** There is one SKU per simulation with no interactions, no ordering costs or constraints, no supplier variability, and no censoring. FIFO selling is assumed.
7. **No external validation.** The method has not been tested on real retail data. No claim of real-world effectiveness is made.
8. **Literature not verified.** No systematic literature review was done for this module, and no novelty claim is made.

## 9. Inconsistencies and open issues found while preparing this report

1. **Some 20-seed files were not inspected.** The statistics in Sections 6.2–6.3 were verified against `results/validation_clustered_ci/rerun/clustered_ci.csv`. However, `config.json`, `environment.json`, `metrics_by_seed.csv` and `paired_differences.csv` from the 20-seed run were not available. As a result:
   - the operational metrics in Section 6.1 and the original unit-level intervals carry the rounding of `results.md`;
   - only the settings visible in `results.md` could be checked against `configs/small.json`: 40 SKUs, 168 test days, 7 warm-up days, and the three condition names. The remaining parameters were not confirmed.
2. **Seed count, now resolved.** An earlier project message described `results/rerun/` as a five-seed run. `results/rerun/results.md` records seeds 0–19 (20 seeds).
3. **Seeds 0–4 of the 20-seed run do not reproduce the 5-seed run: resolved, the cause is the scikit-learn version.** For clean C vs A, seeds 0–4 give −31.7%, −31.5%, −30.9%, −36.8%, −25.0% in `results/rerun/results.md`, against −31.1%, −31.4%, −30.3%, −36.7%, −24.7% in `results/small/results.md`. The configurations are identical apart from the seed list. `results/small/environment.json` records scikit-learn 1.9.1 (with numpy 2.4.6 and pandas 3.1.0), while `results/rerun/` used scikit-learn 1.8.0 (numpy 2.4.4, pandas 3.0.2); both used Python 3.11.9. `results/final/`, a 5-seed run under the same versions as the 20-seed run, matches its seeds 0–4 exactly. Controlled re-runs show that changing scikit-learn alone reproduces the difference, while numpy and pandas have no effect. The details are in `results/reproducibility_check.md`. The two runs remain separate experiments, not a subset and a superset.
4. **No 20-seed configuration is committed.** `configs/small.json` lists seeds 0–4, and there is no 20-seed config in `configs/`. The configuration used is recorded only in `results/rerun/config.json`.
5. **Unit-level intervals appear in two places with slightly different values.** `clustered_ci.md` recomputes the original unit-level bootstrap with its own random stream. For example, imperfect B vs A is [−0.292%, +3.101%] in `results/rerun/results.md` and [−0.4%, +3.1%] in `clustered_ci.md`. The original method's official values are those in `results.md` / `paired_differences.csv`. Either way, these intervals are not the primary evidence.
6. **The per-comparison decision rule is unadjusted for multiple comparisons.** The Section 3.8 decision rule tests each comparison at 0.05. Section 6.3 applies a Holm correction to all eight non-trivial comparisons using the exact CSV p-values. Four comparisons survive it (exact p ≤ 1.5 × 10⁻⁴); imperfect C vs B (p = 0.0470) does not.
7. **The root `README.md` still reports the 5-seed results.** The module README has been updated to the 20-seed results; the root README's "Research Contribution" section has not.
8. **The sign-flip test enumerates every sign pattern.** `clustered_ci.signflip_p` builds all 2ⁿ patterns: about 1.05 million for 20 seeds. That is feasible, but a Monte Carlo version would be needed for many more seeds.
9. **The 5-seed results were produced from an uncommitted worktree.** `results/small/environment.json` records commit `f7450f0` with `git_worktree_dirty: true`. The 20-seed run (`results/rerun/`) records commit `ace2edb`, also with a dirty worktree; no file under `esi/` that affects results changed between those commits.

## 10. Reproducibility

**Environment.** Python 3.11 or newer, in a separate virtual environment, with `research/event_signal_inventory/requirements.txt`: numpy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0, scipy 1.17.1, pytest 9.1.1. These are the versions of the 20-seed run, with Python 3.11.9. The earlier 5-seed run used scikit-learn 1.9.1, numpy 2.4.6 and pandas 3.1.0 (`results/small/environment.json`), which is why its numbers differ (Section 9, item 3).

**Commands supported by the repository.** Run these from `research/event_signal_inventory`, and write to a new output directory so existing results are not overwritten:

```bash
python -m pytest -q tests
# re-run the 20-seed experiment from its recorded configuration
python -m esi.experiment --config results/rerun/config.json --out results/rerun_reproduction
# seed-clustered analysis of a results directory
python -m esi.clustered_ci --results results/rerun --out results/validation_clustered_ci/rerun_reproduction
# earlier 5-seed run and its clustered analysis
python -m esi.experiment --config configs/small.json --out results/small_reproduction
python -m esi.clustered_ci --results results/small --out results/validation_clustered_ci/small_reproduction
# false-alarm sensitivity sweep (5 seeds)
python -m esi.sensitivity --config configs/sensitivity_false_alarm.json --out results/sensitivity_false_alarm_reproduction
```

The `--config results/rerun/config.json` form works because `esi/experiment.py` writes the complete run configuration to `config.json`, and its command-line entry point accepts any such file.

All randomness comes from the configured seeds. Re-running `configs/small.json` in the same environment reproduced `metrics_by_seed.csv` exactly. A different scikit-learn version changes the gradient-boosting fits and therefore the numbers; this is why seeds 0–4 of the 20-seed run do not match the 5-seed run (Section 9, item 3).

**Files used for this report**

| Role | Path (relative to `research/event_signal_inventory/`) | Available here |
|---|---|---|
| Implementation | `esi/generator.py`, `esi/signals.py`, `esi/forecasting.py`, `esi/inventory.py`, `esi/experiment.py`, `esi/clustered_ci.py`, `esi/sensitivity.py` | yes |
| Configuration | `configs/small.json`, `configs/sensitivity_false_alarm.json` | yes |
| 20-seed results (Section 6.1, original intervals) | `results/rerun/results.md` | provided as text; `metrics_by_seed.csv`, `paired_differences.csv`, `config.json` and `environment.json` not inspected |
| 20-seed clustered analysis (Sections 6.2–6.3) | `results/validation_clustered_ci/rerun/clustered_ci.csv` (and `clustered_ci.md`) | yes: CSV provided; all values verified |
| 5-seed results (Appendix A) | `results/small/metrics_by_seed.csv`, `results/small/signal_counts.csv`, `results/small/environment.json` | yes |
| 5-seed clustered analysis (Appendix A) | `results/validation_clustered_ci/small/clustered_ci.csv` | yes |
| Sensitivity clustered analysis (Appendix B) | `results/validation_clustered_ci/sensitivity_false_alarm/clustered_ci.csv` | yes |
| Documentation | `README.md` (module) | yes, updated to match this report |

---

## Appendix A. Earlier 5-seed run (`results/small`, seeds 0–4; descriptive only)

*These are not the 20-seed results.* The tables are generated from `results/small/metrics_by_seed.csv` (seed means; costs summed over 40 SKUs and 161 evaluated test days) and `results/validation_clustered_ci/small/clustered_ci.csv`.

**A.1 Operational and forecast metrics (mean over 5 seeds)**

| Condition | Arm | Total cost | Holding | Shortage | Waste | Lost units | Waste units | Fill rate | WAPE (median) | Pinball (norm.) | Mean selected τ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 16,239 | 4,978 | 10,554 | 707 | 10,554 | 1,178 | 0.898 | 0.276 | 0.125 | 0.80 |
| clean | B_clean_trained | 11,142 | 5,308 | 4,648 | 1,186 | 4,648 | 1,977 | 0.955 | 0.226 | 0.059 | 0.90 |
| clean | C_asavailable_trained | 11,142 | 5,308 | 4,648 | 1,186 | 4,648 | 1,977 | 0.955 | 0.226 | 0.059 | 0.90 |
| imperfect | A_blind | 16,239 | 4,978 | 10,554 | 707 | 10,554 | 1,178 | 0.898 | 0.276 | 0.125 | 0.80 |
| imperfect | B_clean_trained | 17,208 | 6,069 | 7,489 | 3,650 | 7,489 | 6,084 | 0.929 | 0.285 | 0.088 | 0.88 |
| imperfect | C_asavailable_trained | 15,700 | 5,259 | 8,897 | 1,544 | 8,897 | 2,573 | 0.916 | 0.267 | 0.108 | 0.82 |
| false_alarm | A_blind | 16,239 | 4,978 | 10,554 | 707 | 10,554 | 1,178 | 0.898 | 0.276 | 0.125 | 0.80 |
| false_alarm | B_clean_trained | 20,605 | 7,253 | 6,402 | 6,950 | 6,402 | 11,583 | 0.936 | 0.357 | 0.117 | 0.82 |
| false_alarm | C_asavailable_trained | 17,086 | 5,815 | 7,863 | 3,408 | 7,863 | 5,680 | 0.924 | 0.270 | 0.107 | 0.82 |

**A.2 Paired comparisons.** Relative difference in summed test cost; negative means the first arm is cheaper. No 5-seed comparison can satisfy the Section 3.8 decision rule (minimum sign-flip p = 0.0625).

| Condition | Comparison | Estimate | Unit-level bootstrap (original method) | Two-stage bootstrap | Per-seed t-interval | Seeds first arm cheaper | Sign-flip p |
|---|---|---|---|---|---|---|---|
| clean | C vs B | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/5 | 1.0000 |
| clean | C vs A | -31.4% | [-33.8%, -29.0%] | [-35.3%, -26.6%] | [-36.2%, -25.5%] | 5/5 | 0.0625 |
| clean | B vs A | -31.4% | [-33.7%, -28.9%] | [-35.2%, -26.7%] | [-36.2%, -25.5%] | 5/5 | 0.0625 |
| imperfect | C vs B | -8.8% | [-11.9%, -5.9%] | [-15.3%, -2.8%] | [-14.7%, +0.5%] | 5/5 | 0.0625 |
| imperfect | C vs A | -3.3% | [-5.7%, -1.0%] | [-9.3%, +3.2%] | [-12.8%, +4.2%] | 4/5 | 0.2500 |
| imperfect | B vs A | +6.0% | [+1.8%, +10.3%] | [-5.9%, +19.9%] | [-14.7%, +22.2%] | 2/5 | 0.8125 |
| false_alarm | C vs B | -17.1% | [-20.2%, -13.6%] | [-22.9%, -11.0%] | [-25.0%, -8.9%] | 5/5 | 0.0625 |
| false_alarm | C vs A | +5.2% | [+1.9%, +8.9%] | [-3.4%, +18.3%] | [-10.5%, +23.3%] | 1/5 | 0.4375 |
| false_alarm | B vs A | +26.9% | [+19.8%, +34.4%] | [+10.4%, +46.6%] | [+3.5%, +54.4%] | 0/5 | 0.0625 |

## Appendix B. False-alarm sensitivity sweep (`results/sensitivity_false_alarm`, seeds 0–4; descriptive only)

This sweep varies only `spurious_rate`, starting from the clean condition (no misses, late or misleading signals); all other settings come from `configs/small.json`. The 0% condition reproduced the clean condition of `results/small` exactly (`results/sensitivity_false_alarm/baseline_check.csv`). Table generated from `results/validation_clustered_ci/sensitivity_false_alarm/clustered_ci.csv` (C comparisons only).

| Condition | Comparison | Estimate | Unit-level bootstrap (original method) | Two-stage bootstrap | Per-seed t-interval | Seeds first arm cheaper | Sign-flip p |
|---|---|---|---|---|---|---|---|
| spurious_rate=0 | C vs B | +0.0% | [+0.0%, +0.0%] | [+0.0%, +0.0%] | [+0.0%, +0.0%] | 0/5 | 1.0000 |
| spurious_rate=0 | C vs A | -31.4% | [-33.8%, -29.0%] | [-35.3%, -26.6%] | [-36.2%, -25.5%] | 5/5 | 0.0625 |
| spurious_rate=0.04 | C vs B | -4.4% | [-6.6%, -2.4%] | [-7.8%, -1.0%] | [-8.4%, +0.0%] | 4/5 | 0.1250 |
| spurious_rate=0.04 | C vs A | -22.6% | [-24.8%, -20.3%] | [-29.2%, -15.2%] | [-31.7%, -11.8%] | 5/5 | 0.0625 |
| spurious_rate=0.08 | C vs B | -4.6% | [-6.1%, -3.2%] | [-7.9%, -1.3%] | [-9.4%, +0.8%] | 4/5 | 0.1250 |
| spurious_rate=0.08 | C vs A | -8.3% | [-10.8%, -5.7%] | [-14.0%, -1.4%] | [-16.9%, +1.6%] | 4/5 | 0.1250 |
| spurious_rate=0.12 | C vs B | -7.1% | [-8.7%, -5.4%] | [-10.4%, -3.7%] | [-11.1%, -2.2%] | 5/5 | 0.0625 |
| spurious_rate=0.12 | C vs A | -4.5% | [-7.0%, -2.1%] | [-10.9%, +1.2%] | [-11.9%, +4.8%] | 4/5 | 0.3125 |
| spurious_rate=0.2 | C vs B | -15.0% | [-16.7%, -13.5%] | [-19.2%, -10.4%] | [-21.4%, -8.0%] | 5/5 | 0.0625 |
| spurious_rate=0.2 | C vs A | +6.8% | [+3.1%, +10.8%] | [-2.3%, +17.3%] | [-5.5%, +22.1%] | 1/5 | 0.1875 |
