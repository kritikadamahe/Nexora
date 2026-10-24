# Event-signal quality and perishable replenishment — minimal research prototype

**Question.** Does training a demand forecaster on event information *as it would actually be available at ordering time* reduce the inventory-cost harm caused by imperfect event signals?

This directory is self-contained. It does not import from or modify the RetailEdge/Nexora application, its data, or its configuration.

## Setup and execution

```bash
cd research/event_signal_inventory
python3 -m venv .venv && . .venv/bin/activate      # optional
pip install -r requirements.txt
python -m pytest -q tests                                                  # 16 unit tests
python -m esi.experiment --config configs/smoke.json --out results/smoke   # ~3 s end-to-end check
python -m esi.experiment --config configs/small.json --out results/small   # ~100 s on 1 CPU
```

Every run writes the following files to `--out`:

| File | Contents |
|---|---|
| `config.json` | Exact configuration, including seeds |
| `environment.json` | Library versions, git commit, whether the worktree was dirty |
| `metrics_by_seed.csv` | Per seed × condition × arm metrics |
| `metrics_by_sku.csv` | Per-SKU metrics |
| `metrics_summary.csv` | Summary statistics |
| `paired_differences.csv` | Paired arm comparisons |
| `signal_counts.csv` | Event and announcement counts |
| `results.md` | The tables below |

Runs are deterministic: the configured seeds determine the world, the signals, the models, and the bootstrap.

## What is implemented

| File | Contents |
|---|---|
| `esi/generator.py` | Negative-binomial daily demand: SKU base level × weekday profile × linear trend × event multiplier. Event uplifts vary by type and by SKU, and 20% of SKUs don't respond to events. Events are non-overlapping, last 1–3 days, and are 7–21 days apart. |
| `esi/signals.py` | Announcements `(announce_day, start, duration, type)`. At origin *t* only announcements with `announce_day ≤ t` are visible. Error process: missed events (`p_miss`), late announcements on the event's start day (`p_late`), spurious events (`spurious_rate`), and spurious events labelled as the highest-uplift type (`p_misleading`). |
| `esi/inventory.py` | Daily single-SKU simulator. Stock is tracked by remaining shelf life, sold FIFO, and lost when unavailable; orders arrive after lead time *L*; unsold units on their last day expire. Costs are holding (per unit-day on hand), shortage (per lost unit), and waste (per expired unit). The shared replenishment policy is an outdating-corrected order-up-to rule: `q = max(0, S − (inventory position − projected FIFO expiry over L+1 days))`. It is a heuristic and is not claimed to be optimal. |
| `esi/forecasting.py` | Pooled `HistGradientBoostingRegressor(loss="quantile")`, one model per quantile level. The target is cumulative demand over days *t..t+L*. Features use only demand before *t*, scaled by the trailing 28-day mean: SKU id, weekday, 7- and 28-day means, a seasonal-naive window, and volatility. Event arms add per-type counts of signalled days in the window. LightGBM wasn't installed, so scikit-learn is used instead. |
| `esi/experiment.py` | Runs the splits, arms, τ tuning, test simulation, metrics, paired bootstrap, and per-seed table. |

### Arms

The replenishment policy, features, and τ grid are identical across arms.

- **A_blind:** no event features.
- **B_clean_trained:** trained on the true event calendar (every event announced 14 days ahead), then served the imperfect signal.
- **C_asavailable_trained:** trained on the train-period part of the same signal realisation it is served with.

Under the `clean` condition, B and C see identical features and must produce identical results. This acts as a built-in consistency check.

### Protocol (small config)

- 5 seeds, 40 SKUs, 730 days.
- Splits:
  - Train: days 28–417. Training targets end before day 420.
  - Validation: days 420–559. The order-up-to quantile τ ∈ {0.5, 0.65, 0.8, 0.9} is chosen per arm by minimising validation simulation cost.
  - Test: days 560–727. Evaluated once with the selected τ; the first 7 days are excluded as warm-up.
- Models are not refit on train+validation.
- Lead time L = 2, shelf life 4 days. Costs: holding 0.05, shortage 1.0, waste 0.6 per unit.
- Initial stock at the start of each segment is set from pre-segment history only.

### Metrics

- **Operational:** total cost, split into holding, shortage and waste; lost units; expired units; fill rate.
- **Forecast:** WAPE of the median window forecast, and pinball loss at the selected τ normalised by mean demand.
- **Paired comparisons:** relative difference in summed test cost between arms. The 95% CI comes from a bootstrap over (seed, SKU) units, which ignores clustering by seed, so the per-seed table is reported as well.

### Tests (`tests/`)

The tests cover inventory balance, lead-time arrival, exact expiry timing, FIFO versus LIFO, lost sales, the expiry projection and policy, announcement-time visibility, late-signal timing, misses and misleading labels, agreement between the vectorised and reference feature code, invariance of features to current and future demand, invariance to not-yet-announced signals, split boundaries, and generator reproducibility.

During development, two mutation checks confirmed the tests can fail: switching to LIFO broke the FIFO test, and removing the announcement-time filter broke three timing and leakage tests.

## Assumptions and limitations

- **Simulation only.** Effect sizes depend on the generator and the error rates that were chosen, and say nothing about real retail. Because the error process that arm C is trained on is the same one it's evaluated on, C's advantage is partly built into the design. The open questions are how large that advantage is and whether it holds when the process shifts between training and deployment; shift is **not** tested yet.
- **Demand is fully observed** (no censoring). Real sales data would understate demand during stockouts.
- **Single SKU, single echelon.** No capacity or budget limits, no substitution, no ordering cost, no supplier variability.
- **One event at a time.** True events don't overlap; spurious events can overlap true ones.
- **Policy and τ.** The policy is one heuristic, and τ comes from a coarse 4-point grid. Several selected τ values sit at the top of the grid (0.9), so a wider grid could change the results.
- **Small experiment.** Only 5 seeds, one setting of (L, shelf life, costs), and two imperfect conditions. No sensitivity analysis yet.
- **Statistics.** The bootstrap CI treats (seed, SKU) units as independent, which is optimistic. The per-seed table is the more conservative view.

## Results (copied verbatim from `results/small/results.md`, produced by the command above)

Seeds: [0, 1, 2, 3, 4] | SKUs: 40 | test days: 168 (first 7 excluded) | runtime 95s

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

### Reading of these results (observations from this run only)

- With **clean** information, the event-aware arms (B = C) cost 31.4% less than the event-blind arm.
- Under **imperfect** and **false_alarm** signals, arm C cost less than arm B in 5 of 5 seeds in each condition. Pooled differences were −8.8% and −17.1%. Arm B's losses come mainly from waste: it trusts spurious and misleading announcements and over-orders.
- Compared with ignoring events (A), C was slightly cheaper under `imperfect` (−3.3% pooled; 4 of 5 seeds cheaper) but **more expensive under `false_alarm`** (+5.2% pooled; cheaper in only 1 of 5 seeds). Training on as-available signals reduced the harm from bad signals but did **not** make a high-false-alarm signal worth using in this setup.
- These are preliminary simulation results and not confirmatory evidence.
