# Queue-Informed ML for Four-Hour A&E Breaches

## Abstract

This project develops a reproducible machine-learning workflow for predicting whether a simulated A&E attendance exceeds four hours. It extends earlier M/M/1 and M/M/m/K queueing work by comparing a logistic-regression baseline and random forest on a transparent queue-informed simulation. The current NHS Artificial HES A&E sample is used only for schema inspection and EDA. NHS documents that its artificial fields are independently generated, so it cannot support a meaningful patient-level predictive claim. This distinction is central to the project.

## Data and methods

The project uses two privacy-safe sources. First, the official NHS Artificial HES A&E sample is downloaded locally for data-structure inspection and basic EDA. No predictive model is fitted to it. Second, generate_simulated_ed_data.py creates a fixed-seed 150,000-record simulated ED-attendance dataset.

The simulator makes its assumptions explicit: arrivals vary by hour, weekends and winter pressure; arrival mode and age band influence the probability of initial triage category; staffing differs by shift; and recent arrivals divided by shift capacity forms a utilisation proxy. Above an 80% utilisation threshold, queue and boarding delay increase non-linearly; lower-priority patients also receive greater congestion delay. Queue, service and boarding components combine to form total A&E duration. The binary outcome is AE_Time_Mins > 240.

Available-at-arrival predictors are age band, sex, arrival hour, date-derived features, arrival mode, initial triage category, staffing on shift and recent arrivals. Duration and post-visit information are excluded to prevent leakage. The preferred evaluation is a chronological 70/15/15 split. ROC-AUC is primary, complemented by PR-AUC, calibration, a confusion matrix and permutation importance.

## Results

The simulated dataset contained 150,000 A&E attendances. After cleaning and feature engineering, the four-hour breach prevalence was 31.8%. A chronological 70/15/15 split produced 104,975 training records, 22,495 validation records and 22,495 held-out test records.

| Model | Validation ROC-AUC | Validation PR-AUC | Decision |
|---|---:|---:|---|
| Logistic regression | 0.854 | 0.724 | Selected for final evaluation |
| Random forest | 0.851 | 0.714 | No improvement over logistic regression |
| XGBoost | Not run | Not run | Out of scope after the core comparison |

Logistic regression was selected because it achieved slightly stronger validation performance while remaining more interpretable than the random forest. The selected model was then evaluated once on the held-out test set.

| Final model | Test ROC-AUC | Test PR-AUC |
|---|---:|---:|
| Logistic regression | 0.853 | 0.728 |

The similarity between validation and test ROC-AUC values provides no evidence of substantial overfitting within the simulated setting. However, these metrics measure performance only within the specified simulation mechanism and must not be interpreted as estimates of real NHS A&E predictive performance.

Permutation importance identified recent arrivals in the previous 60 minutes as the dominant predictor, followed by staffing level and arrival mode. This pattern is consistent with the simulation design: demand pressure increases breach risk, while staffing moderates the effect of congestion. These feature-importance results are predictive associations within the simulation, not causal effects.

## Discussion: queueing theory and machine learning

Queueing models provide an interpretable mechanism for understanding A&E congestion. The M/M/1 and M/M/m/K models make the relationship between arrivals, service capacity, number of servers, utilisation and finite waiting space explicit. They are particularly useful for scenario analysis: for example, they can be used to examine how a change in staffing levels, service capacity or arrival rate may alter expected queue lengths and waiting times.

### Limitations of queueing models

Queueing models are deliberately simplified representations of an A&E department. In the original M/M/1 and M/M/m/K models, arrivals are assumed to follow a stationary Poisson process and service times are assumed to follow an exponential distribution. In practice, A&E demand varies substantially by hour of day, day of week and season, while treatment times can be long, variable and affected by downstream delays.

The models also simplify patient pathways. Real patients differ in clinical need, triage priority, investigation requirements and eventual discharge or admission routes. A single queue, or a fixed number of identical servers, cannot fully represent these differences. For example, a high-acuity patient may be prioritised over a lower-acuity patient even when they arrive later.

In addition, capacity in a real A&E department is not constant. Staffing, treatment spaces, bed availability, diagnostic delays and hospital-wide crowding can all change over time. Therefore, queueing models are valuable for explaining general congestion mechanisms and testing operational scenarios, but their numerical outputs should not be interpreted as exact predictions of real NHS A&E waiting times.

### What machine learning adds

Machine learning addresses a different question. Given information available at arrival or initial triage, it estimates the probability that an attendance will exceed four hours within the simulated process. It can combine patient-level and operational features, such as age band, triage category, arrival mode, recent arrival pressure and staff on shift. It can also represent non-linear relationships that are difficult to express in a simple queueing model.

However, ML results must be interpreted carefully. Predictive importance is not causal evidence: a feature that helps predict a breach does not necessarily identify an action that would reduce waiting times. Similarly, a high ROC-AUC measures discrimination within the simulated dataset; it does not demonstrate clinical usefulness or real-world performance.

### Why the approaches are complementary

The two approaches should therefore be viewed as complementary rather than competing. ML can identify patterns associated with a high simulated risk of a four-hour breach. Queueing models can then be used to explore operational scenarios motivated by those patterns, such as changes in capacity or demand pressure.

A genuine operational application would require validation using appropriate real-world data, trustworthy time-varying demand and capacity measures, detailed workflow knowledge, clinical governance and careful assessment of fairness and safety. In this project, all predictive results apply only to the transparent queue-informed simulation mechanism and must not be interpreted as evidence about actual NHS A&E performance.

## Limitations and ethics

The machine-learning evaluation is based on a researcher-specified, queue-informed simulation rather than real NHS patient-level data. The official NHS artificial HES A&E data source was considered only for its available fields and data structure; it was not used as evidence of real patient-level relationships. Consequently, the reported ROC-AUC, PR-AUC and permutation feature-importance values measure how well the models recover relationships built into the simulated mechanism. They do not establish predictive accuracy, causal effects, fairness, calibration or clinical utility in real NHS A&E departments.

The simulation design is transparent, but it remains a simplification. The simulator includes time-varying demand, staffing, triage category, arrival mode and congestion effects, yet it omits many important processes. These include diagnostics, specialist routing, detailed staff roles, inpatient bed availability, ambulance handover delays, patient deterioration, local operational policies and variation between NHS trusts. It is also not calibrated against any particular hospital or real NHS performance dataset.

Feature importance should be interpreted as predictive association within this simulation, not as evidence that changing a feature would cause waiting times to improve. For example, recent arrival pressure may be strongly predictive because it was designed to influence congestion in the simulated mechanism. This does not prove that the estimated effect size, or even the same relationship, would occur in a real A&E department.

Using synthetic and simulated data avoids processing identifiable patient information and reduces privacy risk. However, it does not remove the need for ethical caution. If a similar model were developed with real data, it would require appropriate approvals, data-governance procedures, fairness assessment across patient groups, external validation and clinical oversight. A model with good discrimination could still be unsafe if it performed differently across demographic or clinical groups.

This work is intended as a reproducible coding and methodological exercise. It is not medical advice, a clinical decision-support tool or a recommendation for deployment. All findings should be interpreted only as results from the specific transparent queue-informed simulation used in this project.

## References

1. NHS England. [Artificial data pilot](https://digital.nhs.uk/services/artificial-data).
2. NHS England. [A&E Attendances and Emergency Admissions](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/).
3. Little, J. D. C. (1961). A proof for the queuing formula: L = lambda W. Operations Research, 9(3), 383-387.
