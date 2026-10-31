# Reproducibility check: why seeds 0–4 of the 20-seed run differ from the 5-seed run

Run on 2026-10-31. Resolves `RESEARCH_REPORT.md` Section 9, item 3.

## Cause

**The scikit-learn version.** `results/small/` (the 5-seed run) was produced with scikit-learn 1.9.1. `results/rerun/` (the 20-seed run) was produced with scikit-learn 1.8.0. The configurations are identical apart from the seed list, and the experiment code did not change between the runs in any way that affects results.

## Evidence

1. **Recorded environments** (`environment.json`):

   | Run | Seeds | Python | numpy | pandas | scikit-learn |
   |---|---|---|---|---|---|
   | `results/small/` | 0–4 | 3.11.9 | 2.4.6 | 3.1.0 | **1.9.1** |
   | `results/final/` | 0–4 | 3.11.9 | 2.4.4 | 3.0.2 | 1.8.0 |
   | `results/rerun/` | 0–19 | 3.11.9 | 2.4.4 | 3.0.2 | 1.8.0 |

2. **Same environment, same numbers.** `results/final/` (5 seeds, scikit-learn 1.8.0) matches seeds 0–4 of `results/rerun/` exactly: all 45 seed × condition × arm rows, all 14 metric columns, maximum absolute difference 0.

3. **Controlled re-runs of seed 1** (`configs/small.json` with `seeds: [1]`, current code, total test cost per arm):

   | Environment | clean A | clean B = C | imperfect B | imperfect C | false_alarm B | false_alarm C |
   |---|---|---|---|---|---|---|
   | Recorded 5-seed run (sklearn 1.9.1) | 16,243.95 | 10,053.75 | 14,872.75 | 14,193.35 | 21,433.35 | 15,869.85 |
   | Re-run, Python 3.14, numpy 2.4.6, pandas 3.1.0, **sklearn 1.9.1** | 16,236.30 | 10,115.40 | 14,877.05 | 14,033.50 | 21,441.65 | 15,928.70 |
   | Re-run, Python 3.14, numpy 2.4.6, pandas 3.1.0, **sklearn 1.8.0** | 14,770.90 | 10,127.00 | 14,886.80 | 14,195.50 | 20,970.75 | 15,592.15 |
   | Re-run, Python 3.14, numpy 2.4.4, pandas 3.0.2, **sklearn 1.8.0** | 14,770.90 | 10,127.00 | 14,886.80 | 14,195.50 | 20,970.75 | 15,592.15 |
   | Recorded 20-seed run (sklearn 1.8.0) | 14,765.25 | 10,115.65 | 14,892.35 | 14,278.30 | 20,981.50 | 15,709.65 |

   - Changing numpy and pandas with scikit-learn held fixed changes nothing.
   - Changing scikit-learn alone reproduces the large seed-1 difference between the two recorded runs (clean A: about 16,240 vs about 14,770, a 10% gap).
   - Results are deterministic within one environment: repeated runs, and runs with `OMP_NUM_THREADS` set to 1, 4 and the default 22, gave identical output.

4. **Remaining gap.** Each re-run still differs from the recorded run with the same scikit-learn version by up to about 1% per arm, in either direction (largest: imperfect C under 1.9.1, 14,033.50 vs 14,193.35). This is small next to the 10% clean-A gap that the scikit-learn version explains. The recorded runs used Python 3.11.9, and the re-runs used Python 3.14.4, so the compiled scikit-learn wheels differ. Python 3.11 was not available on the machine used for this check, so this last step is attributed, not confirmed.

## Consequence

Every 20-seed result in the paper comes from one consistent environment (Python 3.11.9, numpy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0), which `requirements.txt` pins. Exact reproduction requires that environment, including Python 3.11. Other versions give numerically different per-seed costs. `results/small/` is a separate run in a different environment and is not a subset of `results/rerun/`.
