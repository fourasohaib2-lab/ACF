# ACF LTS MONITORING PLAN (ACF-LTS-001)

## 1. OPERATIONAL & SYSTEM HEALTH INDICATORS

- **HPC Cluster Health**: Real-time polling via `HPCMonitor` & `HPCDashboard` (CPU utilization, Slurm node status, queue latency).
- **Forecast Reliability**: Scorecard monitoring via `NWPForecastCenterPanel` (live RMSE, MAE, ACC tracking).
- **AI Model Health**: Fourier Neural Operator (FNO) and PINN physical loss $R_{physics}$ monitoring.
- **Availability Target**: > 99.9% operational availability for ESOC Command Center widgets.
