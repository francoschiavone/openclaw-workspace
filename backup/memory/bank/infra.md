# Infraestructura & Config

## Container OpenClaw
- Image: `openclaw-openclaw-franco` en OrbStack (Mac Mini M4)
- Compose: `/Users/franco/projects/openclaw/docker-compose.yml`
- Filesystem root: READ-ONLY (no `apt install`)
- Workspace: virtiofs mount desde macOS → persistente, case-insensitive
- `/tmp`: writable pero NO persistente
- RAM: 8GB, Disco: 364GB overlay + 384GB workspace
- User: `node` (uid 1000), no sudo
- Node.js 22, Python 3.11, npm, pip, gcc, make, ffmpeg, git, curl, jq

## Auth Chain
1. Anthropic setup-token (subscription, gratis) — primary
2. Anthropic API key (ANTHROPIC_API_KEY) — backup, ~$10/mes cap
3. Z.ai GLM-5 (ZAI_API_KEY) — fallback si falla Anthropic
4. OpenAI Codex — REMOVIDO (sin API key)

## Monitoreo de Auth
- `.model-status` escrito por monitor del host cada 1 min
- Hook `auth-monitor` (`~/.openclaw/hooks/auth-monitor/`) — inyecta warning en bootstrap si setup-token falla
- Chequear `.model-status` al inicio de cada conversación

## Hooks Activos
- 🔑 auth-monitor — auth status injection (agent:bootstrap)
- 🚀 boot-md — BOOT.md on startup (gateway:startup)
- 📎 bootstrap-extra-files — extra workspace files (agent:bootstrap)
- 📝 command-logger — audit log (command)
- 💾 session-memory — snapshot on /new (command:new)

## Cron Jobs
- Backup workspace → GitHub cada 12hs (`workspace-backup-github`)

## GitHub
- ÚNICO repo: `francoschiavone/openclaw-workspace` (token: `$GH_TOKEN`)
- NUNCA crear repos nuevos ni gists

## Backup iCloud
- Corre diario 2AM en host, session cookies expiran ~60 días
- `.icloud-auth-date` en workspace — verificar días desde última auth

## Pendiente
- DinD sidecar para capacidad de containers de producción
- Docker socket a remover del compose
