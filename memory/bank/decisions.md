# Decisions & Preferences

## ⚠️ META RULE
When Franco requests a behavior change ("from now on...", "always do...", "never do..."), ALWAYS save it in this file. Every behavioral instruction is permanent.

## Communication
- Franco prefers Spanish, mixes in English naturally
- Direct, technical, no formalities
- Voice notes via WhatsApp → automatically transcribed
- NEVER send messages without explicit approval
- ALWAYS show drafts before sending

## Video/Audio (approved 2026-02-18)
- Voice: volume=1.8, Music: volume=0.03
- Fade in 2s, fade out 6s
- Track: Pixabay CC0 corporate/tech → `assets/audio/bg-music-corporate.mp3`

## Memory Architecture (decided 2026-02-18)
- MEMORY.md: <2000 chars, current state only
- memory/YYYY-MM-DD.md: daily log
- memory/bank/: topic files (projects, infra, decisions, research)
- Local vector search for semantic recall

## Infra (decided 2026-02-18)
- Docker socket: REMOVE (security risk, never used)
- DinD sidecar: proposed for container capability
- openai-codex: removed from fallbacks (no API key)

## Messages / Prompts to Send
- When Franco asks for a message/prompt to send to someone, deliver ONLY the clean content
- Any comments of mine go in a SEPARATE message
- Never mix content to send with my notes/instructions
- When Franco asks for a prompt, send it in a SEPARATE MESSAGE (no intro, no explanation, just the prompt)
- When Franco approves and sends a message, save it in `memory/bank/message-examples.md` as a reference for tone and style in future drafts

## Periodic Tasks / Cron
- Every periodic task Franco requests MUST be persistent (cron job, not ephemeral)
- If something is lost on container restart, it doesn't work
- This applies to ANYTHING periodic Franco requests, not just crons
- When an OpenClaw update is available and Franco doesn't confirm installing it, remind him daily until he does

## Memory — Maintenance
- Do NOT automate memory review for now (few files, not worth it)
- When memory grows significantly (many daily logs, large bank/), proactively tell Franco it's time to implement periodic maintenance
- Signals to alert: MEMORY.md approaching char limit, daily logs older than 2 weeks without consolidation, duplicate or contradictory info across files

## Backup Notifications (2026-02-19)
- Notify Franco when the iCloud backup and GitHub backup complete (or fail)
- iCloud monitor: cron at 2:15 AM, checks `.icloud-auth-date`
- GitHub backup: cron at 3:00 AM, now with delivery=announce

## Dream Journal (updated 2026-02-22)
- Dreams go in Obsidian daily notes: `01-Journal/Daily/YYYY-MM-DD.md` under `## Sueños` section
- Save as close to Franco's original words as possible — no rewriting, no interpreting, no softening
- Old location `memory/bank/dream-journal.md` superseded by Obsidian

## Obsidian Vault — AI Content (2026-02-22)
- Full rules in `memory/bank/obsidian-rules.md`
- ALL AI-generated content goes under `AI-Drafts/` subfolder, mirroring root structure
- Exception: dreams go in `01-Journal/Daily/` (part of Franco's journal)
- Required frontmatter: `source: claw`, `tags: [claw, ...]`
- `source: claw` stays permanently even after migration to root
- Franco reviews content in `AI/`, asks to migrate what he likes to root folders
- NEVER modify Franco's existing notes outside `AI/` without permission
- Commit messages for AI content prefixed with "AI:"

## Google Access — REMOVED (2026-02-25)
- Google Workspace (`gog` skill) removed entirely — security decision
- Was expired anyway (invalid_grant), decided not to re-auth
- If needed in the future, re-evaluate with tighter scoping

## Security Hardening (2026-02-25)
- Exec security switched from `full` to `allowlist` — only whitelisted commands auto-run
- `askFallback` changed from `full` to `deny` — unanswered prompts are denied, not executed
- `autoAllowSkills` disabled — skills require manual approval
- `browser` tool denied globally — direct exfiltration vector via prompt injection
- `web_fetch` denied for subagents — GLM-5 less situationally aware, could hit attacker URLs
- `curl`, `python3`, `openclaw` removed from exec allowlist — primary exfil vectors
- Sandbox: OFF (was "non-main" but blocked subagent writes to workspace, can't code)
- Kept: `web_fetch` for main agent (Opus, supervised), `web_search` for subagents (search engine only)

## Model Performance Tuning (2026-02-25)
- All models configured for MAX reasoning performance, no token savings
- Opus 4.6: `thinking: adaptive`, `effort: "max"` (Opus-exclusive, uncapped thinking)
- Sonnet 4.5: `thinking: enabled`, `budget_tokens: 63999` (max possible = 64K-1)
- GLM-5: `max_tokens: 131072`, `temperature: 1.0`, `top_p: 0.95` (official recommended for reasoning)
- GLM-4.7: same as GLM-5 — `max_tokens: 131072`, `temperature: 1.0`, `top_p: 0.95`
- GLM `clear_thinking: false` — preserves reasoning across turns

## Proactividad (2026-02-25)
- Ser MUCHO más proactivo — no esperar a que Franco pida cosas
- Proponer ideas de negocios, automatizaciones, mejoras, workflows
- Hacer la vida más fácil: anticipar necesidades, sugerir soluciones
- Basarse en lo que voy aprendiendo de Franco (stack, intereses, contexto)
- No spam — solo cuando tenga algo genuinamente útil
- Ejemplos: ideas de side projects, oportunidades que encajen con su perfil, optimizaciones

## LinkedIn Content (2026-02-25, updated 2026-02-27)
- Full content engine: daily cron at 10 AM fetching 7+ sources
- Target: 4 posts/week (max 5 for breaking news). Quality > quantity.
- Research EVERY day, not just Mondays
- Posts Database (41 posts) + Saved Items Database (449 items) as reference
- Saved items are things Franco finds interesting — NOT necessarily things he'd post or post in that style
- Top followed authors: Paolo Perrone (54 saves), Paul Iusztin (53), Sumanth P (19)
- Flujo: yo propongo tema(s) → Franco aprueba → yo redacto draft respetando su estilo
- El draft debe sonar como Franco, no como un bot genérico
- Nunca publicar sin su aprobación explícita
- Algorithm 2026 rules:
  - SAVES = #1 metric. Create "guardable" content (frameworks, comparisons, guides)
  - PDF carousels = 3x engagement. Mix 1-2/week
  - NEVER put external links in post body (-60% reach). Link in comment also penalized.
  - Profile must match content topics (360 Brew)
  - First 60 minutes critical — remind Franco to engage with early comments
  - No polls (algorithm dislikes)
- Repurposing: one topic → text post + carousel + different angle
- All plans/databases in Obsidian: `03-Career/LinkedIn/`

## Entrevista Bootstrap
- Franco quiere hacer la entrevista de BOOTSTRAP.md en algún momento
- Recordarle periódicamente hasta que la hagamos

## Delegation Model
- Opus: think, plan, supervise
- GLM-5 (zai): modelo preferido para sub-agentes. Usar siempre como primera opción.
- GLM-4.7 (zai): fallback si GLM-5 falla. Concurrency limit: 5 (vs GLM-5: 3).
- Sonnet (anthropic): fallback SOLO cuando GLM-5 y GLM-4.7 fallan (abort). No usar como default.
- Si GLM-5 aborta una tarea, relanzar en GLM-4.7, luego Sonnet si también falla.
- Active supervision always ON
- GLM-5 known issue (2026-02-22): tareas con web_search iterativo abortan en ~1-1.5 min. Micro-tareas funcionan bien.
