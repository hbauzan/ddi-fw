"""Generador trilingüe para el oficio FILOSOFIA."""

from __future__ import annotations

from scripts.trilingual_generators.base import ClauseData, build_clauses_for_lang

ALMA = "filosofia"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "El imperativo categórico formulado por Kant",
    "La reducción fenomenológica o epojé de Husserl",
    "La dialéctica del amo y el esclavo en Hegel",
    "La semántica de mundos posibles en la lógica modal",
    "La ontología fundamental del Dasein en Heidegger",
    "El falsacionismo metodológico de Karl Popper",
    "La teoría coherentista de la justificación epistémica",
    "El utilitarismo de reglas formulado en la ética analítica",
    "El problema mente-cuerpo en el materialismo eliminativo",
    "La doctrina platónica de las formas e ideas inteligibles",
    "El principio de razón suficiente en la metafísica de Leibniz",
    "La hermenéutica de la distancia temporal en Gadamer",
    "El empirismo radical y la crítica de la causalidad en Hume",
    "La ética del discurso y la acción comunicativa de Habermas",
    "El argumento ontológico de Anselmo sobre el ser necesario",
]

PREDICATES_ES = [
    "exige obrar según máximas universalizables sin contradicción racional",
    "suspende el juicio dogmático sobre la realidad empírica del mundo exterior",
    "describe el surgimiento de la autoconciencia a través del reconocimiento ajeno",
    "evalúa la verdad de proposiciones necesarias mediante accesibilidad entre estados",
    "revela la temporalidad finita como horizonte de comprensión del ser",
    "establece que una teoría solo es científica si admite refutación empírica",
    "sostiene que una creencia es racional si encaja armónicamente en el sistema",
    "juzga la corrección moral en base a normas que maximizan el bienestar general",
    "propone descartar los conceptos de la psicología popular a favor de la neurociencia",
    "sitúa la auténtica realidad en arquetipos inmutables accesibles al intelecto",
    "afirma que ningún hecho puede ser verdadero sin una explicación suficiente",
    "concibe la comprensión como una fusión de horizontes históricos mediada por lenguaje",
    "reduce la conexión necesaria entre causa y efecto a un hábito psicológico asociativo",
    "fundamenta la validez de las normas en consensos logrados en diálogo libre",
    "deduce la existencia real de Dios a partir del concepto de perfección suprema",
]

CONTEXTS_ES = [
    "fundamentando el debate contemporáneo sobre los límites del conocimiento humano",
    "en el marco de la tradición filosófica clásica y la hermenéutica crítica",
    "para superar las aporías del escepticismo radical y el relativismo epistémico",
    "clarificando las condiciones de posibilidad del juicio sintético a priori",
    "enriqueciendo la reflexión sobre la ética normativa y la justicia distributiva",
    "vinculando el rigor analítico conceptual con la fenomenología de la experiencia",
    "cuestionando los supuestos metafísicos no examinados del pensamiento occidental",
    "articulando una comprensión sistemática del sentido de la existencia y la verdad",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "The Kantian categorical imperative formulation",
    "The Husserlian phenomenological epoché technique",
    "The Hegelian master-slave dialectic of recognition",
    "Kripkean possible-worlds semantics in modal logic",
    "The fundamental ontology of Dasein in Being and Time",
    "Popperian falsificationism in scientific methodology",
    "The coherentist theory of epistemic justification",
    "Rule utilitarianism in contemporary analytical ethics",
    "Eliminative materialism regarding mental propositions",
    "The Platonic theory of transcendent intelligible forms",
    "The Leibnizian principle of sufficient reason",
    "Gadamerian philosophical hermeneutics of prejudice",
    "Humean radical skepticism concerning necessary causation",
    "Habermasian communicative action and discourse ethics",
    "Anselmian modal ontological arguments for necessary existence",
]

PREDICATES_EN = [
    "demands acting only according to universalizable rational maxims",
    "brackets the natural attitude regarding the objective external reality",
    "demonstrates that self-consciousness requires dialectical reciprocal mediation",
    "formalizes necessity and possibility across relational model structures",
    "uncovers temporal finitude as the primordial horizon of human existence",
    "distinguishes empirical science from non-falsifiable metaphysical dogma",
    "locates epistemic entitlement within the global coherence of belief webs",
    "derives moral obligatoriness from adherence to welfare-maximizing social rules",
    "asserts that folk-psychological states will be eliminated by cognitive neuroscience",
    "posits eternal immutable archetypes beyond the imperfect sensible world",
    "stipulates that every contingent fact must possess an intelligible explanation",
    "articulates historical understanding as the linguistic fusion of distinct horizons",
    "deconstructs causal necessity into subjective mental habits of associative expectation",
    "grounds normative democratic legitimacy in ideal uncoerced deliberative dialogue",
    "infers necessary objective existence directly from the concept of supreme perfection",
]

CONTEXTS_EN = [
    "advancing modern metaethical inquiry and epistemological foundation theories",
    "situated within the continuous evolution of western philosophical discourse",
    "addressing foundational paradoxes regarding moral duty and rational agency",
    "delineating the structural boundary between analytic and synthetic assertions",
    "illuminating the existential preconditions of linguistic intersubjectivity",
    "interrogating classical metaphysical assumptions through rigorous conceptual critique",
    "reconciling ontological realism with the subjective phenomenology of consciousness",
    "informing contemporary debates on philosophy of mind and normative ethics",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Der kategorische Imperativ der Kantischen Ethik",
    "Die phänomenologische Epoché nach Edmund Husserl",
    "Die Dialektik von Herrschaft und Knechtschaft bei Hegel",
    "Die Semantik möglicher Welten in der Modallogik",
    "Die Fundamentalontologie des Daseins bei Heidegger",
    "Das Falsifikationsprinzip des Kritischen Rationalismus",
    "Die Kohärenztheorie der epistemischen Rechtfertigung",
    "Der Regelutilitarismus in der modernen Moralphilosophie",
    "Der eliminative Materialismus in der Philosophie des Geistes",
    "Die Ideenlehre Platons über das intelligible Sein",
    "Der Satz vom zureichenden Grunde bei Leibniz",
    "Die philosophische Hermeneutik der Horizontverschmelzung",
    "Der Humesche Skeptizismus bezüglich der Kausalität",
    "Die Diskursethik des kommunikativen Handelns nach Habermas",
    "Der ontologische Gottesbeweis des Anselm von Canterbury",
]

PREDICATES_DE = [
    "fordert das Handeln nach Maximen, die allgemeines Gesetz werden können",
    "klammert das unhinterfragte Urteil über die äußere Realität vollständig ein",
    "beschreibt das Selbstbewusstsein als Resultat gegenseitiger Anerkennung",
    "definiert Notwendigkeit als Wahrheit in allen zugänglichen Welten",
    "bestimmt die Zeitlichkeit als den ursprünglichen Sinn des In-der-Welt-Seins",
    "erhebt die prinzipielle Widerlegbarkeit zum Abgrenzungskriterium der Wissenschaft",
    "begründet Wissen durch den widerspruchsfreien Zusammenhang des Systems",
    "beurteilt Handlungen nach allgemeinen Regeln, die den Gesamtnutzen maximieren",
    "erklärt mentale Zustände für überflüssig im Lichte der Neurobiologie",
    "verortet die eigentliche Wahrheit in übergeordneten ewigen Urformen",
    "besagt, dass kein Phänomen ohne hinreichende Ursache existieren kann",
    "versteht Auslegung als geschichtlich vermittelte Begegnung von Text und Leser",
    "führt den Kausalbegriff rein auf psychologische Gewohnheitsassoziationen zurück",
    "legitimiert moralische Normen durch zwanglosen rationalen Argumentationskonsens",
    "leitet die tatsächliche Existenz des Höchsten aus dessen Begriff logisch ab",
]

CONTEXTS_DE = [
    "zur Vertiefung erkenntnistheoretischer Grundfragen in der Gegenwart",
    "im Kontext der klassischen Tradition der europäischen Geistesgeschichte",
    "zur Überwindung metaphysischer Aporien und skeptizistischer Einwände",
    "zur Klärung der Bedingungen der Möglichkeit objektiver Erkenntnis",
    "zur Weiterentwicklung normativer ethischer und politischer Theorien",
    "im Schnittfeld von Sprachphilosophie, Logik und praktischer Philosophie",
    "zur kritischen Reflexion über das Verhältnis von Bewusstsein und Wirklichkeit",
    "gemäß den Maßstäben strenger systematischer Begriffsanalyse",
]


def generate_filosofia_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para filosofia."""
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
