# Schema audit and feature policy

The sampling script checks the header before processing. It is intentionally conservative because this public synthetic dataset may be revised.

| Field | Role | Use in project |
|---|---|---|
| `AE_Time_Mins` | Outcome duration | Defines `breach_4h = AE_Time_Mins > 240`; never a predictor. |
| `AE_Arrive_Date` | Arrival timestamp | Date-derived features and preferred chronological split. |
| `AE_Arrive_HourOfDay` | Arrival timestamp | Arrival hour and night indicator. |
| `Age_Band` | Arrival demographic | Categorical predictor; no exact age is inferred. |
| `Sex` | Arrival demographic | Optional categorical predictor. |
| `AE_Arrival_Mode` | Arrival route | Optional categorical predictor. |
| `IMD_Decile_From_LSOA` | Area deprivation measure | Optional predictor, interpreted cautiously. |
| `ProvID` | Provider identifier | Optional predictor; note potential limited generalisability. |
| `Provider_Patient_Distance_Miles` | Travel-distance measure | Optional numeric predictor. |

## Triage field rule

Do not assume that a triage field is available. The notebook searches for field names containing `triage`. Include one only after confirming it represents initial triage, is known at prediction time, and is documented in the report.

## Leakage policy

Never use final diagnosis, admission/discharge fields, length of stay, departure timestamps, treatment counts, investigation counts, or any direct/derived duration as a feature. These are post-arrival or outcome-proximate variables and would inflate apparent model performance.
