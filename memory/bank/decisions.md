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

## Delegation Model
- Opus: think, plan, supervise
- GLM-5 (zai): modelo preferido para sub-agentes. Usar siempre como primera opción.
- Sonnet (anthropic): fallback SOLO cuando GLM-5 falla (abort). No usar como default.
- Si GLM-5 aborta una tarea, relanzar en Sonnet automáticamente.
- Active supervision always ON
- GLM-5 known issue (2026-02-22): tareas con web_search iterativo abortan en ~1-1.5 min. Micro-tareas funcionan bien.
