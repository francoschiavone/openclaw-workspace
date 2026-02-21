# MEMORY.md — Persistent Context

Last update: 2026-02-18T22:50Z

## ⚠️ Filesystem: case-insensitive (virtiofs macOS). NEVER create files that differ only in case.

## Workspace
- Mounted via virtiofs, survives resets. `/tmp` is NOT persistent.
- Backup every 12h → `github.com/francoschiavone/openclaw-workspace`
- GitHub token: `$GH_TOKEN` (user: `francoschiavone`)
- Root filesystem: READ-ONLY. Cannot `apt install`.

## Research (Feb 17-18, 2026)
- 7 opportunities analyzed in `analisis-oportunidades-franco.md`
- Reports in workspace: business-opportunities, ai-products, market-gaps, consulting, fractional, digital-twins, voice-ai, klondike crypto
- Recommendation: Document Intelligence Sprints ($8-12K) + Micro-SaaS + SimulAI
- 30-day plan proposed. Pending Franco's decision.

## SimulAI
- Full demo with EN/ES videos + music
- Platform in `digital-twins-platform/` (Eclipse Ditto + FastAPI + React + Three.js)
- Contact: Iván (software salesman)

## Obsidian Vault
- Cloned at `obsidian/` in workspace, synced every 5min via cron
- Structure: 00-Inbox, 01-Journal, 02-LumberFi, 03-Career, 04-Personal, 05-Resources, 06-Archive, 99-Templates
- "Note this" → create in appropriate folder; quick capture → 00-Inbox

## Infra
- Auth: setup-token → API key → GLM-5. Check `.model-status` every conversation.
- Hook `auth-monitor` injects warning if setup-token fails
- DinD sidecar configured ✅, Docker socket removed ✅

## Memory
- `MEMORY.md`: <2000 chars, current state (injected every message)
- `memory/YYYY-MM-DD.md`: daily log (today + yesterday injected)
- `memory/bank/`: topic files (projects, infra, decisions, research-index)
- Vector search: LOCAL embeddings (embeddinggemma-300m, GGUF, ~329MB in workspace/.cache/)
- Hybrid search: BM25 + vector (0.3/0.7), sqlite-vec accelerated
- Cron: backup workspace → GitHub daily 3AM, Obsidian sync every 10min

## Pending
- Phase 3 memory: reflect jobs in heartbeats, QMD backend
- Domains schiavone.ai
