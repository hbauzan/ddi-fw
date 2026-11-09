"""Funciones Python de negocios y snippets ajenos. Todo el texto es offline y fijo."""

from __future__ import annotations

import ast

BusinessSpec = tuple[str, str, str]
ForeignSpec = tuple[str, str, str]


def _py(name: str, args: str, doc: str, body: str) -> str:
    if '"""' in doc or '"""' in body:
        raise ValueError(f"comillas triples no permitidas en {name}")
    indented: list[str] = []
    for line in body.strip("\n").splitlines():
        indented.append("" if not line.strip() else "    " + line)
    source = f'def {name}({args}):\n    """{doc}"""\n' + "\n".join(indented) + "\n"
    tree = ast.parse(source)
    if not isinstance(tree.body[0], ast.FunctionDef) or tree.body[0].name != name:
        raise ValueError(f"fixture python invalida: {name}")
    return source


def _biz(subtag: str, name: str, args: str, doc: str, body: str) -> BusinessSpec:
    return (subtag, name, _py(name, args, doc, body))


BUSINESS_FUNCTIONS: list[BusinessSpec] = [
    _biz(
        "finanzas",
        "liquidar_intereses_moratorios",
        "capital: float, tasa_diaria: float, dias: int",
        "Liquida intereses moratorios de un prestamo bancario con tasa diaria nominal.",
        """
if capital < 0 or tasa_diaria < 0 or dias < 0:
    raise ValueError("capital, tasa y dias de mora no pueden ser negativos")
interes = capital * tasa_diaria * float(dias)
iva = interes * 0.21
return capital + interes + iva
""",
    ),
    _biz(
        "finanzas",
        "calcular_cuota_francesa",
        "principal: float, tasa_mensual: float, cuotas: int",
        "Calcula la cuota fija de un prestamo frances amortizable.",
        """
if principal <= 0 or cuotas <= 0:
    raise ValueError("principal y cuotas deben ser positivos")
if tasa_mensual == 0:
    return principal / float(cuotas)
factor = (1.0 + tasa_mensual) ** cuotas
return principal * tasa_mensual * factor / (factor - 1.0)
""",
    ),
    _biz(
        "finanzas",
        "retener_impuesto_ganancias",
        "bruto: float, alicuota: float, minimo_no_imponible: float",
        "Retiene impuesto a las ganancias sobre el excedente del minimo no imponible.",
        """
if bruto < 0 or alicuota < 0 or minimo_no_imponible < 0:
    raise ValueError("importes de retencion invalidos")
base = max(0.0, bruto - minimo_no_imponible)
retenido = base * alicuota
return {"base": base, "retenido": retenido, "neto": bruto - retenido}
""",
    ),
    _biz(
        "finanzas",
        "valorizar_bono_cero_cupon",
        "nominal: float, tasa_efectiva: float, anios: int",
        "Valoriza un bono cero cupon descontando el nominal a tasa efectiva anual.",
        """
if nominal <= 0 or anios < 0 or tasa_efectiva <= -1.0:
    raise ValueError("parametros de bono fuera de dominio")
return nominal / ((1.0 + tasa_efectiva) ** anios)
""",
    ),
    _biz(
        "finanzas",
        "calcular_iva_debito_fiscal",
        "neto_gravado: float, alicuota: float = 0.21",
        "Calcula IVA debito fiscal y el total de factura de un comprobante de venta.",
        """
if neto_gravado < 0 or alicuota < 0:
    raise ValueError("neto y alicuota de IVA no pueden ser negativos")
iva = neto_gravado * alicuota
return {"neto": neto_gravado, "iva": iva, "total": neto_gravado + iva}
""",
    ),
    _biz(
        "finanzas",
        "prorratear_gasto_centro_costo",
        "gasto: float, pesos: dict[str, float]",
        "Prorratea un gasto corporativo entre centros de costo segun pesos positivos.",
        """
if gasto < 0 or not pesos:
    raise ValueError("gasto o pesos de centros de costo invalidos")
total = 0.0
for peso in pesos.values():
    if peso < 0:
        raise ValueError("peso de centro de costo negativo")
    total += peso
if total == 0:
    raise ValueError("la suma de pesos no puede ser cero")
return {centro: gasto * peso / total for centro, peso in pesos.items()}
""",
    ),
    _biz(
        "finanzas",
        "actualizar_saldo_caja_diaria",
        "saldo_inicial: float, ingresos: float, egresos: float",
        "Actualiza el saldo de caja diaria restando egresos operativos de los ingresos.",
        """
if ingresos < 0 or egresos < 0:
    raise ValueError("ingresos y egresos de caja deben ser no negativos")
saldo = saldo_inicial + ingresos - egresos
return {"saldo": saldo, "descubierto": saldo < 0}
""",
    ),
    _biz(
        "finanzas",
        "convertir_moneda_con_spread",
        "monto: float, tipo_cambio: float, spread: float",
        "Convierte un monto aplicando el tipo de cambio y el spread de la mesa.",
        """
if monto < 0 or tipo_cambio <= 0 or spread < 0:
    raise ValueError("monto, tipo de cambio o spread invalidos")
efectivo = tipo_cambio * (1.0 + spread)
return {"tipo_efectivo": efectivo, "monto_destino": monto * efectivo}
""",
    ),
    _biz(
        "finanzas",
        "estimar_tir_biseccion",
        "flujos: list[float], iteraciones: int = 40",
        "Estima la TIR de un flujo de fondos por biseccion sobre el VAN.",
        """
if len(flujos) < 2 or iteraciones < 1:
    raise ValueError("se necesitan al menos dos flujos y una iteracion")

def van(tasa: float) -> float:
    acumulado = 0.0
    for periodo, flujo in enumerate(flujos):
        acumulado += flujo / ((1.0 + tasa) ** periodo)
    return acumulado

lo, hi = -0.9, 5.0
if van(lo) * van(hi) > 0:
    return None
for _ in range(iteraciones):
    medio = (lo + hi) / 2.0
    if van(lo) * van(medio) <= 0:
        hi = medio
    else:
        lo = medio
return (lo + hi) / 2.0
""",
    ),
    _biz(
        "finanzas",
        "provisionar_incobrables",
        "cartera: list[tuple[float, int]]",
        "Provisiona incobrables segun tramos de atraso de la cartera comercial.",
        """
if not cartera:
    return 0.0
provision = 0.0
for saldo, dias in cartera:
    if saldo < 0 or dias < 0:
        raise ValueError("saldo o atraso de cartera invalido")
    if dias >= 180:
        coef = 1.0
    elif dias >= 90:
        coef = 0.50
    elif dias >= 30:
        coef = 0.15
    else:
        coef = 0.02
    provision += saldo * coef
return provision
""",
    ),
    _biz(
        "finanzas",
        "liquidar_aguinaldo_sac",
        "mejor_sueldo: float, meses_trabajados: int",
        "Liquida el sueldo anual complementario proporcional a los meses trabajados.",
        """
if mejor_sueldo < 0 or not 0 <= meses_trabajados <= 6:
    raise ValueError("sueldo o semestre de aguinaldo invalidos")
return mejor_sueldo * (meses_trabajados / 6.0) * 0.5
""",
    ),
    _biz(
        "finanzas",
        "calcular_margen_bruto",
        "ventas_netas: float, costo_mercaderia: float",
        "Calcula el margen bruto absoluto y porcentual de un estado de resultados.",
        """
if ventas_netas < 0 or costo_mercaderia < 0:
    raise ValueError("ventas y costo de mercaderia deben ser no negativos")
margen = ventas_netas - costo_mercaderia
ratio = 0.0 if ventas_netas == 0 else margen / ventas_netas
return {"margen": margen, "ratio": ratio}
""",
    ),
    _biz(
        "medicina",
        "calcular_dosis_mg_por_kg",
        "peso_kg: float, mg_por_kg: float, concentracion_mg_ml: float",
        "Calcula la dosis en miligramos y mililitros a partir del peso del paciente.",
        """
if peso_kg <= 0 or mg_por_kg < 0 or concentracion_mg_ml <= 0:
    raise ValueError("peso, dosis o concentracion clinica invalida")
mg = peso_kg * mg_por_kg
return {"mg": mg, "ml": mg / concentracion_mg_ml}
""",
    ),
    _biz(
        "medicina",
        "ajustar_dosis_clearance",
        "dosis_mg: float, clearance_ml_min: float, clearance_ref: float = 90.0",
        "Ajusta una dosis de farmacia segun el clearance de creatinina del paciente.",
        """
if dosis_mg < 0 or clearance_ml_min < 0 or clearance_ref <= 0:
    raise ValueError("dosis o clearance renal invalido")
factor = min(1.0, clearance_ml_min / clearance_ref)
return dosis_mg * factor
""",
    ),
    _biz(
        "medicina",
        "calcular_imc_clinico",
        "peso_kg: float, talla_m: float",
        "Calcula el indice de masa corporal y una etiqueta clinica gruesa.",
        """
if peso_kg <= 0 or talla_m <= 0:
    raise ValueError("peso y talla clinica deben ser positivos")
imc = peso_kg / (talla_m * talla_m)
if imc < 18.5:
    etiqueta = "bajo"
elif imc < 25.0:
    etiqueta = "normal"
elif imc < 30.0:
    etiqueta = "sobrepeso"
else:
    etiqueta = "obesidad"
return {"imc": imc, "etiqueta": etiqueta}
""",
    ),
    _biz(
        "medicina",
        "clasificar_presion_arterial",
        "sistolica: int, diastolica: int",
        "Clasifica una toma de presion arterial sistolica y diastolica.",
        """
if sistolica <= 0 or diastolica <= 0 or diastolica > sistolica:
    raise ValueError("toma de presion arterial incoherente")
if sistolica >= 180 or diastolica >= 120:
    return "crisis"
if sistolica >= 140 or diastolica >= 90:
    return "hipertension"
if sistolica >= 130 or diastolica >= 80:
    return "elevada"
return "normal"
""",
    ),
    _biz(
        "medicina",
        "calcular_goteo_ml_por_hora",
        "volumen_ml: float, horas: float",
        "Calcula el goteo de una infusion en mililitros por hora y gotas por minuto.",
        """
if volumen_ml < 0 or horas <= 0:
    raise ValueError("volumen u horas de infusion invalidos")
ml_hora = volumen_ml / horas
gotas_min = ml_hora * 20.0 / 60.0
return {"ml_hora": ml_hora, "gotas_min": gotas_min}
""",
    ),
    _biz(
        "medicina",
        "superficie_corporal_mosteller",
        "peso_kg: float, talla_cm: float",
        "Estima la superficie corporal con la formula de Mosteller para dosificar.",
        """
import math
if peso_kg <= 0 or talla_cm <= 0:
    raise ValueError("peso o talla de Mosteller invalidos")
return math.sqrt(peso_kg * talla_cm / 3600.0)
""",
    ),
    _biz(
        "medicina",
        "alerta_glucosa_mg_dl",
        "glucosa_mg_dl: float",
        "Emite una alerta clinica gruesa para una glucemia capilar en mg/dl.",
        """
if glucosa_mg_dl <= 0:
    raise ValueError("glucemia debe ser positiva")
if glucosa_mg_dl < 70:
    return "hipoglucemia"
if glucosa_mg_dl > 180:
    return "hiperglucemia"
return "en_rango"
""",
    ),
    _biz(
        "medicina",
        "dosis_pediatrica_por_superficie",
        "dosis_adulto_mg: float, superficie_m2: float",
        "Escala una dosis pediatrica de farmacia contra una superficie de referencia.",
        """
if dosis_adulto_mg < 0 or superficie_m2 <= 0:
    raise ValueError("dosis o superficie pediatrica invalida")
return dosis_adulto_mg * (superficie_m2 / 1.73)
""",
    ),
    _biz(
        "medicina",
        "balance_hidrico_turno",
        "ingresos_ml: list[float], egresos_ml: list[float]",
        "Calcula el balance hidrico de un turno de enfermeria en mililitros.",
        """
for valor in ingresos_ml + egresos_ml:
    if valor < 0:
        raise ValueError("un volumen hidrico no puede ser negativo")
ingresos = sum(ingresos_ml)
egresos = sum(egresos_ml)
return {"ingresos": ingresos, "egresos": egresos, "balance": ingresos - egresos}
""",
    ),
    _biz(
        "medicina",
        "egfr_ckd_epi_simplificado",
        "creatinina_mg_dl: float, edad: int, mujer: bool",
        "Aproxima el filtrado glomerular con una variante simple de CKD-EPI.",
        """
if creatinina_mg_dl <= 0 or edad <= 0:
    raise ValueError("creatinina o edad invalidas para eGFR")
kappa = 0.7 if mujer else 0.9
alfa = -0.241 if mujer else -0.302
sexo = 1.012 if mujer else 1.0
ratio = creatinina_mg_dl / kappa
termino = min(ratio, 1.0) ** alfa * max(ratio, 1.0) ** -1.200
return 142.0 * termino * (0.9938 ** edad) * sexo
""",
    ),
    _biz(
        "medicina",
        "convertir_insulina_unidades",
        "unidades: float, concentracion_u_ml: float = 100.0",
        "Convierte unidades de insulina a mililitros segun la concentracion del vial.",
        """
if unidades < 0 or concentracion_u_ml <= 0:
    raise ValueError("unidades o concentracion de insulina invalidas")
return unidades / concentracion_u_ml
""",
    ),
    _biz(
        "medicina",
        "puntaje_news_parcial",
        "frecuencia_resp: int, sat_o2: int, temperatura_c: float",
        "Suma un puntaje NEWS parcial con respiracion, saturacion y temperatura.",
        """
if frecuencia_resp <= 0 or not 0 <= sat_o2 <= 100 or temperatura_c <= 0:
    raise ValueError("signos vitales fuera de rango para NEWS")
puntos = 0
if frecuencia_resp <= 8 or frecuencia_resp >= 25:
    puntos += 3
elif frecuencia_resp >= 21:
    puntos += 2
if sat_o2 <= 91:
    puntos += 3
elif sat_o2 <= 93:
    puntos += 2
elif sat_o2 <= 95:
    puntos += 1
if temperatura_c <= 35.0 or temperatura_c >= 39.1:
    puntos += 2
elif temperatura_c >= 38.1:
    puntos += 1
return puntos
""",
    ),
    _biz(
        "derecho",
        "intereses_punitivos_pactados",
        "capital: float, tasa_diaria: float, dias: int, tope: float",
        "Calcula intereses punitorios contractuales sin superar el tope pactado.",
        """
if capital < 0 or tasa_diaria < 0 or dias < 0 or tope < 0:
    raise ValueError("parametros de interes punitorio invalidos")
interes = capital * tasa_diaria * float(dias)
return min(interes, tope)
""",
    ),
    _biz(
        "derecho",
        "dias_habiles_hasta_prescripcion",
        "dias_transcurridos: int, plazo_dias: int",
        "Informa cuantos dias restan de un plazo de prescripcion contractual.",
        """
if dias_transcurridos < 0 or plazo_dias <= 0:
    raise ValueError("plazo de prescripcion invalido")
restantes = plazo_dias - dias_transcurridos
return {"restantes": restantes, "prescripto": restantes < 0}
""",
    ),
    _biz(
        "derecho",
        "honorarios_por_utm",
        "utm: float, cantidad_utm: float, alicuota_iva: float = 0.21",
        "Liquida honorarios profesionales expresados en unidades tributarias.",
        """
if utm <= 0 or cantidad_utm < 0 or alicuota_iva < 0:
    raise ValueError("UTM u honorarios invalidos")
neto = utm * cantidad_utm
iva = neto * alicuota_iva
return {"neto": neto, "iva": iva, "total": neto + iva}
""",
    ),
    _biz(
        "derecho",
        "actualizar_monto_coeficiente",
        "monto: float, coeficiente_inicial: float, coeficiente_actual: float",
        "Actualiza un monto historico de sentencia por el cociente de coeficientes.",
        """
if monto < 0 or coeficiente_inicial <= 0 or coeficiente_actual <= 0:
    raise ValueError("monto o coeficiente de actualizacion invalido")
return monto * (coeficiente_actual / coeficiente_inicial)
""",
    ),
    _biz(
        "derecho",
        "tope_clausula_penal",
        "pena: float, obligacion_principal: float, tope_ratio: float = 1.0",
        "Limita una clausula penal al tope legal respecto de la obligacion principal.",
        """
if pena < 0 or obligacion_principal < 0 or tope_ratio < 0:
    raise ValueError("pena u obligacion principal invalidas")
return min(pena, obligacion_principal * tope_ratio)
""",
    ),
    _biz(
        "derecho",
        "indemnizacion_despido_ar",
        "mejor_sueldo: float, antiguedad_anios: int",
        "Estima una indemnizacion por despido de un mes por anio de antiguedad.",
        """
if mejor_sueldo < 0 or antiguedad_anios < 0:
    raise ValueError("sueldo o antiguedad invalidos")
anios = max(1, antiguedad_anios) if mejor_sueldo > 0 else 0
return mejor_sueldo * float(anios)
""",
    ),
    _biz(
        "derecho",
        "hijuela_legitima_hereditaria",
        "acervo: float, herederos: int, porcion_legitima: float = 0.5",
        "Reparte la porcion legitima de un acervo entre los herederos forzosos.",
        """
if acervo < 0 or herederos <= 0 or not 0 <= porcion_legitima <= 1:
    raise ValueError("acervo, herederos o legitima invalidos")
legitima = acervo * porcion_legitima
return {"legitima_total": legitima, "por_heredero": legitima / float(herederos)}
""",
    ),
    _biz(
        "derecho",
        "costas_procesales_porcentaje",
        "monto_condena: float, porcentaje: float, honorarios_minimos: float",
        "Calcula costas procesales como porcentaje de la condena con un minimo.",
        """
if monto_condena < 0 or porcentaje < 0 or honorarios_minimos < 0:
    raise ValueError("condena o costas invalidas")
return max(honorarios_minimos, monto_condena * porcentaje)
""",
    ),
    _biz(
        "derecho",
        "vencimiento_dias_corridos",
        "fecha_ordinal: int, plazo: int",
        "Calcula el ordinal de vencimiento sumando dias corridos a un plazo contractual.",
        """
if plazo < 0:
    raise ValueError("el plazo contractual no puede ser negativo")
return fecha_ordinal + plazo
""",
    ),
    _biz(
        "derecho",
        "multa_mora_contractual",
        "canon: float, dias_mora: int, tasa_diaria: float",
        "Liquida una multa por mora contractual sobre el canon impago.",
        """
if canon < 0 or dias_mora < 0 or tasa_diaria < 0:
    raise ValueError("canon, mora o tasa contractual invalidos")
return canon * tasa_diaria * float(dias_mora)
""",
    ),
    _biz(
        "derecho",
        "canon_locativo_indexado",
        "canon: float, indice_base: float, indice_actual: float",
        "Indexa un canon locativo por el cociente de un indice publicado.",
        """
if canon < 0 or indice_base <= 0 or indice_actual <= 0:
    raise ValueError("canon o indice locativo invalido")
return canon * (indice_actual / indice_base)
""",
    ),
    _biz(
        "derecho",
        "quita_quirografaria_concurso",
        "credito: float, quita: float",
        "Aplica una quita a un credito quirografario dentro de un concurso.",
        """
if credito < 0 or not 0 <= quita <= 1:
    raise ValueError("credito o quita concursal invalidos")
pagadero = credito * (1.0 - quita)
return {"quirografario": credito, "pagadero": pagadero, "condonado": credito - pagadero}
""",
    ),
    _biz(
        "gastronomia",
        "escalar_gramos_harina_receta",
        "gramos_base: float, porciones_base: int, porciones_destino: int",
        "Escala los gramos de harina de una ficha tecnica al numero de porciones.",
        """
if gramos_base < 0 or porciones_base <= 0 or porciones_destino <= 0:
    raise ValueError("harina o porciones de ficha invalidas")
return gramos_base * (float(porciones_destino) / float(porciones_base))
""",
    ),
    _biz(
        "gastronomia",
        "merma_limpieza_verdura",
        "gramos_brutos: float, merma_ratio: float",
        "Descuenta la merma de limpieza de una verdura y devuelve el neto utilizable.",
        """
if gramos_brutos < 0 or not 0 <= merma_ratio < 1:
    raise ValueError("bruto o merma de verdura invalidos")
neto = gramos_brutos * (1.0 - merma_ratio)
return {"neto": neto, "merma": gramos_brutos - neto}
""",
    ),
    _biz(
        "gastronomia",
        "costeo_porcion_menu",
        "costo_insumos: float, porciones: int, precio_venta: float",
        "Costea una porcion de menu y calcula el food cost contra el precio de venta.",
        """
if costo_insumos < 0 or porciones <= 0 or precio_venta < 0:
    raise ValueError("costo, porciones o precio de menu invalidos")
costo = costo_insumos / float(porciones)
ratio = 0.0 if precio_venta == 0 else costo / precio_venta
return {"costo_porcion": costo, "food_cost": ratio}
""",
    ),
    _biz(
        "gastronomia",
        "convertir_cucharadas_a_mililitros",
        "cucharadas: float, ml_por_cucharada: float = 15.0",
        "Convierte cucharadas de una receta de cocina a mililitros.",
        """
if cucharadas < 0 or ml_por_cucharada <= 0:
    raise ValueError("cucharadas o equivalencia invalidas")
return cucharadas * ml_por_cucharada
""",
    ),
    _biz(
        "gastronomia",
        "ajustar_temperatura_conveccion",
        "celsius_convencional: float, descuento: float = 15.0",
        "Baja la temperatura de horno convencional para una coccion por conveccion.",
        """
if celsius_convencional <= 0 or descuento < 0:
    raise ValueError("temperatura de horno invalida")
ajustada = celsius_convencional - descuento
if ajustada <= 0:
    raise ValueError("la temperatura ajustada debe seguir siendo positiva")
return ajustada
""",
    ),
    _biz(
        "gastronomia",
        "punto_reposicion_insumo",
        "consumo_diario: float, dias_reposicion: int, stock_seguridad: float",
        "Calcula el punto de reposicion de un insumo de deposito de cocina.",
        """
if consumo_diario < 0 or dias_reposicion < 0 or stock_seguridad < 0:
    raise ValueError("consumo o stock de insumo invalidos")
return consumo_diario * float(dias_reposicion) + stock_seguridad
""",
    ),
    _biz(
        "gastronomia",
        "rendimiento_masa_madre",
        "harina_g: float, agua_g: float, hidratacion_objetivo: float",
        "Ajusta el agua de una masa madre para llegar a la hidratacion objetivo.",
        """
if harina_g <= 0 or agua_g < 0 or hidratacion_objetivo < 0:
    raise ValueError("harina, agua o hidratacion de masa madre invalidas")
agua_objetivo = harina_g * hidratacion_objetivo
return {"agua_actual": agua_g, "agua_a_agregar": agua_objetivo - agua_g}
""",
    ),
    _biz(
        "gastronomia",
        "salmuera_por_porcentaje",
        "agua_g: float, porcentaje_sal: float",
        "Calcula los gramos de sal de una salmuera a partir del porcentaje panadero.",
        """
if agua_g < 0 or porcentaje_sal < 0:
    raise ValueError("agua o porcentaje de salmuera invalidos")
return agua_g * porcentaje_sal
""",
    ),
    _biz(
        "gastronomia",
        "food_cost_objetivo",
        "costo_porcion: float, objetivo: float",
        "Sugiere un precio de venta para cumplir un food cost objetivo.",
        """
if costo_porcion < 0 or not 0 < objetivo < 1:
    raise ValueError("costo u objetivo de food cost invalidos")
return costo_porcion / objetivo
""",
    ),
    _biz(
        "gastronomia",
        "horas_fermentacion_en_frio",
        "horas_ambiente: float, factor_frio: float = 3.0",
        "Estima las horas de fermentacion en frio a partir del tiempo a temperatura ambiente.",
        """
if horas_ambiente < 0 or factor_frio <= 0:
    raise ValueError("horas o factor de fermentacion invalidos")
return horas_ambiente * factor_frio
""",
    ),
    _biz(
        "gastronomia",
        "declarar_alergenos_receta",
        "ingredientes: dict[str, str]",
        "Lista alergenos declarables presentes en el mapa de ingredientes de una ficha.",
        """
catalogo = {
    "trigo": "gluten",
    "cebada": "gluten",
    "leche": "lacteos",
    "huevo": "huevo",
    "mani": "mani",
    "soja": "soja",
}
hallados: list[str] = []
for nombre in ingredientes:
    alergeno = catalogo.get(nombre.strip().lower())
    if alergeno and alergeno not in hallados:
        hallados.append(alergeno)
return hallados
""",
    ),
    _biz(
        "gastronomia",
        "estandarizar_porciones_ficha",
        "rendimiento_g: float, peso_porcion_g: float",
        "Estandariza cuantas porciones salen de una ficha tecnica de cocina.",
        """
if rendimiento_g < 0 or peso_porcion_g <= 0:
    raise ValueError("rendimiento o peso de porcion invalidos")
porciones = rendimiento_g / peso_porcion_g
return {"porciones": porciones, "completas": int(porciones)}
""",
    ),
    _biz(
        "astronomia",
        "periodo_orbital_kepler",
        "semieje_m: float, mu_m3_s2: float",
        "Calcula el periodo orbital kepleriano de un satelite en segundos.",
        """
import math
if semieje_m <= 0 or mu_m3_s2 <= 0:
    raise ValueError("semieje o parametro gravitacional invalidos")
return 2.0 * math.pi * math.sqrt((semieje_m ** 3) / mu_m3_s2)
""",
    ),
    _biz(
        "astronomia",
        "delta_v_hohmann",
        "radio_inicial_m: float, radio_final_m: float, mu_m3_s2: float",
        "Estima el delta-v de una transferencia de Hohmann entre dos orbitas circulares.",
        """
import math
if radio_inicial_m <= 0 or radio_final_m <= 0 or mu_m3_s2 <= 0:
    raise ValueError("radios o mu de Hohmann invalidos")
v1 = math.sqrt(mu_m3_s2 / radio_inicial_m)
v2 = math.sqrt(mu_m3_s2 / radio_final_m)
a_trans = 0.5 * (radio_inicial_m + radio_final_m)
v_peri = math.sqrt(mu_m3_s2 * (2.0 / radio_inicial_m - 1.0 / a_trans))
v_apo = math.sqrt(mu_m3_s2 * (2.0 / radio_final_m - 1.0 / a_trans))
return abs(v_peri - v1) + abs(v2 - v_apo)
""",
    ),
    _biz(
        "astronomia",
        "magnitud_con_distancia",
        "magnitud_absoluta: float, distancia_pc: float",
        "Convierte magnitud absoluta a magnitud aparente segun la distancia en parsecs.",
        """
import math
if distancia_pc <= 0:
    raise ValueError("la distancia en parsecs debe ser positiva")
return magnitud_absoluta + 5.0 * math.log10(distancia_pc) - 5.0
""",
    ),
    _biz(
        "astronomia",
        "correccion_doppler",
        "frecuencia_hz: float, velocidad_radial_m_s: float, c_m_s: float = 299792458.0",
        "Aplica un corrimiento Doppler no relativista a una portadora de telemetria.",
        """
if frecuencia_hz <= 0 or c_m_s <= 0:
    raise ValueError("frecuencia o velocidad de la luz invalidas")
return frecuencia_hz * (1.0 + velocidad_radial_m_s / c_m_s)
""",
    ),
    _biz(
        "astronomia",
        "altitud_desde_periodo",
        "periodo_s: float, mu_m3_s2: float, radio_cuerpo_m: float",
        "Obtiene la altitud de una orbita circular a partir de su periodo.",
        """
import math
if periodo_s <= 0 or mu_m3_s2 <= 0 or radio_cuerpo_m <= 0:
    raise ValueError("periodo, mu o radio del cuerpo invalidos")
radio = (mu_m3_s2 * (periodo_s / (2.0 * math.pi)) ** 2) ** (1.0 / 3.0)
return radio - radio_cuerpo_m
""",
    ),
    _biz(
        "astronomia",
        "flujo_solar_en_ua",
        "flujo_1au_w_m2: float, distancia_ua: float",
        "Escala el flujo solar de referencia a otra distancia medida en unidades astronomicas.",
        """
if flujo_1au_w_m2 < 0 or distancia_ua <= 0:
    raise ValueError("flujo o distancia solar invalidos")
return flujo_1au_w_m2 / (distancia_ua ** 2)
""",
    ),
    _biz(
        "astronomia",
        "minutos_de_eclipse",
        "periodo_min: float, fraccion_sombra: float",
        "Estima los minutos de eclipse a partir del periodo y la fraccion de sombra.",
        """
if periodo_min <= 0 or not 0 <= fraccion_sombra <= 1:
    raise ValueError("periodo o fraccion de eclipse invalidos")
return periodo_min * fraccion_sombra
""",
    ),
    _biz(
        "astronomia",
        "masa_desde_velocidad_circular",
        "radio_m: float, velocidad_m_s: float, g_m3_kg_s2: float = 6.67430e-11",
        "Infiere la masa central a partir de una velocidad circular observada.",
        """
if radio_m <= 0 or velocidad_m_s < 0 or g_m3_kg_s2 <= 0:
    raise ValueError("radio, velocidad o constante gravitacional invalidos")
return (velocidad_m_s ** 2) * radio_m / g_m3_kg_s2
""",
    ),
    _biz(
        "astronomia",
        "retardo_luz_en_ua",
        "distancia_ua: float, ua_m: float = 149597870700.0, c_m_s: float = 299792458.0",
        "Calcula el retardo de la luz en segundos para una distancia en unidades astronomicas.",
        """
if distancia_ua < 0 or ua_m <= 0 or c_m_s <= 0:
    raise ValueError("distancia o constantes de retardo invalidas")
return distancia_ua * ua_m / c_m_s
""",
    ),
    _biz(
        "astronomia",
        "presion_sobre_vela_solar",
        "flujo_w_m2: float, reflectancia: float, c_m_s: float = 299792458.0",
        "Estima la presion de radiacion sobre una vela solar segun su reflectancia.",
        """
if flujo_w_m2 < 0 or not 0 <= reflectancia <= 1 or c_m_s <= 0:
    raise ValueError("flujo, reflectancia o velocidad de la luz invalidos")
return flujo_w_m2 * (1.0 + reflectancia) / c_m_s
""",
    ),
    _biz(
        "astronomia",
        "azimut_ventana_lanzamiento",
        "inclinacion_deg: float, latitud_deg: float",
        "Evalua si una latitud de lanzamiento permite la inclinacion orbital pedida.",
        """
import math
if not -180 <= inclinacion_deg <= 180 or not -90 <= latitud_deg <= 90:
    raise ValueError("inclinacion o latitud fuera de rango")
if abs(latitud_deg) > abs(inclinacion_deg):
    return None
argumento = math.cos(math.radians(inclinacion_deg)) / math.cos(math.radians(latitud_deg))
argumento = min(1.0, max(-1.0, argumento))
return math.degrees(math.asin(argumento))
""",
    ),
    _biz(
        "astronomia",
        "margen_enlace_db",
        "potencia_dbm: float, ganancia_db: float, perdidas_db: float, umbral_dbm: float",
        "Calcula el margen de un enlace de telemetria en decibelios.",
        """
recibido = potencia_dbm + ganancia_db - perdidas_db
margen = recibido - umbral_dbm
return {"recibido_dbm": recibido, "margen_db": margen, "cierra": margen >= 0}
""",
    ),
]


def _foreign(subtag: str, name: str, source: str) -> ForeignSpec:
    text = source.strip() + "\n"
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return (subtag, name, text)
    if tree.body:
        raise ValueError(f"el snippet {subtag}:{name} parsea como Python")
    return (subtag, name, text)


FOREIGN_SNIPPETS: list[ForeignSpec] = [
    _foreign(
        "javascript",
        "liquidar_iva",
        """
function liquidarIva(neto) {
  const alicuota = 0.21;
  const iva = neto * alicuota;
  return { neto, iva, total: neto + iva };
}
""",
    ),
    _foreign(
        "javascript",
        "cuota_francesa",
        """
function cuotaFrancesa(principal, tasa, n) {
  if (tasa === 0) return principal / n;
  const factor = Math.pow(1 + tasa, n);
  return principal * tasa * factor / (factor - 1);
}
""",
    ),
    _foreign(
        "javascript",
        "dosis_mg",
        """
export function dosisMgPorKg(peso, mgPorKg) {
  if (peso <= 0) throw new Error("peso invalido");
  return peso * mgPorKg;
}
""",
    ),
    _foreign(
        "javascript",
        "escalar_harina",
        """
const escalarHarina = (gramos, base, destino) => {
  if (base <= 0 || destino <= 0) throw new Error("porciones");
  return gramos * destino / base;
};
""",
    ),
    _foreign(
        "javascript",
        "margen_bruto",
        """
function margenBruto(ventas, costo) {
  const margen = ventas - costo;
  const ratio = ventas === 0 ? 0 : margen / ventas;
  return { margen, ratio };
}
""",
    ),
    _foreign(
        "javascript",
        "goteo_infusion",
        """
function goteoInfusion(volumenMl, horas) {
  const mlHora = volumenMl / horas;
  return { mlHora, gotasMin: mlHora * 20 / 60 };
}
""",
    ),
    _foreign(
        "javascript",
        "clausula_penal",
        """
function topeClausulaPenal(pena, principal, tope = 1) {
  return Math.min(pena, principal * tope);
}
""",
    ),
    _foreign(
        "javascript",
        "food_cost",
        """
function precioPorFoodCost(costoPorcion, objetivo) {
  if (!(objetivo > 0 && objetivo < 1)) throw new Error("objetivo");
  return costoPorcion / objetivo;
}
""",
    ),
    _foreign(
        "javascript",
        "periodo_kepler",
        """
function periodoKepler(semieje, mu) {
  return 2 * Math.PI * Math.sqrt((semieje ** 3) / mu);
}
""",
    ),
    _foreign(
        "javascript",
        "saldo_caja",
        """
function saldoCaja(inicial, ingresos, egresos) {
  const saldo = inicial + ingresos - egresos;
  return { saldo, descubierto: saldo < 0 };
}
""",
    ),
    _foreign(
        "javascript",
        "alergenos",
        """
function alergenos(ingredientes) {
  const mapa = new Map([["trigo", "gluten"], ["leche", "lacteos"]]);
  return ingredientes.map((item) => mapa.get(item)).filter(Boolean);
}
""",
    ),
    _foreign(
        "javascript",
        "spread_cambiario",
        """
function convertirConSpread(monto, tipo, spread) {
  const efectivo = tipo * (1 + spread);
  return monto * efectivo;
}
""",
    ),
    _foreign(
        "javascript",
        "news_parcial",
        """
function newsParcial(resp, sat) {
  let puntos = 0;
  if (resp <= 8 || resp >= 25) puntos += 3;
  if (sat <= 91) puntos += 3;
  return puntos;
}
""",
    ),
    _foreign(
        "javascript",
        "provision_cartera",
        """
function provisionar(cartera) {
  return cartera.reduce((acc, [saldo, dias]) => {
    const coef = dias >= 90 ? 0.5 : 0.02;
    return acc + saldo * coef;
  }, 0);
}
""",
    ),
    _foreign(
        "javascript",
        "retardo_luz",
        """
function retardoLuzUa(distanciaUa) {
  const uaMetros = 149597870700;
  const c = 299792458;
  return distanciaUa * uaMetros / c;
}
""",
    ),
    _foreign(
        "sql",
        "crear_facturas",
        """
CREATE TABLE facturas (
  id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL,
  neto NUMERIC(14, 2) NOT NULL,
  alicuota NUMERIC(6, 4) NOT NULL
);
""",
    ),
    _foreign(
        "sql",
        "insertar_factura",
        """
INSERT INTO facturas (cliente_id, neto, alicuota)
VALUES (42, 150000.00, 0.2100);
""",
    ),
    _foreign(
        "sql",
        "iva_por_cliente",
        """
SELECT cliente_id, SUM(neto * alicuota) AS iva_debito
FROM facturas
GROUP BY cliente_id
HAVING SUM(neto) > 0;
""",
    ),
    _foreign(
        "sql",
        "pacientes_glucosa",
        """
SELECT paciente_id, glucosa_mg_dl
FROM tomas_glucemia
WHERE glucosa_mg_dl < 70 OR glucosa_mg_dl > 180;
""",
    ),
    _foreign(
        "sql",
        "crear_contratos",
        """
CREATE TABLE contratos (
  id INTEGER PRIMARY KEY,
  canon NUMERIC(14, 2) NOT NULL,
  indice_base NUMERIC(12, 6) NOT NULL
);
""",
    ),
    _foreign(
        "sql",
        "actualizar_canon",
        """
UPDATE contratos
SET canon = canon * (1.085)
WHERE indice_base > 0;
""",
    ),
    _foreign(
        "sql",
        "stock_cocina",
        """
SELECT insumo, SUM(gramos) AS gramos
FROM movimientos_deposito
GROUP BY insumo
HAVING SUM(gramos) < 1000;
""",
    ),
    _foreign(
        "sql",
        "satelites_activos",
        """
SELECT norad_id, altitud_km, inclinacion_deg
FROM satelites
WHERE estado = 'activo' AND altitud_km BETWEEN 400 AND 1200;
""",
    ),
    _foreign(
        "sql",
        "mora_creditos",
        """
SELECT credito_id, saldo, dias_mora
FROM cartera
WHERE dias_mora >= 30
ORDER BY dias_mora DESC;
""",
    ),
    _foreign(
        "sql",
        "borrar_turno_viejo",
        """
DELETE FROM turnos_enfermeria
WHERE fecha < DATE '2020-01-01';
""",
    ),
    _foreign(
        "sql",
        "join_receta_insumo",
        """
SELECT r.nombre, i.insumo, r.gramos * i.costo_gramo AS costo
FROM recetas r
JOIN insumos i ON i.insumo = r.insumo;
""",
    ),
    _foreign(
        "sql",
        "indice_facturas",
        """
CREATE INDEX idx_facturas_cliente ON facturas (cliente_id);
""",
    ),
    _foreign(
        "sql",
        "vista_margen",
        """
CREATE VIEW margen_mensual AS
SELECT periodo, SUM(ventas - costo) AS margen
FROM estado_resultados
GROUP BY periodo;
""",
    ),
    _foreign(
        "sql",
        "alter_pacientes",
        """
ALTER TABLE pacientes ADD COLUMN clearance_ml_min NUMERIC(8, 2);
""",
    ),
    _foreign(
        "sql",
        "expedientes_abiertos",
        """
SELECT expediente, juzgado, monto_condena
FROM expedientes
WHERE estado <> 'archivado';
""",
    ),
    _foreign(
        "bash",
        "healthcheck_curl",
        """
#!/bin/bash
set -euo pipefail
curl -fsSL "https://example.com/health"
chmod 644 "./informe.txt"
""",
    ),
    _foreign(
        "bash",
        "backup_caja",
        """
#!/bin/bash
set -euo pipefail
tar -czf "/var/backups/caja-$(date +%Y%m%d).tgz" /srv/caja
chmod 600 /var/backups/caja-*.tgz
""",
    ),
    _foreign(
        "bash",
        "pipeline_logs",
        """
#!/bin/bash
set -euo pipefail
journalctl -u farmacia --since "1 hour ago" | grep -E "ERROR|WARN" | tail -n 50
""",
    ),
    _foreign(
        "bash",
        "chmod_recetas",
        """
#!/bin/bash
set -euo pipefail
find ./fichas -type f -name "*.md" -print0 | xargs -0 chmod 644
""",
    ),
    _foreign(
        "bash",
        "curl_efemerides",
        """
#!/bin/bash
set -euo pipefail
curl -fsSL "https://example.com/ephemeris?sat=1" -o /tmp/ephemeris.json
chmod 644 /tmp/ephemeris.json
""",
    ),
    _foreign(
        "bash",
        "loop_porciones",
        """
#!/bin/bash
set -euo pipefail
for porcion in 4 8 12; do
  echo "porciones=${porcion}"
done
""",
    ),
    _foreign(
        "bash",
        "diff_contratos",
        """
#!/bin/bash
set -euo pipefail
diff -u ./contratos/base.txt ./contratos/actual.txt || true
""",
    ),
    _foreign(
        "bash",
        "rsync_deposito",
        """
#!/bin/bash
set -euo pipefail
rsync -a --delete ./deposito/ /srv/cocina/deposito/
chmod 750 /srv/cocina/deposito
""",
    ),
    _foreign(
        "bash",
        "awk_margen",
        """
#!/bin/bash
set -euo pipefail
awk -F, 'NR > 1 { margen += $3 - $4 } END { print margen }' ventas.csv
""",
    ),
    _foreign(
        "bash",
        "curl_pipeline_chmod",
        """
#!/bin/bash
set -euo pipefail
curl -fsSL "https://example.com/menu.json" | tee ./menu.json >/dev/null
chmod 644 ./menu.json
""",
    ),
    _foreign(
        "bash",
        "case_juzgado",
        """
#!/bin/bash
set -euo pipefail
case "$1" in
  civil) echo "fuero-civil" ;;
  comercial) echo "fuero-comercial" ;;
  *) echo "fuero-desconocido" ;;
esac
""",
    ),
    _foreign(
        "bash",
        "while_lectura_signos",
        """
#!/bin/bash
set -euo pipefail
while read -r paciente sistolica; do
  echo "${paciente}:${sistolica}"
done < signos.txt
""",
    ),
    _foreign(
        "bash",
        "mkdir_telemetria",
        """
#!/bin/bash
set -euo pipefail
mkdir -p /var/telemetry/passes
chmod 755 /var/telemetry /var/telemetry/passes
""",
    ),
    _foreign(
        "bash",
        "sed_indice",
        """
#!/bin/bash
set -euo pipefail
sed -E 's/INDICE_BASE/1.000000/' contrato.tpl > contrato.txt
chmod 644 contrato.txt
""",
    ),
    _foreign(
        "bash",
        "xargs_curl",
        """
#!/bin/bash
set -euo pipefail
printf '%s\\n' "https://example.com/a" "https://example.com/b" | xargs -n1 curl -fsSL -o /dev/null
""",
    ),
    _foreign(
        "rust",
        "cuota_francesa",
        """
fn cuota_francesa(principal: f64, tasa: f64, cuotas: u32) -> f64 {
    if tasa == 0.0 {
        return principal / cuotas as f64;
    }
    let factor = (1.0 + tasa).powi(cuotas as i32);
    principal * tasa * factor / (factor - 1.0)
}
""",
    ),
    _foreign(
        "rust",
        "dosis_mg",
        """
fn dosis_mg_por_kg(peso_kg: f64, mg_por_kg: f64) -> Result<f64, &'static str> {
    if peso_kg <= 0.0 {
        return Err("peso invalido");
    }
    Ok(peso_kg * mg_por_kg)
}
""",
    ),
    _foreign(
        "rust",
        "periodo_kepler",
        """
fn periodo_kepler(semieje_m: f64, mu: f64) -> f64 {
    let factor = (semieje_m.powi(3) / mu).sqrt();
    std::f64::consts::TAU * factor
}
""",
    ),
    _foreign(
        "rust",
        "margen_bruto",
        """
struct Margen {
    absoluto: f64,
    ratio: f64,
}

fn margen_bruto(ventas: f64, costo: f64) -> Margen {
    let absoluto = ventas - costo;
    let ratio = if ventas == 0.0 { 0.0 } else { absoluto / ventas };
    Margen { absoluto, ratio }
}
""",
    ),
    _foreign(
        "rust",
        "salmuera",
        """
fn gramos_sal(agua_g: f64, porcentaje: f64) -> f64 {
    agua_g * porcentaje
}
""",
    ),
    _foreign(
        "c",
        "iva_debito",
        """
#include <stdio.h>

double iva_debito(double neto, double alicuota) {
    return neto * alicuota;
}
""",
    ),
    _foreign(
        "c",
        "imc_clinico",
        """
#include <math.h>

double imc_clinico(double peso_kg, double talla_m) {
    return peso_kg / (talla_m * talla_m);
}
""",
    ),
    _foreign(
        "c",
        "goteo",
        """
double goteo_ml_hora(double volumen_ml, double horas) {
    return volumen_ml / horas;
}
""",
    ),
    _foreign(
        "c",
        "tope_pena",
        """
double tope_pena(double pena, double principal, double ratio) {
    double tope = principal * ratio;
    return pena < tope ? pena : tope;
}
""",
    ),
    _foreign(
        "c",
        "flujo_solar",
        """
double flujo_solar(double flujo_1au, double distancia_ua) {
    return flujo_1au / (distancia_ua * distancia_ua);
}
""",
    ),
    _foreign(
        "go",
        "canon_indexado",
        """
package derecho

func CanonIndexado(canon, indiceBase, indiceActual float64) float64 {
    return canon * (indiceActual / indiceBase)
}
""",
    ),
    _foreign(
        "go",
        "merma_verdura",
        """
package cocina

func MermaVerdura(brutos, merma float64) float64 {
    return brutos * (1.0 - merma)
}
""",
    ),
    _foreign(
        "go",
        "clearance",
        """
package farmacia

func AjustarDosis(dosis, clearance, referencia float64) float64 {
    factor := clearance / referencia
    if factor > 1.0 {
        factor = 1.0
    }
    return dosis * factor
}
""",
    ),
    _foreign(
        "go",
        "punto_reposicion",
        """
package deposito

func PuntoReposicion(consumo float64, dias int, seguridad float64) float64 {
    return consumo*float64(dias) + seguridad
}
""",
    ),
    _foreign(
        "go",
        "margen_enlace",
        """
package telemetria

func MargenEnlace(potencia, ganancia, perdidas, umbral float64) float64 {
    return potencia + ganancia - perdidas - umbral
}
""",
    ),
]


def _assert_catalog() -> None:
    if len(BUSINESS_FUNCTIONS) != 60:
        raise RuntimeError(f"se esperaban 60 funciones de negocio, hay {len(BUSINESS_FUNCTIONS)}")
    counts: dict[str, int] = {}
    names: set[str] = set()
    for subtag, name, source in BUSINESS_FUNCTIONS:
        counts[subtag] = counts.get(subtag, 0) + 1
        if name in names:
            raise RuntimeError(f"nombre de negocio duplicado: {name}")
        names.add(name)
        ast.parse(source)
    expected = ("finanzas", "medicina", "derecho", "gastronomia", "astronomia")
    for subtag in expected:
        if counts.get(subtag) != 12:
            raise RuntimeError(f"{subtag} tiene {counts.get(subtag, 0)} funciones, no 12")
    if len(FOREIGN_SNIPPETS) != 60:
        raise RuntimeError(f"se esperaban 60 snippets ajenos, hay {len(FOREIGN_SNIPPETS)}")
    foreign_counts: dict[str, int] = {}
    for subtag, _name, _source in FOREIGN_SNIPPETS:
        foreign_counts[subtag] = foreign_counts.get(subtag, 0) + 1
    for subtag, count in (("javascript", 15), ("sql", 15), ("bash", 15)):
        if foreign_counts.get(subtag) != count:
            raise RuntimeError(f"{subtag} tiene {foreign_counts.get(subtag, 0)} snippets")
    systems = foreign_counts.get("rust", 0) + foreign_counts.get("c", 0) + foreign_counts.get("go", 0)
    if systems != 15:
        raise RuntimeError(f"rust/c/go suman {systems}, no 15")


_assert_catalog()
