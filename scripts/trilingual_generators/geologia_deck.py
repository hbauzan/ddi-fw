"""Generador trilingüe para el oficio GEOLOGIA."""

from __future__ import annotations

from scripts.trilingual_generators.base import ClauseData, build_clauses_for_lang

ALMA = "geologia"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "La subducción de la litosfera oceánica densa en fosas abisales",
    "El metamorfismo regional dinamotérmico en facies de esquistos verdes",
    "La propagación de ondas sísmicas primarias y secundarias por el manto",
    "La diagénesis y cementación química de areniscas en cuencas de antepaís",
    "La cristalización fraccionada en cámaras magmáticas félsicas",
    "El desplazamiento transcurrente a lo largo de fallas de rumbo dextrales",
    "La alteración hidrotermal de depósitos minerales de pórfido cuprífero",
    "La datación radiométrica de circones mediante series de uranio y plomo",
    "La orogenia compresiva y el apilamiento de mantos de corrimiento",
    "La sedimentación turbidítica en taludes y cañones submarinos",
    "La foliación milonítica en zonas de cizalla dúctil profunda",
    "El vulcanismo intraplaca asociado a plumas del manto y puntos calientes",
    "La estructura cristalina tetraédrica de los minerales nesosilicatos",
    "La meteorización química de basaltos olivínicos bajo clima tropical",
    "La inversión tectónica positiva de cuencas de rift sedimentarias",
]

PREDICATES_ES = [
    "induce la fusión parcial del manto superior generando arcos volcánicos",
    "recristaliza minerales arcillosos en clorita, moscovita y cuarzo orientado",
    "refleja discontinuidades composicionales y reológicas en el interior terrestre",
    "reduce la porosidad intergranular mediante precipitación de sílice y calcita",
    "enriquece progresivamente el magma residual en sílice, sodio y potasio",
    "acumula esfuerzos tectónicos elásticos hasta provocar rupturas cosísmicas",
    "precipita sulfuros metálicos de cobre y molibdeno en redes de vetillas",
    "determina con exactitud cronológica la cristalización de rocas ígneas",
    "engrosa la corteza continental generando relieve montañoso escarpado",
    "deposita secuencias granocrecientes con estratificación gradada típica",
    "deforma intensamente los granos de cuarzo y feldespato por flujo plástico",
    "produce coladas basálticas fluidas de gran extensión y baja viscosidad",
    "conecta vértices de oxígeno compartidos determinando su clivaje y dureza",
    "libera iones de magnesio y hierro formando minerales secundarios de arcilla",
    "reactiva antiguas fallas normales transformándolas en fallas inversas",
]

CONTEXTS_ES = [
    "reconstruyendo la evolución geodinámica de las placas tectónicas terrestres",
    "de acuerdo con los principios de la estratigrafía y la petrología ígnea",
    "proporcionando claves esenciales para la prospección de recursos minerales",
    "mitigando el riesgo geológico de terremotos, tsunamis y erupciones volcánicas",
    "en el marco del ciclo de Wilson de apertura y cierre de cuencas oceánicas",
    "revelando la historia paleoambiental y climática de eras geológicas pasadas",
    "utilizando técnicas analíticas avanzadas de microscopía petrográfica y difracción",
    "integrando datos geofísicos de gravimetría, magnetometría y reflexión sísmica",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "Subduction of dense oceanic lithosphere into deep oceanic trenches",
    "Regional dynamothermal metamorphism in greenschist and amphibolite facies",
    "Propagation of seismic P-waves and S-waves through the mantle",
    "Diagenetic cementation of quartz arenite in sedimentary foreland basins",
    "Fractional crystallization within shallow felsic magma chambers",
    "Strike-slip displacement along active dextral transform faults",
    "Hydrothermal alteration in porphyry copper and molybdenum deposits",
    "Radiometric dating of zircon crystals via uranium-lead isotope decay",
    "Compressional orogeny resulting in extensive thrust sheet stacking",
    "Turbidite sequence deposition across continental slopes and abyssal plains",
    "Mylonitic foliation developed within deep ductile shear zones",
    "Intraplate hotspot volcanism fueled by deep mantle upwelling plumes",
    "Silicate tetrahedra polymerization governing igneous mineral cleavages",
    "Chemical weathering of olivine-bearing basalt under humid tropical regimes",
    "Tectonic inversion reactivating ancient extensional graben structures",
]

PREDICATES_EN = [
    "triggers partial melting of the asthenospheric mantle wedge above",
    "realigns platy phyllosilicates into distinct metamorphic foliation planes",
    "reveals structural discontinuities across the lithosphere-asthenosphere boundary",
    "occludes primary porosity through secondary quartz overgrowth precipitation",
    "progressively enriches residual silicate melts in incompatible elements",
    "accumulates elastic strain culminating in periodic coseismic slip events",
    "precipitates chalcopyrite and molybdenite in dense stockwork veinlet systems",
    "yields concordant absolute crystallization ages for igneous host rocks",
    "accretes exotic terranes while thickening continental crustal roots",
    "deposits characteristic Bouma sequences with rhythmic graded bedding units",
    "records ductile crystal-plastic deformation under elevated metamorphic grades",
    "erupts voluminous flood basalts characterized by low-viscosity pahoehoe flows",
    "determines hardness, chemical durability, and fracture habits of rock-forming minerals",
    "leaches soluble cations yielding deep bauxitic and lateritic residual soils",
    "converts sedimentary basins into elevated compressional fold-thrust belts",
]

CONTEXTS_EN = [
    "reconstructing the long-term geodynamic evolution of tectonic plates",
    "consistent with core paradigms of structural geology and petrology",
    "guiding economic mineral exploration across deformed metamorphic terranes",
    "mitigating geohazards associated with active faulting and volcanic eruptions",
    "within the global framework of oceanic opening and closing Wilson cycles",
    "deciphering paleotectonic regimes and Earth's dynamic thermal history",
    "synthesizing field mapping data with microstructural and petrographic analysis",
    "integrating gravity, magnetic, and seismic reflection imaging surveys",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Die Subduktion ozeanischer Lithosphäre an konvergenten Plattengrenzen",
    "Die Regionalmetamorphose unter Grünschiefer- und Blauschieferbedingungen",
    "Die Ausbreitung von seismischen P- und S-Wellen durch den Erdmantel",
    "Die chemische Diagenese und Zementation klastischer Sedimente",
    "Die fraktionierte Kristallisation in magmatischen Plutonen",
    "Die Horizontalverschiebung an aktiven dextralen Blattverschiebungen",
    "Die hydrothermale Alteration in porphyrischen Kupferlagerstätten",
    "Die Uran-Blei-Datierung an akzessorischen Zirkonkristallen",
    "Die kompressive Gebirgsbildung mit Überschiebungstektonik",
    "Die turbiditische Sedimentation im marinen Tiefwasserbereich",
    "Die mylonitische Foliation in duktilen Scherzonen der Unterkruste",
    "Der Intraplattenvulkanismus über tief sitzenden Mantelplumes",
    "Die räumliche Vernetzung von Silikat-Tetraedern in Mineralien",
    "Die chemische Verwitterung basaltischer Gesteine im warmen Klima",
    "Die tektonische Inversion ehemaliger Dehnungsbecken und Gräben",
]

PREDICATES_DE = [
    "führt zur partiellen Aufschmelzung des Mantelkeils und Inselbogenvulkanismus",
    "transformiert Tonminerale in Chlorit, Epidot und ausgerichteten Glimmer",
    "liefert präzise Tomographiebilder von Dichteanomalien im Erdinneren",
    "verringert das Porenvolumen durch Abscheidung von sekundärem Quarz",
    "reichert die Restschmelze kontinuierlich an Kieselsäure und Alkalien an",
    "baut elastische Spannungen auf, die sich in Erdbeben schlagartig entladen",
    "scheidet Erzminerale wie Chalkopyrit in fein verzweigten Adernetzwerken ab",
    "liefert verlässliche radiometrische Alter für Erstarrungsgesteine",
    "führt zur Krustenverdickung und zur Entstehung mächtiger Hochgebirge",
    "lagert charakteristische Bouma-Zyklen mit gradierten Schichtungen ab",
    "zeugt von plastischer Verformung bei hohen Temperaturen und Drücken",
    "fördert dünnflüssige basaltische Laven über riesige Flächen zutage",
    "bestimmt die physikalischen Eigenschaften und Spaltbarkeiten der Silikate",
    "zerlegt Olivin und Plagioklas in sekundäre Tonminerale und Eisenoxide",
    "reaktiviert alte Abschiebungen zu steil stehenden inversen Verwerfungen",
]

CONTEXTS_DE = [
    "zur Rekonstruktion der großräumigen plattentektonischen Erdgeschichte",
    "in Übereinstimmung mit den Grundgesetzen der Geochemie und Geophysik",
    "als wissenschaftliche Grundlage für die Erkundung von Rohstoffvorkommen",
    "zur präzisen Erfassung und Minderung seismischer Naturgefahren",
    "im Kontext globaler Wilson-Zyklen der Ozeanbeckenentwicklung",
    "zur Aufklärung paläoklimatischer und paläogeographischer Bedingungen",
    "unter Einsatz moderner polarisationsmikroskopischer Dünnschliffanalysen",
    "durch Kombination geologischer Geländekartierungen mit geophysikalischen Messungen",
]


def generate_geologia_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para geologia."""
    clauses_es = build_clauses_for_lang(
        ALMA, "es", 167, [], SUBJECTS_ES, PREDICATES_ES, CONTEXTS_ES
    )
    clauses_en = build_clauses_for_lang(
        ALMA, "en", 167, [], SUBJECTS_EN, PREDICATES_EN, CONTEXTS_EN
    )
    clauses_de = build_clauses_for_lang(
        ALMA, "de", 166, [], SUBJECTS_DE, PREDICATES_DE, CONTEXTS_DE
    )

    return clauses_es + clauses_en + clauses_de
