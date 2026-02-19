# MEMORY.md — Contexto Persistente

Último update: 2026-02-18T22:50Z

## ⚠️ Filesystem: case-insensitive (virtiofs macOS). NUNCA crear archivos que difieran solo en case.

## Workspace
- Montado via virtiofs, sobrevive resets. `/tmp` NO es persistente.
- Backup cada 12hs → `github.com/francoschiavone/openclaw-workspace`
- GitHub token: `$GH_TOKEN` (user: `francoschiavone`)
- Root filesystem: READ-ONLY. No puedo `apt install`.

## Research (Feb 17-18, 2026)
- 7 oportunidades analizadas en `analisis-oportunidades-franco.md`
- Reportes en workspace: business-opportunities, ai-products, market-gaps, consulting, fractional, digital-twins, voice-ai, klondike crypto
- Recomendación: Document Intelligence Sprints ($8-12K) + Micro-SaaS + SimulAI
- Plan de 30 días propuesto. Pendiente decisión de Franco.

## SimulAI
- Demo completo con videos EN/ES + música
- Plataforma en `digital-twins-platform/` (Eclipse Ditto + FastAPI + React + Three.js)
- Contacto: Iván (vendedor software)

## Infra
- Auth: setup-token → API key → GLM-5. Chequear `.model-status` cada conversación.
- Hook `auth-monitor` inyecta warning si setup-token falla
- DinD sidecar pendiente (prompt listo para Claude Code en Mac)
- Docker socket a remover

## Memoria
- `MEMORY.md`: <2000 chars, estado actual (se inyecta cada mensaje)
- `memory/YYYY-MM-DD.md`: daily log (se inyecta hoy + ayer)
- `memory/bank/`: archivos por tema (projects, infra, decisions, research-index)
- Vector search: LOCAL embeddings (embeddinggemma-300m, GGUF, ~329MB en workspace/.cache/)
- Hybrid search: BM25 + vector (0.3/0.7), sqlite-vec acelerado
- Cron: backup workspace → GitHub cada 12hs

## Pendientes
- Fase 3 memoria: reflect jobs en heartbeats, QMD backend
- DinD sidecar setup
- Dominios schiavone.ai
