"""Generador trilingüe para el oficio BOTANICA."""

from __future__ import annotations

from scripts.trilingual_generators.base import ClauseData, build_clauses_for_lang

ALMA = "botanica"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "El transporte floemático de fotoasimilados por flujo de presión",
    "La diferenciación de traqueidas y elementos de los vasos en el xilema",
    "La vía fotosintética CAM con fijación nocturna de dióxido de carbono",
    "La regulación estomática mediada por ácido abscísico y flujo de potasio",
    "La actividad mitótica en el meristemo apical de la raíz",
    "La simbiosis micorrízica arbuscular en la rizosfera vegetal",
    "La síntesis de auxinas y su transporte polar basipétalo",
    "La lignificación de las paredes celulares secundarias en el esclerénquima",
    "La fecundación doble característica de las plantas angiospermas",
    "El fotoperiodismo inducido por el fitocromo en la floración",
    "La germinación epígea con elongación marcada del hipocótilo",
    "La dormición de semillas regulada por el equilibrio giberelina-ABA",
    "La taxonomía filogenética basada en secuencias de cloroplastos",
    "La exudación de savia elaborada a través de los tubos cribosos",
    "El gravitropismo radical coordinado por estatolitos amiloplásticos",
]

PREDICATES_ES = [
    "moviliza sacarosa desde las hojas fuente hacia los órganos sumidero",
    "conduce agua y solutos inorgánicos bajo tensión y presión negativa",
    "minimiza la pérdida de agua por transpiración en ambientes áridos",
    "controla la turgencia de las células oclusivas cerrando los poros estomáticos",
    "genera células precursoras protegidas por la caliptra o cofia radical",
    "facilita la absorción de fósforo y micronutrientes del sustrato edáfico",
    "estimula la elongación celular y la dominancia apical del tallo",
    "confiere rigidez mecánica y resistencia a la compresión estructural",
    "origina simultáneamente el embrión diploide y el endosperma triploide",
    "sincroniza el desarrollo reproductivo con las estaciones climáticas del año",
    "eleva los cotiledones por encima de la superficie del suelo agrícola",
    "impide la germinación precoz en condiciones ambientales desfavorables",
    "resuelve relaciones evolutivas entre familias de plantas vasculares",
    "mantiene la continuidad citoplasmática mediante placas cribosas perforadas",
    "redistribuye auxinas hacia la cara inferior promoviendo la curvatura",
]

CONTEXTS_ES = [
    "optimizando la adaptación fisiológica de las especies vegetales al estrés",
    "en el marco de la botánica estructural y la fisiología vegetal moderna",
    "esencial para la comprensión del rendimiento agronómico de los cultivos",
    "garantizando la supervivencia y reproducción en ecosistemas terrestres diversos",
    "conforme a los modelos mecanicistas de transporte y desarrollo vegetal",
    "revelando la complejidad de las interacciones bióticas en el suelo",
    "mediante estudios histológicos de microscopía electrónica de transmisión",
    "integrando la ecología vegetal con la conservación de la biodiversidad",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "Phloem transport of photoassimilates driven by hydrostatic pressure",
    "Differentiation of tracheids and vessel elements in secondary xylem",
    "Crassulacean acid metabolism with nocturnal carbon dioxide fixation",
    "Stomatal closure modulated by abscisic acid and potassium ion efflux",
    "Mitotic division in the root apical meristem and quiescent center",
    "Arbuscular mycorrhizal symbiosis established within root cortical cells",
    "Polar auxin transport mediated by PIN-formed efflux carrier proteins",
    "Secondary cell wall lignification in sclerenchyma fiber tissues",
    "Double fertilization producing a diploid zygote and triploid endosperm",
    "Phytochrome-mediated photoperiodic floral induction pathways",
    "Epigeal seed germination characterized by rapid hypocotyl elongation",
    "Seed dormancy breaking regulated by the gibberellin-to-ABA ratio",
    "Angiosperm molecular phylogenetics based on plastid gene loci",
    "Pressure-driven bulk flow through perforated sieve tube elements",
    "Root gravitropism directed by sedimentation of amyloplast statoliths",
]

PREDICATES_EN = [
    "translocates sucrose from photosynthesizing sources to storage sinks",
    "conducts water and dissolved inorganic ions under negative xylem tensions",
    "drastically suppresses daytime evapotranspirational water loss in succulents",
    "deflates guard cells to prevent fatal desiccation during drought stress",
    "supplies continuous cell lineages protected by the protective root cap",
    "enhances inorganic phosphate and nitrogen uptake from depleted soils",
    "maintains primary shoot apical dominance and directs vascular patterning",
    "provides essential tensile strength and vertical compressive support",
    "initiates coordinated seed development following compatible pollination",
    "entrains flowering time to seasonal day-length shifts via systemic florigen",
    "lifts photosynthetic cotyledons above the soil level into ambient light",
    "ensures seed emergence occurs only during favorable seasonal conditions",
    "clarifies evolutionary branching orders across basal angiosperm lineages",
    "sustains nutrient streaming through callose-lined plasmodesmatal pores",
    "induces asymmetric auxin accumulation on the lower organ flank",
]

CONTEXTS_EN = [
    "optimizing plant physiological adaptations across varying microclimates",
    "consistent with foundational principles of modern plant physiology",
    "critical for enhancing crop agricultural productivity and drought resilience",
    "governing growth and development across diverse terrestrial botanical clades",
    "advancing mechanical understanding of long-distance vascular fluid transport",
    "shedding light on intricate plant-rhizosphere microbial mutualisms",
    "elucidated through high-resolution confocal laser scanning microscopy",
    "informing global plant conservation biology and ecological restoration",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Der Phloemtransport von Assimilaten über hydrostatische Druckgradienten",
    "Die Differenzierung von Tracheen und Tracheiden im sekundären Xylem",
    "Der CAM-Photosyntheseweg mit nächtlicher CO2-Vorfixierung",
    "Der durch Abscisinsäure gesteuerte Spaltöffnungsverschluss",
    "Die mitotische Zellteilung im Wurzelspitzenmeristem",
    "Die arbuskuläre Mykorrhiza-Symbiose im Wurzelkortex",
    "Der polare Auxintransport durch zelluläre PIN-Efflux-Carrier",
    "Die Lignifizierung sekundärer Zellwände im Festigungsgewebe",
    "Die doppelte Befruchtung bei bedecktsamigen Blütenpflanzen",
    "Die phytochromgesteuerte Photoperiodik bei der Blüteninduktion",
    "Die epigäische Keimung mit starker Streckung des Hypokotyls",
    "Die Samenruhe und Dormanzbrechung durch Gibberelline",
    "Die molekulare Pflanzensystematik anhand von Chloroplasten-DNA",
    "Der Massenstrom gelöster Nährstoffe durch die Siebröhrenglieder",
    "Der Wurzelgravitropismus gesteuert durch sedimentierende Amyloplasten",
]

PREDICATES_DE = [
    "transportiert Saccharose von den photosynthetischen Quellen zu den Senken",
    "leitet Wasser und Mineralstoffe unter negativem hydrostatischem Druck",
    "reduziert den transpiratorischen Wasserverlust bei extremer Trockenheit",
    "senkt den Turgordruck der Schließzellen zur Vermeidung von Welkeschäden",
    "liefert neue Zellschichten unter dem Schutz der schützenden Wurzelhaube",
    "verbessert die Aufnahme von schwer löslichem Phosphat aus dem Boden",
    "steuert die apikale Dominanz und das gerichtete Sprosswachstum",
    "verleiht den Zellwänden hohe mechanische Druck- und Biegefestigkeit",
    "erzeugt gleichzeitig den diploiden Embryo und das triploide Nährgewebe",
    "synchronisiert den Blühzeitpunkt mit den jahreszeitlichen Tageslängen",
    "hebt die Speicherkeimblätter zur frühen Photosynthese über die Erde",
    "verhindert das vorzeitige Auskeimen unter ungünstigen Witterungsbedingungen",
    "rekonstruiert die Stammesgeschichte Höherer Pflanzen mit hoher Auflösung",
    "gewährleistet den kontinuierlichen Stoffaustausch über durchbrochene Siebplatten",
    "lenkt das Wurzelwachstum durch asymmetrische Auxinverteilung erdnah",
]

CONTEXTS_DE = [
    "zur Erforschung pflanzlicher Anpassungsmechanismen an Umweltstress",
    "gemäß den aktuellen Erkenntnissen der pflanzlichen Zell- und Entwicklungsbiologie",
    "von zentraler Bedeutung für die Züchtung ertragreicher und robuster Nutzpflanzen",
    "zur Aufklärung grundlegender biophysikalischer Stofftransportprozesse",
    "im Einklang mit den Modellen der pflanzlichen Morphologie und Anatomie",
    "zur Vertiefung des Verständnisses biotischer Interaktionen im Boden",
    "gestützt auf histologische Untersuchungen und Fluoreszenzmikroskopie",
    "zur Förderung des weltweiten Schutzes der pflanzlichen Biodiversität",
]


def generate_botanica_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para botanica."""
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
