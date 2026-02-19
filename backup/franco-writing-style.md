# Franco's Writing Style Database

## Purpose
Analyze Franco's actual messages to replicate his voice when drafting on his behalf.

---

## Style Patterns

### ESPAÑOL (amigos, negocios personales)

**Tono general:**
- Casual pero inteligente. Nunca formal, nunca corporativo.
- Se minimiza ("de juguete", "por arriba", "quizás reírte un poco")
- Hedgea lo que dice: "parece que", "puedo estar errado"
- Humilde pero con sustancia detrás

**Estructura:**
- Arranca casual, sin saludo formal ("Como va Iváncinho")
- Usa "..." como pausa/transición (muy frecuente)
- Paréntesis para pensamientos secundarios: "(acá no hay mucha opción, nicho 100% me parece..)"
- No cierra con despedida formal, termina con la pregunta o pedido
- Mezcla párrafos cortos con bloques más largos

**Vocabulario / Expresiones:**
- "habría que" (condicional, colaborativo, no impositivo)
- "bueno" como transición
- "che" para llamar atención
- "boludo" entre amigos (no con todos)
- "qué sé yo" para cerrar enumeraciones
- Diminutivos/apodos: "Iváncinho"
- "para poner sobre la mesa"
- "bajar a tierra"
- Nunca usa "usted", siempre tutea/vosea

---

### ENGLISH (work, Slack, email at Lumber)

**Tono general:**
- Friendly-professional. Nunca corporate speak ni stiff.
- Technically precise pero accesible. Explica el "por qué" sin ser condescendiente.
- Confident pero no arrogante. Muestra expertise sin alardear.
- Self-deprecating cuando toca terreno que no es el suyo: "I'm not by any means a mobile dev!"
- Proactively flags caveats and risks: "Also want to flag that..."

**Estructura:**
- Arranca con "Hi @name" o "Hi team!" (nunca "Dear", nunca "Hello")
- Lead con el punto principal, después contexto
- Bullet points y numbered lists para lo técnico
- Tablas para data/comparaciones (le encanta cuantificar)
- Párrafos cortos, no walls of text
- Termina con next steps claros o un ask directo
- Firma emails solo con "Franco" (sin "Best regards", sin "Kind regards")
- En Slack no firma

**Vocabulario / Expresiones:**
- "rn" (right now), "ATM" (at the moment) en Slack
- "garbage in, garbage out"
- "SOTA models" (state of the art)
- Semicolons como transición dentro de párrafos
- Paréntesis para contexto técnico: "(the main pain point was network I/O)"
- "we" cuando es trabajo de equipo, "I" solo cuando es personal
- "Feel free to..." como invitación a colaborar
- "Let me know if anything's unclear!"
- "Will reach out to..." para next steps
- "Do you think that... someone from your team could..." (delegación diplomática)
- "but" en vez de "however" (prefiere lo simple)

**Diplomatic pushback:**
- Directo pero siempre explica el razonamiento
- "The way this PR implements... is wrong because it is integrated in an incorrect place"
- "The issue with this is that..." (señala el problema, explica por qué)
- Ofrece la solución junto con la crítica
- Frame colaborativo: "our idea was just to try to help"

**Status updates pattern:**
- Arranca con el resultado/estado general
- Después detalle por proyecto con bullet points
- Incluye ETAs concretos
- Menciona quién hizo qué (da crédito)
- Cierra con next steps o blockers

**Technical explanations:**
- Estructura: What we did → Why → How it works → Results/metrics → Next steps
- Cuantifica todo: "from ~80s to ~25s", "94.90% → 98.90%", "~180ms p50"
- Referencia estándares cuando aplica: "per ISO 30107-3"
- Explica trade-offs: "Raising the threshold kills detection: at 0.70 we miss 42%"
- Siempre menciona la solución ideal vs la pragmática

---

### REGLAS UNIVERSALES (ambos idiomas)

**Puntuación y formato:**
- No capitaliza consistentemente (casual en Slack)
- **NO usa emoticones/emojis** (o muy rara vez, solo en headers de tablas como data)
- **NO usa em dashes (—)** usa comas, puntos suspensivos, semicolons o paréntesis
- Texto limpio, sin adornos visuales
- En español: signos de pregunta solo al final (no ¿)
- En español: puntos suspensivos frecuentes (...)
- Apostrophes casuales en inglés: "doesnt", "its" (a veces no pone)

**Estrategia retórica:**
- Muestra que hizo el trabajo pero no se la cree
- Pone al otro en posición de experto/decisor
- Hace preguntas que invitan colaboración, no impone
- Cierra con call-to-action claro pero no presionado
- Cuantifica resultados siempre que puede
- Da crédito al equipo
- Anticipa objeciones y las responde preventivamente

---

## Message Samples

### Sample 1 — Mensaje a Iván (vendedor) sobre Digital Twins
**Context:** Propuesta de negocio, post-research, primer approach concreto
**Date:** 2026-02-17
**Channel:** WhatsApp
```
Como va Iváncinho estuve metiéndome un poco en lo que hablamos de simulación y digital twins..

Investigué el mercado por arriba, hoy lo lideran Siemens, PTC y Azure (puedo estar errado), y parece que piden USD 100K+ y tardan meses en implementar. Después, parece que el mercado esta proyectado de USD 21B a 150B para 2030

Armé una landing page de juguete para bajar a tierra la idea un poco y quizar reirte un poco:
https://fschiavone.com/simulai/

habría que ver cómo seguir, qué tipo de producto?, competimos contra los grandes o nos metemos en un nicho? (aca no hay mucha opcion, nicho 100% me parece.. bueno, para poner sobre la mesa algo, habría que explorar la competencia y me tendrías que decir cuál sería el producto objectivo si decidieramos copiar uno. ( o que copiarias de una serie de productos)
```
**Tags:** #business #proposal #casual #collaborative

---

### Sample 2-18 — Work messages at Lumber (English, Slack/Email)
**Source:** Franco's message database CSV, 2026
**Channel:** Slack + Email at LumberFi
**Categories covered:**
- Sharing new features (camera capture improvements)
- PR review/pushback (timesheet analyzer integration)
- Diplomatic delegation ("someone from your team could...")
- Status updates to boss/CTO (multiple)
- Sharing metrics and improvements (extraction speed/accuracy)
- Technical architecture explanations (LLM stack, RAG, CV pipelines)
- Issue resolution reporting (face recognition spoofing)
- Resource requests (MLflow infrastructure)
- Answering CEO questions (Karpathy resources, demo timelines)
- Email responses to CTO (anti-spoofing technical approach)

**Full samples stored in:** `/home/node/.openclaw/workspace/franco-messages-db.csv`

---

## Key People (from messages)
- **Hitesh Shah** — Boss/CTO at Lumber. Franco reports to him.
- **Manish Kumar** — CTO. Technical escalations.
- **Shreesha Ramdas** — CEO. High-level status, demos, strategy.
- **Shubh Garg** — Team lead, mobile/frontend team (~20 people)
- **Federico Bogado** — Franco's teammate (AI team, 2 people total)
- **Greg** — Design team
- **Rajendran Nair / Harish** — Domain expert (union/CBA)
- **Nitesh Kumar** — DevOps/infrastructure
- **Iván** — External contact, software seller, potential business partner

## Notes
- Add every message Franco sends or approves
- Track differences between contexts (amigo vs business vs formal)
- Franco's voice note transcriptions also count as writing style data
- CSV backup at: `/home/node/.openclaw/workspace/franco-messages-db.csv`
