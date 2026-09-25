"""Generador trilingüe para el oficio FINANZAS."""

from __future__ import annotations

from scripts.trilingual_generators.base import ClauseData, build_clauses_for_lang

ALMA = "finanzas"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "La permuta financiera de tipos de interés swap",
    "La curva de rendimientos cupón cero de la deuda soberana",
    "El cálculo del valor en riesgo mediante simulación histórica",
    "El coeficiente beta de volatilidad respecto al índice bursátil",
    "La ratio de cobertura de liquidez según la normativa Basilea III",
    "El diferencial de crédito credit spread en bonos corporativos",
    "La valoración de opciones europeas mediante la fórmula Black-Scholes",
    "La emisión de obligaciones convertibles en acciones ordinarias",
    "La estrategia de cobertura delta neutral en mesas de derivados",
    "La duración modificada de una cartera de renta fija",
    "El colchón de conservación de capital bancario contracíclico",
    "El arbitraje estadístico de pares en mercados de renta variable",
    "La tasa interna de retorno corregida por riesgo inflacionario",
    "El margen de garantía exigido por la cámara de compensación central",
    "La política monetaria expansiva de operaciones de mercado abierto",
]

PREDICATES_ES = [
    "permite transformar pasivos a tipo variable en compromisos a tipo fijo",
    "refleja las expectativas del mercado sobre la trayectoria de tipos de interés",
    "estima la pérdida patrimonial máxima esperada bajo un nivel de confianza dado",
    "mide la sensibilidad del activo frente a movimientos del mercado general",
    "obliga a mantener activos líquidos de alta calidad frente a salidas netas",
    "compensa al inversor institucional por el riesgo intrínseco de impago",
    "determina la prima teórica a partir de la volatilidad implícita del subyacente",
    "ofrece al tenedor la facultad de canje ante escenarios alcistas del emisor",
    "inmuniza la posición frente a pequeñas oscilaciones en el precio del subyacente",
    "cuantifica la variación porcentual del precio ante un cambio en la curva de tipos",
    "absorbe pérdidas no previstas durante fases de severo estrés macroeconómico",
    "explota desalineaciones temporales entre activos con alta correlación histórica",
    "descuenta flujos de caja futuros ponderando la estructura temporal del dinero",
    "mitiga el riesgo de contraparte mediante liquidaciones de pérdidas y ganancias",
    "inyecta liquidez al sistema bancario para estimular el crédito y la inversión",
]

CONTEXTS_ES = [
    "optimizando la gestión del balance en entidades financieras internacionales",
    "en estricto cumplimiento de los estándares regulatorios de solvencia bancaria",
    "para preservar la rentabilidad ajustada por riesgo de los fondos de inversión",
    "minimizando la exposición neta a perturbaciones imprevistas en los tipos de cambio",
    "salvaguardando la estabilidad del sistema financiero frente a riesgos sistémicos",
    "conforme a las directrices de supervisión prudencial de los bancos centrales",
    "mediante modelos cuantitativos de optimización de carteras de inversión",
    "durante períodos de alta volatilidad en los mercados de capitales globales",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "The plain vanilla interest rate swap agreement",
    "The zero-coupon yield curve for sovereign treasury benchmarks",
    "The parametric Value-at-Risk computation model",
    "The equity beta coefficient relative to the market index",
    "The Liquidity Coverage Ratio mandate under Basel III regulations",
    "The credit default swap spread on investment-grade debt",
    "The Black-Scholes valuation formula for European options",
    "The convertible bond issuance featuring embedded call options",
    "The dynamic delta-hedging protocol on derivatives trading desks",
    "The modified duration metric for fixed-income bond portfolios",
    "The countercyclical capital buffer requirement for Tier 1 capital",
    "Statistical pairs trading strategies across liquid equities",
    "The risk-adjusted net present value of capital budgeting cash flows",
    "Initial margin requirements posted at central clearing counterparties",
    "Central bank quantitative easing through open market purchases",
]

PREDICATES_EN = [
    "exchanges floating cash flows for fixed commitments across maturities",
    "derives forward interest rates from instantaneous discount factors",
    "quantifies extreme downside portfolio exposure at defined confidence limits",
    "estimates systematic market risk exposure across diversified equity holdings",
    "mandates unencumbered high-quality liquid asset reserves against runoffs",
    "reflects the market-implied probability of default and loss recovery rates",
    "prices contract premia using underlying asset volatility and risk-free rates",
    "grants bondholders equity upside participation while preserving yield floors",
    "continuously balances option delta exposures against underlying equity shifts",
    "measures bond price elasticity relative to instantaneous interest rate shifts",
    "strengthens banking sector resilience during systemic downturns and stress",
    "captures mean-reverting alpha from temporary market pricing dislocations",
    "discounts expected future cash flows using weighted average cost of capital",
    "insulates clearinghouse participants against bilateral counterparty defaults",
    "expands central bank balance sheet reserves to suppress long-term yield curves",
]

CONTEXTS_EN = [
    "optimizing balance-sheet asset-liability management in commercial banking",
    "in compliance with international prudential financial regulatory frameworks",
    "preserving risk-adjusted returns across institutional multi-asset funds",
    "mitigating direct credit contagion across global interbank wholesale markets",
    "safeguarding macroeconomic liquidity throughout severe market downturns",
    "calibrating stochastic volatility surfaces against observed market quotes",
    "adhering to rigorous capital adequacy guidelines mandated by Basel accords",
    "enhancing portfolio Sharpe ratios under adverse macroeconomic interest environments",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Der Zinsswap mit quartalsweiser Zinsanpassung",
    "Die Nullkupon-Zinsstrukturkurve für Staatsanleihen",
    "Der Value-at-Risk unter Verwendung historischer Simulation",
    "Das Beta-Maß für das systematische Marktrisiko der Aktie",
    "Die Liquiditätsdeckungsquote gemäß den Basel-III-Richtlinien",
    "Der Credit-Default-Swap-Spread auf Unternehmensanleihen",
    "Das Black-Scholes-Optionspreismodell für europäische Optionen",
    "Die Ausgabe von Wandelschuldverschreibungen mit Umtauschrecht",
    "Die dynamische Delta-Hedging-Strategie im Derivatehandel",
    "Die modifizierte Duration festverzinslicher Rentenportfolios",
    "Der antizyklische Kapitalpuffer für systemrelevante Kreditinstitute",
    "Das statistische Arbitrage-Trading mit korrelierten Aktienpaaren",
    "Die risikoadjustierte Kapitalrendite im Rahmen der Projektbewertung",
    "Die von zentralen Gegenparteien erhobene Initial-Margin",
    "Die expansive Offenmarktpolitik der Europäischen Zentralbank",
]

PREDICATES_DE = [
    "wandelt variable Verbindlichkeiten in feste Zinszahlungen um",
    "bildet die Markterwartungen bezüglich künftiger Zinsniveaus präzise ab",
    "beziffert das maximale Verlustrisiko bei gegebenem Konfidenzniveau",
    "misst die relative Schwankungsbreite im Vergleich zum Gesamtmarkt",
    "verpflichtet Kreditinstitute zur Haltung erstklassiger liquider Aktiva",
    "kompensiert institutionelle Investoren für das Ausfallrisiko des Emittenten",
    "ermittelt den theoretischen Optionswert aus der impliziten Volatilität",
    "bietet Anlegern eine feste Verzinsung mit partizipativer Aktienoption",
    "neutralisiert Richtungsrisiken des Basiswerts durch stetige Anpassung",
    "quantifiziert die Zinssensitivität des Portfolios bei Zinsänderungen",
    "dämpft prozyklische Kreditvergaben in Phasen übermäßigen Wachstums",
    "nutzt kurzfristige Bewertungsanomalien historisch eng verbundener Titel",
    "diskontiert zukünftige Zahlungsströme mit den gewichteten Kapitalkosten",
    "schützt Marktteilnehmer vor dem Ausfall bilateraler Handelspartner",
    "versorgt den Bankensektor mit zusätzlicher Liquidität zur Zinsstabilisierung",
]

CONTEXTS_DE = [
    "zur Optimierung des Zins- und Liquiditätsmanagements von Geschäftsbanken",
    "in strikter Erfüllung der bankenaufsichtsrechtlichen Eigenkapitalvorschriften",
    "zur Erzielung attraktiver risikobereinigter Renditen im Fondsmanagement",
    "zur verlässlichen Absicherung gegen unvorhergesehene Währungsschwankungen",
    "zur Gewährleistung der Stabilität des europäischen Finanzsystems",
    "gemäß den Vorgaben der internationalen Ausschüsse für Bankenaufsicht",
    "unter Einsatz mathematisch-statistischer Risikomodelle an den Kapitalmärkten",
    "während Phasen ausgeprägter Marktvolatilität an den globalen Wertpapierbörsen",
]


def generate_finanzas_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para finanzas."""
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
