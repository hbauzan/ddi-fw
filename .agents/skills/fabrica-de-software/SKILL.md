---
name: fabrica-de-software
description: >-
  Orquestador y daemon de fábrica de software multi-agente local. Úsalo para
  inspeccionar, validar y gobernar el estado de tareas vía TASKS.md, correr
  ciclos de observación con agent.sh y disparar notificaciones nativas de macOS
  ante cambios de estado o hitos de entrega.
argument-hint: "<validar | ejecutar ciclo | iniciar daemon | notificar>"
---

# Fábrica de Software — Skill de Orquestación Local

Skill para integrar cualquier repositorio del workspace con el orquestador local `fabrica-de-software`.

## 1. Ubicación Canónica del Orquestador

El CLI está disponible de forma global en tu entorno a través de:
```bash
/Users/hbauzan/treepwood/fabrica_de_software/agent.sh
```
El script es auto-contenido y ejecuta su propio entorno canónico con `uv` sin alterar el entorno del repo anfitrión.

---

## 2. Contrato de Tareas (`TASKS.md`)

Cualquier proyecto administrado por la fábrica debe contener un archivo `TASKS.md` en su raíz, respetando estrictamente el schema Pydantic `TaskDefinition`:

```markdown
---
task_id: "TASK-001"
status: "PENDING"
assigned_architect: "maximum-architect-agent"
protocol: "transparent-dev-protocol"
title: "Título de la Tarea en Alta Densidad"
created_at: "2026-10-31T10:00:00-03:00"
---

# TASK-XXX: Título

## 1. Objective
Descripción técnica del cambio o feature sin ambigüedad.

## 2. Invariants & Constraints
- Invariantes arquitectónicas y de concurrencia.
- Toolchain canónico del proyecto (Cargo en Rust, pnpm en Frontend, uv en Python).

## 3. Tracer Bullet Slices
- [ ] **Slice 1**: Especificación del primer slice vertical verificable.
- [ ] **Slice 2**: Segundo slice...
```

### Estados Válidos (`status`):
* `PENDING`: Tarea especificada, lista para ser tomada por un agente.
* `IN_PROGRESS`: Agente ejecutando activamente los tracer bullets.
* `BLOCKED`: Esperando resolución humana o dependencia externa.
* `DONE`: TDD completado, linters en verde y lista para entrega/approval gate.
* `FAILED`: Falla en compilación, suite roja o violación de invariante.

---

## 3. Comandos de la Fábrica

### 3.1. Validar Contrato de Tarea
Verifica que `TASKS.md` cumpla el esquema estricto (falla si el YAML está mal formado o faltan campos):
```bash
/Users/hbauzan/treepwood/fabrica_de_software/agent.sh validate --task-file TASKS.md
```

### 3.2. Ejecutar un Ciclo de Observación (Run-Once)
Lee el estado actual, emite evento de ciclo y notifica si hubo transición de estado:
```bash
/Users/hbauzan/treepwood/fabrica_de_software/agent.sh run-once --task-file TASKS.md
```

### 3.3. Disparar Notificación Nativa de macOS
Notifica al desarrollador en el Centro de Notificaciones de macOS sin bloquear el proceso.
Auto-formatea automáticamente el proyecto, ID, estado y título leyendo `TASKS.md`:
```bash
/Users/hbauzan/treepwood/fabrica_de_software/agent.sh notify --task-file TASKS.md
```
Salida generada en pantalla y macOS Notification Center:
* **Title**: `[3hm-dimentional-fw] TASK-001`
* **Subtitle**: `✅ COMPLETADO (DONE) — Tests en verde` (o `🚀 EN PROGRESO (IN_PROGRESS)`)
* **Message**: `Frontend Chat Layout Overhaul (Option A - Dense Studio)`

Opcionalmente, se pueden sobreescribir campos manualmente:
```bash
/Users/hbauzan/treepwood/fabrica_de_software/agent.sh notify \
  --title "[Proyecto] TASK-001" \
  --subtitle "✅ Listo para entrega" \
  --message "Descripción detallada del cambio"
```

### 3.4. Iniciar Daemon en Background
Inicia el loop asíncrono continuo de observación (polling de `TASKS.md` cada 2.0s):
```bash
/Users/hbauzan/treepwood/fabrica_de_software/agent.sh start --task-file TASKS.md
```

---

## 4. Invocación desde el Prompt

Para ordenar a un agente que utilice este protocolo y orquestador, invocá:

> 🇪🇸 **`Usando fabrica-de-software y transparent-dev-protocol, <qué tarea tomar o implementar>`**  
> 🇬🇧 **`Using fabrica-de-software and transparent-dev-protocol, <what task to take or implement>`**

Al invocar esto, el agente:
1. Crea o actualiza `TASKS.md` con el hito/slice correspondiente en estado `IN_PROGRESS`.
2. Valida la integridad con `/Users/hbauzan/treepwood/fabrica_de_software/agent.sh validate`.
3. Ejecuta la implementación TDD según `transparent-dev-protocol`.
4. Al dejar los tests 100% verdes, actualiza `status: "DONE"`.
5. Notifica vía `/Users/hbauzan/treepwood/fabrica_de_software/agent.sh notify`.
6. Presenta el **Approval Gate** para git commit / entrega.
