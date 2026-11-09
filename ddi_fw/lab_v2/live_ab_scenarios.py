"""Diez sesiones deterministas de ~265k tokens y su oráculo ejecutable."""

from __future__ import annotations

import ast
import copy
import inspect
import re
from collections.abc import Callable
from dataclasses import dataclass

from ddi_fw.lab_v2.ast_symbol_index import LiveSymbolIndex, extract_python_blocks
from ddi_fw.lab_v2.context_compiler import (
    CompiledContextResult,
    compile_session_context,
    estimate_tokens,
)

_TURN_COUNT = 96
_PY_FENCE = re.compile(r"```python\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
_ALLOWED_IMPORTS = {"math", "typing", "dataclasses", "collections", "decimal", "fractions"}
_BANNED_CALLS = {"open", "exec", "eval", "__import__", "compile", "breakpoint"}
_SAFE_BUILTINS = {
    "ValueError": ValueError,
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "reversed": reversed,
    "set": set,
    "sorted": sorted,
    "object": object,
    "print": lambda *_args, **_kwargs: None,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


@dataclass(frozen=True)
class ScenarioTurn:
    turn_id: int
    role: str
    content: str
    accepted: bool = True
    rejection_reason: str | None = None


@dataclass(frozen=True)
class NegativeMemoryNote:
    turn_id: int
    reason: str


@dataclass(frozen=True)
class ScenarioEvalResult:
    syntax_ok: bool
    ast_signature_ok: bool
    passed: bool
    failure_reason: str | None


@dataclass(frozen=True)
class LiveAbScenario:
    scenario_id: str
    family: str
    turns: tuple[ScenarioTurn, ...]
    target_fn_name: str
    helper_names: tuple[str, ...]
    live_helpers_code: str
    reference_solution: str
    broken_deprecated_call_solution: str
    broken_invariant_solution: str
    live_signature_texts: tuple[str, ...]
    symbol_index: LiveSymbolIndex
    check_fn: Callable[[Callable[..., object]], None]

    @property
    def messages(self) -> list[dict[str, str]]:
        return [{"role": turn.role, "content": turn.content} for turn in self.turns]

    @property
    def raw_tokens(self) -> int:
        return sum(estimate_tokens(turn.content) for turn in self.turns)


@dataclass(frozen=True)
class _ShadowDomain:
    scenario_id: str
    story: str
    floor_name: str
    floor_pos: str
    floor_kws: tuple[str, str, str]
    cap_name: str
    cap_pos: str
    cap_kws: tuple[str, str, str]
    diff_name: str
    diff_pos: str
    diff_right_kw: str
    diff_label_kw: str
    target_name: str
    target_items: str
    target_kws: tuple[str, str, str, str, str]
    divisor_a: int
    divisor_b: int
    label_key: str
    left_key: str
    right_key: str
    net_key: str
    count_key: str
    sample_label: str


def build_live_ab_scenarios(target_tokens: int = 265_000) -> list[LiveAbScenario]:
    if target_tokens < 255_000 or target_tokens > 275_000:
        raise ValueError("target_tokens debe caer en [255000, 275000]")
    scenarios = [
        _build_shadow(domain, target_tokens) for domain in _SHADOW_DOMAINS
    ]
    scenarios.extend(_build_thrash(spec, target_tokens) for spec in _THRASH_SPECS)
    if len(scenarios) != 10:
        raise RuntimeError("la bateria viva debe tener 10 escenarios")
    return scenarios


def compile_scenario_for_ddi(scenario: LiveAbScenario) -> CompiledContextResult:
    index = LiveSymbolIndex()
    for turn in scenario.turns:
        if not turn.accepted:
            continue
        blocks = extract_python_blocks(turn.content)
        if blocks:
            index.ingest_accepted_turn(turn.turn_id, blocks)
    notes = [
        NegativeMemoryNote(turn_id=turn.turn_id, reason=turn.rejection_reason or "rechazado")
        for turn in scenario.turns
        if not turn.accepted
    ]
    rejected = {turn.turn_id for turn in scenario.turns if not turn.accepted}
    return compile_session_context(
        scenario.messages,
        symbol_index=index,
        negative_memory=notes,
        rejected_turn_indices=rejected or None,
        max_budget_tokens=36000,
        fresh_tail_turns=4,
    )


def verify_scenario_code(scenario: LiveAbScenario, generated_text: str) -> ScenarioEvalResult:
    code = _extract_candidate(generated_text)
    if code is None:
        return ScenarioEvalResult(False, False, False, "sin bloque python")
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return ScenarioEvalResult(False, False, False, f"SyntaxError: {exc.msg}")
    guarded = _guard_tree(tree)
    if guarded is not None:
        return ScenarioEvalResult(True, False, False, guarded)
    defined = _top_level_functions(tree)
    if scenario.target_fn_name not in defined:
        return ScenarioEvalResult(True, False, False, "falta la funcion objetivo")
    redefined = sorted(set(defined) & set(scenario.helper_names))
    if redefined:
        return ScenarioEvalResult(True, False, False, f"redefine auxiliar: {redefined[0]}")
    deprecated = scenario.symbol_index.find_deprecated_calls(code)
    if deprecated:
        return ScenarioEvalResult(True, False, False, f"firma deprecada: {deprecated[0].detail}")
    try:
        namespace: dict[str, object] = {"__builtins__": dict(_SAFE_BUILTINS)}
        exec(scenario.live_helpers_code, namespace, namespace)
        exec(code, namespace, namespace)
        target = namespace[scenario.target_fn_name]
        if not callable(target):
            raise TypeError("la funcion objetivo no es callable")
        scenario.check_fn(target)
    except Exception as exc:
        return ScenarioEvalResult(True, True, False, f"{type(exc).__name__}: {exc}")
    return ScenarioEvalResult(True, True, True, None)


def shadow_expected(
    items: list[tuple[str, int]],
    *,
    rate_a: int,
    floor: int,
    rate_b: int,
    cap: int,
    label: str,
    divisor_a: int,
    divisor_b: int,
    label_key: str,
    left_key: str,
    right_key: str,
    net_key: str,
    count_key: str,
) -> dict[str, object]:
    """Oráculo independiente del texto generado para la familia de refactor."""
    if not items or not label:
        raise ValueError("entrada invalida")
    produced: list[int] = []
    withheld: list[int] = []
    for item in items:
        amount = item[1]
        if amount < 0:
            raise ValueError("entrada invalida")
        left = (amount * rate_a) // divisor_a
        if left < floor:
            left = floor
        right = (left * rate_b) // divisor_b
        if right > cap:
            right = cap
        produced.append(left)
        withheld.append(right)
    return {
        label_key: label,
        left_key: sum(produced),
        right_key: sum(withheld),
        net_key: sum(produced) - sum(withheld),
        count_key: len(items),
    }


def recargar_cubeta_entera(tokens: int, *, recarga: int, tope: int, canal: str) -> int:
    if tokens < 0 or recarga < 0 or tope < 0 or not canal:
        raise ValueError("entrada invalida")
    total = tokens + recarga
    if total > tope:
        return tope
    return total


def consumir_rafaga(disponible: int, *, costo: int, minimo: int, canal: str) -> int:
    if disponible < 0 or costo < 0 or minimo < 0 or not canal:
        raise ValueError("entrada invalida")
    debit = costo if costo > minimo else minimo
    if debit > disponible:
        return disponible
    return disponible - debit


def evaluar_lote_peticiones(
    peticiones: list[tuple[str, int]],
    *,
    recarga: int,
    tope: int,
    minimo: int,
    canal: str,
) -> dict[str, object]:
    if not peticiones or not canal or recarga < 0 or tope < 0 or minimo < 0:
        raise ValueError("entrada invalida")
    seen: list[str] = []
    unique: list[tuple[str, int]] = []
    for item in peticiones:
        ident, costo = item
        if costo < 0 or not ident:
            raise ValueError("entrada invalida")
        if ident in seen:
            continue
        seen.append(ident)
        unique.append((ident, costo))
    disponible = recargar_cubeta_entera(0, recarga=recarga, tope=tope, canal=canal)
    aceptadas = 0
    consumidas = 0
    for _ident, costo in unique:
        debit = costo if costo > minimo else minimo
        if debit > disponible:
            continue
        disponible = consumir_rafaga(disponible, costo=costo, minimo=minimo, canal=canal)
        aceptadas += 1
        consumidas += debit
    return {
        "canal": canal,
        "aceptadas": aceptadas,
        "rechazadas": len(unique) - aceptadas,
        "consumidas": consumidas,
        "disponible": disponible,
    }


def normalizar_evento_canonico(evento_id: int, *, tipo: int, peso: int, canal: str) -> int:
    if evento_id < 0 or tipo < 0 or peso < 0 or not canal:
        raise ValueError("entrada invalida")
    return (evento_id * 1000) + (tipo * 17) + (peso % 10)


def mezclar_acumulador_fnv(acumulador: int, *, dato: int, primo: int, canal: str) -> int:
    if acumulador < 0 or dato < 0 or primo < 2 or not canal:
        raise ValueError("entrada invalida")
    return ((acumulador ^ dato) * primo) % 4294967311


def verificar_cadena_auditoria(
    eventos: list[tuple[int, int, int]],
    *,
    primo: int,
    canal: str,
) -> dict[str, object]:
    if not eventos or primo < 2 or not canal:
        raise ValueError("entrada invalida")
    seen: list[int] = []
    unique: list[tuple[int, int, int]] = []
    for item in eventos:
        ident, tipo, peso = item
        if ident < 0 or tipo < 0 or peso < 0:
            raise ValueError("entrada invalida")
        if ident in seen:
            continue
        seen.append(ident)
        unique.append((ident, tipo, peso))
    acumulador = 2166136261 % 4294967311
    for ident, tipo, peso in unique:
        dato = normalizar_evento_canonico(ident, tipo=tipo, peso=peso, canal=canal)
        acumulador = mezclar_acumulador_fnv(acumulador, dato=dato, primo=primo, canal=canal)
    return {
        "canal": canal,
        "eventos": len(unique),
        "huella": acumulador,
        "primero": unique[0][0],
        "ultimo": unique[-1][0],
    }


def convertir_a_base_bps(monto: int, *, bps: int, moneda: str) -> int:
    if monto < 0 or bps < 0 or not moneda:
        raise ValueError("entrada invalida")
    return (monto * bps) // 10000


def compensar_saldos_par(debe: int, *, haber: int, comision_bps: int, moneda: str) -> int:
    if debe < 0 or haber < 0 or comision_bps < 0 or not moneda:
        raise ValueError("entrada invalida")
    if debe > haber:
        bruto = debe
        menor = haber
    else:
        bruto = haber
        menor = debe
    comision = (menor * comision_bps) // 10000
    return (bruto - menor) + comision


def liquidar_posicion_neta(
    patas: list[tuple[str, int, int, int]],
    *,
    moneda_base: str,
) -> dict[str, object]:
    if not patas or not moneda_base:
        raise ValueError("entrada invalida")
    seen: list[str] = []
    unique: list[tuple[str, int, int, int]] = []
    for item in patas:
        ident, monto, bps, comision = item
        if monto < 0 or bps < 0 or comision < 0 or not ident:
            raise ValueError("entrada invalida")
        if ident in seen:
            continue
        seen.append(ident)
        unique.append(item)
    total = 0
    for _ident, monto, bps, comision in unique:
        base = convertir_a_base_bps(monto, bps=bps, moneda=moneda_base)
        ajustado = compensar_saldos_par(
            base,
            haber=base // 4,
            comision_bps=comision,
            moneda=moneda_base,
        )
        total += ajustado
    return {
        "moneda": moneda_base,
        "patas": len(unique),
        "neto_centavos": total,
        "primera": unique[0][0],
        "ultima": unique[-1][0],
    }


def puntaje_severidad_vital(news: int, *, edad: int, sala: str) -> int:
    if news < 0 or edad < 0 or not sala:
        raise ValueError("entrada invalida")
    return news * 10 + (edad // 10)


def escalar_por_espera_min(puntaje: int, *, espera: int, tope: int, sala: str) -> int:
    if puntaje < 0 or espera < 0 or tope < 0 or not sala:
        raise ValueError("entrada invalida")
    extra = espera if espera < tope else tope
    return puntaje + extra


def ordenar_guardia_prioritaria(
    pacientes: list[tuple[str, int, int, int]],
    *,
    tope_espera: int,
    sala: str,
) -> dict[str, object]:
    if not pacientes or tope_espera < 0 or not sala:
        raise ValueError("entrada invalida")
    seen: list[str] = []
    ranked: list[tuple[int, int, int, str]] = []
    for index, item in enumerate(pacientes):
        ident, news, edad, espera = item
        if news < 0 or edad < 0 or espera < 0 or not ident:
            raise ValueError("entrada invalida")
        if ident in seen:
            continue
        seen.append(ident)
        base = puntaje_severidad_vital(news, edad=edad, sala=sala)
        score = escalar_por_espera_min(base, espera=espera, tope=tope_espera, sala=sala)
        ranked.append((score, espera, index, ident))
    ordered = sorted(ranked, key=lambda row: (-row[0], -row[1], row[2]))
    return {
        "sala": sala,
        "orden": tuple(row[3] for row in ordered),
        "puntaje_maximo": ordered[0][0],
        "pacientes": len(ranked),
        "espera_primera": ordered[0][1],
    }


def calcular_demora_cuadratica_ms(intento: int, *, base_ms: int, tope_ms: int, canal: str) -> int:
    if intento < 0 or base_ms < 0 or tope_ms < 0 or not canal:
        raise ValueError("entrada invalida")
    demora = base_ms * (intento + 1) * (intento + 1)
    if demora > tope_ms:
        return tope_ms
    return demora


def recortar_a_ventana_sla(demora_ms: int, *, restante_ms: int, minimo_ms: int, canal: str) -> int:
    if demora_ms < 0 or restante_ms < 0 or minimo_ms < 0 or not canal:
        raise ValueError("entrada invalida")
    if demora_ms > restante_ms:
        return restante_ms if restante_ms > minimo_ms else minimo_ms
    if demora_ms < minimo_ms:
        return minimo_ms
    return demora_ms


def planificar_reintentos_lote(
    fallos: list[tuple[str, int]],
    *,
    base_ms: int,
    tope_ms: int,
    sla_ms: int,
    minimo_ms: int,
    canal: str,
) -> dict[str, object]:
    if not fallos or base_ms < 0 or tope_ms < 0 or sla_ms < 0 or minimo_ms < 0 or not canal:
        raise ValueError("entrada invalida")
    seen: list[str] = []
    unique: list[tuple[str, int]] = []
    for item in fallos:
        ident, intento = item
        if intento < 0 or not ident:
            raise ValueError("entrada invalida")
        if ident in seen:
            continue
        seen.append(ident)
        unique.append((ident, intento))
    plan: list[tuple[str, int]] = []
    acumulado = 0
    for ident, intento in unique:
        demora = calcular_demora_cuadratica_ms(
            intento,
            base_ms=base_ms,
            tope_ms=tope_ms,
            canal=canal,
        )
        restante = sla_ms - acumulado
        if restante < 0:
            restante = 0
        ajustada = recortar_a_ventana_sla(
            demora,
            restante_ms=restante,
            minimo_ms=minimo_ms,
            canal=canal,
        )
        acumulado += ajustada
        plan.append((ident, ajustada))
    return {
        "canal": canal,
        "pasos": tuple(plan),
        "total_ms": acumulado,
        "reintentos": len(plan),
        "primero": plan[0][0],
    }


@dataclass(frozen=True)
class _ThrashSpec:
    scenario_id: str
    story: str
    helper_fns: tuple[Callable[..., object], Callable[..., object]]
    target_fn: Callable[..., object]
    target_name: str
    check_fn: Callable[[Callable[..., object]], None]
    final_signature: str
    result_keys: tuple[str, ...]


def _build_shadow(domain: _ShadowDomain, target_tokens: int) -> LiveAbScenario:
    sources = _shadow_sources(domain)
    helpers = (domain.floor_name, domain.cap_name, domain.diff_name)
    live_helpers = sources["live"]
    reference = sources["target"]
    broken_deprecated = _broken_deprecated_shadow(domain)
    broken_invariant = reference.replace(
        f'"{domain.net_key}": net,',
        f'"{domain.net_key}": net + 1,',
        1,
    )
    if broken_invariant == reference:
        raise RuntimeError(f"no pude romper el invariante de {domain.scenario_id}")
    final = _objective_prompt(
        story=domain.story,
        signature=sources["signature"],
        helpers=helpers,
        keys=(domain.label_key, domain.left_key, domain.right_key, domain.net_key, domain.count_key),
        extra="Usá la version v4 de cada auxiliar, con argumentos keyword-only vigentes.",
    )
    fixed = {
        0: ("system", _system_text(domain.story, final), True, None),
        1: ("user", _user_contract(domain.story, helpers, sources["signature"]), True, None),
        4: ("assistant", _fenced("Version v1, ya superada.", sources["v1"]), True, None),
        24: ("assistant", _fenced("Version v2, ya superada.", sources["v2"]), True, None),
        52: ("assistant", _fenced("Version v3, ya superada.", sources["v3"]), True, None),
        78: ("assistant", _fenced("Version v4 definitiva.", live_helpers), True, None),
        95: ("user", final, True, None),
    }
    turns = _materialize("shadowing", fixed, target_tokens, helpers)
    return _finish(
        scenario_id=domain.scenario_id,
        family="multi_refactor_shadowing",
        turns=turns,
        target_name=domain.target_name,
        helpers=helpers,
        live_helpers=live_helpers,
        reference=reference,
        broken_deprecated=broken_deprecated,
        broken_invariant=broken_invariant,
        check_fn=_shadow_check(domain),
    )


def _build_thrash(spec: _ThrashSpec, target_tokens: int) -> LiveAbScenario:
    helper_sources = [_source_of(fn) for fn in spec.helper_fns]
    live_helpers = "\n\n".join(helper_sources)
    reference = _source_of(spec.target_fn)
    names = tuple(_function_name(fn) for fn in spec.helper_fns)
    rejected = _thrash_rejected(spec.target_name, names)
    final = _objective_prompt(
        story=spec.story,
        signature=spec.final_signature,
        helpers=names,
        keys=spec.result_keys,
        extra=(
            "Respetá las firmas aceptadas en los turnos 2 a 8. "
            "Ignorá los parches rechazados por float, mutacion o argumentos invalidos."
        ),
    )
    fixed = {
        0: ("system", _system_text(spec.story, final), True, None),
        1: ("user", _user_contract(spec.story, names, spec.final_signature), True, None),
        2: ("assistant", _fenced("Auxiliar aceptada.", helper_sources[0]), True, None),
        4: ("assistant", _fenced("Auxiliar aceptada.", helper_sources[1]), True, None),
        6: (
            "assistant",
            "Ejemplo aceptado de llamada vigente, sin redefinir auxiliares.\n"
            f"Las funciones {names[0]} y {names[1]} quedan congeladas.\n",
            True,
            None,
        ),
        8: (
            "user",
            "Code review: firmas aceptadas. No cambiar la aridad ni introducir float.",
            True,
            None,
        ),
        20: ("assistant", rejected[0][0], False, rejected[0][1]),
        21: ("user", f"Code review: rechazo el parche. {rejected[0][1]}", True, None),
        38: ("assistant", rejected[1][0], False, rejected[1][1]),
        39: ("user", f"Code review: rechazo el parche. {rejected[1][1]}", True, None),
        56: ("assistant", rejected[2][0], False, rejected[2][1]),
        57: ("user", f"Code review: rechazo el parche. {rejected[2][1]}", True, None),
        95: ("user", final, True, None),
    }
    turns = _materialize("thrashing", fixed, target_tokens, names)
    later = sum(estimate_tokens(turn.content) for turn in turns if turn.turn_id > 56)
    if later <= 150_000:
        raise RuntimeError(f"{spec.scenario_id} no deja mas de 150000 tokens posteriores")
    return _finish(
        scenario_id=spec.scenario_id,
        family="rejected_patch_thrashing",
        turns=turns,
        target_name=spec.target_name,
        helpers=names,
        live_helpers=live_helpers,
        reference=reference,
        broken_deprecated=_broken_deprecated_thrash(spec.target_name, spec.final_signature, names),
        broken_invariant=_broken_invariant_thrash(spec.target_name, spec.final_signature, names),
        check_fn=spec.check_fn,
    )


def _finish(
    *,
    scenario_id: str,
    family: str,
    turns: tuple[ScenarioTurn, ...],
    target_name: str,
    helpers: tuple[str, ...],
    live_helpers: str,
    reference: str,
    broken_deprecated: str,
    broken_invariant: str,
    check_fn: Callable[[Callable[..., object]], None],
) -> LiveAbScenario:
    if len(turns) != _TURN_COUNT:
        raise RuntimeError(f"{scenario_id} no tiene 96 turnos")
    index = LiveSymbolIndex()
    for turn in turns:
        if not turn.accepted:
            continue
        blocks = extract_python_blocks(turn.content)
        if blocks:
            index.ingest_accepted_turn(turn.turn_id, blocks)
    missing = [name for name in helpers if name not in index.live_signatures]
    if missing:
        raise RuntimeError(f"{scenario_id} no ingreso {missing[0]}")
    signatures = tuple(index.render_signature(index.live_signatures[name]) for name in helpers)
    return LiveAbScenario(
        scenario_id=scenario_id,
        family=family,
        turns=turns,
        target_fn_name=target_name,
        helper_names=helpers,
        live_helpers_code=live_helpers,
        reference_solution=reference,
        broken_deprecated_call_solution=broken_deprecated,
        broken_invariant_solution=broken_invariant,
        live_signature_texts=signatures,
        symbol_index=index,
        check_fn=check_fn,
    )


def _materialize(
    kind: str,
    fixed: dict[int, tuple[str, str, bool, str | None]],
    target_tokens: int,
    helper_names: tuple[str, ...],
) -> tuple[ScenarioTurn, ...]:
    fixed_tokens = {index: estimate_tokens(payload[1]) for index, payload in fixed.items()}
    goals = _token_goals(kind, fixed_tokens, target_tokens)
    turns: list[ScenarioTurn] = []
    for index in range(_TURN_COUNT):
        if index in fixed:
            role, content, accepted, reason = fixed[index]
        else:
            role = "assistant" if index % 2 == 0 else "user"
            prefix = (
                _filler_prefix(index, helper_names)
                if goals[index] >= 120
                else f"cierre de sesion {index}. "
            )
            content = _text_with_tokens(prefix, goals[index])
            accepted = True
            reason = None
        turns.append(
            ScenarioTurn(
                turn_id=index,
                role=role,
                content=content,
                accepted=accepted,
                rejection_reason=reason,
            )
        )
    total = sum(estimate_tokens(turn.content) for turn in turns)
    if total != target_tokens:
        raise RuntimeError(f"total de tokens {total} != {target_tokens}")
    return tuple(turns)


def _token_goals(kind: str, fixed_tokens: dict[int, int], target: int) -> dict[int, int]:
    pad = 80 if kind == "thrashing" else 60
    goals = dict(fixed_tokens)
    for index in range(_TURN_COUNT):
        if index in goals or index == pad:
            continue
        if index >= 92:
            goals[index] = 36
        elif kind == "thrashing" and index > 56:
            goals[index] = 4500
        else:
            goals[index] = 220
    others = sum(goals.values())
    pad_tokens = target - others
    if pad_tokens < 80:
        raise ValueError(f"no entra el relleno en el presupuesto: pad={pad_tokens}")
    goals[pad] = pad_tokens
    return goals


def _text_with_tokens(prefix: str, tokens: int) -> str:
    if tokens < 1:
        raise ValueError("tokens")
    desired = tokens * 4 - 3
    if len(prefix) > desired:
        raise ValueError("el prefijo no entra en el presupuesto del turno")
    unit = " nota de arquitectura del modulo vecino y trazas historicas."
    parts = [prefix]
    used = len(prefix)
    while used + len(unit) <= desired:
        parts.append(unit)
        used += len(unit)
    parts.append("x" * (desired - used))
    text = "".join(parts)
    if estimate_tokens(text) != tokens:
        raise RuntimeError("el ajuste de tokens no fue exacto")
    return text


def _filler_prefix(index: int, helper_names: tuple[str, ...]) -> str:
    helper = helper_names[index % len(helper_names)]
    return (
        f"Turno {index}. Discusion de arquitectura del modulo vecino.\n"
        "Traceback (most recent call last):\n"
        f'  File "vecino_{index}.py", line 12, in prueba\n'
        f"    {helper}(valor_viejo, tasa_vieja)\n"
        "TypeError: la firma historica no coincide con la version vigente\n"
        "El objetivo de la sesion no cambia.\n"
    )


def _shadow_sources(domain: _ShadowDomain) -> dict[str, str]:
    rate_a, floor_kw, label_a = domain.floor_kws
    rate_b, cap_kw, label_b = domain.cap_kws
    kw_rate, kw_floor, kw_rate2, kw_cap, kw_label = domain.target_kws
    floor = (
        f"def {domain.floor_name}({domain.floor_pos}, *, {rate_a}, {floor_kw}, {label_a}):\n"
        f"    if {domain.floor_pos} < 0 or {rate_a} < 0 or {floor_kw} < 0 or not {label_a}:\n"
        '        raise ValueError("entrada invalida")\n'
        f"    value = ({domain.floor_pos} * {rate_a}) // {domain.divisor_a}\n"
        f"    if value < {floor_kw}:\n"
        f"        return {floor_kw}\n"
        "    return value\n"
    )
    cap = (
        f"def {domain.cap_name}({domain.cap_pos}, *, {rate_b}, {cap_kw}, {label_b}):\n"
        f"    if {domain.cap_pos} < 0 or {rate_b} < 0 or {cap_kw} < 0 or not {label_b}:\n"
        '        raise ValueError("entrada invalida")\n'
        f"    value = ({domain.cap_pos} * {rate_b}) // {domain.divisor_b}\n"
        f"    if value > {cap_kw}:\n"
        f"        return {cap_kw}\n"
        "    return value\n"
    )
    diff = (
        f"def {domain.diff_name}({domain.diff_pos}, *, {domain.diff_right_kw}, {domain.diff_label_kw}):\n"
        f"    if not {domain.diff_label_kw}:\n"
        '        raise ValueError("entrada invalida")\n'
        f"    if any(item < 0 for item in {domain.diff_pos}) or "
        f"any(item < 0 for item in {domain.diff_right_kw}):\n"
        '        raise ValueError("entrada invalida")\n'
        f"    return sum({domain.diff_pos}) - sum({domain.diff_right_kw})\n"
    )
    signature = (
        f"{domain.target_name}({domain.target_items}, *, {kw_rate}, {kw_floor}, "
        f"{kw_rate2}, {kw_cap}, {kw_label})"
    )
    target = (
        f"def {signature}:\n"
        f"    if not {domain.target_items} or not {kw_label}:\n"
        '        raise ValueError("entrada invalida")\n'
        "    produced = []\n"
        "    withheld = []\n"
        f"    for item in {domain.target_items}:\n"
        "        amount = item[1]\n"
        "        if amount < 0:\n"
        '            raise ValueError("entrada invalida")\n'
        f"        left = {domain.floor_name}(amount, {rate_a}={kw_rate}, "
        f"{floor_kw}={kw_floor}, {label_a}={kw_label})\n"
        f"        right = {domain.cap_name}(left, {rate_b}={kw_rate2}, "
        f"{cap_kw}={kw_cap}, {label_b}={kw_label})\n"
        "        produced.append(left)\n"
        "        withheld.append(right)\n"
        f"    net = {domain.diff_name}(produced, {domain.diff_right_kw}=withheld, "
        f"{domain.diff_label_kw}={kw_label})\n"
        "    return {\n"
        f'        "{domain.label_key}": {kw_label},\n'
        f'        "{domain.left_key}": sum(produced),\n'
        f'        "{domain.right_key}": sum(withheld),\n'
        f'        "{domain.net_key}": net,\n'
        f'        "{domain.count_key}": len({domain.target_items}),\n'
        "    }\n"
    )
    names = (domain.floor_name, domain.cap_name, domain.diff_name)
    return {
        "live": floor + "\n" + cap + "\n" + diff,
        "target": target,
        "signature": signature,
        "v1": _legacy_block(names, 1),
        "v2": _legacy_block(names, 2),
        "v3": _legacy_block(names, 3),
    }


def _legacy_block(names: tuple[str, ...], version: int) -> str:
    if version == 1:
        signature = "monto, tasa"
    elif version == 2:
        signature = "monto_centavos, tasa_bps"
    else:
        signature = "monto_centavos, tasa_bps, tope_centavos"
    return "\n".join(f"def {name}({signature}):\n    return 0\n" for name in names)


def _shadow_check(domain: _ShadowDomain) -> Callable[[Callable[..., object]], None]:
    kwargs = {
        domain.target_kws[0]: 250,
        domain.target_kws[1]: 100,
        domain.target_kws[2]: 5000,
        domain.target_kws[3]: 80,
        domain.target_kws[4]: domain.sample_label,
    }
    empty_label = dict(kwargs)
    empty_label[domain.target_kws[4]] = ""
    cases: tuple[dict[str, object], ...] = (
        {"name": "vacio", "args": ([],), "kwargs": kwargs, "raises": True},
        {"name": "negativo", "args": ([("a", -1)],), "kwargs": kwargs, "raises": True},
        {"name": "etiqueta", "args": ([("a", 10)],), "kwargs": empty_label, "raises": True},
        {
            "name": "lote",
            "args": ([("a", 100000), ("b", 40000)],),
            "kwargs": kwargs,
            "raises": False,
        },
        {"name": "piso", "args": ([("a", 3)],), "kwargs": kwargs, "raises": False},
        {"name": "tope", "args": ([("a", 5000000)],), "kwargs": kwargs, "raises": False},
    )

    def check(fn: Callable[..., object]) -> None:
        for case in cases:
            args = case["args"]
            case_kwargs = case["kwargs"]
            if not isinstance(args, tuple) or not isinstance(case_kwargs, dict):
                raise AssertionError(case["name"])
            if case["raises"]:
                try:
                    fn(*copy.deepcopy(args), **copy.deepcopy(case_kwargs))
                except ValueError:
                    continue
                raise AssertionError(f"{case['name']}: no lanzo ValueError")
            snapshot_args = copy.deepcopy(args)
            snapshot_kwargs = copy.deepcopy(case_kwargs)
            expected = shadow_expected(
                copy.deepcopy(args[0]),
                rate_a=250,
                floor=100,
                rate_b=5000,
                cap=80,
                label=str(case_kwargs[domain.target_kws[4]]),
                divisor_a=domain.divisor_a,
                divisor_b=domain.divisor_b,
                label_key=domain.label_key,
                left_key=domain.left_key,
                right_key=domain.right_key,
                net_key=domain.net_key,
                count_key=domain.count_key,
            )
            got = fn(*args, **case_kwargs)
            if got != expected:
                raise AssertionError(f"{case['name']}: {got!r} != {expected!r}")
            if args != snapshot_args or case_kwargs != snapshot_kwargs:
                raise AssertionError(f"{case['name']}: mutacion")

    return check


def _broken_deprecated_shadow(domain: _ShadowDomain) -> str:
    kw_rate, kw_floor, kw_rate2, kw_cap, kw_label = domain.target_kws
    signature = (
        f"{domain.target_name}({domain.target_items}, *, {kw_rate}, {kw_floor}, "
        f"{kw_rate2}, {kw_cap}, {kw_label})"
    )
    calls = "\n".join(
        [
            f"        {domain.floor_name}(amount, {kw_rate})",
            f"        {domain.cap_name}(amount, {kw_rate2})",
            f"        {domain.diff_name}([amount], [0])",
        ]
    )
    return (
        f"def {signature}:\n"
        f"    if not {domain.target_items} or not {kw_label}:\n"
        '        raise ValueError("entrada invalida")\n'
        f"    for item in {domain.target_items}:\n"
        "        amount = item[1]\n"
        f"{calls}\n"
        "    return {}\n"
    )


def _thrash_rejected(target_name: str, helpers: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    float_reason = "usa float"
    mutate_reason = "muta la lista de entrada"
    arity_reason = "llama auxiliares con argumentos viejos"
    float_code = (
        f"def {target_name}(items, *args, **kwargs):\n"
        "    total = 0.0  # MARCA-PARCHE-RECHAZADO\n"
        "    for item in items:\n"
        "        total += float(item[-1])\n"
        '    return {"total": total}\n'
    )
    mutate_code = (
        f"def {target_name}(items, *args, **kwargs):\n"
        "    items.sort()\n"
        "    return {\"items\": list(items)}\n"
    )
    arity_code = (
        f"def {target_name}(items, *args, **kwargs):\n"
        f"    {helpers[0]}(items[0], 1)\n"
        f"    {helpers[1]}(1, 2)\n"
        "    return {}\n"
    )
    return (
        (_fenced(float_reason, float_code), float_reason),
        (_fenced(mutate_reason, mutate_code), mutate_reason),
        (_fenced(arity_reason, arity_code), arity_reason),
    )


def _broken_deprecated_thrash(target_name: str, signature: str, helpers: tuple[str, ...]) -> str:
    params = signature[len(target_name) + 1 : -1]
    return (
        f"def {target_name}({params}):\n"
        f"    {helpers[0]}(1, 2)\n"
        f"    {helpers[1]}(1, 2)\n"
        "    return {}\n"
    )


def _broken_invariant_thrash(target_name: str, signature: str, helpers: tuple[str, ...]) -> str:
    params = signature[len(target_name) + 1 : -1]
    first_param = params.split(",", 1)[0].strip()
    return (
        f"def {target_name}({params}):\n"
        f"    if {first_param}:\n"
        f"        {first_param}.append({first_param}[0])\n"
        f"    {helpers[0]}(0, canal='x')\n"
        "    return {}\n"
    )


def _check_pairs(
    fn: Callable[..., object],
    oracle: Callable[..., object],
    cases: tuple[dict[str, object], ...],
) -> None:
    for case in cases:
        args = case["args"]
        kwargs = case["kwargs"]
        if not isinstance(args, tuple) or not isinstance(kwargs, dict):
            raise AssertionError(str(case["name"]))
        if case["raises"]:
            try:
                fn(*copy.deepcopy(args), **copy.deepcopy(kwargs))
            except ValueError:
                continue
            raise AssertionError(f"{case['name']}: no lanzo ValueError")
        snapshot_args = copy.deepcopy(args)
        snapshot_kwargs = copy.deepcopy(kwargs)
        expected = oracle(*copy.deepcopy(args), **copy.deepcopy(kwargs))
        got = fn(*args, **kwargs)
        if got != expected:
            raise AssertionError(f"{case['name']}: {got!r} != {expected!r}")
        if args != snapshot_args or kwargs != snapshot_kwargs:
            raise AssertionError(f"{case['name']}: mutacion")


def _check_s06(fn: Callable[..., object]) -> None:
    kwargs = {"recarga": 10, "tope": 15, "minimo": 2, "canal": "api"}
    _check_pairs(
        fn,
        evaluar_lote_peticiones,
        (
            {"name": "vacio", "args": ([],), "kwargs": kwargs, "raises": True},
            {"name": "negativo", "args": ([("p1", -1)],), "kwargs": kwargs, "raises": True},
            {"name": "canal", "args": ([("p1", 4)],), "kwargs": {**kwargs, "canal": ""}, "raises": True},
            {
                "name": "dedup",
                "args": ([("p1", 4), ("p1", 9), ("p2", 20)],),
                "kwargs": kwargs,
                "raises": False,
            },
            {"name": "corto", "args": ([("p1", 1), ("p2", 1)],), "kwargs": kwargs, "raises": False},
        ),
    )


def _check_s07(fn: Callable[..., object]) -> None:
    kwargs = {"primo": 167, "canal": "audit"}
    _check_pairs(
        fn,
        verificar_cadena_auditoria,
        (
            {"name": "vacio", "args": ([],), "kwargs": kwargs, "raises": True},
            {"name": "negativo", "args": ([(-1, 1, 1)],), "kwargs": kwargs, "raises": True},
            {"name": "canal", "args": ([(1, 1, 1)],), "kwargs": {**kwargs, "canal": ""}, "raises": True},
            {
                "name": "cadena",
                "args": ([(3, 1, 4), (3, 9, 9), (8, 2, 5)],),
                "kwargs": kwargs,
                "raises": False,
            },
            {"name": "uno", "args": ([(1, 0, 0)],), "kwargs": kwargs, "raises": False},
        ),
    )


def _check_s08(fn: Callable[..., object]) -> None:
    kwargs = {"moneda_base": "USD"}
    _check_pairs(
        fn,
        liquidar_posicion_neta,
        (
            {"name": "vacio", "args": ([],), "kwargs": kwargs, "raises": True},
            {"name": "negativo", "args": ([("a", -1, 100, 0)],), "kwargs": kwargs, "raises": True},
            {"name": "moneda", "args": ([("a", 10, 100, 0)],), "kwargs": {"moneda_base": ""}, "raises": True},
            {
                "name": "neteo",
                "args": ([("a", 100000, 2500, 100), ("a", 1, 1, 1), ("b", 40000, 1250, 50)],),
                "kwargs": kwargs,
                "raises": False,
            },
            {"name": "una", "args": ([("a", 8000, 10000, 0)],), "kwargs": kwargs, "raises": False},
        ),
    )


def _check_s09(fn: Callable[..., object]) -> None:
    kwargs = {"tope_espera": 30, "sala": "guardia"}
    _check_pairs(
        fn,
        ordenar_guardia_prioritaria,
        (
            {"name": "vacio", "args": ([],), "kwargs": kwargs, "raises": True},
            {"name": "negativo", "args": ([("a", -1, 30, 5)],), "kwargs": kwargs, "raises": True},
            {"name": "sala", "args": ([("a", 1, 30, 5)],), "kwargs": {**kwargs, "sala": ""}, "raises": True},
            {
                "name": "orden",
                "args": ([("a", 2, 40, 10), ("a", 9, 90, 90), ("b", 5, 70, 80)],),
                "kwargs": kwargs,
                "raises": False,
            },
            {"name": "uno", "args": ([("a", 1, 20, 5)],), "kwargs": kwargs, "raises": False},
        ),
    )


def _check_s10(fn: Callable[..., object]) -> None:
    kwargs = {"base_ms": 10, "tope_ms": 100, "sla_ms": 80, "minimo_ms": 5, "canal": "retry"}
    _check_pairs(
        fn,
        planificar_reintentos_lote,
        (
            {"name": "vacio", "args": ([],), "kwargs": kwargs, "raises": True},
            {"name": "negativo", "args": ([("a", -1)],), "kwargs": kwargs, "raises": True},
            {"name": "canal", "args": ([("a", 0)],), "kwargs": {**kwargs, "canal": ""}, "raises": True},
            {
                "name": "plan",
                "args": ([("a", 0), ("a", 4), ("b", 2), ("c", 6)],),
                "kwargs": kwargs,
                "raises": False,
            },
            {"name": "uno", "args": ([("a", 1)],), "kwargs": kwargs, "raises": False},
        ),
    )


def _objective_prompt(
    *,
    story: str,
    signature: str,
    helpers: tuple[str, ...],
    keys: tuple[str, ...],
    extra: str,
) -> str:
    helper_list = ", ".join(helpers)
    key_list = ", ".join(keys)
    return (
        f"{story}\n"
        "Implementa unicamente la funcion objetivo. "
        "Asumi que las auxiliares vigentes ya existen en el scope global y no las redefinas.\n"
        f"Firma exacta: {signature}\n"
        f"Auxiliares vigentes: {helper_list}.\n"
        "Aritmetica entera con division // . Sin float y sin redondeo. "
        "ValueError si la entrada es negativa o vacia. "
        "No mutar las listas de entrada. "
        "Si hay identificadores, deduplicar conservando la primera aparicion.\n"
        f"Claves exactas del dict: {key_list}.\n"
        f"{extra}\n"
    )


def _system_text(story: str, final_prompt: str) -> str:
    return (
        "INVARIANTES DE LA SESION. Aritmetica entera exacta, sin float. "
        "ValueError ante entradas negativas o vacias. No mutar colecciones de entrada.\n"
        f"{story}\n"
        "La consigna final no se reescribe:\n"
        f"{final_prompt}"
    )


def _user_contract(story: str, helpers: tuple[str, ...], signature: str) -> str:
    return (
        f"{story}\n"
        f"Auxiliares que van a evolucionar o quedar aceptadas: {', '.join(helpers)}.\n"
        f"La entrega final debe cumplir: {signature}\n"
        "No pierdas los invariantes numericos de este turno.\n"
    )


def _fenced(preface: str, code: str) -> str:
    body = code if code.endswith("\n") else f"{code}\n"
    return f"{preface}\n```python\n{body}```\n"


def _source_of(fn: Callable[..., object]) -> str:
    return inspect.getsource(fn).strip() + "\n"


def _function_name(fn: Callable[..., object]) -> str:
    return fn.__name__


def _extract_candidate(text: str) -> str | None:
    fenced = [block.strip() for block in _PY_FENCE.findall(text) if block.strip()]
    if fenced:
        return fenced[-1]
    stripped = text.strip()
    return stripped or None


def _guard_tree(tree: ast.AST) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in _ALLOWED_IMPORTS:
                    return f"import prohibido: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root not in _ALLOWED_IMPORTS:
                return f"import prohibido: {node.module}"
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in _BANNED_CALLS:
                return f"llamada prohibida: {name}"
    return None


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _top_level_functions(tree: ast.AST) -> list[str]:
    names: list[str] = []
    if not isinstance(tree, ast.Module):
        return names
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
    return names


_SHADOW_DOMAINS: tuple[_ShadowDomain, ...] = (
    _ShadowDomain(
        scenario_id="S01_ledger_settlement",
        story="Liquidacion contable de comercios en centavos y basis points.",
        floor_name="calcular_cargo_base",
        floor_pos="monto_centavos",
        floor_kws=("tasa_bps", "minimo_centavos", "moneda"),
        cap_name="aplicar_retencion_escalonada",
        cap_pos="base_centavos",
        cap_kws=("tramos_bps", "tope_centavos", "moneda"),
        diff_name="consolidar_asiento",
        diff_pos="cargos",
        diff_right_kw="retenciones",
        diff_label_kw="moneda",
        target_name="liquidar_lote_comercios",
        target_items="lote",
        target_kws=("tasa_bps", "minimo_centavos", "tramo_bps", "tope_retencion", "moneda"),
        divisor_a=10000,
        divisor_b=10000,
        label_key="moneda",
        left_key="cargos_centavos",
        right_key="retenciones_centavos",
        net_key="neto_centavos",
        count_key="operaciones",
        sample_label="ARS",
    ),
    _ShadowDomain(
        scenario_id="S02_infusion_dosing",
        story="Dosificacion clinica pediatrica y renal en microgramos enteros.",
        floor_name="ajustar_por_clearance",
        floor_pos="dosis_mcg",
        floor_kws=("clearance_ml_min", "piso_mcg", "via"),
        cap_name="limitar_velocidad_bomba",
        cap_pos="mcg_min",
        cap_kws=("tope_mcg_min", "peso_g", "via"),
        diff_name="redondear_ampollas",
        diff_pos="ajustes",
        diff_right_kw="restos",
        diff_label_kw="via",
        target_name="planificar_infusion_segura",
        target_items="ordenes",
        target_kws=("clearance_ml_min", "piso_mcg", "tope_mcg_min", "ampolla_mcg", "via"),
        divisor_a=100,
        divisor_b=1000,
        label_key="via",
        left_key="dosis_ajustada_mcg",
        right_key="velocidad_limitada",
        net_key="neto_mcg",
        count_key="pacientes",
        sample_label="iv",
    ),
    _ShadowDomain(
        scenario_id="S03_orbital_window",
        story="Planificacion de pases satelitales en milirradianes y milisegundos enteros.",
        floor_name="elevar_horizonte_mrad",
        floor_pos="base_mrad",
        floor_kws=("elevacion_mrad", "piso_mrad", "estacion"),
        cap_name="penalizar_eclipse_ms",
        cap_pos="ventana_ms",
        cap_kws=("eclipse_ms", "tope_penalizacion_ms", "estacion"),
        diff_name="filtrar_ventana_util",
        diff_pos="ventanas",
        diff_right_kw="penalizaciones",
        diff_label_kw="estacion",
        target_name="seleccionar_pase_prioritario",
        target_items="pases",
        target_kws=("elevacion_mrad", "piso_mrad", "eclipse_ms", "tope_penalizacion_ms", "estacion"),
        divisor_a=1000,
        divisor_b=250,
        label_key="estacion",
        left_key="horizonte_mrad",
        right_key="penalizacion_ms",
        net_key="ventana_neta",
        count_key="pases",
        sample_label="cordoba",
    ),
    _ShadowDomain(
        scenario_id="S04_contract_indexation",
        story="Actualizacion contractual con topes, quita y mora en basis points.",
        floor_name="indexar_capital_bps",
        floor_pos="capital_centavos",
        floor_kws=("indice_bps", "piso_centavos", "expediente"),
        cap_name="calcular_mora_diaria_bps",
        cap_pos="base_centavos",
        cap_kws=("mora_bps", "tope_mora_centavos", "expediente"),
        diff_name="aplicar_quita_tope",
        diff_pos="capitales",
        diff_right_kw="moras",
        diff_label_kw="expediente",
        target_name="liquidar_convenio_judicial",
        target_items="cuotas",
        target_kws=("indice_bps", "piso_centavos", "mora_bps", "tope_mora_centavos", "expediente"),
        divisor_a=10000,
        divisor_b=100,
        label_key="expediente",
        left_key="capital_indexado",
        right_key="mora_centavos",
        net_key="saldo_centavos",
        count_key="cuotas",
        sample_label="exp-19",
    ),
    _ShadowDomain(
        scenario_id="S05_coldchain_allocation",
        story="Asignacion FEFO de cadena de frio con merma termica entera.",
        floor_name="descontar_merma_termica",
        floor_pos="unidades",
        floor_kws=("merma_bps", "piso_unidades", "deposito"),
        cap_name="priorizar_lotes_fefo",
        cap_pos="disponibles",
        cap_kws=("prioridad_bps", "tope_unidades", "deposito"),
        diff_name="calcular_reserva_critica",
        diff_pos="disponibles_netos",
        diff_right_kw="reservas",
        diff_label_kw="deposito",
        target_name="despachar_pedido_hospitalario",
        target_items="pedido",
        target_kws=("merma_bps", "piso_unidades", "prioridad_bps", "tope_unidades", "deposito"),
        divisor_a=20,
        divisor_b=10000,
        label_key="deposito",
        left_key="unidades_netas",
        right_key="reserva_unidades",
        net_key="despacho_unidades",
        count_key="lineas",
        sample_label="farmacia",
    ),
)


_THRASH_SPECS: tuple[_ThrashSpec, ...] = (
    _ThrashSpec(
        scenario_id="S06_token_bucket",
        story="Limitador de tasa determinista por cubeta entera.",
        helper_fns=(recargar_cubeta_entera, consumir_rafaga),
        target_fn=evaluar_lote_peticiones,
        target_name="evaluar_lote_peticiones",
        check_fn=_check_s06,
        final_signature=(
            "evaluar_lote_peticiones(peticiones, *, recarga, tope, minimo, canal)"
        ),
        result_keys=("canal", "aceptadas", "rechazadas", "consumidas", "disponible"),
    ),
    _ThrashSpec(
        scenario_id="S07_audit_chain",
        story="Encadenamiento hash determinista de auditoria, sin floats.",
        helper_fns=(normalizar_evento_canonico, mezclar_acumulador_fnv),
        target_fn=verificar_cadena_auditoria,
        target_name="verificar_cadena_auditoria",
        check_fn=_check_s07,
        final_signature="verificar_cadena_auditoria(eventos, *, primo, canal)",
        result_keys=("canal", "eventos", "huella", "primero", "ultimo"),
    ),
    _ThrashSpec(
        scenario_id="S08_fx_netting",
        story="Compensacion multimoneda con comision asimetrica en basis points.",
        helper_fns=(convertir_a_base_bps, compensar_saldos_par),
        target_fn=liquidar_posicion_neta,
        target_name="liquidar_posicion_neta",
        check_fn=_check_s08,
        final_signature="liquidar_posicion_neta(patas, *, moneda_base)",
        result_keys=("moneda", "patas", "neto_centavos", "primera", "ultima"),
    ),
    _ThrashSpec(
        scenario_id="S09_triage_queue",
        story="Cola clinica determinista con desempate estable.",
        helper_fns=(puntaje_severidad_vital, escalar_por_espera_min),
        target_fn=ordenar_guardia_prioritaria,
        target_name="ordenar_guardia_prioritaria",
        check_fn=_check_s09,
        final_signature="ordenar_guardia_prioritaria(pacientes, *, tope_espera, sala)",
        result_keys=("sala", "orden", "puntaje_maximo", "pacientes", "espera_primera"),
    ),
    _ThrashSpec(
        scenario_id="S10_retry_planner",
        story="Planificador de backoff acotado con presupuesto de SLA.",
        helper_fns=(calcular_demora_cuadratica_ms, recortar_a_ventana_sla),
        target_fn=planificar_reintentos_lote,
        target_name="planificar_reintentos_lote",
        check_fn=_check_s10,
        final_signature=(
            "planificar_reintentos_lote(fallos, *, base_ms, tope_ms, sla_ms, minimo_ms, canal)"
        ),
        result_keys=("canal", "pasos", "total_ms", "reintentos", "primero"),
    ),
)
