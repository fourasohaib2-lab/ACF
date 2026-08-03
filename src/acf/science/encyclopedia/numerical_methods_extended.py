"""
Discontinuous Galerkin, Wavelets, Parallel HPC & Numerical Solvers Encyclopedia Module
"""

from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="discontinuous_galerkin_method_dg",
        name="Méthode des Éléments Finis Discontinus (Discontinuous Galerkin - DG)",
        domain="Mathématiques Numériques NWP",
        subdomain="Solveurs géométriques haute précision",
        equation="Formulation DG élément par élément avec flux numériques de Riemann aux interfaces",
        latex_equation=r"\int_{\Omega_e} \frac{\partial u}{\partial t} v d\Omega - \int_{\Omega_e} \mathbf{F}(u) \cdot \nabla v d\Omega + \int_{\partial \Omega_e} \hat{\mathbf{F}}(u^-, u^+) v n d\Gamma = 0",
        variables={"Omega_e": "Élément géométrique local", "F_hat": "Flux numérique de Riemann aux interfaces inter-éléments"},
        units={"Résolution": "Éléments polynomiaux discontinus"},
        description="Schéma de discrétisation spatiale combinant la flexibilité géométrique des éléments finis avec la conservativité locale rigoureuse des volumes finis. Hautement parallélisable sur supercalculateurs.",
        application_conditions=["Solveurs dynamiques exaflopiques de nouvelle génération (ex: ICON-DG, NUMA)"],
        limitations=["Exige des limiteurs de pente (limiters) près des chocs ou forts gradients"],
        references=["Cockburn & Shu (2001) J. Sci. Comput.", "Giraldo et al. (2013) J. Comput. Phys."],
    ),
    EncyclopediaEntry(
        key="hpc_parallel_mpi_openmp_gpu",
        name="Calcul Haute Performance (HPC, MPI, OpenMP et Accélération GPU)",
        domain="Mathématiques Numériques NWP",
        subdomain="Calcul distribué & Exascale",
        equation="Parallélisme hybride: Décomposition de domaine MPI + Threads OpenMP + Noyaux GPU (CUDA/OpenACC)",
        latex_equation=r"\text{Speedup} = \frac{T_1}{\frac{T_1}{S} + \frac{T_1(1-S)}{P} + T_{\text{comms}}}",
        variables={"S": "Fraction séquentielle du code", "P": "Nombre de processeurs/GPU", "T_comms": "Surcoût des échanges réseau MPI"},
        units={"Performance": "FLOPS / TFLOPS / PFLOPS"},
        description="Architecture logicielle parallèle sous-jacente aux modèles météo mondiaux modernes leur permettant d'exploiter des dizaines de milliers de cœurs CPU et GPU simultanément.",
        application_conditions=["Prévision numérique opérationnelle exaflopique sur supercalculateurs"],
        limitations=["Le goulot d'étranglement des communications réseau MPI peut limiter la scalabilité Amdahl"],
        references=["WMO HPC Guidelines", "ECMWF Exascale Roadmap"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
