"""Generador trilingüe para el oficio ASTRONOMIA."""

from __future__ import annotations

from scripts.trilingual_generators.base import (
    ClauseData,
    build_clauses_for_lang,
    load_extended_seeds,
)

ALMA = "astronomia"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "El corrimiento al rojo cosmológico de galaxias distantes",
    "La curva de rotación galáctica de las nebulosas espirales",
    "El espectro de líneas de emisión del hidrógeno ionizado",
    "El límite de masa de Chandrasekhar para enanas blancas",
    "La radiación cósmica de fondo de microondas a tres Kelvin",
    "La detección interferométrica de ondas gravitacionales",
    "El colapso del núcleo de hierro en supernovas tipo dos",
    "La paralaje trigonométrica medida por el telescopio espacial",
    "La acreción de materia en torno al horizonte de sucesos",
    "El campo magnético toroidal de los púlsares de milisegundos",
    "El diagrama de Hertzsprung-Russell para cúmulos estelares globulares",
    "La nucleosíntesis primordial de helio y deuterio ligero",
    "La constante de Hubble calculada a partir de supernovas tipo Ia",
    "La dispersión de velocidad en el halo de materia oscura galáctico",
    "La emisión en ondas de radio de chorros relativistas extragalácticos",
]

PREDICATES_ES = [
    "evidencia la expansión métrica acelerada del tejido espaciotemporal",
    "sugiere la presencia masiva de componentes de materia oscura no bariónica",
    "permite determinar la temperatura cinética y densidad electrónica nebular",
    "marca el umbral de degeneración electrónica antes del colapso gravitatorio",
    "preserva fluctuaciones térmicas primordiales de la era de recombinación",
    "registra fusiones de pares de agujeros negros de masa estelar binaria",
    "desencadena la expulsión explosiva de las capas estelares externas",
    "determina distancias geométricas precisas sin depender de modelos cósmicos",
    "genera intensos flujos de rayos X en el disco de plasma circundante",
    "acelera partículas cargadas emitiendo haces coherentes de radiación sincrotrón",
    "calibra la edad isócrona mediante el punto de desvío de la secuencia principal",
    "fija las abundancias químicas de elementos livianos en el universo temprano",
    "mide la tasa de expansión cósmica local con baja incertidumbre estadística",
    "mantiene la estabilidad virial en cúmulos densos de galaxias elípticas",
    "colima plasma magnetizado a velocidades cercanas a la de la luz en el vacío",
]

CONTEXTS_ES = [
    "confirmando las predicciones teóricas de la relatividad general de Einstein",
    "de acuerdo con el modelo cosmológico estándar Lambda-CDM",
    "revelando la evolución física de las estructuras a gran escala del universo",
    "utilizando observaciones fotométricas y espectroscópicas de alta resolución",
    "para restringir la ecuación de estado de la energía oscura repulsiva",
    "contrastando modelos analíticos con simulaciones numéricas de N cuerpos",
    "ampliando el horizonte observacional hacia las primeras estrellas del cosmos",
    "a partir de relevamientos astronómicos satelitales en longitudes de onda múltiples",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "The cosmological redshift of distant high-z galaxies",
    "The flat galactic rotation curve of spiral nebulae",
    "The forbidden line emission spectrum of ionized hydrogen",
    "The Chandrasekhar mass limit for electron-degenerate dwarfs",
    "The cosmic microwave background radiation temperature anisotropy",
    "The interferometric detection of transient gravitational waves",
    "The iron core-collapse mechanism in core-collapse supernovae",
    "The trigonometric parallax measured by astrometric space observatories",
    "Relativistic plasma accretion onto the event horizon of black holes",
    "The toroidal magnetic field topology of millisecond pulsars",
    "The color-magnitude diagram for dense globular stellar clusters",
    "The primordial nucleosynthesis yields of deuterium and helium isotopes",
    "The Hubble expansion rate derived from type Ia standard candles",
    "The velocity dispersion tensor within virialized dark matter halos",
    "Synchrotron emission from collimated extragalactic relativistic jets",
]

PREDICATES_EN = [
    "demonstrates the accelerated metric expansion of the spacetime fabric",
    "necessitates substantial components of non-baryonic cold dark matter",
    "diagnoses local kinetic temperatures and nebular electron densities",
    "sets the boundary beyond which electron degeneracy pressure collapses",
    "encodes primordial density fluctuations from the recombination epoch",
    "characterizes the inspiral and coalescence of binary compact remnants",
    "drives explosive ejection of outer stellar envelopes into the ISM",
    "provides direct geometric distance anchors across the Milky Way disc",
    "dissipates angular momentum through magnetohydrodynamic turbulence",
    "directs beamed synchrotron radiation along rotating magnetic poles",
    "constrains cluster age through the main-sequence turnoff point",
    "constrains baryon-to-photon ratios in the early inflationary cosmos",
    "calibrates the extragalactic distance ladder with high fidelity",
    "balances gravitational attraction against kinetic velocity dispersions",
    "transports magnetized energy out to megaparsec-scale intergalactic lobes",
]

CONTEXTS_EN = [
    "reinforcing the observational framework of the standard Lambda-CDM model",
    "consistent with the rigorous predictions of Einstein's general relativity",
    "probing the thermodynamic history of the early expanding universe",
    "utilizing high-resolution submillimeter and infrared space telescopes",
    "constraining the equation of state of repulsive cosmological dark energy",
    "benchmarking theoretical stellar interior models against observational data",
    "advancing multi-messenger astrophysics across electromagnetic spectrums",
    "deepening understanding of cosmic reionization epochs and early galaxy seeds",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Die kosmologische Rotverschiebung ferner Galaxien",
    "Die flache Rotationskurve von Spiralgalaxien im Halo",
    "Das Emissionslinienspektrum ionisierter H-II-Regionen",
    "Die Chandrasekhar-Massegrenze für Weiße Zwerge",
    "Die kosmische Mikrowellen-Hintergrundstrahlung bei 2,7 Kelvin",
    "Der interferometrische Nachweis von Gravitationswellen",
    "Der gravitative Kollaps des Eisenkerns bei Typ-II-Supernovae",
    "Die trigonometrische Parallaxenmessung der Astrometriesatelliten",
    "Die Akkretion heißer Materie um den Ereignishorizont",
    "Das extrem starke Dipol-Magnetfeld rotierender Millisekundenpulsare",
    "Das Hertzsprung-Russell-Diagramm für alte Kugelsternhaufen",
    "Die primordiale Nukleosynthese leichter Elemente nach dem Urknall",
    "Die lokale Hubble-Konstante gemessen an Typ-Ia-Supernovae",
    "Die Geschwindigkeitsdispersion im virialisierten Dunkle-Materie-Halo",
    "Die Synchrotronstrahlung relativistischer extragalaktischer Radio-Jets",
]

PREDICATES_DE = [
    "belegt die beschleunigte Expansion des metrischen Raumes zweifelsfrei",
    "erfordert die Existenz großer Mengen nicht-baryonischer Dunkler Materie",
    "liefert Aufschluss über Elektronendichte und Gastemperatur im Nebel",
    "definiert die maximale Stabilitätsgrenze des Elektronenentartungsdrucks",
    "konserviert Dichtefluktuationen aus der Epoche der kosmischen Rekombination",
    "bestätigt die Verschmelzung stellarer und intermediärer Schwarzer Löcher",
    "schleudert schwere synthetisierte Elemente in das interstellare Medium",
    "erlaubt eine modellunabhängige direkte geometrische Distanzbestimmung",
    "erzeugt intensive hochenergetische Röntgenstrahlung im Plasmascheibenbereich",
    "bündelt geladene relativistische Teilchen zu schmalen Strahlungskegeln",
    "bestimmt das stellare Alter anhand des Hauptreihenabknickpunkts präzise",
    "bestimmt die relative Häufigkeit von Deuterium und Helium-4 im Kosmos",
    "kalibriert die extragalaktische Entfernungsleiter mit hoher Genauigkeit",
    "stabilisiert die Raumdichte großer elliptischer Galaxienhaufen gravitationsdynamisch",
    "transportiert magnetisiertes Plasma über kosmische Distanzen ins Vakuum",
]

CONTEXTS_DE = [
    "in Übereinstimmung mit den Gesetzen der Allgemeinen Relativitätstheorie",
    "zur Überprüfung des modernen kosmologischen Lambda-CDM-Standardmodells",
    "unter Verwendung moderner satellitengestützter Weltraumteleskope",
    "zur Erforschung der physikalischen Natur der Dunklen Energie im Universum",
    "durch hochauflösende spektroskopische und photometrische Himmelsdurchmusterungen",
    "zur Rekonstruktion der chemischen Entwicklungsgeschichte früher Sternpopulationen",
    "im Rahmen internationaler Multi-Messenger-Beobachtungskampagnen",
    "zur Bestimmung fundamentaler astrophysikalischer Konstanten im Kosmos",
]


def generate_astronomia_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para astronomia."""
    seeds_es = load_extended_seeds(ALMA, "es")
    seeds_en = load_extended_seeds(ALMA, "en")

    clauses_es = build_clauses_for_lang(
        ALMA, "es", 167, seeds_es, SUBJECTS_ES, PREDICATES_ES, CONTEXTS_ES
    )
    clauses_en = build_clauses_for_lang(
        ALMA, "en", 167, seeds_en, SUBJECTS_EN, PREDICATES_EN, CONTEXTS_EN
    )
    clauses_de = build_clauses_for_lang(
        ALMA, "de", 166, [], SUBJECTS_DE, PREDICATES_DE, CONTEXTS_DE
    )

    return clauses_es + clauses_en + clauses_de
