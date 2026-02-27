# Infrastructure & Config

## OpenClaw Container
- Version: **2026.2.24** (updated 2026-02-25)
- Dockerfile pinned to `ghcr.io/openclaw/openclaw:2026.2.24` (`:latest` was stale)
- Image: `openclaw-openclaw-franco` on OrbStack (Mac Mini M4)
- Compose: `/Users/franco/projects/openclaw/docker-compose.yml`
- Filesystem root: READ-ONLY (no `apt install`)
- Workspace: virtiofs mount from macOS → persistent, case-insensitive
- `/tmp`: writable but NOT persistent
- RAM: 8GB, Disk: 364GB overlay + 384GB workspace
- User: `node` (uid 1000), no sudo
- Node.js 22, Python 3.11, npm, pip, gcc, make, ffmpeg, git, curl, jq

## Auth Chain
1. Anthropic setup-token (subscription, free) — primary
2. Anthropic API key (ANTHROPIC_API_KEY) — backup, ~$10/month cap
3. Z.ai GLM-5 (ZAI_API_KEY) — fallback if Anthropic fails
4. OpenAI Codex — REMOVED (no API key)

## Auth Monitoring
- `.model-status` written by host monitor every 1 min
- Hook `auth-monitor` (`~/.openclaw/hooks/auth-monitor/`) — injects warning on bootstrap if setup-token fails
- Check `.model-status` at the start of every conversation

## Active Hooks (bundled with OpenClaw)
- 🚀 boot-md — BOOT.md on startup (gateway:startup)
- 📎 bootstrap-extra-files — extra workspace files (agent:bootstrap)
- 📝 command-logger — audit log (command)
- 💾 session-memory — snapshot on /new (command:new)
- Note: auth-monitor hook was lost in v2026.2.24 update. Function covered by host-side model-monitor.sh + auth-watchdog.sh

## Cron Jobs
- GitHub workspace backup → daily 3AM (`GitHub workspace backup`)
- iCloud backup monitor → daily 2:15 AM (`iCloud backup monitor`)
- Obsidian vault sync → every 5min (`Obsidian vault sync`)
- Bass Chiropractic tracking → daily 2PM ART (job `9eaeaa4b`, isolated agentTurn)
- ⚠️ All cron jobs backed up in `cron-persistent.json` (workspace root). On restart, verify jobs exist and recreate from this file if missing.

## GitHub
- Repos: `francoschiavone/openclaw-workspace` (projects), `francoschiavone/obsidian` (vault)
- Token: `$GH_TOKEN` (fine-grained PAT)
- NEVER create new repos or gists

## iCloud Backup
- Runs daily 2AM on host, session cookies expire ~60 days
- `.icloud-auth-date` in workspace — check days since last auth

## Aerobox (Miami mailbox)
- Name: Franco Schiavone
- Address: 5459 Nw 72nd Ave, Miami, FL 33166-6219, United States
- Phone: (305) 456-6247
- Support WhatsApp: +54 9 11 5235-6174

## Exec Security
- Mode: `allowlist` — only whitelisted commands auto-execute
- Unknown commands: prompt Franco (`ask: "on-miss"`)
- If Franco doesn't respond: DENY (`askFallback: "deny"`)
- Skills: manual approval required (`autoAllowSkills: false`)
- Removed from allowlist: `curl`, `python3`, `openclaw` (exfil vectors)
- Sandbox: OFF (non-main blocked workspace writes, subagents need to code)

## Model Performance (2026-02-25)
- Opus 4.6: adaptive thinking + effort "max" (uncapped, Opus-exclusive)
- Sonnet 4.5: manual thinking, budget_tokens: 63999 (max)
- GLM-5: max_tokens: 131072, temperature: 1.0, top_p: 0.95, clear_thinking: false
- GLM-4.7: same as GLM-5, fallback for subagents (concurrency: 5 vs GLM-5: 3)
- Subagent maxConcurrent: 3 (matches GLM-5 API limit)

## Completed
- ✅ DinD sidecar configured
- ✅ Docker socket removed from compose
- ✅ Security hardening applied (2026-02-25): exec allowlist, browser denied, subagent web_fetch denied
- ✅ Model performance tuning (2026-02-25): max thinking on all models
- ✅ Updated to v2026.2.24, Dockerfile pinned

## Pending
- Domains schiavone.ai / francoschiavone.ai — setup
