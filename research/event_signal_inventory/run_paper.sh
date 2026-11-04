#!/usr/bin/env bash
# Re-run every experiment reported in paper/paper.tex, from committed code, in three
# parallel streams. Run from research/event_signal_inventory with the pinned environment
# (Python 3.11.9 + requirements.txt), e.g.:
#     PYTHON=../../.venv-esi/bin/python nohup ./run_paper.sh > results/logs/run_paper.log 2>&1 &
# Results are deterministic for a fixed environment and do not depend on the thread count.
# Favorita and M5 need the Kaggle data in data/ (see README.md).
set -euo pipefail
PY=${PYTHON:-python}
THREADS=${THREADS:-7}
mkdir -p results/logs results/validation_clustered_ci

run() {  # name, command...
  local name=$1; shift
  echo "[$(date -u +%FT%TZ)] start $name"
  OMP_NUM_THREADS=$THREADS "$@" > "results/logs/$name.log" 2>&1
  echo "[$(date -u +%FT%TZ)] done  $name"
}

synthetic() {
  run synthetic20 $PY -m esi.experiment --config configs/seed20.json --out results/synthetic20
  run synthetic20_ci $PY -m esi.clustered_ci --results results/synthetic20 \
      --out results/validation_clustered_ci/synthetic20
  run grid $PY -m esi.grid --config configs/grid_strength_false_alarm.json \
      --out results/grid_strength_false_alarm_v2
}

mismatch() {
  run mismatch $PY -m esi.mismatch --config configs/mismatch_false_alarm.json \
      --out results/mismatch_false_alarm
}

real_data() {
  run m5 $PY -m esi.experiment --config configs/m5.json --out results/m5
  for c in item store; do
    run m5_ci_$c $PY -m esi.clustered_ci --results results/m5 --cluster $c \
        --out results/validation_clustered_ci/m5_$c
  done
  run favorita $PY -m esi.experiment --config configs/favorita.json --out results/favorita_v3
  for c in item store; do
    run favorita_ci_$c $PY -m esi.clustered_ci --results results/favorita_v3 --cluster $c \
        --out results/validation_clustered_ci/favorita_v3_$c
  done
  run favorita_windows $PY -m esi.event_windows --results results/favorita_v3
  run m5_windows $PY -m esi.event_windows --results results/m5
}

synthetic & mismatch & real_data &
wait
echo "[$(date -u +%FT%TZ)] ALL DONE"
