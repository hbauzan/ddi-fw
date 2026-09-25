"""Generador trilingüe para el oficio MUSICA."""

from __future__ import annotations

from scripts.trilingual_generators.base import ClauseData, build_clauses_for_lang

ALMA = "musica"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "La conducción de voces en el contrapunto riguroso por especies",
    "La modulación armónica mediante acorde pivote a la tonalidad vecina",
    "La resolución de la sensible sobre la tónica en la cadencia perfecta",
    "El acorde de séptima disminuida como recurso cromático de enlace",
    "La serie armónica natural de sobretonos en tubos sonoros abiertos",
    "El bajo continuo cifrado en la música instrumental barroca",
    "El uso de síncopas y contratiempos en compases de amalgama",
    "La afinación por temperamento igual frente a la entonación pitagórica",
    "La polifonía imitativa en el canon a la quinta justa",
    "El acorde de sexta napolitana que precede a la cadencia dominante",
    "La tesitura de los instrumentos de viento madera en la orquesta",
    "El desarrollo motívico temático en la forma sonata clásica",
    "La disonancia de retardo con resolución descendente por grado conjunto",
    "El timbre acústico determinado por la envolvente espectral de armónicos",
    "La escala pentatónica menor empleada en melodías folclóricas",
]

PREDICATES_ES = [
    "evita movimientos paralelos de quintas y octavas prohibidas por la norma",
    "establece un nuevo centro tonal sin saltos auditivos abruptos o bruscos",
    "proporciona una sensación conclusiva definitiva de reposo armónico tonal",
    "funciona como puente enarmónico facilitando modulaciones a tonos lejanos",
    "determina las relaciones interválicas fundamentales de octava, quinta y tercera",
    "suministra la base armónica improvisada sobre una línea melódica grave",
    "desplaza la acentuación métrica natural generando tensión rítmica constante",
    "distribuye la coma sintónica dividiendo la octava en doce semitonos iguales",
    "repite el sujeto melódico principal manteniendo relaciones canónicas estrictas",
    "introduce un grado rebajado que intensifica la atracción hacia la dominante",
    "explota los registros dinámicos y colorísticos de las familias orquestales",
    "transforma células temáticas mediante inversión, retrogradación y aumentación",
    "mantiene una nota disonante sobre el cambio de armonía antes de resolver",
    "distingue un clarinete de un oboe aun cuando interpreten la misma frecuencia fundamental",
    "elimina tensiones de semitono facilitando giros melódicos diáfanos y fluidos",
]

CONTEXTS_ES = [
    "garantizando la coherencia estructural y el equilibrio formal de la obra",
    "siguiendo las reglas de la teoría musical y la armonía funcional clásica",
    "enriqueciendo la expresividad melódica y la densidad polifónica coral",
    "conforme a las convenciones estilísticas de las grandes escuelas sinfónicas",
    "para maximizar la claridad acústica en salas de concierto especializadas",
    "integrando la tradición contrapuntística con la innovación armónica tonal",
    "respetando el fraseo musical y la dinámica de ejecución orquestal",
    "logrando un impacto estético refinado y conmovedor en la audiencia",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "Voice leading principles in strict species counterpoint",
    "Harmonic modulation to related keys via common pivot chords",
    "The melodic resolution of the leading tone to the tonic pitch",
    "The fully diminished seventh chord functioning as a chromatic hinge",
    "The acoustic overtone series in vibrating open air columns",
    "Figured bass realization in Baroque chamber ensemble continuo",
    "Syncopated rhythmic patterns across asymmetrical complex meters",
    "Equal temperament tuning dividing the octave into twelve semitones",
    "Imitative polyphonic counterpoint in strict canon at the fifth",
    "The Neapolitan sixth chord preceding final authentic cadences",
    "Orchestral woodwind instrument tessituras and spectral formants",
    "Motivic development and fragmentation in classical sonata-allegro form",
    "Suspension dissonance resolving downward by step onto consonance",
    "Instrumental timbre determined by harmonic envelope spectral decay",
    "The minor pentatonic scale structuring modal folk melodies",
]

PREDICATES_EN = [
    "strictly forbids parallel fifths and octaves to preserve voice independence",
    "establishes new tonal polarity smoothly without disorienting listener ear",
    "provides definitive harmonic closure within classical cadential formulas",
    "enables enharmonic reinterpretation facilitating distant tonal excursions",
    "governs physical intervals of octaves, fifths, and natural major thirds",
    "provides improvised chordal realization above an unadorned bass contour",
    "shifts metric accentuation creating deliberate rhythmic tension and momentum",
    "equalizes frequency ratios to enable unrestricted modulation across all keys",
    "repeats primary musical subjects across contrasting contrapuntal voices",
    "lowers the supertonic pitch degree to dramatically intensify dominant arrival",
    "blends distinct instrumental colors across rich orchestral tutti textures",
    "develops fundamental thematic material via melodic inversion and retrograde",
    "prolongs harmonic tension across the barline before falling to stable rest",
    "distinguishes clarinet from flute through overtone harmonic distribution",
    "avoids half-step dissonances allowing open consonant melodic contours",
]

CONTEXTS_EN = [
    "preserving structural coherence throughout multi-movement symphonic works",
    "adhering to canonical treatises on functional harmony and voice leading",
    "enhancing polyphonic clarity and emotional expression across vocal choirs",
    "fulfilling stylistic requirements of classical and baroque compositional schools",
    "optimizing acoustic resonance and blend in dedicated orchestral halls",
    "synthesizing strict contrapuntal discipline with free melodic invention",
    "guiding nuanced expressive phrasing and dynamic shaping during performance",
    "creating compelling dramatic tension across classical sonata expositions",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Die Stimmführung im strengen Kontrapunkt nach Johann Joseph Fux",
    "Die harmonische Modulation in Nachbartonarten über Zwischendominanten",
    "Die Auflösung des Leittons in den Grundton bei der Ganzschlusskadenz",
    "Der verminderte Septakkord als enharmonisches Modulationswerkzeug",
    "Die physikalische Obertonreihe schwingender Luftsäulen und Saiten",
    "Die Generalbassbegleitung in der barocken Kammermusik",
    "Synkopische Rhythmen und Taktverschiebungen in ungeraden Metren",
    "Die gleichstufige Stimmung der zwölf chromatischen Halbtöne",
    "Die polyphone Imitation im strengen Quintkanon für Vokalstimmen",
    "Der neapolitanische Sextakkord vor dem dominanten Halbschluss",
    "Die klangliche Farbpalette und der Tonumfang der Holzblasinstrumente",
    "Die thematische Durchführung in der klassischen Sonatenhauptsatzform",
    "Die Dissonanz des Vorhalts mit stufenweiser Auflösung nach unten",
    "Die akustische Klangfarbe geformt durch das Obertoneinspektrum",
    "Die pentatonische Tonleiter in traditionellen Volksmelodien",
]

PREDICATES_DE = [
    "verbietet verdeckte und offene Quintenparallelen zur Wahrung der Selbständigkeit",
    "ermöglicht einen nahtlosen Übergang in eine neue Tonart ohne Bruch",
    "verleiht der Phrase einen klaren harmonischen und formalen Ruhepunkt",
    "eröffnet durch vieldeutige Schreibweisen Wege in weit entfernte Tonbereiche",
    "bestimmt die physikalischen Frequenzverhältnisse von Oktave, Quinte und Quarte",
    "liefert das harmonische Fundament für improvisierte Auszierungen des Cembalos",
    "erzeugt reizvolle rhythmische Spannungen gegen das starre Taktgerüst",
    "macht alle Tonarten ohne störende Schwebungen der Wolfsquinte spielbar",
    "führt das Thema zeitversetzt in exakten Intervallabständen polyphon durch",
    "vertieft die Moll-Charakteristik vor der abschließenden dominanten Kadenz",
    "bereichert das orchestrale Klangbild um fein abgestimmte Farbnuancen",
    "zerlegt Hauptmotive in kleinste Bruchstücke und verarbeitet sie kontrapunktisch",
    "erzeugt harmonische Reibung, die sich sanft in die Konsonanz auflöst",
    "unterscheidet Instrumente selbst bei identischer Tonhöhe und Lautstärke",
    "verzichtet auf leittönige Halbtöne und wirkt dadurch besonders schwebend",
]

CONTEXTS_DE = [
    "zur Erzielung vollendeter formaler Geschlossenheit im musikalischen Werk",
    "unter Beachtung der historischen Regeln der klassischen Tonsatzlehre",
    "zur Steigerung der kontrapunktischen Dichte und klanglichen Transparenz",
    "gemäß den stilistischen Kriterien der westeuropäischen Musiktradition",
    "für ein optimales Zusammenspiel von Orchester, Chor und Solisten",
    "zur kunstvollen Verbindung von Formdisziplin und emotionalem Ausdruck",
    "unter Berücksichtigung historischer Aufführungspraxis alter Musik",
    "zur Entfaltung eines reichen und dynamisch ausgewogenen Klangraums",
]


def generate_musica_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para musica."""
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
