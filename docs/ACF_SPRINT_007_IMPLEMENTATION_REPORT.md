<!-- ACF_RECONCILIATION_BANNER_2026-09-02 -->
> **⚠️ Historical / unverified document.** This file was auto-generated as part
> of an earlier documentation sprint, and its completion, certification, or
> "100%"-style claims were not independently reproduced. For the actual,
> reproducible test/status numbers, see [`ROADMAP.md`](../ROADMAP.md) and
> [`README.md`](../README.md)'s "Verified Status" section; for what has
> genuinely been audited and fixed since, see
> [`ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md).
> Treat any specific number, percentage, or "CERTIFIED"/"COMPLETE" claim below
> as aspirational unless it also appears in one of those documents.
>
> _Banner added 2026-09-02 per `ROADMAP.md`'s "reconcile ~150 certificate/
> sprint-report documents" near-term priority — original content preserved
> unchanged below._

---

# ACF SPRINT-007 IMPLEMENTATION REPORT (ACF-EXEC-007)

## 1. IMPLEMENTATION DETAILS

- **Target File**: `src/acf/ai/simulation/neural_operator.py`
- **Classes Provided**:
  - `FourierNeuralOperator`: Spectral space neural solver utilizing Fast Fourier Transforms (`fft.rfftn` / `fft.irfftn`) for accelerated surrogate atmospheric physics prediction.
  - `PINNEngine`: Physics-Informed Neural Network engine enforcing mass, momentum, and thermodynamic energy conservation constraints ($R_{physics} \to 0$).
  - `AIBiasCorrector`: ML-based systematic forecast error and bias correction engine with uncertainty estimation.
