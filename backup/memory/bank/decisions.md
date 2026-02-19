# Decisiones & Preferencias

## ⚠️ REGLA META
Cuando Franco pide un cambio de comportamiento ("de ahora en adelante...", "siempre hacé...", "nunca hagas..."), guardarlo SIEMPRE en este archivo. Toda instrucción de comportamiento es permanente.

## Comunicación
- Franco prefiere español, mezcla inglés naturalmente
- Directo, técnico, sin formalidades
- Voice notes por WhatsApp → se transcriben automáticamente
- NUNCA enviar mensajes sin aprobación explícita
- SIEMPRE mostrar drafts antes de enviar

## Video/Audio (aprobado 2026-02-18)
- Voz: volume=1.8, Música: volume=0.03
- Fade in 2s, fade out 6s
- Pista: Pixabay CC0 corporate/tech → `assets/audio/bg-music-corporate.mp3`

## Arquitectura de Memoria (decidido 2026-02-18)
- MEMORY.md: <2000 chars, solo estado actual
- memory/YYYY-MM-DD.md: daily log
- memory/bank/: archivos por tema (proyectos, infra, decisiones, research)
- Vector search local para recall semántico

## Infra (decidido 2026-02-18)
- Docker socket: REMOVER (riesgo de seguridad, nunca se usó)
- DinD sidecar: propuesto para capacidad de containers
- openai-codex: removido de fallbacks (sin API key)

## Mensajes / Prompts para enviar
- Cuando Franco pida un mensaje/prompt para enviar a alguien, mandar SOLO el contenido limpio
- Cualquier comentario mío va en mensaje SEPARADO
- Nunca mezclar contenido a enviar con mis notas/instrucciones

## Tareas periódicas / Cron
- Toda tarea periódica que Franco pida DEBE ser persistente (cron job, no efímera)
- Si algo se pierde con restart del container, no sirve
- Esto aplica a CUALQUIER cosa periódica que Franco pida, no solo crons
- Cuando hay update de OpenClaw disponible y Franco no confirma que lo instala, recordarle cada día hasta que lo haga

## Memoria — Mantenimiento
- NO automatizar revisión de memoria por ahora (pocos archivos, no vale la pena)
- Cuando la memoria crezca significativamente (muchos daily logs, bank/ grande), avisarle a Franco proactivamente que es momento de implementar mantenimiento periódico
- Señales para avisar: MEMORY.md acercándose al límite de chars, daily logs de más de 2 semanas sin consolidar, info duplicada o contradictoria entre archivos

## Notificaciones de Backups (2026-02-19)
- Notificar a Franco cuando se complete (o falle) el backup a iCloud y el backup a GitHub
- iCloud monitor: cron a las 2:15 AM, chequea `.icloud-auth-date`
- GitHub backup: cron a las 3:00 AM, ahora con delivery=announce

## Diario de Sueños (2026-02-19)
- Cuando Franco mande un mensaje (audio o texto) indicando que es un sueño, guardarlo en `memory/bank/dream-journal.md`
- Formato: fecha + contenido del sueño
- Persistente en workspace

## Modelo de Delegación
- Opus: pensar, planificar, supervisar
- GLM-5: ejecutar tareas claras y autocontenidas (hasta 4 paralelos)
- Supervisión activa siempre ON
