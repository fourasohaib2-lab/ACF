# ACF FORECAST VERIFICATION STANDARD (ACF-VAL-001)

## 1. CONTINUOUS METRICS STANDARD FORMULAE

- **Root Mean Square Error (RMSE)**:
  $$RMSE = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (F_i - O_i)^2}$$
- **Mean Error (BIAS)**:
  $$BIAS = \frac{1}{N} \sum_{i=1}^{N} (F_i - O_i)$$
- **Mean Absolute Error (MAE)**:
  $$MAE = \frac{1}{N} \sum_{i=1}^{N} |F_i - O_i|$$
- **Anomaly Correlation Coefficient (ACC)**:
  $$ACC = \frac{\sum (F_i - C_i)(O_i - C_i)}{\sqrt{\sum (F_i - C_i)^2 \sum (O_i - C_i)^2}}$$

## 2. CATEGORICAL PRECIPITATION METRICS FORMULAE

Using 2x2 contingency table (Hits $a$, False Alarms $b$, Misses $c$, Correct Negatives $d$):
- **Probability of Detection (POD)**: $POD = \frac{a}{a + c}$
- **False Alarm Ratio (FAR)**: $FAR = \frac{b}{a + b}$
- **Critical Success Index (CSI)**: $CSI = \frac{a}{a + b + c}$
- **Equitable Threat Score (ETS)**: $ETS = \frac{a - a_{random}}{a + b + c - a_{random}}$
