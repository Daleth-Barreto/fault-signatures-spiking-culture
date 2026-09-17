# Fault signatures in the spike stream of a closed-loop neuronal culture substrate

Reproducible artifacts for the ICRA 2027 manuscript of the same name: every
detection, authority, dead-null, localization, and recovery number in the paper
is read verbatim from the JSON files in `results/`.

## Abstract of the study

A walking humanoid is commanded in closed loop through a 64-electrode,
homeostatic, untrained spiking rate substrate read by a fixed Nengo hub. Four
actuator faults are injected during walking. A threshold detector on per-tick
total spikes flags every fault within 0--0.4 s of injection (AUC 0.890--0.995,
lead 0.58--3.07 s before physical collapse). A matched dead-null control
(Poisson spikes, identical plant/encoder/readout) collapses every metric to
chance, and a closed-loop recovery experiment shows a detector-triggered soft
halt changes survival in no fault (0/3 per arm). The substrate reports and
localizes actuator failures but does not compensate for them.

## Repository layout

- `src/` — simulation and analysis scripts (see Reproduction below)
- `results/` — canonical artifacts the paper reads verbatim
- `figures/` — publication figures generated from `results/`
- `paper/` — LaTeX source (`main.tex`, `main_anon.tex`, `body.tex`) and
  compiled PDFs (`main.pdf`, `main_anon.pdf`)
- `deploy/` — Deploy12 (Unitree G1) MuJoCo plant environment
- `requirements.lock.txt` — pinned Python environment

## Results provenance

The paper reports numbers only from the canonical analysis JSONs. Any
discrepancy between a number in the manuscript and its JSON is an error in the
manuscript, not in the experiment.

| Artifact | Content |
|---|---|
| `results/fault_analysis.json` | Detection battery: AUC, detection/lead/fall times, per-channel MI with permutation null, topography (seeds `{7, 29, 13}`, rate substrate, fault at t = 2.0 s) |
| `results/fault_analysis_dead.json` | Dead-null battery: same schema on the Poisson substrate, with live-vs-dead deltas |
| `results/failure_battery.json` | Authority battery: survival/distance/RMSE across 5 readout conditions (seeds `{1, 7, 13, 29}`, 12 s runs) |
| `results/localization_analysis.json` | Per-seed top-delta channels, majority channel, top-k hit rate, channel-23 telegraph, leave-one-seed-out classifier |
| `results/recovery_battery.json` | Closed-loop recovery: per-seed survival and online detection time, control vs. halt arms (seeds `{7, 13, 29}`) |
| `results/fault_*.npz`, `results/fault_dead_*.npz` | Raw per-tick spike counts and plant state for every trial |

## Reproduction

Setup:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.lock.txt
```

The simulation is driven by the culture platform contract (TPS = 40, 25 ms
ticks) with a committed stimulation step through the `cl` SDK; the plant is
MuJoCo via `deploy/deploy12.py`.

Sequence:

```bash
# 1. Detection battery (rate substrate)
python src/fault_detection.py --seeds 7,29,13

# 2. Authority battery (5 readout conditions, 12 s runs)
python src/failure_battery.py

# 3. Dead-null control (same protocol, Poisson substrate, lambda = 0.14)
python src/fault_dead_null.py --seeds 7,29,13
python src/fault_analysis_dead.py

# 4. Localization consistency analysis
python src/localization.py

# 5. Closed-loop recovery battery (control vs. soft-halt arms)
python src/recovery_battery.py --seeds 7,13,29

# 6. Figures
python src/supplementary_figures.py
python src/figures_fault.py
```

Fixed protocol constants: detection threshold z >= 3 on per-tick total spikes;
permutation null over fault labels; dead null lambda = 0.14; recovery detector
threshold 3 sigma for 2 consecutive ticks over a 0--1.5 s self-baseline; soft
halt vx -> 0.02 m/s (an exact zero is forbidden by the SDK's biphasic
stimulation); commanded forward speed vx ~ 0.5 m/s, target pelvis height
0.5 m, flat ground.

Seed-level variance in per-seed results reflects the simulator RNG, substrate
spike RNG, and real-time hub scheduling; the recovery battery shows
run-to-run timing variance from the latter, which is reported in the paper.

## Citations

This study is one of a pair. The companion paper (``Closed-loop task function
across a spiking culture substrate on a humanoid'', ICRA 2027) establishes the
load-bearing protocol, the same plant/substrate/hub configuration, and the
Gate B dead null used here. Please cite the current paper for the fault
detection, localization, and recovery results, and the companion paper for the
underlying closed-loop protocol.

## License

Code and data are released for reproducible research use. The MuJoCo plant and
the `cl` SDK retain their respective upstream licenses; see `third_party/`.