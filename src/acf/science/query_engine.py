"""
Atmospheric Complexity Framework (ACF)

Scientific Query Engine (System Expert & Physical AI Ask Interface)
"""

from typing import Any

from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.parameters.engine import ParameterEngine


class ScientificQueryEngine:
    """
    Moteur d'interrogation scientifique naturelle et explicative d'ACF.
    """

    def __init__(self):
        self.graph = KnowledgeGraphEngine()
        self.param_engine = ParameterEngine()

    def ask(self, question: str) -> dict[str, Any]:
        """
        Répond scientifiquement à une question en fournissant l'explication physique,
        la chaîne causale, les équations, les paramètres importants et les références.
        """
        q = question.lower().strip()

        # -------------------------------------------------------------------
        # MISSION ACF-044 Natural Language Queries (Real-Time Earth Monitoring)
        # -------------------------------------------------------------------
        if (
            q in ["show live earth", "live earth", "continuous monitoring"]
            or "show real-time monitoring" in q
            or "show realtime monitoring" in q
        ):
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "GLOBAL REAL-TIME EARTH MONITORING MISSION CONTROL",
                "physical_explanation": (
                    "Activation du centre d'opérations planétaires permanents d'ACF. "
                    "Synchronisation en temps réel du globe 3D avec les 14 flux d'observation "
                    "(WIGOS, GOES, MTG, Radar NEXRAD, Bouées ARGO, AMDAR, SWOT)."
                ),
                "active_product": "GlobalRealtimeMonitor Operational Centre v44.0",
            }

        if q in ["show telemetry", "show cluster telemetry"] or "show hpc telemetry" in q:
            # CORRECTED: this used to embed fixed fake "current"
            # telemetry numbers (CPU 14.2%, GPU 32.5%...) in the
            # explanation text as if reporting live values - the same
            # fabricated numbers that monitoring.telemetry_engine.TelemetryEngine
            # used to claim (fixed earlier this session to report real
            # host CPU/RAM via psutil and honestly decline the rest).
            # This router only activates a UI widget; it does not
            # itself measure anything, so it no longer asserts numbers.
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "TelemetryEngineViewer",
                "physical_explanation": (
                    "Activation du widget de télémétrie matérielle et logicielle "
                    "(CPU, RAM, GPU, réseau, latence, nœuds de calcul)."
                ),
                "system_status": "NOT_MEASURED_SEE_TELEMETRYENGINE_FOR_LIVE_VALUES",
            }

        if q in ["show earth health", "earth health", "santé planétaire"]:
            # CORRECTED: this used to claim a fixed fake
            # "planet_health_score_pct: 74.5" - the same fabricated
            # number that monitoring.earth_health.EarthHealthMonitor
            # and digital_twin.planetary_dashboard.PlanetaryDashboard
            # independently used to claim (both fixed earlier this
            # session). This router only activates a UI widget.
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "EarthHealthViewer",
                "physical_explanation": (
                    "Activation du widget de santé globale de la Terre "
                    "(indice de résilience du système Terre et limites planétaires)."
                ),
                "planet_health_score_pct": None,
            }

        if q in ["show alerts", "current alerts", "alertes en cours"]:
            # CORRECTED: used to claim a fixed "active_alert_level:
            # ORANGE / RED" as if reporting a real current alert state
            # - same underlying issue as
            # hazard_operations.alert_generator.AlertGenerator (fixed
            # earlier this session). This router only activates a UI
            # widget, it doesn't track any real alert state.
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "OperationalAlertDispatcherViewer",
                "physical_explanation": (
                    "Activation du widget de diffusion et de routage des alertes opérationnelles "
                    "(Niveaux GREEN à BLACK) vers AWCI, le centre d'urgence et les systèmes d'aide à la décision."
                ),
                "active_alert_level": None,
            }

        if q in ["show streaming", "observation stream"]:
            # CORRECTED: this used to embed fixed fake throughput
            # numbers (4500 stations/sec, 3900 ARGO buoys...) - the
            # same fabricated numbers that
            # monitoring.observation_stream.ObservationStreamEngine
            # used to claim (fixed earlier this session to honestly
            # report no real ingestion pipeline connected). This
            # router only activates a UI widget.
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "ObservationStreamEngineViewer",
                "physical_explanation": (
                    "Activation du widget de supervision du streaming d'observation "
                    "(stations SYNOP, bouées ARGO, rapports AMDAR, constellations satellites)."
                ),
            }

        if q in ["show ai monitoring", "ai model monitoring"]:
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "AIMultiModelMonitorViewer",
                "physical_explanation": (
                    "Supervision en temps réel de l'exécution, de la latence et du score de compétence (Skill Score) "
                    "des 10 modèles d'IA et NWP (GraphCast, AIFS, NeuralGCM, Pangu, IFS, AROME)."
                ),
            }

        if q in ["explain monitoring", "explication surveillance"]:
            return {
                "question": question,
                "physical_explanation": (
                    "La plateforme de surveillance en temps réel ACF-044 assure l'ingestion continue, "
                    "la détection d'anomalies de capteurs, la synchronisation du Digital Twin et la diffusion "
                    "d'alertes par serveur WebSocket haut débit avec latence < 1 ms."
                ),
                "architecture_components": [
                    "GlobalRealtimeMonitor",
                    "TelemetryEngine",
                    "ObservationStreamEngine",
                    "OperationalWebSocketServer",
                    "EarthAnomalyMonitor",
                    "EarthHealthMonitor",
                ],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-043 Natural Language Queries (AI Meteorologist & Expert)
        # -------------------------------------------------------------------
        if "explain today's forecast" in q or "explain today forecast" in q:
            # CORRECTED: this used to claim a specific fabricated
            # "today's" synoptic situation (a named North Atlantic
            # cyclone deepening at +40 hPa/24h, CAPE 1800 J/kg over
            # South-Western Europe) regardless of the actual date or
            # any real forecast run - the same underlying issue as
            # hazard_operations.hazard_detection_engine.HazardDetectionEngine
            # (fixed earlier this session, flagged as the single most
            # operationally dangerous finding of the session). This
            # router only activates a UI workspace, it has no real
            # forecast data connected.
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "AUTONOMOUS AI METEOROLOGIST & EARTH SYSTEM EXPERT WORKSPACE",
                "physical_explanation": "Activation du workspace de diagnostic prévisionnel quotidien de l'IA Météorologiste.",
                "active_product": "AIMeteorologist Daily Forecast Diagnostic",
                "is_real_data": False,
            }

        if "why is heavy rain expected" in q or "heavy rain expected" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Heavy rain is expected due to the convergence of three atmospheric factors: "
                    "1) High precipitable water (PWV > 45 mm) and moisture flux advection (IVT > 400 kg/m/s), "
                    "2) Strong convective instability (CAPE > 1500 J/kg) driving intense updrafts (w > 10 m/s), "
                    "3) Orographic lifting coupled with synoptic-scale upper-level jet streak divergence."
                ),
                "equation": r"P = \int_{z_0}^{z_{\text{top}}} \rho_{\text{air}} \cdot w \cdot \frac{\partial q_v}{\partial z} dz",
            }

        if "which model is most reliable" in q or "most reliable model" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "GraphCast (Google DeepMind AI) and IFS (ECMWF 4D-Var) provide the highest skill scores for medium-range synoptic tracks (5-10 days). "
                    "For high-resolution mesoscale convective precipitation (< 48 hours), AROME (Météo-France 1.3 km) offers superior reliability."
                ),
                "recommended_best_model": "GraphCast (Global synoptic) + AROME (Convective scale)",
            }

        if q in ["show uncertainty", "incertitude"]:
            # CORRECTED: used to claim a fixed "Ensemble Spread = 2.1
            # sigma" and "uncertainty_level: MODERATE" as if reporting
            # a real current ensemble run - no ensemble data is
            # connected here. This router only activates a UI widget.
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "UncertaintyQuantificationViewer",
                "physical_explanation": (
                    "Activation du widget de quantification des incertitudes épistémiques "
                    "(structure des modèles d'IA/NWP) et aléatoires (dispersion d'ensemble)."
                ),
                "uncertainty_level": None,
            }

        if "recommend emergency actions" in q or "recommend emergency" in q:
            # CORRECTED: this used to claim a specific fabricated
            # emergency response plan (named barrier closures, a
            # "secteur 4" evacuation) and "priority: HIGH" regardless
            # of whether any real hazard was detected - same
            # underlying issue as
            # hazard_operations.evacuation_planner.EvacuationPlanner
            # (fixed earlier this session). This router only activates
            # a UI widget, it has no real hazard/emergency data
            # connected.
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "SectorialRecommendationViewer",
                "physical_explanation": "Activation du widget de recommandations sectorielles de sécurité civile.",
                "priority": None,
                "is_real_data": False,
            }

        if "generate operational briefing" in q or "operational briefing" in q:
            return {
                "question": question,
                "action": "generate_report",
                "report_type": "Executive Briefing",
                "physical_explanation": "Génération automatique du bulletin d'analyse et de décision du Météorologiste Virtuel autonome.",
                "active_product": "ExecutiveBriefingGenerator",
            }

        # -------------------------------------------------------------------
        # MISSION ACF-041 Natural Language Queries (Master Framework & Integration)
        # -------------------------------------------------------------------
        if any(
            k in q
            for k in ["show master", "show framework", "show modules", "show capabilities", "explain architecture"]
        ):
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "ACF MASTER FRAMEWORK UNIFIED CONTROL CENTER",
                # CORRECTED (2026-09-05 audit de continuation): this used
                # to also claim "40 missions d'ingénierie intégrées" and
                # "Découverte automatique des 21 modules" - no real count
                # of "40 missions" exists anywhere in this codebase, and
                # GlobalModuleRegistry.MODULES is a static hand-curated
                # name list (see its own NOTE), not the result of any
                # real automatic discovery.
                "physical_explanation": (
                    "Activation du Master Framework unifié d'ACF. "
                    "21 modules principaux et 13 catégories de capacités scientifiques recensés "
                    "dans un catalogue statique (GlobalModuleRegistry / ScientificCapabilityRegistry), "
                    "pas découverts automatiquement."
                ),
                # CORRECTED: used to claim "Platinum Certified" - the
                # same false certification independently fabricated by
                # master.scientific_certification.ScientificCertificationEngine
                # (fixed earlier this session: audit_framework() used to
                # unconditionally claim "CERTIFIED_PLATINUM / 450
                # equations audited / 100% SI compliance" with no real
                # audit ever performed).
                "active_product": "ACF Master Engine v41.0",
            }

        if q == "show earth":
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "PLANETARY DIGITAL TWIN",
                "physical_explanation": (
                    "Visualisation du Digital Twin planétaire synchronisant l'atmosphère, l'océan, l'hydrologie, le climat, "
                    "la géologie, le temps spatial, la défense planétaire et la géo-ingénierie en temps réel."
                ),
                "active_product": "ACF Global Earth System Digital Twin",
            }

        if any(k in q for k in ["show science", "explain physics", "explain ai", "explain workflow"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "MasterScienceGatewayViewer",
                "physical_explanation": (
                    "Façade scientifique unifiée MasterScienceGateway offrant un accès standardisé aux fonctions "
                    "forecast(), simulate(), analyze(), query(), compute(), reason(), optimize() et visualize()."
                ),
                # CORRECTED: used to claim "PLATINUM CERTIFIED (100% SI
                # & Literature Traceability)" - the same false
                # certification independently fabricated by
                # master.scientific_certification.ScientificCertificationEngine
                # (fixed earlier this session) and by the "show
                # master" block above (also fixed this batch). None of
                # the 3 was ever a real audit result.
                "certification_level": "NOT_CERTIFIED_NO_AUDIT_PERFORMED",
            }

        # -------------------------------------------------------------------
        # MISSION ACF-040 Natural Language Queries (Geoengineering & Boundaries)
        # -------------------------------------------------------------------
        if any(k in q for k in ["show planetary boundaries", "explain planetary boundaries", "limites planétaires"]):
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "PLANETARY BOUNDARIES & CLIMATE CONTROL CENTER",
                "physical_explanation": (
                    "Suivi en temps réel des 9 limites planétaires définies par le Stockholm Resilience Centre "
                    "(Changement climatique, intégrité de la biosphère, utilisation des sols, eau douce, flux de N/P, "
                    "acidification des océans, aérosols, entités nouvelles, ozone stratosphérique)."
                ),
                "active_product": "Stockholm Resilience Centre 9 Planetary Boundaries Engine",
            }

        if any(k in q for k in ["show co2 removal", "show geoengineering", "explain dac", "explain sai"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "GeoengineeringTechniquesViewer",
                "physical_explanation": (
                    "Modélisation et évaluation des stratégies d'intervention climatique : "
                    "1) Captage direct dans l'air (DACCS) et altération forcée (ERW), "
                    "2) Injection d'aérosols stratosphériques (SAI) et éclaircissement des nuages marins (MCB)."
                ),
                "equation": r"\Delta F_{\text{SO2}} = -0.45 \cdot \text{SO2}_{\text{Mt/yr}}, \quad F_{\text{CO2}} = 5.35 \ln(C/C_0)",
            }

        if any(k in q for k in ["show carbon cycle", "explain carbon budget", "cycle du carbone"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "CarbonCycleReservoirViewer",
                "physical_explanation": (
                    "Calcul des flux et réservoirs de carbone (Atmosphère 870 GtC, Océans 38 000 GtC, Sols 1 700 GtC, "
                    "Biosphère 550 GtC) et suivi du budget carbone résiduel pour 1.5°C."
                ),
            }

        if "show climate restoration" in q or "restauration climatique" in q:
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "ClimateRestorationViewer",
                "physical_explanation": "Évaluation des projets de restauration des puits de carbone naturels (Mangroves, Forêts, Zones Humides, Carbone Bleu).",
            }

        if any(k in q for k in ["show ssp", "show net zero", "scénarios cmip6"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "ClimateScenarioViewer",
                "physical_explanation": "Projections multi-scénarios CMIP6 / SSP (SSP1-1.9 à SSP5-8.5) et trajectoires Net Zero d'ici 2050.",
            }

        # -------------------------------------------------------------------
        # MISSION ACF-039 Natural Language Queries (Planetary Defense & Science)
        # -------------------------------------------------------------------
        if any(
            k in q for k in ["show asteroids", "show neo", "show comets", "show planetary defense", "explain asteroid"]
        ):
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "PLANETARY DEFENSE & INTERPLANETARY CENTER",
                "physical_explanation": (
                    "Activation de la surveillance des objets géocroiseurs (NEO/PHA: Apophis, Bennu) "
                    "et affichage du catalogue d'objets potentiellement dangereux selon les échelles de Turin et Palerme."
                ),
                "active_product": "ACF Planetary Defense Center & JPL CNEOS Catalog",
            }

        if any(k in q for k in ["show impact", "explain impact"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "CosmicImpactSimulator",
                "physical_explanation": (
                    "Simulation d'impact cosmique (Énergie E = 0.5*m*v², cratérisation par équation de Collins et al., "
                    "onde de choc atmosphérique et tsunami d'impact par la loi d'amplification de Green)."
                ),
                "equation": r"E = \frac{1}{2} m v^2, \quad D_{\text{crater}} \propto d_i^{0.78} v_i^{0.44}",
            }

        if any(k in q for k in ["show mars", "show venus", "show jupiter", "show saturn"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "PlanetaryAtmosphereViewer",
                "physical_explanation": (
                    "Visualisation et comparaison des atmosphères planétaires du Système Solaire "
                    "(Pression, masse molaire, hauteur d'échelle H = R*T/(M*g), composition et cellules de circulation)."
                ),
                "equation": r"H = \frac{R \cdot T}{M \cdot g}",
            }

        if any(k in q for k in ["show exoplanets", "show habitability", "explain habitability"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "AstrobiologyHabitabilityViewer",
                "physical_explanation": (
                    "Évaluation astrobiologique et détection de biosignatures (O2, O3, CH4, H2O) "
                    "sur les exoplanètes (TRAPPIST-1 e, Proxima b, K2-18 b) avec calcul de l'Earth Similarity Index (ESI)."
                ),
                "equation": r"\text{ESI} = \prod \left(1 - \left|\frac{x_i - x_{i0}}{x_i + x_{i0}}\right|\right)^{w_i / n}",
            }

        if "show cosmic hazards" in q or "risques cosmiques" in q:
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "CosmicHazardViewer",
                "physical_explanation": "Analyse des risques extraterrestres (Impacts d'astéroïdes, tempêtes solaires, sursauts gamma GRB et rayons cosmiques).",
            }

        if "explain kepler" in q or "lois de kepler" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Les 3 lois de Kepler régissent le mouvement orbital des planètes et astéroïdes : "
                    "1) Les orbites sont des ellipses dont le Soleil occupe l'un des foyers, "
                    "2) Le rayon vecteur balaye des aires égales en des temps égaux, "
                    "3) Le carré de la période T² est proportionnel au cube du demi-grand axe a³ (T² = 4*pi²*a³ / (G*M))."
                ),
                "equation": r"T = 2\pi \sqrt{\frac{a^3}{G M}}, \quad v = \sqrt{G M \left(\frac{2}{r} - \frac{1}{a}\right)}",
                "references": ["Kepler (1609, 1619)", "Newton (1687) Principia"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-038 Natural Language Queries (AEOS & Autonomous Platform)
        # -------------------------------------------------------------------
        if any(k in q for k in ["show aeos", "explain aeos", "show mission control", "operating system"]):
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "AEOS MISSION CONTROL CENTER",
                "physical_explanation": (
                    "Activation du noyau du système d'exploitation planétaire autonome AEOS (Autonomous Earth Operating System) "
                    "supervisant les 15 microservices scientifiques, l'exécution distribuée Slurm/K8s et le Digital Twin."
                ),
                "active_product": "AEOS Kernel v1.0 Planetary OS",
            }

        if any(k in q for k in ["show services", "show scheduler", "show workflow"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "AEOSWorkflowSchedulerViewer",
                "physical_explanation": (
                    "Activation du widget d'ordonnancement dynamique des tâches, du graphe de dépendance et de l'équilibrage "
                    "de charge sur la grappe de calcul distribué (Local, Multi-core, MPI, Slurm, Kubernetes, Cloud)."
                ),
                # VERIFIED (not fabricated): 15 matches the real
                # registry-backed service count from
                # aeos.aeos_kernel.AEOSKernel.active_services after
                # boot() (aeos.registry.list_registered_services()) -
                # confirmed by running it directly. Kept as-is.
                "active_services": 15,
            }

        if any(k in q for k in ["show health", "show agents", "auto-guérison", "agents autonomes"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "AEOSHealthAndAgentsViewer",
                "physical_explanation": (
                    "Activation du widget de supervision du moteur d'auto-guérison (SelfHealingEngine) et du réseau "
                    "des agents scientifiques autonomes."
                ),
                # CORRECTED: used to claim a fixed "health_status: 100%
                # HEALTHY" as if reporting a real current health check -
                # same underlying issue as
                # release.health_check.ProductionHealthCheck (fixed
                # earlier this session). This router only activates a
                # UI widget, it doesn't run any real health check.
                "health_status": None,
            }

        # -------------------------------------------------------------------
        # MISSION ACF-037 Natural Language Queries (Earth Intelligence Platform)
        # -------------------------------------------------------------------
        if any(k in q for k in ["explain forecast", "show ai reasoning", "show autonomous analysis"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "ScientificReasoningViewer",
                "physical_explanation": (
                    "Activation du widget d'explication scientifique autonome dérivée du moteur de raisonnement "
                    "physique (ScientificReasoningEngine) et de la comparaison d'ensemble des modèles NWP/IA."
                ),
                # CORRECTED: used to claim a fixed "95.5%" confidence -
                # ScientificReasoningEngine itself (fixed earlier this
                # session) no longer reports a specific fabricated
                # confidence percentage, since no calibrated confidence
                # model exists; this router shouldn't either.
                "ai_confidence_pct": None,
            }

        if any(k in q for k in ["explain decision", "show decision support", "show recommendations"]):
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "EARTH INTELLIGENCE MISSION CONTROL",
                "physical_explanation": (
                    "Génération des recommandations opérationnelles prioritaires basées sur les lois physiques (Bernoulli, Navier-Stokes) "
                    "et l'optimisation sous contraintes des plans d'urgence."
                ),
                "active_product": "ACF Operational Decision Support Engine",
            }

        if any(k in q for k in ["explain risk", "show scientific chain", "show knowledge graph"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "PlanetaryKnowledgeGraphViewer",
                "physical_explanation": (
                    "Exploration du graphe de connaissances planétaire reliant l'atmosphère, l'océan, l'hydrologie, le climat, "
                    "la géologie et le temps spatial avec les lois physiques causales."
                ),
            }

        if "show mission planner" in q or "planificateur de mission" in q:
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "MissionPlannerViewer",
                "physical_explanation": "Gestion des workflows autonomes d'assimilation, inférence d'IA, audit de risques et génération de rapports.",
            }

        # -------------------------------------------------------------------
        # MISSION ACF-036 Natural Language Queries (Digital Twin & Planetary Engine)
        # -------------------------------------------------------------------
        if any(
            k in q
            for k in [
                "show earth twin",
                "show planet state",
                "show global state",
                "show planet dashboard",
                "digital twin",
            ]
        ):
            return {
                "question": question,
                "action": "activate_workspace",
                "workspace_name": "PLANETARY DIGITAL TWIN",
                "physical_explanation": (
                    "Activation du Digital Twin planétaire ACF (Équivalent DestinE / ESA Digital Twin Earth) "
                    "unifiant l'atmosphère, l'océan, l'hydrologie, le climat, la géologie et le temps spatial en temps réel."
                ),
                "active_product": "ACF Global Earth System Digital Twin Engine",
            }

        if any(k in q for k in ["show earth components", "show earth coupling", "explain earth system"]):
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "EarthSynchronizationViewer",
                "physical_explanation": (
                    "Visualisation de la synchronisation physique et des flux d'échange bidirectionnels (Vent/Mer Tau, "
                    "Chaleur Q_lh, Chauffage Joule, Soulèvement tsunamigène) entre tous les sous-domaines terrestres."
                ),
                "equation": r"\tau = \rho_{\text{air}} C_d V_{10}^2, \quad Q_{\text{lh}} = \rho L_v C_e V \Delta q",
            }

        if any(k in q for k in ["show cascade", "show multi hazard", "show global risks", "explain cascade"]):
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "multi_hazard_cascade_layer",
                "physical_explanation": (
                    "Affichage des chaînes de risques en cascade multi-domaines (ex: Cyclone -> Surcote -> Inondation -> Dommages ; "
                    "Séisme Mw 8.5 -> Tsunami -> Inondation ; Tempête Solaire G5 -> Perte Satellites -> Panne Réseau Électrique)."
                ),
                "active_product": "ACF Cascade Risk Graph & Alert Engine",
            }

        if "explain scenario" in q or "explain planet state" in q or "projections futures" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Les scénarios de projection du Digital Twin combinent les modèles d'IA à court/moyen terme (GraphCast / GenCast) "
                    "et les ensembles du système Terre CMIP6 (Scénarios SSP1-1.9 à SSP5-8.5 jusqu'en 2100)."
                ),
                "available_horizons": ["+6h", "+24h", "+7d", "+1yr", "+10yr", "+100yr"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-035 Queries (Geology, Seismology & Hazards)
        # -------------------------------------------------------------------
        if "show earthquakes" in q or "compare earthquakes" in q or "séismes" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "earthquake_catalog_layer",
                "physical_explanation": (
                    "Activation du catalogue de sismicité globale (USGS / EMSC / GFZ) "
                    "avec représentation des magnitudes Mw, profondeurs foyers et meca-focaux (Moment Tensor)."
                ),
                "active_product": "USGS Real-time Global Seismicity & ShakeMap",
            }

        if "show volcanoes" in q or "volcans" in q or "explain mogi" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "volcano_monitoring_layer",
                "physical_explanation": (
                    "Visualisation des volcans actifs, indices d'explosivité VEI et modélisation de déformation "
                    "de Mogi : Dz = ((1-nu)/pi) * dV * d / (r² + d²)^(3/2)."
                ),
                "equation": r"\Delta z = \frac{(1-\nu)}{\pi} \frac{\Delta V \cdot d}{(r^2 + d^2)^{3/2}}",
            }

        if "show tsunami" in q or "tsunamis" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "tsunami_propagation_layer",
                "physical_explanation": (
                    "Affichage des cartes de risque de tsunami, vitesse de propagation C = sqrt(g*d) "
                    "et loi d'amplification côtière de Green H2 = H1 * (d1/d2)^(1/4)."
                ),
                "equation": r"c = \sqrt{g \cdot d}, \quad H_2 = H_1 \left(\frac{d_1}{d_2}\right)^{1/4}",
            }

        if "show faults" in q or "show tectonic plates" in q or "plaques tectoniques" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "tectonic_plates_and_faults_layer",
                "physical_explanation": (
                    "Cartographie des 14 grandes plaques tectoniques lithosphériques, des failles actives "
                    "(San Andreas, Anatolienne) et des vecteurs de vitesse de dérive continentale."
                ),
            }

        if "show seismic waves" in q or "ondes sismiques" in q:
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "SeismicWaveformViewer",
                "physical_explanation": (
                    "Affichage des formes d'ondes sismiques P (compressives Vp), S (cisaillement Vs) "
                    "et ondes de surface de Rayleigh/Love."
                ),
                "equations": [r"V_p = \sqrt{\frac{K + \frac{4}{3}\mu}{\rho}}", r"V_s = \sqrt{\frac{\mu}{\rho}}"],
            }

        if "show gps deformation" in q or "show insar" in q or "déformation insar" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "insar_deformation_layer",
                "physical_explanation": (
                    "Activation du champ de déplacement par interférométrie radar InSAR (Sentinel-1) "
                    "et des vecteurs de vitesse du réseau d'observation GNSS continu."
                ),
            }

        if "explain mw" in q or "magnitude de moment" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "La magnitude de moment (Mw) mesure l'énergie physique totale libérée par un séisme, "
                    "dérivée du moment sismique scalaire M0 = mu * A * D (où mu est la rigidité du milieu, "
                    "A la surface de la faille rompue et D le glissement moyen)."
                ),
                "equation": r"M_w = \frac{2}{3}\log_{10} M_0 - 6.07 \quad (\text{avec } M_0 \text{ en N.m})",
                "references": ["Kanamori (1977) JGR", "Hanks & Kanamori (1979) JGR"],
            }

        if "explain gutenberg richter" in q or "gutenberg-richter" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "La loi de Gutenberg-Richter décrit la relation fréquence-magnitude de la sismicité : "
                    "log10(N) = a - b*M, où N est le nombre de séismes de magnitude >= M. "
                    "La valeur b est généralement voisine de 1.0 (1 séisme de M6 pour 10 séismes de M5)."
                ),
                "equation": r"\log_{10} N = a - b \cdot M",
                "references": ["Gutenberg & Richter (1944) BSSA"],
            }

        if "explain omori" in q or "loi d'omori" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "La loi d'Omori modifiée décrit la décroissance temporelle du taux de répliques n(t) "
                    "après un séisme majeur : n(t) = K / (t + c)^p, avec p ~ 1.0."
                ),
                "equation": r"n(t) = \frac{K}{(t + c)^p}",
                "references": ["Omori (1894)", "Utsu (1961)"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-034 Queries (Space Weather & Heliophysics)
        # -------------------------------------------------------------------
        if "show aurora" in q or "aurore boréale" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "auroral_oval_layer",
                "physical_explanation": (
                    "Activation de la couche d'ovale auroral (Auroral Oval) montrant la probabilité de précipitation "
                    "des électrons magnétosphériques guidés par le champ magnétique terrestre."
                ),
                "active_product": "OVATION Prime Model Auroral Oval",
            }

        if "show kp" in q or "show dst" in q or "predict geomagnetic storm" in q or "tempête géomagnétique" in q:
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "GeomagneticIndicesViewer",
                "physical_explanation": (
                    "Affichage des indices géomagnétiques Kp (0 à 9) et Dst (nT) mesurant les perturbations "
                    "du champ magnétique terrestre et l'intensité de la ceinture de courant (Ring Current)."
                ),
                "active_product": "NOAA Planetary Kp & Kyot Dst Indices",
            }

        if "show solar wind" in q or "show parker spiral" in q or "vent solaire" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "solar_wind_streamlines",
                "physical_explanation": (
                    "Visualisation 3D du vent solaire (vitesse Vsw en km/s, densité Nsw) et de la spirale de Parker "
                    "modélisés par WSA-ENLIL et mesurés au point L1 par DSCOVR / ACE."
                ),
                "equation": r"r - r_0 = -\frac{V_{\text{sw}}}{\Omega}(\phi - \phi_0)",
            }

        if "show cme" in q or "éjection de masse coronale" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "cme_propagation_layer",
                "physical_explanation": (
                    "Affichage de la propagation d'une Éjection de Masse Coronale (CME) dans l'héliosphère "
                    "décelée par SOHO / LASCO C2/C3 et modélisée par WSA-ENLIL."
                ),
            }

        if "show tec" in q or "show radio blackout" in q or "panne radio" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "ionospheric_tec_layer",
                "physical_explanation": (
                    "Cartographie du Contenu Électronique Total de l'ionosphère (TEC en TECU) et dégradation "
                    "des liaisons HF (Échelle NOAA Radio Blackout R1-R5)."
                ),
                "equation": r"\Delta s = \frac{40.3}{f^2} \text{TEC}",
            }

        if "show satellite charging" in q or "explain van allen belts" in q or "ceintures de van allen" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Les ceintures de Van Allen constituent deux régions toroïdales piégeant des particules chargées à haute énergie "
                    "(protons > 100 MeV dans la ceinture interne et électrons relativistes > 1 MeV dans la ceinture externe), "
                    "provoquant le risque de charge diélectrique profonde et des anomalies SEU sur les satellites."
                ),
                "van_allen_belts": ["Inner Belt (1.2 to 2.5 Re)", "Outer Belt (3 to 7 Re)"],
                "references": ["Van Allen & Frank (1959)", "NOAA Space Weather Prediction Manual"],
            }

        if "explain solar flare" in q or "éruption solaire" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Une éruption solaire (Solar Flare) est une libération soudaine d'énergie magnétique "
                    "accumulée dans l'atmosphère du Soleil au niveau des régions actives (Active Regions). "
                    "Elle émet un rayonnement électromagnétique intense dans les rayons X (Classifié GOES A, B, C, M, X) "
                    "provoquant l'ionisation immédiate de la couche D de l'ionosphère terrestre (Radio Blackout)."
                ),
                "goes_classes": ["C-Class (Minor)", "M-Class (Moderate)", "X-Class (Extreme)"],
                "references": ["Priest & Forbes (2002) Magnetic Reconnection", "GOES X-Ray Sensor Manual"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-033 Queries (Hydrology & Flooding)
        # -------------------------------------------------------------------
        if "show rivers" in q or "river discharge" in q or "hydrograph" in q or "débit rivière" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "river_network_layer",
                "physical_explanation": (
                    "Activation du réseau hydrographique et des jauges de débit Q (m³/s) "
                    "dérivés de LISFLOOD, HEC-RAS et des stations in-situ (Vigicrues / USGS)."
                ),
                "active_product": "River Network & Real-Time Discharge Hydrographs",
            }

        if "show flood risk" in q or "risques d'inondation" in q or "show watershed" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "flood_inundation_layer",
                "physical_explanation": (
                    "Affichage des cartes de risque d'inondation et d'extension des crues "
                    "générées par les simulations 2D HEC-RAS / EFAS pour une période de retour T = 100 ans."
                ),
            }

        if "show reservoir" in q or "show groundwater" in q or "nappe phréatique" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "groundwater_layer",
                "physical_explanation": "Activation de la couche des aquifères, du niveau de la nappe phréatique et des retenues de barrages.",
            }

        if "compare hec-hms and lisflood" in q or ("hec-hms" in q and "lisflood" in q):
            return {
                "question": question,
                "physical_explanation": (
                    "Comparaison des modèles hydrologiques HEC-HMS (USACE) et LISFLOOD (ECMWF EFAS) : "
                    "HEC-HMS est un modèle semi-distribué par sous-bassins très utilisé pour l'ingénierie des barrages et l'aménagement local. "
                    "LISFLOOD est un modèle distribué sur grille (1-5 km) couplé à la prévision numérique pour l'alerte précoce aux inondations à l'échelle continentale."
                ),
                "comparison_table": {
                    "HEC-HMS (USACE)": "Semi-distribué par sous-bassins, SCS Runoff, Muskingum, ingénierie d'aménagement local",
                    "LISFLOOD (ECMWF)": "Distribué sur grille 1-5 km, Bilan 2L, Onde kinématique, EFAS/GloFAS opérationnel",
                },
                "references": ["USACE HEC-HMS Manual (2021)", "Van Der Knijff et al. (2010) LISFLOOD JRC Report"],
            }

        if "explain infiltration" in q or "explain runoff" in q or "explication ruissellement" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le ruissellement de surface se produit lorsque le taux de précipitation dépasse la capacité d'infiltration du sol (Infiltration de Hortonian) "
                    "ou lorsque le sol atteint la saturation complète (Ruissellement Dunne)."
                ),
                "equation": r"S = \frac{25400}{CN} - 254, \quad Q = \frac{(P - 0.2S)^2}{P + 0.8S}",
                "references": ["USDA-SCS National Engineering Handbook Section 4"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-032 Queries (Marine & Oceanography)
        # -------------------------------------------------------------------
        if "show waves" in q or "show swell" in q or "afficher les vagues" in q or "houle" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "wave_height_layer",
                "physical_explanation": (
                    "Activation du champ de hauteur significative des vagues Hs (mètres) et de la période pic Tp "
                    "dérivé de WAVEWATCH III et des altimètres satellitaires."
                ),
                "active_product": "WaveWatch III Significant Wave Height Hs",
            }

        if "show sst" in q or "température de mer" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "sst_layer",
                "physical_explanation": "Affichage de la Température de Surface de la Mer (SST en °C) satellitaire et réanalyse ERA5/CMEMS.",
            }

        if "show ocean currents" in q or "courants océaniques" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "ocean_currents_layer",
                "physical_explanation": "Activation du champ de courants géostrophiques et de surface (NEMO / HYCOM 1/12°).",
            }

        if "show storm surge" in q or "surcote" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "storm_surge_layer",
                "physical_explanation": "Visualisation des surcotes de tempête (Storm Surge en mètres) générées par la dépression et le vent.",
            }

        if "show cyclone" in q or "ouragan" in q or "typhon" in q or "explain cyclone evolution" in q:
            return {
                "question": question,
                "action": "activate_widget",
                "widget_type": "TropicalCycloneTracker",
                "physical_explanation": "Affichage du suivi des cyclones tropicaux IBTrACS, cône d'incertitude et intensité Saffir-Simpson.",
            }

        if "show buoy" in q or "show argo" in q or "flotteur argo" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "marine_obs_layer",
                "physical_explanation": "Localisation et profils verticaux T/S du réseau de flotteurs autonomes ARGO et bouées d'ancrage NDBC.",
            }

        if "compare wavewatch and wam" in q or ("wavewatch" in q and "wam" in q):
            return {
                "question": question,
                "physical_explanation": (
                    "Comparaison des modèles spectraux de vagues WAVEWATCH III (NOAA) et WAM (ECMWF) : "
                    "WAVEWATCH III excelle dans les domaines globaux/régionaux avec propagation multi-grille et dissipation par déferlement. "
                    "WAM est directement couplé au modèle atmosphérique IFS d'ECMWF pour un échange bidirectionnel de rugosité de surface."
                ),
                "comparison_table": {
                    "WAVEWATCH III": "NOAA NCEP, grille 1/6°, 24 directions, 32 fréquences, propagation multi-résolution",
                    "WAM (ECMWF)": "ECMWF, couplé IFS, 36 directions, 36 fréquences, rétroaction de la rugosité de mer",
                },
                "references": ["Tolman (2014) NOAA Tech Note", "Komen et al. (1994) WAM Book"],
            }

        if "explain ekman transport" in q or "transport d'ekman" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le transport d'Ekman est le déplacement net de la couche de mélange océanique à 90° à droite du vent dans l'Hémisphère Nord "
                    "(à gauche dans l'Hémisphère Sud), résultant de l'équilibre entre la tension de surface du vent et la force de Coriolis."
                ),
                "equation": r"M_e = \frac{\tau}{\rho_0 f}",
                "references": ["Ekman (1905) Ark. Mat. Astron. Fys."],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-031 Queries (Aviation & Flight Safety)
        # -------------------------------------------------------------------
        if "show turbulence" in q or "afficher la turbulence" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "cat_turbulence_layer",
                "physical_explanation": (
                    "Activation de la couche de Turbulence en Air Clair (CAT) basée sur le taux de dissipation turbulente EDR "
                    "et le Nombre de Richardson Ri < 0.25 au-dessus de FL240."
                ),
                "threshold": "EDR >= 0.44 m^(2/3)/s (Severe Turbulence Alert)",
            }

        if "show icing" in q or "afficher le givrage" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "airframe_icing_layer",
                "physical_explanation": (
                    "Activation de la couche de givrage en vol (Airframe Icing Index) "
                    "dérivée du contenu en eau liquide surfondue (SLW) et des zones de pluie verglaçante FZRA."
                ),
            }

        if "decode metar" in q or "décoder metar" in q:
            return {
                "question": question,
                "action": "parse_product",
                "product_type": "METAR",
                "physical_explanation": "Décodage OACI/OMM du METAR : Pression QNH, Vent au sol, Visibilité, Nuages, Température/Point de rosée.",
            }

        if "decode sigmet" in q or "décoder sigmet" in q:
            return {
                "question": question,
                "action": "parse_product",
                "product_type": "SIGMET",
                "physical_explanation": "Décodage du SIGMET OACI : Zone de phénomène dangereux en FIR (EMBD TS, SEV TURB, SEV ICE, VA).",
            }

        if "best flight level" in q or "meilleur niveau de vol" in q:
            # CORRECTED: this used to claim a specific fabricated
            # "recommended_flight_level: FL360" with a fabricated
            # "+45kt tailwind" justification, regardless of any real
            # route, aircraft, or current wind/turbulence data - no
            # real flight-planning computation is connected here.
            return {
                "question": question,
                "recommended_flight_level": None,
                "physical_explanation": (
                    "Le choix du niveau de vol optimal dépend du compromis entre la consommation spécifique de carburant, "
                    "l'absence de Turbulence CAT (Ri > 0.5) et un vent arrière favorable - une recommandation réelle "
                    "nécessite la route, le type d'avion et les données de vent/turbulence actuelles, non fournies ici."
                ),
                "is_real_data": False,
            }

        if "find alternate airport" in q or "trouver terrain alternat" in q:
            # CORRECTED: this used to claim 2 specific fabricated
            # alternate airports (LFPO, LILH) with a fabricated
            # visibility/ceiling justification, regardless of any real
            # departure/destination airport or current weather data.
            return {
                "question": question,
                "recommended_alternates": [],
                "physical_explanation": (
                    "La sélection des terrains de déroutement nécessite une visibilité > 5000 m, un plafond > 1000 ft "
                    "et un ILS opérationnel - une recommandation réelle nécessite l'aéroport de référence et les "
                    "conditions météorologiques actuelles, non fournies ici."
                ),
                "is_real_data": False,
            }

        # -------------------------------------------------------------------
        # MISSION ACF-030 Queries (Operational Center)
        # -------------------------------------------------------------------
        if "show radar" in q or "afficher le radar" in q or "display radar" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "radar_volume",
                "physical_explanation": "Mosaïque radar nationale activée : Réflectivité ZH Max et vitesse Doppler VR.",
                "active_product": "NEXRAD / PANTHERE Composite ZH",
            }

        if "show satellite" in q or "afficher le satellite" in q or "display satellite" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "satellite_rgb",
                "physical_explanation": "Composition multispectrale EUMETSAT MTG / GOES-R activée (Canaux IR 10.8 µm et VIS 0.6 µm).",
                "active_product": "EUMETSAT RGB Day Natural",
            }

        if "generate briefing" in q or "générer le briefing" in q or "generate aviation briefing" in q:
            return {
                "question": question,
                "action": "generate_report",
                "report_type": "Aviation Briefing",
                "physical_explanation": "Génération automatique du bulletin météo aéronautique OACI (METAR, TAF, SIGWX, WAFC).",
            }

        if "explain warning" in q or "expliquer l'alerte" in q:
            # CORRECTED: this used to claim a fixed "severity: ORANGE"
            # as if reporting a real current alert severity - same
            # underlying issue as
            # hazard_operations.alert_generator.AlertGenerator (fixed
            # earlier this session). The physical_explanation text is
            # a genuine general explainer of what conditions WOULD
            # justify a warning, kept as-is; only the specific "current
            # severity" claim is removed.
            return {
                "question": question,
                "physical_explanation": (
                    "Une alerte opérationnelle est généralement justifiée par la combinaison d'une instabilité convective marquée "
                    "(CAPE > 2000 J/kg) et d'un cisaillement vertical fort (Shear 0-6km > 18 m/s), entraînant un risque élevé "
                    "d'orages supercellulaires avec grêle - la sévérité réelle dépend des conditions actuelles, non fournies ici."
                ),
                "severity": None,
                "references": ["WMO Severe Weather Guidelines", "Météo-France Directives Vigicrues"],
            }

        if "show sounding" in q or "afficher le sondage" in q or "emagramme" in q:
            return {
                "question": question,
                "action": "open_widget",
                "widget_type": "ThermodynamicSoundingViewer",
                "physical_explanation": "Profil vertical thermodynamique Skew-T / Emagramme 761 du radiosondage TEMP.",
            }

        # -------------------------------------------------------------------
        # MISSION ACF-029 Queries (Climate & Earth System)
        # -------------------------------------------------------------------
        if "explain enso" in q or "expliquer enso" in q or q.strip() == "enso":
            return {
                "question": question,
                "physical_explanation": (
                    "L'Oscillation Australe El Niño (ENSO) est le principal mode de variabilité interannuelle du couplage océan-atmosphère. "
                    "En phase El Niño (ONI >= +0.5°C), le réchauffement des eaux du Pacifique Est affaiblit les alizés et déplace la circulation de Walker. "
                    "En phase La Niña (ONI <= -0.5°C), le renforcement des alizés accentue la résurgence d'eau froide le long des côtes équatoriales."
                ),
                "causal_chain": "Trade Wind Weakening -> Reduced Upwelling -> East Pacific Warming -> Walker Cell Disruption -> Global Teleconnections",
                "latex_equation": r"\text{ONI} = \overline{\text{SST}_{\text{NINO3.4}} - \text{SST}_{\text{climatology}}}^{\,3\text{ mois}}",
                "impacts": [
                    "Sécheresses en Australie/Indonésie",
                    "Inondations au Pérou",
                    "Modification des trajectoires des tempêtes synoptiques",
                ],
                "references": ["Trenberth (1997) BAMS", "IPCC AR6 WG1"],
            }

        if "compare era5 and merra2" in q or ("era5" in q and "merra2" in q):
            return {
                "question": question,
                "physical_explanation": (
                    "Comparaison entre la réanalyse ERA5 (ECMWF) et MERRA-2 (NASA GMAO) : "
                    "ERA5 offre une résolution spatiale de 0.25° (~31 km) avec assimilation 4D-Var IFS Cy41r2 sur 137 niveaux verticaux (1940-Présent). "
                    "MERRA-2 offre une résolution de 0.5° x 0.625° avec 3D-Var GSI et se distingue par l'assimilation explicite du cycle des aérosols et du bilan radiatif."
                ),
                "comparison_table": {
                    "ERA5 (ECMWF)": "0.25° grid, 4D-Var, 137 levels, 1940-Present, référence mondiale pour la dynamique atmosphérique",
                    "MERRA-2 (NASA)": "0.5°x0.625° grid, 3D-Var GSI, 72 levels, 1980-Present, référence pour l'ozone, aérosols et radiation",
                },
                "references": ["Hersbach et al. (2020) QJRMS", "Gelaro et al. (2017) J. Climate"],
            }

        if "cmip6 projections" in q or "projections cmip6" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Les projections climatiques CMIP6 reposent sur les scénarios d'émissions socio-économiques SSP (Shared Socioeconomic Pathways) : "
                    "SSP1-1.9 (1.5°C), SSP1-2.6 (2.0°C), SSP2-4.5 (2.7°C), SSP3-7.0 (3.6°C), et SSP5-8.5 (4.4°C d'ici 2100)."
                ),
                "available_scenarios": ["SSP1-1.9", "SSP1-2.6", "SSP2-4.5", "SSP3-7.0", "SSP5-8.5"],
                "references": ["IPCC AR6 WG1 Report (2021)", "Eyring et al. (2016) GMD"],
            }

        if "explain ssp2-4.5" in q or "ssp2-4.5" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le scénario SSP2-4.5 est le scénario intermédiaire 'Middle of the Road' de CMIP6. "
                    "Il suppose la poursuite des tendances environnementales et économiques actuelles avec des politiques climatiques modérées, "
                    "aboutissant à un forçage radiatif de 4.5 W/m² et un réchauffement moyen mondial de ~2.7°C d'ici 2100."
                ),
                "forcing_2100": "4.5 W/m²",
                "warming_2100": "~2.7°C (Plage 2.1°C à 3.5°C)",
                "co2_concentration": "600 ppm en 2100",
                "references": ["Fricko et al. (2017) Glob. Environ. Change"],
            }

        if "drought index" in q or "indice de sécheresse" in q or "show drought" in q or "show spi" in q:
            return {
                "question": question,
                "action": "activate_layer",
                "layer_type": "drought_index_layer",
                "physical_explanation": (
                    "L'indice de sécheresse standardisé WMO est le SPI (Standardized Precipitation Index) et le SPEI (incorporant l'évapotranspiration) : "
                    "SPI <= -2.0 correspond à une sécheresse extrême, tandis que SPI >= +2.0 correspond à une humidité extrême."
                ),
                "drought_indices": [
                    "SPI (Standardized Precipitation Index)",
                    "SPEI (Evapotranspiration-based)",
                    "PDSI (Palmer Drought Severity Index)",
                ],
                "references": ["WMO-No. 1090 SPI User Guide", "McKee et al. (1993)"],
            }

        if "compare climate models" in q or "comparer les modèles climatiques" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Comparaison des grands modèles du système Terre CMIP6 : "
                    "CESM2 (NCAR) offre une dynamique continentale CLM5 très poussée (ECS = 5.2 K). "
                    "EC-Earth3 (Europe) intègre le noyau spectral IFS d'ECMWF. "
                    "SCREAM (DOE) est le premier modèle mondial d'atmosphère non-hydrostatique à 3 km résolvant explicitement les nuages."
                ),
                "models_compared": ["CESM2", "EC-Earth3", "MPI-ESM1.2", "CNRM-CM6-1", "SCREAM"],
                "references": ["Danabasoglu et al. (2020)", "Döscher et al. (2022)", "Caldwell et al. (2021)"],
            }

        if "explain amo" in q or "expliquer amo" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "L'Oscillation Multidécennale de l'Atlantique (AMO) est un mode de variabilité naturelle des températures de surface "
                    "de l'Atlantique Nord sur un cycle de 60 à 80 ans. Sa phase chaude (AMO+) favorise l'activité cyclonique dans l'Atlantique."
                ),
                "region": "Atlantique Nord (0°-60°N)",
                "references": ["Enfield et al. (2001) GRL"],
            }

        if "nao positive" in q or "nao+" in q or "nao est positive" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "La NAO est en phase positive (NAO+) lorsque le gradient de pression entre l'Anticyclone des Açores et la Dépression d'Islande est particulièrement renforcé. "
                    "Cela accélère le jet stream de l'Atlantique Nord, canalisant les tempêtes et l'air doux vers le Nord-Ouest de l'Europe."
                ),
                "synoptic_pattern": "Strong Azores High + Deep Icelandic Low -> Accelerated Jet Stream -> Mild & Wet West Europe",
                "references": ["Hurrell (1995) Science"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-028 Queries (AI & Physics-Informed AI)
        # -------------------------------------------------------------------
        if "ai predict heavy rain" in q or "prédit de fortes pluies" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "L'IA (ex: GraphCast / AROME-AI) prédit de fortes pluies en raison de la convergence de trois facteurs majeurs : "
                    "1) Un transport d'humidité élevé (Precipitable Water PWV > 40 mm et IVT > 400 kg/m/s), "
                    "2) Une forte instabilité convective (CAPE > 1500 J/kg) générant de puissantes ascendances (w > 10 m/s), "
                    "3) Un forçage synoptique d'altitude (divergence de ligne de jet et advection de vorticité)."
                ),
                "causal_chain": "Moisture Advection + Synoptic Forcing -> Strong Updrafts -> Cloud Water Coalescence -> Heavy Precipitation",
                "equations": [
                    r"P = \int_{z_0}^{z_{\text{top}}} \rho_{\text{air}} \cdot w \cdot \frac{\partial q_v}{\partial z} dz"
                ],
                "key_variables": ["PWV (mm)", "IVT (kg/m/s)", "CAPE (J/kg)", "Vertical Velocity w (m/s)"],
                "references": ["Lam et al. (2023) Science", "Doswell et al. (1996)"],
            }

        if "confidence low" in q or "confiance est faible" in q or "why is confidence" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "La confiance de la prévision est faible (incertitude élevée) lorsque l'écart-type d'ensemble (Ensemble Spread) est important. "
                    "Cela se produit généralement lors de situations de bifurcation dynamique : "
                    "1) Creusement incertain d'une dépression secondaire ou trajectoire d'un cyclone tropical, "
                    "2) Transitoire convectif méso-échelle sensible aux conditions initiales (incertitude épistémique du modèle d'IA), "
                    "3) Bifurcation dans la position du Jet Stream à moyen terme (> 7 jours)."
                ),
                "uncertainty_metrics": {
                    "Epistemic Uncertainty": "Sensibilité aux poids et architectures des modèles d'IA",
                    "Aleatoric Uncertainty": "Bruit intrinsèque des observations météo",
                    "Ensemble Spread": "Standard Deviation de l'ensemble > 2.5 sigma",
                },
                "references": ["Bauer et al. (2015) Nature", "Price et al. (2024) GenCast Paper"],
            }

        if (
            "compare graphcast and ifs" in q
            or ("graphcast" in q and "ifs" in q)
            or ("compare ecmwf and graphcast" in q)
        ):
            return {
                "question": question,
                "physical_explanation": (
                    "Comparaison entre GraphCast (IA Google DeepMind) et IFS (Modèle Numérique Physique ECMWF) : "
                    "GraphCast effectue la prévision globale 10 jours en ~1 minute via un Graph Neural Network sur grille icosaédrique 0.25°. "
                    "IFS résout de manière déterministe les équations primitives de la dynamique des fluides et de la thermodynamique (4D-Var). "
                    "GraphCast surpasse IFS sur la plupart des métriques RMSE à 5-10 jours, mais IFS conserve une meilleure résolution des gradients extrêmes locaux."
                ),
                "comparison_table": {
                    "GraphCast (IA)": "GNN icosaédrique 0.25°, 37 niveaux, 60 secondes d'inférence GPU, très faible RMSE",
                    "ECMWF IFS (NWP)": "Solveur dynamique spectral TCo1279 (~9 km), 137 niveaux, physique explicite 4D-Var",
                },
                "references": ["Lam et al. (2023) Science 382, 1416-1421", "ECMWF IFS Documentation"],
            }

        if "explain ensemble spread" in q or "expliquer l'écart-type d'ensemble" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "L'écart-type d'ensemble (Ensemble Spread) mesure la dispersion géographique et d'amplitude "
                    "des N membres de prévision (NWP ou IA stochastique comme GenCast). "
                    "Un spread faible indique une prévision prédictible à forte confiance. "
                    "Un spread élevé traduit une forte incertitude dynamique quant à l'évolution future de l'atmosphère."
                ),
                "equation": r"\text{Spread} = \sqrt{\frac{1}{N-1} \sum_{i=1}^N (x_i - \bar{x})^2}",
                "references": ["Leutbecher & Palmer (2008) J. Comp. Phys."],
            }

        if "severe weather risk" in q or "risque de temps violent" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le risque de temps violent est évalué par la combinaison de la vulnérabilité environnementale "
                    "et des indices physiques composites : "
                    "1) Instabilité convective (CAPE > 1000 J/kg), "
                    "2) Cisaillement vertical du vent (Shear 0-6 km > 15 m/s et Helicity SREH > 150 m²/s²), "
                    "3) Contenu en vapeur d'eau (PWV > 35 mm et IVT > 300 kg/m/s)."
                ),
                "risk_indices": [
                    "Energy Helicity Index (EHI)",
                    "Significant Severe Parameter (STP)",
                    "MESH Hail Index",
                ],
                "references": ["NOAA SPC Severe Weather Manual", "Doswell (2001)"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-026 Queries (Dataset Ingestion)
        # -------------------------------------------------------------------
        if "variables exist in" in q or "variables grib" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Les fichiers GRIB (GRIB1/GRIB2) contiennent des champs tridimensionnels codés selon la table de paramètres WMO. "
                    "Dans les fichiers GRIB opérationnels d'IFS, AROME ou GFS, on retrouve typiquement :"
                ),
                "grib_variables": [
                    "Temperature (t / ta) - GRIB2 Discipline 0, Category 0, Number 0",
                    "Geopotential Height (gh / z) - GRIB2 Discipline 0, Category 3, Number 5",
                    "U & V Wind Components (u, v) - GRIB2 Discipline 0, Category 2, Number 2 & 3",
                    "Relative Humidity (r / hur) - GRIB2 Discipline 0, Category 1, Number 1",
                    "CAPE (cape) - GRIB2 Discipline 0, Category 7, Number 6",
                    "Surface Pressure (sp / ps) - GRIB2 Discipline 0, Category 3, Number 0",
                ],
                "references": ["WMO GRIB2 Code Manual (WMO-No. 306)"],
            }

        if "cf standard names" in q or "noms standards cf" in q:
            return {
                "question": question,
                "physical_explanation": "La convention Climate and Forecast (CF) définit des noms standardisés universels :",
                "available_cf_standard_names": [
                    "air_temperature (K)",
                    "air_pressure (Pa)",
                    "relative_humidity (%)",
                    "atmosphere_convective_available_potential_energy (J/kg)",
                    "eastward_wind (m/s)",
                    "northward_wind (m/s)",
                    "mass_fraction_of_cloud_liquid_water_in_air (kg/kg)",
                    "equivalent_potential_temperature (K)",
                ],
                "references": ["CF Conventions v1.10 Standard Name Table"],
            }

        if "datasets contain cape" in q or "fichiers contiennent le cape" in q:
            return {
                "question": question,
                "physical_explanation": "Le CAPE est une variable diagnostique convective clé présente dans les jeux de données suivants :",
                "datasets_with_cape": [
                    "ECMWF ERA5 Reanalysis (Single Levels NetCDF/GRIB)",
                    "Météo-France AROME Operational Forecasts (GRIB2 1.3 km)",
                    "NOAA GFS / HRRR Operational Severe Weather Grids (GRIB2)",
                    "DWD ICON-EU / ICON-D2 NWP Datasets (GRIB2)",
                    "Sondages verticalement intégrés WMO RADIOSONDE / TEMP",
                ],
                "parameter_key": "CAPE",
                "references": ["WMO NWP Operational Product Guide"],
            }

        if "radar reflectivity" in q or "réflectivité radar" in q:
            return {
                "question": question,
                "physical_explanation": "La réflectivité radar horizontale (Z_H) est stockée dans les volumes et mosaïques radar suivants :",
                "radar_file_formats": [
                    "HDF5 OPERA Data Information Model (ODIM H5)",
                    "NEXRAD Level II & Level III Binary Grids",
                    "Météo-France PANTHERE / BUFR Radar Mosaics",
                    "NetCDF RADAR CF-Conventions Radial Volume Files",
                ],
                "variable": "Z_H (dBZ)",
                "references": ["EUMETNET OPERA ODIM Specifications"],
            }

        if "come from metar" in q or "observations metar" in q:
            return {
                "question": question,
                "physical_explanation": "Les messages d'observation d'aérodrome METAR / SPECI fournissent en temps réel :",
                "metar_variables": [
                    "Wind Direction & Speed (dddffKT)",
                    "Horizontal Visibility (meters / Statute Miles)",
                    "Runway Visual Range (RVR Rxx/xxxx)",
                    "Present Weather (WW: RA, SN, TS, FG, BR, GR)",
                    "Cloud Layers (FEW, SCT, BKN, OVC) & Ceiling (ft)",
                    "Air Temperature & Dewpoint (T'T'/T'dT'd)",
                    "Altimeter Setting (QNH hPa / inHg)",
                ],
                "references": ["ICAO Annex 3", "WMO-No. 782"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-025 Queries (Observations)
        # -------------------------------------------------------------------
        if "measure humidity" in q or "mesurent l'humidité" in q:
            return {
                "question": question,
                "physical_explanation": "Les systèmes d'observation mesurant la vapeur d'eau et l'humidité atmosphérique sont :",
                "observing_systems": [
                    "Radiosondages TEMP (Hygromètres capacitifs à film mince Vaisala RS41)",
                    "Stations de Surface SYNOP / AWS (Hygromètres électroniques et psychromètres)",
                    "GNSS / GPS Radio Occultation & Zenith Wet Delay (ZWD / PWV)",
                    "Sondes Infrarouges Satellitaires (EUMETSAT IASI, NOAA CrIS)",
                    "Radiomètres Hyperfréquences Satellitaires (MHS, AMSU-B, ATMS)",
                    "Lidars Raman et DIAL d'humidité (Water Vapor Lidar)",
                ],
                "measured_variables": ["RH (%)", "Dewpoint Td (K)", "Mixing ratio w (g/kg)", "PWV (mm)"],
                "references": ["WMO-No. 8 Guide to Meteorological Instruments", "GCOS Standards"],
            }

        if "radar variables detect hail" in q or ("variables radar" in q and "grêle" in q):
            return {
                "question": question,
                "physical_explanation": (
                    "La détection de la grêle par radar météorologique à double polarisation repose sur la signature spécifique "
                    "de la Réflectivité forte (Z_H > 50 dBZ) combinée à une Réflectivité Différentielle très faible ou négative (Z_DR ~ 0 dB à -1 dB) "
                    "due à la forme sphérique des grêlons en tumbling, ainsi qu'à une baisse du coefficient de corrélation (rho_hv < 0.95)."
                ),
                "polarimetric_radar_signatures": {
                    "Reflectivity Z_H": "> 50 dBZ (Fortes rétrodiffusions)",
                    "Differential Reflectivity Z_DR": "~ 0 dB (Forme sphérique des grêlons tournoyants)",
                    "Correlation Coefficient rho_hv": "< 0.95 (Mélange de phases et formes incohérentes)",
                    "MESH / SHI Index": "Maximum Expected Size of Hail / Severe Hail Index",
                },
                "references": ["Bringi & Chandrasekar (2001)", "Kumjian (2013) J. Operational Meteor."],
            }

        if "assimilated by ifs" in q or "assimilées par ifs" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le modèle global de l'ECMWF (IFS) assimile en continu via son algorithme 4D-Var toutes les composantes du WIGOS :"
                ),
                "assimilated_observation_types": [
                    "Radiance satellitaire brute 4D-Var All-Sky (IASI, CrIS, SEVIRI, ATMS, SSMIS, MWHS-2)",
                    "Profils thermiques et de vent par avions de ligne (AMDAR / ACARS)",
                    "Radio-Occultation GPS / GNSS-RO (COSMIC-2, Spire, MetOp)",
                    "Radiosondages TEMP et Dropsondes",
                    "Vents de surface océanique par Scatteromètre (ASCAT)",
                    "Stations de surface SYNOP, SHIP, BUOY (Pression QFF, Vent)",
                    "Atmospheric Motion Vectors (AMV satellitaires)",
                ],
                "references": ["ECMWF IFS Documentation - Data Assimilation", "Hersbach et al. (2020) ERA5"],
            }

        if "metar visibility encoded" in q or "visibilité metar" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "La visibilité prédominante horizontale dans un message METAR est codée en mètres sur 4 chiffres : "
                    "0000 (< 50 m), 0500 (500 m), 1500 (1500 m), 9999 (Visibilité >= 10 km, ou CAVOK). "
                    "Aux USA, elle est codée en Miles Statutaires (ex: 1/4SM, 3SM, 10SM)."
                ),
                "examples": {
                    "9999": ">= 10 km (Visibilité illimitée)",
                    "0800": "800 mètres",
                    "10SM": "10 Miles Statutaires (16 km)",
                },
                "references": ["ICAO Annex 3 Section 4.6", "WMO-No. 782 Aerodrome Reports Guide"],
            }

        if "provide cape inputs" in q or "entrées du cape" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le calcul du CAPE nécessite le profil vertical complet de la température (T) et de l'humidité (Td) "
                    "depuis la surface jusqu'à la tropopause."
                ),
                "input_observations": [
                    "Radiosondages TEMP (Profil vertical in-situ le plus précis)",
                    "Profils d'ascendance/descente AMDAR / ACARS d'avions",
                    "Sondeurs satellite thermodynamiques infrarouges et hyperfréquences (IASI, CrIS, NUCAPS)",
                    "Stations de surface AWS / SYNOP",
                ],
                "references": ["NOAA SPC Sounding Analysis", "WMO Guide to Observations"],
            }

        if "radiosonde quality control" in q or "qc radiosondage" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le contrôle qualité (QC) des radiosondages s'effectue en plusieurs étapes automatisées : "
                    "Gross Error Check, Hydrostatic Consistency Check, Lapse Rate Check, Wind Shear Check, Background Check."
                ),
                "qc_steps": ["Physic limits", "Hydrostatic test", "Superadiabatic check", "Background O-B test"],
                "references": ["WMO-No. 8 Chapter 12", "ECMWF Data Quality Control Manual"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-024 Queries (Operational Physics)
        # -------------------------------------------------------------------
        if "why cape increases" in q or "pourquoi le cape augmente" in q or "explain why cape" in q:
            return {
                "question": question,
                "parameter_key": "CAPE",
                "physical_explanation": (
                    "Le CAPE augmente sous l'effet de deux facteurs principaux : "
                    "1) Le réchauffement radiatif diurne de la couche de surface qui augmente la température potentielle équivalente (theta_e) de la parcelle, "
                    "2) L'advection d'air chaud et humide dans les basses couches combinée au refroidissement adiabatique ou synoptique en altitude."
                ),
                "causal_chain": "Surface Heating + Low-Level Moisture Advection -> Increased Theta_e -> Higher Buoyancy -> Increased CAPE",
                "equations": [
                    r"\text{CAPE} = \int_{z_{\text{LFC}}}^{z_{\text{EL}}} g \frac{T_{v,\text{parcel}} - T_{v,\text{env}}}{T_{v,\text{env}}} dz"
                ],
                "parameters": {"CAPE": "J/kg", "Theta_e": "K", "Lapse_Rate": "K/km"},
                "references": ["NOAA SPC Severe Weather Manual", "Emanuel (1994)"],
            }

        if "schemes predict graupel" in q or ("microphysique" in q and "graupel" in q):
            return {
                "question": question,
                "physical_explanation": "Les schémas microphysiques à 5 et 6 espèces prédisant explicitement le rapport de mélange du graupel (qg) sont :",
                "microphysics_schemes": [
                    "Thompson Aerosol-Aware 2-Moment Scheme (WRF / HRRR)",
                    "Morrison 2-Moment Microphysics Scheme (WRF / CESM)",
                    "Meso-NH ICE3 / ICE4 Schemes (Météo-France / AROME / ACCORD)",
                    "WDM6 / WSM6 6-Class Microphysics (WRF)",
                    "Seifert & Beheng 2-Moment Scheme (DWD ICON)",
                    "Lin-Farley-Orville Scheme (WRF)",
                ],
                "prognostic_species": [
                    "q_c (eau nuageuse)",
                    "q_i (glace)",
                    "q_r (pluie)",
                    "q_s (neige)",
                    "q_g (graupel)",
                ],
                "references": ["Thompson et al. (2008)", "Morrison et al. (2005)", "Lac et al. (2018)"],
            }

        if ("thompson" in q and "morrison" in q) or "compare thompson" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Comparaison des schémas microphysiques Thompson et Morrison : "
                    "Le schéma de Thompson prédit 2 moments pour la glace et la pluie avec aérosols CCN/INP explicites. "
                    "Le schéma de Morrison prédit 2 moments pour toutes les espèces d'hydrométéores."
                ),
                "comparison_table": {
                    "Thompson": "2-moment pour pluie/glace, 1-moment pour neige/graupel/eau, Aerosol-Aware explicite",
                    "Morrison": "Full 2-moment pour les 5 espèces d'hydrométéores (masse + nombre)",
                },
                "references": ["Thompson et al. (2008) Mon. Wea. Rev.", "Morrison et al. (2009) Mon. Wea. Rev."],
            }

        if "volcanic ash" in q or "cendres volcaniques" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Les cendres volcaniques sont détectées par la méthode Brightness Temperature Difference (BTD) "
                    "entre les canaux IR 10.8 µm et 12.0 µm (Split Window) et par lidars (CALIPSO, EarthCARE)."
                ),
                "satellite_sensors": [
                    "EUMETSAT Meteosat SEVIRI (Canaux IR 10.8 µm - IR 12.0 µm BTD Ash Product)",
                    "NOAA GOES-16/17 ABI (Canaux 14 - 15 Volcanic Ash RGB)",
                    "Terra/Aqua MODIS & Suomi NPP VIIRS (Volcanic Ash Detection)",
                    "CALIPSO / EarthCARE Lidar (Profil vertical des aérosols de cendres)",
                ],
                "applications": [
                    "Centre d'Avis de Cendres Volcaniques (ICAO VAAC)",
                    "Sécurité des vols transcontinentaux",
                ],
                "references": ["ICAO Doc 9766 Volcanic Ash", "Prata (1989) J. Geophys. Res."],
            }

        if "bergeron" in q or "processus de bergeron" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le processus de Bergeron-Findeisen se produit dans les nuages en phase mixte (-10°C à -40°C) "
                    "car e_i(T) < e_w(T). L'eau surfondue s'évapore au profit de la croissance par déposition des cristaux de glace."
                ),
                "governing_inequality": r"e_i(T) < e_{\text{vapeur}} \le e_w(T) \quad (\text{pour } T < 0^\circ\text{C})",
                "references": ["Bergeron (1935)", "Findeisen (1938)", "Pruppacher & Klett (1997)"],
            }

        if "richardson" in q or "nombre de richardson" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le Nombre de Richardson (Ri) mesure le rapport entre la flottabilité et le cisaillement du vent. "
                    "Si Ri < 0.25 (Ri_c), l'écoulement devient turbulent (CAT)."
                ),
                "equation": r"Ri = \frac{\frac{g}{\theta}\frac{\partial \theta}{\partial z}}{\left(\frac{\partial u}{\partial z}\right)^2 + \left(\frac{\partial v}{\partial z}\right)^2}",
                "critical_value": "Ri_c = 0.25",
                "references": ["Richardson (1920) Proc. R. Soc. Lond.", "Stull (1988) Boundary Layer Meteorology"],
            }

        if "ice4" in q:
            return {
                "question": question,
                "physical_explanation": "Les modèles de prévision numérique intégrant le schéma microphysique ICE4 sont :",
                "nwp_models": [
                    "AROME (Météo-France)",
                    "AROME-NWC (Nowcasting haute fréquence Météo-France)",
                    "HARMONIE-AROME (Consortium ACCORD - 26 services météo européens)",
                    "Meso-NH (CNRS / Météo-France Cloud Resolving Model)",
                ],
                "microphysics_species": [
                    "q_c (eau nuageuse)",
                    "q_i (glace)",
                    "q_r (pluie)",
                    "q_s (neige)",
                    "q_g (graupel)",
                    "q_h (grêle)",
                ],
                "references": ["Lac et al. (2018) Geosci. Model Dev."],
            }

        if "cloud producing hail" in q or "clouds producing hail" in q or "nuages grêle" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "Le Cumulonimbus (Cb) est le seul genre de nuage capable de produire de la grêle."
                ),
                "cloud_types": [
                    "Cumulonimbus capillatus incus (OMM)",
                    "Supercellule Mesocyclonique (Classic, HP, LP)",
                    "Ligne de grain / Bow Echo (QLCS)",
                ],
                "necessary_conditions": [
                    "w_max > 25 m/s",
                    "Sursaturation en phase mixte (-10°C à -25°C)",
                    "Forte présence de graupels et eau surfondue",
                ],
                "references": ["WMO Cloud Atlas (2017)", "Knight & Knight (2001) Hail Physics"],
            }

        # -------------------------------------------------------------------
        # MISSION ACF-023 Queries (Parameters & Thermodynamics)
        # -------------------------------------------------------------------
        if "potential temperature" in q or "température potentielle" in q:
            param = self.param_engine.get("potential_temperature")
            return {
                "question": question,
                "parameter_key": "potential_temperature",
                "equation": r"\theta = T \left(\frac{p_0}{p}\right)^{0.286}",
                "physical_explanation": (
                    "La température potentielle (Theta) est la température qu me aura une parcelle d'air "
                    "si elle était ramenée de manière adiabatique sèche à la pression de référence p0 = 1000 hPa."
                ),
                "equations": [r"\theta = T \left(\frac{p_0}{p}\right)^{0.286}"],
                "parameters": {"theta": "K (Température potentielle)"},
                "references": param.references if param else ["Poisson (1823)", "WMO Physics"],
            }

        if "what is cape" in q or "qu'est-ce que le cape" in q or q.strip() == "cape":
            param = self.param_engine.get("CAPE")
            return {
                "question": question,
                "parameter_key": "CAPE",
                "physical_explanation": (
                    "Le CAPE (Convective Available Potential Energy) "
                    "est l'intégrale verticale de la poussée d'Archimède positive exercée sur une parcelle d'air "
                    "ascendante depuis le niveau de libre convection (LFC) jusqu'au niveau d'équilibre (EL)."
                ),
                "causal_chain": "Surface heating -> Instability -> CAPE -> Updraft",
                "equations": [
                    r"\text{CAPE} = \int_{z_{\text{LFC}}}^{z_{\text{EL}}} g \frac{T_{v,\text{parcel}} - T_{v,\text{env}}}{T_{v,\text{env}}} dz"
                ],
                "parameters": {"CAPE": "J/kg", "LFC": "m", "EL": "m"},
                "units": "J/kg",
                "references": param.references if param else ["WMO Severe Weather Manual", "NOAA SPC"],
            }

        if "depend on humidity" in q or "dépendent de l'humidité" in q or ("humidity" in q and "depend" in q):
            dependent_params = self.param_engine.dependents("humidity")
            param_names = [p.name for p in dependent_params]
            param_keys = [p.key for p in dependent_params]
            return {
                "question": question,
                "physical_explanation": "Les paramètres météorologiques dépendant directement de l'humidité relative ou spécifique de l'air sont :",
                "dependent_parameters": param_names
                if param_names
                else [
                    "Température Virtuelle (Tv)",
                    "Température Potentielle Équivalente (Theta_e)",
                    "CAPE",
                    "CIN",
                    "Rapport de Mélange (w)",
                    "Eau Liquide Nuageuse (qc)",
                ],
                "dependent_keys": param_keys
                if param_keys
                else [
                    "virtual_temperature",
                    "equivalent_potential_temperature",
                    "CAPE",
                    "CIN",
                    "mixing_ratio",
                    "cloud_water",
                ],
                "references": ["WMO Atmospheric Thermodynamics Manual"],
            }

        if "cloud top" in q or "cloud-top" in q or "sommet du nuage" in q:
            return {
                "question": question,
                "physical_explanation": (
                    "La température au sommet des nuages (Cloud Top Temperature / CTT) est observée par les canaux infrarouges "
                    "thermiques (10.8 µm - 12.0 µm) des satellites géostationnaires et défilants."
                ),
                "satellite_instruments_and_products": [
                    "MSG / SEVIRI (EUMETSAT Channel 9 10.8 µm CTT Product)",
                    "GOES-16/17 ABI (NOAA Channel 14 11.2 µm)",
                    "Himawari-8/9 AHI (JMA Band 14)",
                    "MetOp IASI / Terra-Aqua MODIS (Cloud Top Temperature Retrieval)",
                ],
                "applications": [
                    "Détection du sommet des Cumulonimbus (Overshooting Tops)",
                    "Prévision d'orage immédiat (Nowcasting)",
                ],
                "references": ["EUMETSAT MSG User Guide", "NOAA GOES-R Series Product Definition"],
            }

        # Default convective storm response
        source_concept = "cape"
        target_concept = "grêle"
        if ("orage" in q or "cumulonimbus" in q) and "grêle" in q:
            source_concept = "cumulonimbus"
            target_concept = "grêle"

        chain_info = self.graph.explain_chain(source_concept, target_concept)
        matched_entries = EncyclopediaRegistry.search("grêle") + EncyclopediaRegistry.search("cumulonimbus")

        seen_keys = set()
        unique_entries = []
        for e in matched_entries:
            if e.key not in seen_keys:
                seen_keys.add(e.key)
                unique_entries.append(e)

        equations = [e.latex_equation for e in unique_entries if e.latex_equation]
        references = [ref for e in unique_entries for ref in e.references]
        references = list(dict.fromkeys(references))

        explanation_text = (
            "Un orage (Cumulonimbus) produit de la grêle en raison du couplage fort entre la dynamique de l'ascendance "
            "et la microphysique de la phase mixte. L'instabilité convective (CAPE) engendre un courant ascendant très rapide "
            "(w_max > 25 m/s) capable de maintenir en suspension des embryons de glace (graupels) au-dessus du niveau 0°C. "
            "Dans la zone de surfrusion (-10°C à -25°C), les graupels capturent par accrétion des gouttelettes d'eau surfondue "
            "(givrage en régime humide), augmentant de taille jusqu'à ce que leur masse dépasse la sustentation "
            "offerte par le vent ascendant, déclenchant leur chute vers le sol."
        )

        return {
            "question": question,
            "physical_explanation": explanation_text,
            "causal_chain": chain_info.get("explanation", ""),
            "detailed_chain_steps": chain_info.get("chain", []),
            "equations": equations
            if equations
            else [r"z_{\text{LCL}} = 125(T-T_d)", r"\text{CAPE} = \int g \frac{T_v - T_{ve}}{T_{ve}} dz"],
            "parameters": {
                "CAPE": "J/kg (Énergie potentielle d'ascendance)",
                "Updraft_w_max": "m/s (Vitesse maximale du courant ascendant)",
                "Freezing_level": "m (Altitude du niveau 0°C)",
                "LWC": "g/m³ (Liquid Water Content)",
            },
            "references": references
            if references
            else [
                "WMO International Cloud Atlas (2017)",
                "Knight & Knight (2001) Hailstorm Physics",
                "Pruppacher & Klett (1997)",
            ],
        }


def ask(question: str) -> dict[str, Any]:
    """Fonction raccourci globale acf.science.ask()."""
    engine = ScientificQueryEngine()
    return engine.ask(question)
