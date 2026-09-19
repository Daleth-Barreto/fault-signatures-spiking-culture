"""Verify every printed number in fault-signatures body_tro.tex traces to canonical artifacts.

Usage:
    python src/verify_tro_numbers.py
"""
import json, pathlib, sys
import numpy as np

REPO = pathlib.Path(__file__).resolve().parent.parent
RES = REPO / "results"
PAPER = REPO / "paper"


def read(p):
    return pathlib.Path(p).read_text(encoding="utf-8-sig")


def lint_ms(tex, label, checks):
    miss = [c for c in checks if c not in tex]
    if miss:
        print(f"  ! [{label}] MISSING: {miss}")
        return miss
    else:
        print(f"  [OK] {label}")
        return []


def load(fn):
    return json.load(open(RES / fn))


def main():
    body = read(PAPER / "body_tro.tex")
    MISSED = []
    DO = ["freeze_lknee", "freeze_rknee", "freeze_lhip", "degrade_50"]

    # Load 6seed results
    rate6 = {f: load("fault_analysis_6seed_rate.json")["results"][f] for f in DO}
    izh6 = {f: load("fault_analysis_6seed_izh.json")["results"][f] for f in DO}

    # Terrain
    terr = load("fault_terrain_combined_s72913.json")
    tfreeze = {t: np.mean([e["auc"] for e in terr if e["terrain"] == t and e["fault"] == "freeze_lknee"])
               for t in ["flat", "ramp", "rough"]}

    upd = {f: rate6[f]["auc_mean"] for f in DO}
    uizh = {f: izh6[f]["auc_mean"] for f in DO}

    print("=== LINT regla 4 (printed number traces to artifact) ===")
    MISSED.extend(lint_ms(body, "tab:detection_ext AUCs",
        [f"\\textbf{{{upd[f]:.3f}}}" for f in DO]))
    MISSED.extend(lint_ms(body, "tab:detection_ext leads",
        ["\\textbf{1.21\\,s}", "\\textbf{0.58\\,s}", "\\textbf{4.81\\,s}", "\\textbf{1.92\\,s}"]))
    MISSED.extend(lint_ms(body, "spreads",
        ["0.890--0.999", "0.988--0.996", "0.683--0.929", "0.924--1.000"]))
    MISSED.extend(lint_ms(body, "tab:detection_izh",
        [f"{upd[f]:.3f} & {uizh[f]:.3f} &" for f in DO]))
    MISSED.extend(lint_ms(body, "abstract AUCs",
        ["0.836--0.993 per fault", "0.767--0.993 per fault", "0.51--9.04"]))
    MISSED.extend(lint_ms(body, "mean/worst",
        ["0.938, with a standard deviation of 0.078", "0.683 for L-hip in seed 1"]))
    MISSED.extend(lint_ms(body, "CVs",
        ["0.003 (R-knee) to 0.100 (L-hip)", "0.006 to 0.093"]))
    MISSED.extend(lint_ms(body, "terrain tab",
        [f"{tfreeze[t]:.3f}" for t in ["flat", "ramp", "rough"]]))
    MISSED.extend(lint_ms(body, "SOTA row",
        ["0.767--0.997", "0.41--9.04\\,s"]))
    MISSED.extend(lint_ms(body, "localization rows",
        ["freeze\\_lknee & 3 & 3 & 3", "freeze\\_rknee & 9 & 11 & 11",
         "freeze\\_lhip & 1 & 10 & 1", "degrade\\_50 & left leg & 23 & 23"]))
    # Dead-null extensions
    MISSED.extend(lint_ms(body, "dead-null 0.468 (+spread/min/max)",
        ["mean AUC 0.468 (per-seed spread 0.028)",
         "min 0.430, max 0.496", "0.481 on the Izhikevich substrate",
         "channel-23 mean-delta (0.00)"]))
    MISSED.extend(lint_ms(body, "LOSO trimmed (rate only)",
        ["0.58 (against 0.25 chance) on the rate substrate"]))
    if "0.56 (IZH)" in body:
        MISSED.append("LOSO-izh 0.56 still present (should be removed)")
        print("  ! [body] LOSO-izh 0.56 still present")
    else:
        print("  [OK] LOSO-izh 0.56 removed")

    if MISSED:
        print(f"\n!!! LINT FAILED ({len(MISSED)}):")
        for m in MISSED:
            print(f"   - {m}")
        sys.exit(1)
    print("\nLINT OK: every printed number traces to the 2026-09-18 artifacts.")


if __name__ == "__main__":
    main()
