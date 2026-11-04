"""Generate a transparent, queue-informed synthetic ED dataset for ML practice.

This dataset is NOT NHS patient data and is NOT calibrated for clinical use. It
exists because the current NHS Artificial HES release intentionally breaks
record-level relationships, making it unsuitable for predictive modelling.
Every simulated mechanism is documented below for reproducibility.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261014


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-records", type=int, default=150_000)
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()

    rng = np.random.default_rng(SEED)
    output_dir = args.data_dir / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    n = args.n_records

    # Arrival process: a 90-day non-homogeneous pattern with evening peaks,
    # weekend uplift and random hourly demand shocks.
    dates = pd.date_range("2025-01-01", periods=90, freq="D")
    date = rng.choice(dates, size=n)
    hour_weights = np.array([.45, .35, .30, .28, .30, .40, .65, .95, 1.15, 1.25, 1.30, 1.35,
                             1.40, 1.45, 1.50, 1.55, 1.70, 1.85, 1.90, 1.70, 1.35, 1.00, .75, .55])
    hour = rng.choice(np.arange(24), size=n, p=hour_weights / hour_weights.sum())
    arrival_date = pd.to_datetime(date)
    weekend = (arrival_date.dayofweek >= 5).astype(int)
    winter_pressure = (arrival_date.month.isin([1, 2, 12])).astype(int)

    age_band = rng.choice(["0-15", "16-39", "40-64", "65+"], size=n, p=[.18, .31, .29, .22])
    age_effect = np.select([age_band == "0-15", age_band == "65+"], [-.10, .35], default=0)
    arrival_mode = rng.choice(["Walk-in", "Ambulance", "Other referral"], size=n, p=[.61, .27, .12])
    ambulance = (arrival_mode == "Ambulance").astype(int)

    # Initial triage is more urgent on average for ambulance arrivals and older patients.
    acuity_score = rng.normal(0, 1, n) + .8 * ambulance + .55 * (age_band == "65+")
    triage = np.where(acuity_score > 1.7, "1", np.where(acuity_score > .85, "2",
             np.where(acuity_score > .05, "3", np.where(acuity_score > -.85, "4", "5"))))
    staff_on_shift = np.select([np.isin(hour, [0, 1, 2, 3, 4, 5, 6]), np.isin(hour, [16, 17, 18, 19])],
                               [5, 8], default=7)
    recent_arrivals_60m = np.maximum(1, rng.poisson(10 + 5 * hour_weights[hour] + 3 * weekend))
    demand_pressure = recent_arrivals_60m / staff_on_shift
    boarding_pressure = rng.gamma(shape=1.8, scale=.8, size=n) + .45 * winter_pressure
    lower_priority = pd.Series(triage).astype(int).to_numpy() - 1

    # Queueing-theory proxy: utilisation rises when recent demand approaches
    # the service capacity of the staff currently on shift.  The excess term
    # creates a congestion threshold, reflecting the sharp rise in delay as
    # utilisation approaches one rather than a purely linear wait-time rule.
    utilisation_proxy = recent_arrivals_60m / (staff_on_shift * 2.55)
    congestion_excess = np.maximum(utilisation_proxy - .80, 0)

    # Duration mechanism: queue delay increases with pressure and lower priority;
    # service/boarding time increases for higher-acuity and older attendances.
    # Non-linear queue delay: after the 80% utilisation threshold, congestion
    # rises sharply. Lower-priority patients are additionally delayed in busy
    # periods, representing a simplified priority-queue mechanism.
    queue_minutes = np.maximum(
        0,
        10 + 30 * utilisation_proxy**1.25 + 120 * congestion_excess**1.4
        + 8 * lower_priority * (1 + 1.5 * congestion_excess)
        + rng.normal(0, 16, n),
    )
    service_minutes = np.maximum(15, 32 + 16 * (6 - pd.Series(triage).astype(int).to_numpy())
                                 + 20 * ambulance + 15 * (age_band == "65+")
                                 + rng.normal(0, 22, n))
    boarding_minutes = np.maximum(
        0,
        22 * boarding_pressure * (1 + .30 * ambulance) * (1 + 1.2 * congestion_excess)
        + rng.normal(0, 20, n),
    )
    total_minutes = np.round(np.clip(queue_minutes + service_minutes + boarding_minutes, 5, 1_440)).astype(int)

    frame = pd.DataFrame({
        "Age_Band": age_band,
        "Sex": rng.choice(["Female", "Male"], size=n, p=[.52, .48]),
        "AE_Arrive_Date": arrival_date.strftime("%Y-%m-%d"),
        "AE_Arrive_HourOfDay": hour,
        "AE_Arrival_Mode": arrival_mode,
        "Triage_Category": triage,
        "Staff_On_Shift": staff_on_shift,
        "Recent_Arrivals_60m": recent_arrivals_60m,
        "AE_Time_Mins": total_minutes,
    })
    output = output_dir / "simulated_ed_attendances.parquet"
    frame.to_parquet(output, index=False)
    print(f"Saved {len(frame):,} simulated attendances to {output}")
    print(f"Four-hour breach prevalence: {(frame['AE_Time_Mins'] > 240).mean():.1%}")


if __name__ == "__main__":
    main()
