"""Generador trilingüe para el oficio LEGAL."""

from __future__ import annotations

from scripts.trilingual_generators.base import (
    ClauseData,
    build_clauses_for_lang,
    load_extended_seeds,
)

ALMA = "legal"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "La cláusula de indemnidad e inmunidad patrimonial",
    "La cesión de derechos de explotación sobre patentes de invención",
    "La estipulación de arbitraje comercial internacional",
    "La rescisión unilateral por incumplimiento grave de obligaciones",
    "El pacto de confidencialidad y no divulgación de secretos industriales",
    "La renuncia expresa a la interposición de recursos ordinarios",
    "La fijación de cláusula penal por mora en el cumplimiento",
    "El régimen de responsabilidad civil extracontractual solidaria",
    "La limitación temporal de las licencias de software propietario",
    "La validez probatoria de documentos firmados digitalmente",
    "La doctrina de los actos propios en sede contenciosa",
    "La excepción de contrato no cumplido interpuesta por la demandada",
    "El derecho de retención legal sobre bienes muebles en depósito",
    "La extinción de obligaciones por novación subjetiva u objetiva",
    "El deber de diligencia exigible a los administradores societarios",
]

PREDICATES_ES = [
    "obliga a mantener indemne a la parte afectada frente a terceros",
    "transfiere la titularidad exclusiva con efectos erga omnes",
    "somete las controversias a tribunales arbitrales de derecho",
    "opera de pleno derecho previa intimación fehaciente por plazo legal",
    "subsiste con posterioridad a la terminación del contrato principal",
    "precluye la posibilidad de revisar el laudo en segunda instancia",
    "determina anticipadamente la cuantía líquida de los daños y perjuicios",
    "exige la acreditación de nexo causal adecuado y factor de atribución",
    "restringe la modificación y distribución del código objeto compilado",
    "otorga plena eficacia jurídica equivalente a la firma ológrafa",
    "impide adoptar conductas procesales contradictorias con pactos previos",
    "suspende válidamente la exigibilidad de la prestación correlativa",
    "faculta a conservar la posesión hasta la cancelación del crédito debido",
    "sustituye el vínculo originario liberando al primitivo deudor",
    "impone responder con el patrimonio personal ante omisiones culposas",
]

CONTEXTS_ES = [
    "salvaguardando la seguridad jurídica en las transacciones comerciales",
    "de conformidad con los principios generales del derecho contractual",
    "sin perjuicio de las acciones resarcitorias por dolo o negligencia grave",
    "garantizando el derecho fundamental a la tutela judicial efectiva",
    "conforme a las disposiciones imperativas del ordenamiento jurídico aplicable",
    "para evitar situaciones de enriquecimiento sin causa en perjuicio ajeno",
    "respetando las normas de orden público internacional y buena fe negocial",
    "en cumplimiento de las regulaciones sobre protección de datos personales",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "The indemnification and defense covenant",
    "The assignment of proprietary intellectual property rights",
    "The binding commercial arbitration agreement",
    "The unilateral termination clause for material breach",
    "The nondisclosure agreement governing trade secrets",
    "The express waiver of consequential and punitive damages",
    "The liquidated damages clause for delayed performance",
    "The statutory joint and several liability doctrine",
    "The grant of non-exclusive software licensing rights",
    "The evidentiary admissibility of digital audit logs",
    "The doctrine of equitable promissory estoppel",
    "The affirmative defense of force majeure and impossibility",
    "The common law possessory lien on commercial bailments",
    "The contractual novation substituting the primary debtor",
    "The fiduciary duty of care owed by corporate directors",
]

PREDICATES_EN = [
    "holds the harmless party indemnified against third-party claims",
    "transfers title and copyright ownership free and clear of encumbrances",
    "submits all disputes exclusively to administered arbitral tribunals",
    "authorizes contract cancellation upon written notice without penalty",
    "survives the expiration or termination of the master agreement",
    "precludes recovery of indirect losses beyond specified contract caps",
    "establishes a pre-agreed financial remedy representing actual loss",
    "requires proof of proximate causation and proximate foreseeability",
    "prohibits reverse engineering and unauthorized sublicensing to competitors",
    "confers prima facie authenticity under evidentiary statutory rules",
    "bars a party from taking positions contrary to prior explicit assertions",
    "excuses contract non-performance during unprecedented market disruptions",
    "entitles retention of custody until outstanding balances are discharged",
    "extinguishes prior obligations in exchange for newly executed covenants",
    "imposes civil liability for reckless mismanagement of corporate assets",
]

CONTEXTS_EN = [
    "ensuring robust risk allocation across international enterprise agreements",
    "consistent with established principles of governing commercial jurisprudence",
    "without prejudice to statutory remedies available under antitrust law",
    "safeguarding intellectual property integrity during cross-border operations",
    "in compliance with mandatory consumer protection and privacy regulations",
    "preventing unjust enrichment and maintaining contractual balance",
    "upholding the fundamental canon of good faith and fair dealing",
    "subject to the exclusive jurisdiction of the designated state courts",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Die Freistellungs- und Schadloshaltungsklausel",
    "Die Abtretung von Rechten an gewerblichen Schutzrechten",
    "Die verbindliche Schiedsgerichtsvereinbarung nach UNCITRAL-Regeln",
    "Die außerordentliche fristlose Kündigung aus wichtigem Grund",
    "Die Geheimhaltungsvereinbarung bezüglich geschützter Betriebsgeheimnisse",
    "Der Haftungsausschluss für leichte Fahrlässigkeit und Mangelfolgeschäden",
    "Die Vereinbarung einer verschuldensunabhängigen Vertragsstrafe",
    "Die gesamtschuldnerische Haftung mehrerer Vertragspartner",
    "Die Einräumung einfacher Nutzungsrechte an proprietärer Software",
    "Der Beweiswert qualifizierter elektronischer Signaturen",
    "Der Grundsatz von Treu und Glauben nach Paragraph 242 BGB",
    "Die Einrede des nicht erfüllten Vertrags im Zivilprozess",
    "Das kaufmännische Zurückbehaltungsrecht an gelagerten Waren",
    "Die befreiende Schuldübernahme durch dreiseitigen Vertrag",
    "Die organschaftliche Sorgfaltspflicht von Vorstandsmitgliedern",
]

PREDICATES_DE = [
    "schützt die begünstigte Partei vor Ansprüchen und Klagen Dritter",
    "überträgt die ausschließlichen Verwertungsrechte mit dinglicher Wirkung",
    "schließt den ordentlichen Rechtsweg zu den staatlichen Gerichten aus",
    "beendet das Vertragsverhältnis sofort nach Zugang der Kündigungserklärung",
    "bleibt auch nach vollständiger Vertragsabwicklung dauerhaft in Kraft",
    "begrenzt die finanzielle Ersatzpflicht auf die vorhersehbaren Schäden",
    "sichert die rechtzeitige Leistungserbringung durch feste Pauschalen ab",
    "ermöglicht dem Gläubiger den vollen Regress bei jedem Einzelschuldner",
    "untersagt die unbefugte Weitergabe und Dekompilierung des Quellcodes",
    "begründet den vollen Beweis der formellen Echtheit der Erklärung",
    "verbietet widersprüchliches und treuwidriges Verhalten im Rechtsverkehr",
    "hemmt den Verzugseintritt bis zur Erbringung der geschuldeten Gegenleistung",
    "berechtigt zur Verweigerung der Herausgabe bis zum vollständigen Ausgleich",
    "entlässt den bisherigen Schuldner vollständig aus seiner Verbindlichkeit",
    "führt bei schuldhafter Pflichtverletzung zur persönlichen Schadensersatzpflicht",
]

CONTEXTS_DE = [
    "zur Gewährleistung maximaler Rechtssicherheit im grenzüberschreitenden Handel",
    "in strikter Übereinstimmung mit den zwingenden Bestimmungen des BGB",
    "unbeschadet gesetzlicher Schadensersatzansprüche wegen vorsätzlicher Täuschung",
    "zur verlässlichen Risikominimierung bei komplexen Unternehmenskäufen",
    "unter Beachtung der europäischen Datenschutz-Grundverordnung DSGVO",
    "zur Verhinderung ungerechtfertigter Bereicherungen im Wirtschaftsverkehr",
    "gemäß den anerkannten Grundsätzen ordnungsgemäßer Unternehmensführung",
    "unter Wahrung des rechtlichen Gehörs im Zivil- und Schiedsverfahren",
]


def generate_legal_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para legal."""
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
