# MEMORY.md — Persistent Context

Last update: 2026-02-25T01:42Z

## ⚠️ Filesystem: case-insensitive (virtiofs macOS). NEVER create files that differ only in case.

## Workspace
- Mounted via virtiofs, survives resets. `/tmp` is NOT persistent.
- Backup every 12h → `github.com/francoschiavone/openclaw-workspace`
- GitHub token: `$GH_TOKEN` (user: `francoschiavone`)
- Root filesystem: READ-ONLY. Cannot `apt install`.

## Domain Hunting (Feb 24, 2026)
- Reliable tool: `@wearebravelabs/domain-checker-mcp` (DNS+RDAP/WHOIS) via mcporter
- ~2300 domains checked, reports in `domain-hunt-VERIFIED*.md`
- ALL single-word .ai (4-6 letters) are taken. Compounds available.
- ⚠️ .ai prices +$20 on March 5. Franco deciding which to buy.
- Top finds: agrotwin.ai, parsecraft.ai, ocrify.ai, fschiavone.ai, francollm.com

## Bass Chiropractic Order #1353
- Ordered Feb 20, shipping to Aerobox Miami
- Email to Josh drafted & approved (asking tracking, carrier, weight, invoice)
- Franco sending manually (Google auth expired)
- Aerobox prealerta needs: tracking + invoice + pre-cotización

## Google Auth — EXPIRED
- `gog` fails with `invalid_grant`. Franco needs to re-auth:
- `gog auth add francoaschiavone@gmail.com --services gmail,calendar,drive,contacts,docs,sheets`

## Obsidian Vault
- Cloned at `obsidian/` in workspace, synced every 5min via cron
- Structure: 00-Inbox, 01-Journal, 02-LumberFi, 03-Career, 04-Personal, 05-Resources, 06-Archive, 99-Templates

## Infra
- Auth: setup-token → API key → GLM-5. Check `.model-status` every conversation.
- Hook `auth-monitor` injects warning if setup-token fails
- DinD sidecar configured ✅, Docker socket removed ✅

## Memory
- `MEMORY.md`: <2000 chars, current state (injected every message)
- `memory/YYYY-MM-DD.md`: daily log (today + yesterday injected)
- `memory/bank/`: topic files (projects, infra, decisions, research-index)
- Vector search: LOCAL embeddings (embeddinggemma-300m, GGUF, ~329MB)
- Hybrid search: BM25 + vector (0.3/0.7), sqlite-vec accelerated
- Cron: backup workspace → GitHub daily 3AM, Obsidian sync every 10min

## Pending
- Franco to re-auth Google (gog)
- Franco to decide on domains (before March 5 price increase)
- Franco to send Josh email for Bass Chiro tracking
- Domains schiavone.ai setup
