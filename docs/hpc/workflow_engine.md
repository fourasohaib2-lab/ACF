# ACF HPC WORKFLOW ENGINE SPECIFICATION (ACF-HPC-104)

## 1. Executive Summary
The ACF HPC Workflow Engine orchestrates 20 operational forecasting stages for AROME (1.3km) and ALADIN (7.5km) models across 00UTC, 06UTC, 12UTC, and 18UTC cycles on SLURM HPC clusters.

## 2. Supported Cycles & Forecast Lengths
- **Cycles**: `00UTC`, `06UTC`, `12UTC`, `18UTC`
- **Forecast Horizons**: `6h`, `12h`, `24h`, `48h`, `72h`, `96h`, `120h`

## 3. Architecture & 20 Operational Stages
1. Initialization
2. Environment Validation
3. Input Validation
4. Boundary Condition Check
5. Observation Availability
6. Pre-processing
7. Static Data Validation
8. Configuration Validation
9. SLURM Generation
10. Job Submission
11. Queue Monitoring
12. Execution Monitoring
13. Restart Handling
14. Failure Recovery
15. Output Validation
16. Post Processing
17. Archiving
18. Distribution
19. Notification
20. Cleanup
