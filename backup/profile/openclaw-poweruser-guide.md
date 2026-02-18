# 🦞 OpenClaw Power User Setup Guide

*Guía para hacer la entrevista de introducción lo mejor posible.*

---

## Workspace Files Clave

| Archivo | Propósito |
|---------|-----------|
| `AGENTS.md` | Protocolo de orquestación, cuándo/cómo delegar, reglas de canales |
| `SOUL.md` | Personalidad, valores, tono, boundaries — **quién es** el AI |
| `IDENTITY.md` | Info del AI: nombre, criatura, vibe, emoji |
| `USER.md` | Info del humano: nombre, timezone, contexto, preferencias |
| `TOOLS.md` | Notas específicas del entorno (cámaras, SSH hosts, etc.) |
| `MEMORY.md` | Memoria a largo plazo: proyectos, decisiones, personas |

---

## Qué Definir en la Entrevista

### 1. Identidad del AI (IDENTITY.md)
- **Nombre** — algo que te guste, no tiene que ser genérico
- **Criatura** — ¿AI? ¿familiar? ¿ghost in the machine?
- **Vibe** — ¿sharp? ¿warm? ¿chaotic? ¿calm?
- **Emoji** — signature emoji
- **Avatar** — opcional, imagen

### 2. Personalidad (SOUL.md)
Power users recomiendan definir:
- **Valores jerárquicos** — ej: honestidad > ser servicial
- **Estilo de comunicación** — directo, técnico, sin formalidades
- **Boundaries** — qué NO hacer nunca
- **Relación** — ¿herramienta? ¿colaborador? ¿amigo?

### 3. Protocolo de Orquestación (AGENTS.md)
- Modelo principal vs sub-agentes
- Cuándo delegar vs hacer directo
- Reglas por canal (WhatsApp, Telegram)
- Reglas de seguridad

### 4. Memoria (MEMORY.md)
- Proyectos activos con estado
- Personas clave y contexto
- Decisiones importantes tomadas
- Tareas recurrentes
- Preguntas abiertas

---

## Features que Power Users Aprovechan

### Comandos de Chat
| Comando | Uso |
|---------|-----|
| `/status` | Estado de sesión (modelo, tokens, costo) |
| `/mesh <goal>` | Auto-plan + ejecutar workflow multi-step |
| `/new` o `/reset` | Reset de sesión |
| `/compact` | Compactar contexto (resumen) |
| `/think <level>` | Nivel de thinking |
| `/usage tokens` | Mostrar uso de tokens |

### Memory System
- SQLite + vector search sobre workspace Markdown y transcripts
- Embedding: OpenAI text-embedding-3-small
- Hybrid search: 70% vector similarity + 30% BM25 keyword
- Chunking: 400 tokens con 80 overlap

### Multi-Agent Routing
- Diferentes agentes para diferentes canales
- Workspace separados por contexto (work vs personal)

### Security
- DM pairing para senders desconocidos
- Sandboxing para grupos
- Tool policies por perfil (minimal, coding, messaging, full)

---

## Tips para la Entrevista

1. **No sea robótica** — es una conversación, no un cuestionario
2. **Definir valores > definir reglas** — los valores guían mejor que reglas rígidas
3. **Ser específico** — "directo, técnico, sin formalidades" > "sé nice"
4. **Incluir contexto personal** — el AI trabaja mejor cuando te conoce
5. **Definir boundaries explícitamente** — qué NO debe hacer
6. **Pensar en la relación** — ¿qué tipo de interacción querés?
7. **Guardar todo** — cada decisión en los archivos correspondientes

---

## Checklist Post-Entrevista

- [ ] IDENTITY.md — nombre, criatura, vibe, emoji del AI
- [ ] SOUL.md — personalidad, valores, boundaries
- [ ] USER.md — info completa del humano ✅ (ya hecho)
- [ ] AGENTS.md — protocolo de orquestación ✅ (ya hecho)
- [ ] TOOLS.md — notas del entorno
- [ ] MEMORY.md — crear con proyectos activos
- [ ] Borrar BOOTSTRAP.md — ya no se necesita post-entrevista
