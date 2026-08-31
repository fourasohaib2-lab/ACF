# ACF SCIENTIFIC REFERENCE (ACF-POST-001)

## 1. ATMOSPHERIC GOVERNING EQUATIONS & OPERATORS

- **Navier-Stokes Equations for Atmospheric Fluid**:
  $$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p - 2\mathbf{\Omega} \times \mathbf{u} + \mathbf{g} + \mathbf{F}$$
- **Data Assimilation Increment**:
  $$x_a = x_b + \mathbf{K} \left( y - H(x_b) \right)$$
- **Fourier Neural Operator (FNO) Spectral Mapping**:
  $$v_{l+1}(x) = \sigma \left( W v_l(x) + \mathcal{F}^{-1} \left( R_{\theta} \cdot \mathcal{F}(v_l) \right)(x) \right)$$
