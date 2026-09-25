"""Generador trilingüe para el oficio RECETA."""

from __future__ import annotations

from scripts.trilingual_generators.base import (
    ClauseData,
    build_clauses_for_lang,
    load_extended_seeds,
)

ALMA = "receta"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "El templado de chocolate cobertura sobre mesada de mármol",
    "La emulsión de yemas frescas con mostaza de Dijón y vinagre",
    "El amasado manual sobre superficie enharinada",
    "La fermentación lenta de masa madre en ambiente templado",
    "El desglasado de la cacerola caliente con vino blanco seco",
    "La cocción al vacío sous-vide a temperatura controlada",
    "El tamizado fino de harina de repostería con polvo leudante",
    "La reducción de fondo oscuro de ternera con aromáticas",
    "El confitado de dientes de ajo en aceite de oliva virgen extra",
    "El batido de claras a punto de nieve con cremor tártaro",
    "El escalfado de peras en almíbar especiado con canela",
    "La caramelización de cebollas a fuego lento en manteca clarificada",
    "El hojaldrado de la masa con sucesivas vueltas dobles",
    "La gelificación de mermelada con pectina cítrica natural",
    "El marinado en frío de pescados blancos con jugo de lima",
]

PREDICATES_ES = [
    "asegura un brillo satinado y un quiebre crocante perfecto",
    "estabiliza la estructura coloidal impidiendo que se corte la salsa",
    "desarrolla una red elástica de gluten de gran extensibilidad",
    "multiplica los aromas complejos mediante fermentación láctica y acética",
    "disuelve los jugos caramelizados adheridos al fondo de cocción",
    "preserva la terneza y jugosidad interna sin sobrecocer las fibras",
    "airea las partículas secas evitando la formación de grumos densos",
    "concentra el colágeno natural otorgando cuerpo espeso y aterciopelado",
    "ablanda los tejidos vegetales infundiendo un sabor suave y dulce",
    "incorpora burbujas microscópicas que dan volumen al soufflé",
    "tierniza la pulpa conservando la forma geométrica de la fruta",
    "desarrolla notas dulces profundas mediante reacciones de Maillard lentas",
    "crea láminas crujientes y separadas al fundirse las capas grasas",
    "alcanza la viscosidad óptima sin alterar el sabor frutal original",
    "desnaturaliza suavemente las proteínas superficiales mediante acidez",
]

CONTEXTS_ES = [
    "garantizando un resultado gastronómico de alta pastelería artesanal",
    "siguiendo las técnicas tradicionales de la cocina clásica francesa",
    "optimizando la textura y la presentación en emplatados gourmet",
    "manteniendo un riguroso control higiénico y térmico de los alimentos",
    "para realzar el equilibrio organoléptico entre acidez, grasa y dulzor",
    "evitando la pérdida de humedad durante el reposo previo al servicio",
    "asegurando una cocción uniforme en hornos de convección profesional",
    "respetando los tiempos de reposo necesarios para asentar los sabores",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "The tempering of dark couverture chocolate on cold marble",
    "The delicate emulsion of egg yolks with Dijon mustard",
    "The kneading of high-protein sourdough bread dough",
    "The slow fermentation of wild yeast levain in proofing baskets",
    "The deglazing of stainless steel roasting pans with dry vermouth",
    "The precision sous-vide poaching of salmon fillets",
    "The repeated sifting of cake flour with cornstarch",
    "The reduction of roasted veal stock with mirepoix and thyme",
    "The gentle confiting of whole garlic heads in olive oil",
    "The whipping of fresh egg whites with a pinch of cream of tartar",
    "The poaching of peeled Bosc pears in sweet mulled wine",
    "The low-temperature caramelization of thinly sliced yellow onions",
    "The lamination of viennoiserie pastry through multiple turns",
    "The setting of fruit coulis with powdered citrus pectin",
    "The cold acid ceviche curing of freshly caught flounder",
]

PREDICATES_EN = [
    "produces a mirror-like sheen and crisp audible snap",
    "stabilizes the suspension into a silky, unctuous sauce",
    "develops an extensive gluten matrix capable of holding oven spring",
    "yields rich lactic and acetic flavor complexity throughout crumb",
    "dissolves caramelized Maillard fond into an aromatic pan sauce",
    "yields an exceptionally buttery and tender internal flakiness",
    "removes heavy clumps and incorporates optimal aeration into batter",
    "concentrates extracted bone collagen into a glossy glaze",
    "transforms pungent sulfur notes into sweet mellow spreadable cloves",
    "creates microscopic air pockets essential for airy souffle rise",
    "infuses warm aromatics while keeping fruit pulp structurally intact",
    "converts natural allium sugars into deep amber caramelized notes",
    "generates dozens of micro-thin crispy pastry layers in the oven",
    "produces a clean, spreadable jelly without clouding transparency",
    "firms muscle fibers while preserving delicate raw marine moisture",
]

CONTEXTS_EN = [
    "elevating the final sensory presentation in fine dining service",
    "adhering to classical European culinary and confectionery methods",
    "balancing acidity, sweetness, and savory umami on the palate",
    "preventing culinary fat separation under precise thermal control",
    "yielding superior crumb structure and oven spring in artisan baking",
    "maximizing the retention of aromatic volatile flavor compounds",
    "ensuring consistent texture across multi-course tasting menus",
    "maintaining pristine kitchen hygiene and standardized timing",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Das Temperieren von dunkler Kuvertüre auf der Marmorplatte",
    "Die Emulsion frischer Eigelbe mit französischem Senf",
    "Das intensive Kneten von Roggensauerteig auf der Arbeitsfläche",
    "Die lange Teigführung mit Natursauerteig im Gärkorb",
    "Das Ablöschen des heißen Bräterbodens mit trockenem Weißwein",
    "Das Vakuumgaren von Kalbsfilets bei konstanter Niedrigtemperatur",
    "Das sorgfältige Sieben von Weizenmehl mit Backtriebmittel",
    "Das Reduzieren von dunklem Rinderfond mit Röstgemüse",
    "Das schonende Konfieren von Knoblauchzehen in Olivenöl",
    "Das Aufschlagen von frischem Eiklar zu festem Eischnee",
    "Das Pochieren geschälter Birnen in würzigem Weißweinsud",
    "Das langsame Schmoren fein geschnittener Zwiebeln in Butter",
    "Das Tourieren von Blätterteig mit kalten Butterplatten",
    "Das Gelieren von Fruchtpüree mit reinem Apfelpektin",
    "Das Marinieren von Meeresfrüchten in frischem Limettensaft",
]

PREDICATES_DE = [
    "garantiert perfekten Glanz und einen knackigen Bruch beim Erkalten",
    "verhindert das Gerinnen und sorgt für eine sämige Konsistenz",
    "baut ein stabiles Glutengerüst für ein optimales Backvolumen auf",
    "entwickelt komplexe Säuren und ein ausgeprägtes Brotaroma",
    "löst die karamellisierten Röstaromen zu einer feinen Bratensauce",
    "erhält die Saftigkeit und Zartheit des Fleisches ohne Saftverlust",
    "lockert das Gemenge auf und verhindert unerwünschte Klümpchen",
    "konzentriert die Gelatine zu einer glänzenden, gehaltvollen Demi-Glace",
    "mildert die Schärfe und verleiht ein nussig-süßes Aroma",
    "schließt feine Luftbläschen für die Lockerung von Biskuitteigen ein",
    "durchzieht das Fruchtfleisch mit Aromen von Zimt und Nelken",
    "entwickelt intensive Karamellnoten durch langsame Maillard-Reaktionen",
    "erzeugt hauchdünne, knusprige Teigschichten im Backofen",
    "sorgt für streichfähige Festigkeit bei voller Fruchtfrische",
    "gahrt das zarte Fischgewebe rein physikalisch durch Säureeinwirkung",
]

CONTEXTS_DE = [
    "zur Vollendung anspruchsvoller handwerklicher Gourmet-Kreationen",
    "gemäß den klassischen Standards der gehobenen Gastronomie",
    "unter präziser Überwachung der optimalen Kerntemperatur",
    "zur harmonischen Abstimmung von Süße, Säure und feinen Röstaromen",
    "für ein perfektes Mundgefühl und ansprechende Tellerpräsentation",
    "zur Vermeidung von Feuchtigkeitsverlust während der Ruhephase",
    "für erstklassige Textur und saubere Schnittfestigkeit beim Servieren",
    "unter Beachtung traditioneller Rezepturen und Kochtechniken",
]


def generate_receta_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para receta."""
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
