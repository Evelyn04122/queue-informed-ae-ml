# Queue-Informed ML for Four-Hour A&E Breaches

## Overview

This project extends an earlier A&E queueing-theory study based on M/M/1 and M/M/m/K models. It asks whether information available at arrival can predict whether a simulated A&E attendance exceeds four hours.

The project compares logistic regression and random forest models, evaluates them using ROC-AUC and PR-AUC, and uses permutation importance for interpretation. It also considers how machine learning and queueing theory can complement one another when studying healthcare congestion.

> This is an educational data-science project. It is not a clinical decision-support tool and makes no claim about real NHS A&E predictive performance.

## Research question

Can arrival-time, triage and operational-pressure information predict whether a simulated A&E attendance exceeds four hours, and how can this complement queueing-theory models of congestion?

## Data design

The project uses two privacy-safe sources:

1. **NHS Artificial HES A&E data** is used only to inspect the structure of publicly available artificial A&E data. NHS states that its artificial fields are independently generated, so real patient-level relationships are not preserved.
2. **A queue-informed simulated A&E dataset** is used for all machine-learning analysis. The fixed-seed simulator creates 150,000 attendances and explicitly represents time-varying arrivals, staffing by shift, arrival mode, age band, triage category and recent arrival pressure.

The binary target is `AE_Time_Mins > 240`, representing a simulated four-hour A&E breach.

## Main results

- Simulated four-hour breach prevalence: **31.8%**
- Selected model: **Logistic regression**
- Held-out test ROC-AUC: **0.853**
- Held-out test PR-AUC: **0.728**
- Random forest did not improve validation performance.
- The strongest predictive feature was `Recent_Arrivals_60m`, followed by `Staff_On_Shift` and `AE_Arrival_Mode`.

These results apply only to the specified simulation mechanism. They do not establish predictive accuracy, causal effects or clinical utility in real NHS A&E departments.

## Methods

- Data-quality checks and cleaning
- Leakage-controlled feature engineering
- Chronological 70/15/15 train/validation/test split
- Logistic-regression baseline and random-forest comparison
- ROC-AUC, PR-AUC, calibration and confusion-matrix evaluation
- Permutation importance for predictive interpretation

## Project structure

```text
src/
  generate_simulated_ed_data.py       Generate the local simulated dataset
  download_nhs_artificial_data.py     Optional NHS artificial-data download
notebooks/
  01_ae_four_hour_prediction.ipynb    EDA, modelling and interpretation
docs/
  data_dictionary.md                  Variable definitions
report.md                             Full project report
advisor_email.md                      Supervisor email draft
requirements.txt                      Python dependencies
```

## Running the project

Install the dependencies in a virtual environment:

```powershell
python -m pip install -r requirements.txt
```

Generate the simulated dataset on the D drive:

```powershell
python src/generate_simulated_ed_data.py --data-dir "D:\NHS_AE_ML_Data"
```

Open and run `notebooks/01_ae_four_hour_prediction.ipynb`. The notebook reads:

```text
D:\NHS_AE_ML_Data\processed\simulated_ed_attendances.parquet
```

## Limitations and responsible use

The model is evaluated on a researcher-specified simulation, not real NHS patient-level data. Its metrics therefore show how well a model learns the simulated queueing mechanism, not how it would work in a real hospital. The simulation omits important real-world processes, including diagnostics, inpatient bed availability, ambulance handovers, specialist routing, detailed staffing and local hospital policies. Feature importance is predictive association within the simulation, not causal evidence.

## References

- [NHS Artificial Data Pilot](https://digital.nhs.uk/services/artificial-data)
- [NHS A&E Attendances and Emergency Admissions](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/)
- Little, J. D. C. (1961). *A proof for the queuing formula: L = lambda W*. Operations Research, 9(3), 383-387.
