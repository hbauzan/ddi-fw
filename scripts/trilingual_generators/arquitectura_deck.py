"""Generador trilingüe para el oficio ARQUITECTURA."""

from __future__ import annotations

from scripts.trilingual_generators.base import ClauseData, build_clauses_for_lang

ALMA = "arquitectura"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "El cálculo de momentos flectores en pórticos hiperestáticos de hormigón",
    "El pretensado de vigas maestras mediante cordones de acero de alta resistencia",
    "El diseño de cimentaciones profundas mediante pilotes de hormigón armado",
    "La verificación del estado límite de deformación y flecha elástica",
    "El arriostramiento estructural frente a acciones sísmicas horizontales",
    "El dimensionamiento de losas macizas bidireccionales apoyadas sobre columnas",
    "La armadura de refuerzo transversal para absorber esfuerzos de corte",
    "El análisis de tensiones en nudos rígidos de estructuras metálicas",
    "La física de la envolvente edilicia y el aislamiento de puentes térmicos",
    "El cálculo de cargas gravitatorias permanentes y sobrecargas de uso",
    "La cimentación superficial mediante losa continua de hormigón armado",
    "La estabilidad frente al pandeo de pilares esbeltos comprimidos",
    "El diseño bioclimático de fachadas ventiladas con protección solar",
    "La colocación de juntas de dilatación térmica en edificios de gran longitud",
    "El anclaje de barras corrugadas por longitud de solape en zona confinada",
]

PREDICATES_ES = [
    "distribuye los esfuerzos internos optimizando la sección geométrica resistente",
    "introduce compresiones previas que contrarrestan las tracciones por flexión",
    "transfiere las cargas estructurales a estratos portantes profundos del terreno",
    "garantiza el confort de los usuarios y previene fisuras en tabiquerías",
    "disipa energía cinética mediante deformaciones dúctiles de los pórticos",
    "resiste punzonamiento mediante refuerzos radiales alrededor de los apoyos",
    "previene la rotura frágil por tensión diagonal en las almas de las vigas",
    "asegura la transmisión integral de momentos sin plastificaciones locales",
    "reduce la transmitancia térmica minimizando condensaciones intersticiales",
    "determina las solicitaciones pésimas para la combinación de hipótesis de carga",
    "uniformiza las presiones de contacto sobre suelos de baja capacidad portante",
    "evita fallos catastróficos por inestabilidad elástica de segundo orden",
    "optimiza la ganancia solar pasiva y la ventilación natural cruzada",
    "absorbe movimientos dimensionales evitando tensiones térmicas destructivas",
    "desarrolla la adherencia mecánica necesaria para alcanzar la tensión de fluencia",
]

CONTEXTS_ES = [
    "en estricto apego a las normas de seguridad estructural y códigos de edificación",
    "garantizando la integridad sismorresistente y la durabilidad de la obra civil",
    "optimizando la eficiencia energética y la sostenibilidad ambiental del edificio",
    "para asegurar el cumplimiento de los estados límites últimos y de servicio",
    "mediante modelos numéricos avanzados de análisis por elementos finitos",
    "coordinando el proyecto arquitectónico con la ingeniería estructural de detalle",
    "garantizando un factor de seguridad adecuado frente al colapso estructural",
    "respetando las condiciones de habitabilidad y funcionalidad arquitectónica",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "Calculation of bending moment diagrams in indeterminate concrete frames",
    "Prestressing of primary bridge girders using high-tensile steel strands",
    "Deep foundation engineering utilizing reinforced concrete cast-in-place piles",
    "Verification of serviceability limit state for maximum elastic deflection",
    "Cross-bracing structural systems designed to resist horizontal wind and seismic forces",
    "Two-way reinforced concrete flat slab design under punch shear stresses",
    "Transverse shear stirrup reinforcement within slender beam webs",
    "Finite element stress analysis of moment-resisting steel beam-column joints",
    "Building envelope thermal envelope physics and thermal bridge mitigation",
    "Gravitational dead load and live occupancy load combination calculations",
    "Mat foundation design over soils exhibiting low bearing capacity",
    "Euler buckling analysis for slender vertical structural compression columns",
    "Passive solar bioclimatic architecture and natural cross-ventilation facades",
    "Structural expansion joint placement across large continuous building footprints",
    "Deformed rebar development length anchorage in heavily congested joints",
]

PREDICATES_EN = [
    "redistributes internal forces to optimize cross-sectional concrete efficiency",
    "imparts pre-compressive stress to cancel anticipated tensile tensile stresses",
    "transfers heavy superstructure loads into competent deep bedrock strata",
    "prevents cosmetic cracking in non-structural masonry partitions and finishes",
    "dissipates seismic kinetic energy through controlled plastic ductile yielding",
    "prevents brittle punching shear failure around internal column perimeters",
    "resists diagonal tension stresses preventing sudden diagonal shear cracking",
    "guarantees full moment transmission without localized plate yield buckling",
    "minimizes interstitial moisture condensation and reduces heating demand",
    "defines governing load cases for ultimate structural limit state checks",
    "mitigates differential settlement across heterogeneous compressible clay layers",
    "prevents sudden catastrophic second-order elastic bifurcation failures",
    "maximizes daylighting while mitigating excessive summer solar cooling loads",
    "accommodates cyclical thermal expansion preventing secondary tensile stress",
    "ensures steel rebar yields prior to localized mechanical concrete pullout",
]

CONTEXTS_EN = [
    "complying strictly with modern international structural building codes",
    "ensuring long-term structural durability and catastrophic collapse resilience",
    "optimizing structural efficiency alongside sustainable environmental design",
    "fulfilling ultimate strength and serviceability limit state requirements",
    "validated through three-dimensional finite element computational simulations",
    "harmonizing architectural spatial intent with rigorous structural mechanics",
    "providing adequate structural safety margins under extreme environmental events",
    "elevating energy efficiency standards across contemporary civic architectures",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Die Biegemomentenberechnung in statisch unbestimmten Stahlbetonrahmen",
    "Das Vorspannen von Spannbetonbrücken mit hochfesten Stahllitzen",
    "Die Pfahlgründung mit Großbohrpfählen in wenig tragfähigen Böden",
    "Der Nachweis der Gebrauchstauglichkeit gegen unzulässige Durchbiegung",
    "Die statische Aussteifung gegen horizontale Wind- und Erdbebenlasten",
    "Die Bemessung punktgestützter Flachdecken gegen Durchstanzen",
    "Die Bügelbewehrung zur Aufnahme von Querkräften im Trägersteg",
    "Die Spannungsanalyse biegesteifer Rahmenknoten im Stahlbau",
    "Die bauphysikalische Dämmung zur Vermeidung von Wärmebrücken",
    "Die Überlagerung von ständigen Eigenlasten und veränderlichen Verkehrslasten",
    "Die durchgehende Gründungsplatte auf setzungsempfindlichem Baugrund",
    "Der Stabilitätsnachweis gegen Knicken für schlanke Druckstützen",
    "Die Planung vorgehängter hinterlüfteter Fassaden zur Energieeinsparung",
    "Die Anordnung von Dehnungsfugen in langgestreckten Baukörpern",
    "Die Verankerungslänge von Betonrippenstählen im hochbewehrten Knoten",
]

PREDICATES_DE = [
    "optimiert den inneren Kräfteverlauf und die Querschnittsabmessungen",
    "überdrückt Zugspannungen im Beton zur Rissvermeidung im Nutzungszustand",
    "leitet hohe Bauwerkslasten in tief liegende tragfähige Erdschichten ab",
    "gewährleistet die Rissfreiheit und den optischen Komfort des Bauwerks",
    "leitet Horizontalkräfte über aussteifende Wandscheiben in das Fundament",
    "verhindert das schlagartige Durchstanzen der Decke an den Stützenköpfen",
    "sichert das Bauteil gegen spröden Schubbruch infolge von Querkräften",
    "stellt die volle Momentenübertragung zwischen Riegel und Stütze sicher",
    "senkt den Transmissionswärmeverlust und verhindert Tauwasserausfall",
    "liefert die maßgebenden Bemessungsschnittgrößen für den Grenzzustand",
    "egalisiert ungleichmäßige Setzungen im heterogenen Bodenprofil",
    "schützt das Tragwerk vor Versagen durch Theorie II. Ordnung",
    "reguliert das Raumklima durch optimierten sommerlichen Wärmeschutz",
    "kompensiert temperaturbedingte Längenänderungen ohne Rissbildung",
    "gewährleistet den sicheren Kraftschluss zwischen Bewehrungsstahl und Beton",
]

CONTEXTS_DE = [
    "unter strikter Einhaltung der geltenden Eurocodes für den konstruktiven Ingenieurbau",
    "zur Gewährleistung höchster Standsicherheit und Dauerhaftigkeit von Tragwerken",
    "im Sinne einer ressourceneffizienten und nachhaltigen Gebäudeplanung",
    "zur Erfüllung aller Anforderungen an Tragfähigkeit und Gebrauchstauglichkeit",
    "gestützt auf dreidimensionale Finite-Elemente-Berechnungen der Statik",
    "in enger Abstimmung zwischen Architekturentwurf und Tragwerksplanung",
    "zur Gewährleistung ausreichender Sicherheitsbeiwerte gegen Strukturversagen",
    "unter Beachtung zeitgemäßer bauphysikalischer und energetischer Standards",
]


def generate_arquitectura_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para arquitectura."""
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
