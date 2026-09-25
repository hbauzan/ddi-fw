"""Generador trilingüe para el oficio MEDICINA."""

from __future__ import annotations

from scripts.trilingual_generators.base import (
    ClauseData,
    build_clauses_for_lang,
    load_extended_seeds,
)

ALMA = "medicina"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "La hipertrofia ventricular izquierda concéntrica",
    "El aclaramiento renal de creatinina endógena",
    "La biodisponibilidad plasmática de fármacos liposolubles",
    "La elevación patológica del segmento ST en el electrocardiograma",
    "El diagnóstico histopatológico de necrosis coagulativa",
    "La tormenta de citoquinas proinflamatorias interleucina seis",
    "El monitoreo hemodinámico mediante catéter arterial pulmonar",
    "La resistencia bacteriana mediada por betalactamasas de espectro extendido",
    "La gasometría arterial en insuficiencia respiratoria aguda",
    "El tratamiento trombolítico en el accidente cerebrovascular isquémico",
    "La biopsia por punción con aguja fina de nódulos tiroideos",
    "La disfunción endotelial inducida por aterosclerosis coronaria",
    "El filtrado glomerular estimado por la fórmula CKD-EPI",
    "La taquicardia ventricular sostenida con inestabilidad hemodinámica",
    "La respuesta inmune celular mediada por linfocitos T citotóxicos",
]

PREDICATES_ES = [
    "refleja sobrecarga crónica de presión en pacientes hipertensos",
    "evalúa con precisión la tasa de filtración glomerular basal",
    "depende del metabolismo hepático de primer paso microsomal",
    "indica oclusión coronaria transmural aguda que exige reperfusión",
    "demuestra desnaturalización proteica irreversible tras isquemia tisular",
    "desencadena vasodilatación sistémica y choque séptico refractario",
    "mide presiones de llenado ventricular y gasto cardíaco en tiempo real",
    "inactiva antibióticos carbapenémicos comprometiendo el pronóstico clínico",
    "revela hipoxemia severa con acidosis respiratoria descompensada",
    "restablece la perfusión cerebral dentro de la ventana terapéutica",
    "distingue lesiones foliculares benignas de carcinomas papilares",
    "promueve la formación de placas de ateroma vulnerables a rotura",
    "estratifica el estadio de la enfermedad renal crónica progresiva",
    "requiere cardioversión eléctrica sincronizada de emergencia médica",
    "reconoce antígenos tumorales presentados en moléculas HLA clase uno",
]

CONTEXTS_ES = [
    "conforme a las guías de práctica clínica de las sociedades médicas",
    "reduciendo significativamente la tasa de morbimortalidad hospitalaria",
    "en el marco de protocolos estandarizados de terapia intensiva",
    "optimizando la titulación posológica en pacientes nefropáticos",
    "para prevenir secuelas neurológicas irreversibles a largo plazo",
    "garantizando un enfoque diagnóstico oportuno basado en evidencia",
    "minimizando el riesgo de efectos adversos y toxicidad farmacológica",
    "bajo estricto control hemodinámico y de constantes vitales en quirófano",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "Concentric left ventricular hypertrophy on echocardiography",
    "The endogenous creatinine clearance rate calculation",
    "The systemic bioavailability of orally administered drugs",
    "Acute ST-segment elevation on twelve-lead electrocardiograms",
    "Histopathological evidence of myocardial coagulative necrosis",
    "The systemic cytokine storm driven by interleukin-6 elevation",
    "Invasive hemodynamic monitoring via pulmonary artery catheters",
    "Plasmid-mediated extended-spectrum beta-lactamase resistance",
    "Arterial blood gas analysis in acute respiratory distress syndrome",
    "Intravenous thrombolysis in acute ischemic stroke management",
    "Fine-needle aspiration cytology of indeterminate thyroid nodules",
    "Coronary endothelial dysfunction induced by systemic atherosclerosis",
    "Estimated glomerular filtration rate determined by CKD-EPI",
    "Sustained monomorphic ventricular tachycardia with hypotension",
    "Cell-mediated cytotoxic T-cell immune responses against viral pathogens",
]

PREDICATES_EN = [
    "indicates chronic hemodynamic pressure overload in severe hypertension",
    "provides an accurate clinical estimate of baseline filtration capacity",
    "is constrained by hepatic cytochrome P450 first-pass clearance",
    "signals transmural epicardial ischemia mandating urgent reperfusion",
    "confirms irreversible cellular injury following prolonged tissue hypoxia",
    "induces systemic capillary leakage and refractory distributive shock",
    "quantifies cardiac output and pulmonary capillary wedge pressure",
    "hydrolyzes third-generation cephalosporins in nosocomial infections",
    "reveals severe uncompensated hypoxemia and metabolic acidosis",
    "recanalizes occluded cerebral vessels within the narrow therapeutic window",
    "differentiates benign follicular adenomas from malignant carcinomas",
    "impairs nitric oxide bioavailability across the coronary microvasculature",
    "stages progression across chronic kidney disease classifications",
    "necessitates immediate synchronized DC cardioversion in resuscitation",
    "induces apoptotic lysis of infected cells presenting MHC class I peptides",
]

CONTEXTS_EN = [
    "improving survival outcomes in multidisciplinary clinical care units",
    "in compliance with established medical consensus guidelines and protocols",
    "mitigating long-term neurological and cardiovascular morbidity risks",
    "optimizing patient-specific antimicrobial stewardship regimens",
    "preventing multi-organ dysfunction syndrome in critical care scenarios",
    "tailoring individualized pharmacotherapy based on organ function",
    "ensuring high diagnostic precision through evidence-based medicine",
    "facilitating rapid clinical decision-making in hospital emergency rooms",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Die konzentrische linksventrikuläre Hypertrophie im Echokardiogramm",
    "Die glomeruläre Filtrationsrate berechnet mittels Kreatinin-Clearance",
    "Die orale Bioverfügbarkeit lipophiler Arzneistoffe",
    "Die pathologische ST-Streckenhebung im Zwölf-Kanal-EKG",
    "Der histologische Nachweis von Koagulationsnekrosen im Gewebe",
    "Der systemische Zytokinsturm mit erhöhten Interleukin-6-Spiegeln",
    "Das invasive hämodynamische Monitoring mit dem Pulmonaliskatheter",
    "Die Resistenzbildung durch plasmidkodierte Betalaktamasen",
    "Die arterielle Blutgasanalyse bei respiratorischer Insuffizienz",
    "Die systemische Thrombolysetherapie beim akuten ischämischen Hirninfarkt",
    "Die Feinnadelaspirationsbiopsie verdächtiger Schilddrüsenknoten",
    "Die endotheliale Dysfunktion bei koronarer Herzkrankheit",
    "Die Berechnung der Nierenfunktion nach der CKD-EPI-Gleichung",
    "Die anhaltende ventrikuläre Tachykardie mit Blutdruckabfall",
    "Die zelluläre Immunantwort durch zytotoxische CD8-T-Lymphozyten",
]

PREDICATES_DE = [
    "belegt eine chronische Druckbelastung bei arterieller Hypertonie",
    "erlaubt eine präzise Beurteilung der renalen Ausscheidungsleistung",
    "unterliegt einem ausgeprägten hepatischen First-Pass-Metabolismus",
    "zeigt einen transmuralen Myokardinfarkt mit sofortiger Katheterindikation",
    "bestätigt den irreversiblen Zelltod infolge akuter Gewebehypoxie",
    "führt zur generalisierten Vasodilatation und zum septischen Schock",
    "erfasst Herzzeitvolumen und pulmonalkapillären Verschlussdruck direkt",
    "zerstört Cephalosporine und erschwert die antibiotische Therapie",
    "zeigt eine schwere Hypoxämie mit dekompensierter metabolischer Azidose",
    "eröffnet verschlossene Hirnarterien innerhalb des Zeitfensters",
    "ermöglicht die zytologische Differenzierung von Schilddrüsentumoren",
    "begünstigt die Bildung instabiler lipidreicher atherosklerotischer Plaques",
    "dient der Stadieneinteilung chronischer Nierenerkrankungen",
    "erfordert eine unverzügliche synchrone elektrische Kardioversion",
    "zerstört virusinfizierte Zellen über Perforin- und Granzym-Freisetzung",
]

CONTEXTS_DE = [
    "zur Senkung der Morbidität und Mortalität auf Intensivstationen",
    "unter strikter Beachtung evidenzbasierter klinischer Leitlinien",
    "zur Vermeidung irreversibler neurologischer Spätschäden",
    "im Rahmen interdisziplinärer notfallmedizinischer Behandlungspfade",
    "für eine zielgerichtete Anpassung der individuellen Medikamentendosis",
    "zur frühzeitigen Erkennung potenziell lebensbedrohlicher Komplikationen",
    "unter kontinuierlicher engmaschiger Überwachung der Vitalparameter",
    "gemäß den aktuellen Richtlinien der Fachgesellschaften für Kardiologie",
]


def generate_medicina_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para medicina."""
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
