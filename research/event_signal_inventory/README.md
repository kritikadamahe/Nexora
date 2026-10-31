# Event-signal quality and perishable replenishment — minimal research prototype

**Question.** Does training a demand forecaster on event information *as it would actually be available at ordering time* reduce the inventory-cost harm caused by imperfect event signals?

This directory is self-contained. It does not import from or modify the RetailEdge/Nexora application, its data, or its configuration.

## Setup and execution

**Requirements.** Python 3.11 or newer, because the pinned numpy 2.4 and pandas 3.0 need it. The recorded runs used Python 3.11.9; exact reproduction needs the pinned scikit-learn 1.8.0 (see `results/reproducibility_check.md`). Use a **separate virtual environment**: `requirements.txt` here pins versions that can differ from the main application's dependencies.

Windows (PowerShell), from the Nexora repository root:

```powershell
cd research\event_signal_inventory
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
cd research/event_signal_inventory
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -r requirements.txt
```

Then, from `research/event_signal_inventory` with the environment active:

```bash
python -m pytest -q tests                                                  # 32 tests, ~10 s
python -m esi.experiment --config configs/smoke.json --out results/smoke   # end-to-end check, ~3 s
python -m esi.experiment --config configs/small.json --out results/small_reproduction   # earlier 5-seed experiment, ~100 s on 1 CPU
```

Always write to a new folder, such as `results/small_reproduction` above. Writing to `results/small/` would overwrite the committed 5-seed results, and `results/rerun/` holds the final 20-seed results.

The final 20-seed experiment can be reproduced from its recorded configuration. Its seed-level uncertainty analysis is produced by `esi/clustered_ci.py`. Write to new directories so existing results are kept:

```bash
python -m esi.experiment --config results/rerun/config.json --out results/rerun_reproduction
python -m esi.clustered_ci --results results/rerun --out results/validation_clustered_ci/rerun_reproduction
```

Every run writes the following files to `--out`:

| File | Contents |
|---|---|
| `config.json` | Exact configuration, including seeds |
| `environment.json` | Python and library versions, git commit, and whether the worktree had uncommitted changes. The 5-seed results (`results/small/environment.json`) show `git_worktree_dirty: true` because `research/` was not yet committed when they were produced. The 20-seed run's `environment.json` was not inspected for this documentation. |
| `metrics_by_seed.csv` | Per seed × condition × arm metrics |
| `metrics_by_sku.csv` | Per-SKU metrics |
| `metrics_summary.csv` | Mean and standard deviation per condition × arm |
| `paired_differences.csv` | Paired arm comparisons with bootstrap intervals |
| `signal_counts.csv` | True events and announcements in the test period |
| `results.md` | The tables reproduced in the Results section below |

`results/small_stdout.log` is the console output of the recorded 5-seed run (`results/small/`).

**Determinism.** All randomness comes from the seeds in the config: the world, the signals, the models, and the bootstrap. Re-running `configs/small.json` in the same environment reproduced `metrics_by_seed.csv` exactly. A different scikit-learn version changes the gradient-boosting fits and therefore the numbers. This is why seeds 0–4 of the 20-seed run (scikit-learn 1.8.0) do not match the 5-seed run (1.9.1); see `results/reproducibility_check.md`.

## Sensitivity analysis: false-alarm rate

```bash
python -m esi.sensitivity --config configs/sensitivity_false_alarm.json --out results/sensitivity_false_alarm_reproduction
```

The recorded sweep results are in `results/sensitivity_false_alarm/`. Writing to that folder would overwrite them.

This takes about 170 s on 1 CPU. `esi/sensitivity.py` builds one condition per value of `spurious_rate` (expected spurious event announcements per day: 0, 0.04, 0.08, 0.12, 0.20). It starts from the `clean` condition, so p_miss = p_late = p_misleading = 0, and takes every other setting unchanged from `configs/small.json`: the world, splits, arms, policy, costs, τ grid, and the 5 seeds. It then calls the unchanged `experiment.run`.

These conditions isolate false alarms, so they are **not** the same as the earlier `false_alarm` condition. That condition also had 10% missed events and 80% misleading labels.

Outputs:
- the standard run files;
- `sensitivity_results.md` (tables);
- `per_seed_relative_cost.csv`;
- `baseline_check.csv`, which compares the 0% condition with `clean` in `results/small/metrics_by_seed.csv`;
- `sensitivity_spec.json`.

## What is implemented

| File | Contents |
|---|---|
| `esi/generator.py` | Negative-binomial daily demand: SKU base level × weekday profile × linear trend × event multiplier. Event uplifts vary by type and by SKU, and 20% of SKUs don't respond to events. Events are non-overlapping, last 1–3 days, and are 7–21 days apart. |
| `esi/signals.py` | Announcements `(announce_day, start, duration, type)`. At origin *t* only announcements with `announce_day ≤ t` are visible. Error process: missed events (`p_miss`), late announcements on the event's start day (`p_late`), spurious events (`spurious_rate`), and spurious events labelled as the highest-uplift type (`p_misleading`). |
| `esi/inventory.py` | Daily single-SKU simulator. Stock is tracked by remaining shelf life, sold FIFO, and lost when unavailable; orders arrive after lead time *L*; unsold units on their last day expire. Costs are holding (per unit-day on hand), shortage (per lost unit), and waste (per expired unit). The shared replenishment policy is an outdating-corrected order-up-to rule: `q = max(0, S − (inventory position − projected FIFO expiry over L+1 days))`. It is a heuristic and is not claimed to be optimal. |
| `esi/forecasting.py` | Pooled `HistGradientBoostingRegressor(loss="quantile")`, one model per quantile level. The target is cumulative demand over days *t..t+L*. Features use only demand before *t*, scaled by the trailing 28-day mean: SKU id, weekday, 7- and 28-day means, a seasonal-naive window, and volatility. Event arms add per-type counts of signalled days in the window. LightGBM wasn't installed, so scikit-learn is used instead. |
| `esi/sensitivity.py` | One-factor sensitivity sweep over a single signal-error parameter. It reuses `experiment.run` unchanged and compares the zero-error point with a baseline run. |
| `esi/clustered_ci.py` | Seed-level uncertainty for an existing results directory: seed-cluster and two-stage bootstraps, per-seed t-interval, and exact sign-flip test. It does not re-run any simulation. |
| `esi/experiment.py` | Runs the splits, arms, τ tuning, test simulation, metrics, paired bootstrap, and per-seed table. |

### Arms

The replenishment policy, features, and τ grid are identical across arms.

- **A_blind:** no event features.
- **B_clean_trained:** trained on the true event calendar (every event announced 14 days ahead), then served the imperfect signal.
- **C_asavailable_trained:** trained on the train-period part of the same signal realisation it is served with.

Under the `clean` condition, B and C see identical features and must produce identical results. This acts as a built-in consistency check.

### Protocol (small config)

The final 20-seed run (`results/rerun/`) records its configuration in `results/rerun/config.json`. No 20-seed config is committed in `configs/`.

- 5 seeds, 40 SKUs, 730 days.
- Splits:
  - Train: days 28–417. Training targets end before day 420.
  - Validation: days 420–559. The order-up-to quantile τ ∈ {0.5, 0.65, 0.8, 0.9} is chosen separately for each arm and condition by minimising validation simulation cost.
  - Test: days 560–727. Evaluated once with the selected τ; the first 7 days are excluded as warm-up.
- Models are not refit on train+validation.
- Lead time L = 2, shelf life 4 days. Costs: holding 0.05, shortage 1.0, waste 0.6 per unit.
- Initial stock at the start of each segment is set from pre-segment history only.
- Each day, the order is placed after the day's delivery is received and before that day's demand is served. Feature definitions are in `esi/forecasting.py`; the day sequence is in `esi/inventory.py`.

Signal conditions (`configs/small.json`). One signal realisation per seed and condition covers the train, validation and test periods:

| Condition | p_miss | p_late (announced on event start day) | spurious events per day | p_misleading |
|---|---|---|---|---|
| clean | 0 | 0 | 0 | 0 |
| imperfect | 0.3 | 0.3 | 0.04 | 0.5 |
| false_alarm | 0.1 | 0 | 0.08 | 0.8 |

On-time announcements arrive 14 days before the event. Arm B's training calendar announces every true event 14 days ahead.

### Metrics

- **Operational:** total cost, split into holding, shortage and waste; lost units; expired units; fill rate.
- **Forecast:** WAPE of the median window forecast, and pinball loss at the selected τ normalised by mean demand.
- **Paired comparisons:** relative difference in summed test cost between arms.
  - `esi/experiment.py` reports a 95% bootstrap CI over (seed, SKU) units. It ignores clustering by seed and is unadjusted for multiple comparisons.
  - The primary uncertainty assessment comes from `esi/clustered_ci.py`: per-seed t-intervals and exact sign-flip tests, with Holm's correction applied in `RESEARCH_REPORT.md`.

### Tests (`tests/`)

The tests cover inventory balance, lead-time arrival, exact expiry timing, FIFO versus LIFO, lost sales, the expiry projection and policy, announcement-time visibility, late-signal timing, misses and misleading labels, agreement between the vectorised and reference feature code, invariance of features to current and future demand, invariance to not-yet-announced signals, split boundaries, and generator reproducibility.

During development, two mutation checks confirmed the tests can fail: switching to LIFO broke the FIFO test, and removing the announcement-time filter broke three timing and leakage tests.

Later additions: `tests/test_sensitivity.py` covers sweep-config construction, rejection of invalid sweep specs, reproducibility, the zero-false-alarm point matching the clean baseline, and τ selection being unaffected by changes to test-period demand. `tests/test_validation.py` covers the lead-time leakage guard, orders being unaffected by same-day and future demand, empirical signal error rates, identical test demand across arms with B = C under clean signals, and the clustered-interval statistics.

## Assumptions and limitations

- **Simulation only.** Effect sizes depend on the generator and the error rates that were chosen, and say nothing about real retail. Because the error process that arm C is trained on is the same one it's evaluated on, C's advantage is partly built into the design. The open questions are how large that advantage is and whether it holds when the process shifts between training and deployment; shift is **not** tested yet.
- **Demand is fully observed** (no censoring). Real sales data would understate demand during stockouts.
- **Single SKU, single echelon.** No capacity or budget limits, no substitution, no ordering cost, no supplier variability.
- **One event at a time.** True events don't overlap; spurious events can overlap true ones.
- **Policy and τ.** The policy is one heuristic, and τ comes from a coarse 4-point grid. Several selected τ values sit at the top of the grid (0.9), so a wider grid could change the results.
- **Limited replication and scope.** The final experiment uses 20 independent seeds, one setting of (lead time, shelf life, costs), and two imperfect-signal conditions. The false-alarm sensitivity sweep has only 5 seeds.
- **Statistics.** The bootstrap intervals in `paired_differences.csv` and `results.md` treat (seed, SKU) units as independent, which makes them too narrow. Primary evidence is the seed-level analysis from `esi/clustered_ci.py`: per-seed t-intervals and exact sign-flip tests. The original unit-level bootstrap intervals are unadjusted for multiple comparisons. The primary seed-level comparisons use Holm's correction across the eight non-trivial comparisons at family-wise α = 0.05 (`RESEARCH_REPORT.md`, Section 6.3). The per-comparison rule (t-interval excludes 0 and p < 0.05) is reported alongside it.
- **No external validation.** Nothing has been tested on real retail data, and no claim of real-world effectiveness is made.

## Results

Full report: [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md). The **final experiment is the 20-seed run** (`results/rerun/`, seeds 0–19). The 5-seed run and the false-alarm sensitivity sweep are earlier, descriptive-only experiments.

### Final experiment: 20 seeds (`results/rerun/`)

Sources: `results/rerun/results.md` and `results/validation_clustered_ci/rerun/clustered_ci.csv`, from which all statistics below were verified at full precision.

The estimate is the pooled relative difference in summed test cost; negative means C is cheaper. The primary evidence is the per-seed 95% t-interval, centred on the mean per-seed difference, and the exact sign-flip p-value. A comparison is "supported" only if the t-interval excludes 0 and p < 0.05. The Holm column applies Holm's correction across the eight non-trivial comparisons at family-wise α = 0.05. This table is a selected summary of five comparisons; the full eight-comparison Holm table is in `RESEARCH_REPORT.md` (Section 6.3).

| Condition | Comparison | Estimate | Per-seed t-interval | Sign-flip p | Seeds C cheaper | Holm-adjusted p | Supported? |
|---|---|---|---|---|---|---|---|
| clean | C vs A (B is identical to C) | −36.9% | [−38.68%, −33.75%] | 1.9 × 10⁻⁶ (= 2/2²⁰) | 20/20 | 1.5 × 10⁻⁵ | Yes |
| imperfect | C vs B | −4.8% | [−8.09%, −0.08%] | 0.047 | 15/20 | 0.188 | Marginal: meets the per-comparison rule but not Holm's correction |
| imperfect | C vs A | −3.5% | [−7.73%, +0.27%] | 0.063 | 15/20 | 0.189 | **No** |
| false_alarm | C vs B | −16.6% | [−19.63%, −12.64%] | 1.9 × 10⁻⁶ (= 2/2²⁰) | 20/20 | 1.5 × 10⁻⁵ | Yes |
| false_alarm | C vs A | −3.5% | [−8.25%, +2.55%] | 0.287 | 15/20 | 0.574 | No |

What these results show:
- **Clean signals:** accurate event information clearly reduced cost.
- **Training on as-available signals reduced the cost harm of imperfect signals** compared with training on the clean calendar. The evidence is firm for false-alarm-heavy signals and weak for mixed errors.
- **Using imperfect signals was not shown to beat ignoring events.** Under imperfect signals, C cost more than A in 5 of 20 seeds, so the results do **not** show that C consistently beats A.
- **Clean-calendar training with false-alarm-heavy signals was worse than ignoring events:** B vs A was +15.6%, t-interval [+8.21%, +25.60%], p = 1.5 × 10⁻⁴ (= 160/2²⁰), Holm-adjusted p = 7.6 × 10⁻⁴.

The unit-level bootstrap intervals in `results/rerun/results.md` overstate certainty. For example, they exclude 0 for both C vs A comparisons, whereas the seed-level intervals do not.

Seeds 0–4 of the 20-seed run are not identical to the 5-seed run below, because the 5-seed run used scikit-learn 1.9.1 instead of 1.8.0 (`results/reproducibility_check.md`).

Simulation only; see the limitations above and in the report.

### Earlier 5-seed run (`results/small/`, seeds 0–4; descriptive only)

The tables below are copied verbatim from `results/small/results.md`. Their bootstrap intervals are unit-level and therefore too narrow. Seed-level intervals for this run are in `results/validation_clustered_ci/small/clustered_ci.md`. With 5 seeds, no comparison can reach p < 0.05 in the sign-flip test (minimum 0.0625).

Seeds: [0, 1, 2, 3, 4] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 106s

Test-period metrics, mean ± sd across seeds (cost summed over SKUs):

| condition | arm | total_cost | shortage_cost | waste_cost | holding_cost | lost_units | waste_units | fill_rate | wape_median | pinball_tau_norm | tau_selected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| clean | B_clean_trained | 11142 ± 1503 | 4648 ± 669 | 1186 ± 380 | 5308 ± 505 | 4648 ± 669 | 1977 ± 634 | 0.955 ± 0.003 | 0.226 ± 0.003 | 0.059 ± 0.001 | 0.900 ± 0.000 |
| clean | C_asavailable_trained | 11142 ± 1503 | 4648 ± 669 | 1186 ± 380 | 5308 ± 505 | 4648 ± 669 | 1977 ± 634 | 0.955 ± 0.003 | 0.226 ± 0.003 | 0.059 ± 0.001 | 0.900 ± 0.000 |
| false_alarm | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| false_alarm | B_clean_trained | 20605 ± 2575 | 6402 ± 777 | 6950 ± 1613 | 7253 ± 1349 | 6402 ± 777 | 11583 ± 2688 | 0.936 ± 0.013 | 0.357 ± 0.030 | 0.117 ± 0.024 | 0.820 ± 0.045 |
| false_alarm | C_asavailable_trained | 17086 ± 2361 | 7863 ± 2092 | 3408 ± 1283 | 5815 ± 680 | 7863 ± 2092 | 5680 ± 2139 | 0.924 ± 0.013 | 0.270 ± 0.015 | 0.107 ± 0.018 | 0.820 ± 0.045 |
| imperfect | A_blind | 16239 ± 3119 | 10554 ± 2625 | 707 ± 150 | 4978 ± 402 | 10554 ± 2625 | 1178 ± 250 | 0.898 ± 0.014 | 0.276 ± 0.014 | 0.125 ± 0.009 | 0.800 ± 0.000 |
| imperfect | B_clean_trained | 17208 ± 6182 | 7489 ± 3702 | 3650 ± 2226 | 6069 ± 1346 | 7489 ± 3702 | 6084 ± 3710 | 0.929 ± 0.029 | 0.285 ± 0.029 | 0.088 ± 0.022 | 0.880 ± 0.045 |
| imperfect | C_asavailable_trained | 15700 ± 4275 | 8897 ± 4147 | 1544 ± 742 | 5259 ± 867 | 8897 ± 4147 | 2573 ± 1236 | 0.916 ± 0.028 | 0.267 ± 0.018 | 0.108 ± 0.018 | 0.820 ± 0.045 |

Paired relative test-cost difference (negative = first arm cheaper), bootstrap 95% CI over (seed, SKU) units:

| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |
|---|---|---|---|---|
| clean | C_asavailable_trained vs B_clean_trained | +0.000% | [+0.000%, +0.000%] | 0.00 |
| clean | C_asavailable_trained vs A_blind | -31.388% | [-33.613%, -29.110%] | 0.91 |
| clean | B_clean_trained vs A_blind | -31.388% | [-33.765%, -29.003%] | 0.91 |
| false_alarm | C_asavailable_trained vs B_clean_trained | -17.078% | [-20.201%, -13.746%] | 0.80 |
| false_alarm | C_asavailable_trained vs A_blind | +5.214% | [+1.990%, +9.111%] | 0.41 |
| false_alarm | B_clean_trained vs A_blind | +26.882% | [+19.428%, +34.552%] | 0.24 |
| imperfect | C_asavailable_trained vs B_clean_trained | -8.767% | [-11.893%, -5.805%] | 0.64 |
| imperfect | C_asavailable_trained vs A_blind | -3.323% | [-5.745%, -0.867%] | 0.63 |
| imperfect | B_clean_trained vs A_blind | +5.966% | [+1.807%, +10.581%] | 0.49 |

Per-seed relative test cost (cluster-level check; each seed is one independent world):

| condition | seed | C vs B | C vs A |
|---|---|---|---|
| clean | 0 | +0.0% | -31.1% |
| clean | 1 | +0.0% | -31.4% |
| clean | 2 | +0.0% | -30.3% |
| clean | 3 | +0.0% | -36.7% |
| clean | 4 | +0.0% | -24.7% |
| false_alarm | 0 | -20.9% | +3.2% |
| false_alarm | 1 | -25.6% | +5.6% |
| false_alarm | 2 | -10.1% | +0.3% |
| false_alarm | 3 | -11.6% | -6.3% |
| false_alarm | 4 | -16.5% | +29.5% |
| imperfect | 0 | -5.1% | -4.1% |
| imperfect | 1 | -4.6% | -3.9% |
| imperfect | 2 | -6.7% | -9.2% |
| imperfect | 3 | -17.4% | +6.7% |
| imperfect | 4 | -1.4% | -10.9% |

Mean event counts in the test period (announcements include spurious ones):

- clean: true events 10.0, announcements 10.0
- false_alarm: true events 10.0, announcements 26.4
- imperfect: true events 10.0, announcements 13.2

#### Reading of the 5-seed results (descriptive, this run only)

- With **clean** information, the event-aware arms (B = C) cost 31.4% less than the event-blind arm.
- Under **imperfect** and **false_alarm** signals, arm C cost less than arm B in 5 of 5 seeds in each condition. Pooled differences were −8.8% and −17.1%. Arm B's losses come mainly from waste: it trusts spurious and misleading announcements and over-orders.
- Compared with ignoring events (A), C was slightly cheaper under `imperfect` (−3.3% pooled; 4 of 5 seeds cheaper) but **more expensive under `false_alarm`** (+5.2% pooled; cheaper in only 1 of 5 seeds). Training on as-available signals reduced the harm from bad signals but did **not** make a high-false-alarm signal worth using in this setup.
- These are preliminary simulation results and not confirmatory evidence. In the 20-seed run, the pooled false_alarm C vs A estimate was −3.5% instead of +5.2%, and neither is statistically supported.
