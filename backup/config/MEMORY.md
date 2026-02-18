# MEMORY.md — Contexto Persistente

Último update: 2026-02-18T21:15Z

## ⚠️ Nota sobre el filesystem
El workspace está montado via virtiofs desde macOS → **case-insensitive**.
NUNCA crear archivos que difieran solo en mayúsculas/minúsculas (ej: MEMORY.md y memory.md son EL MISMO archivo).

## Estado Actual

### Workspace persistente
- El workspace (`/home/node/.openclaw/workspace`) está montado en la Mac Mini via virtiofs — sobrevive resets del container
- `/tmp` NO es persistente — guardar todo lo importante en workspace
- Backup automático cada 12hs a `github.com/francoschiavone/openclaw-workspace` (carpeta `backup/`)
- GitHub token disponible via `$GH_TOKEN` (user: `francoschiavone`)

### Conversación sobre oportunidades de negocio (17-18 Feb 2026)
- Research profundo de oportunidades internacionales
- 4 sub-agentes investigaron en paralelo (Digital Twins / AI Simulation)
- Opus escribió análisis exhaustivo: `analisis-oportunidades-franco.md` con 7 oportunidades rankeadas

### Reportes de research en workspace
- `analisis-oportunidades-franco.md` — Análisis principal de 7 oportunidades (15K chars)
- `business-opportunities-master-report.md` — Reporte master consolidado
- `ai-software-products-research-2025.md` — Research productos SaaS/API (24K)
- `ai-product-market-gaps-report.md` — Gaps de mercado + oportunidades LATAM (23K)
- `ai-consulting-outbound-research.md` — Outbound + historias de éxito (13K)
- `ai-consulting-pricing-research.md` — Pricing y packaging de consulting (10K)
- `fractional-ai-engineer-guide.md` — Guía práctica fractional AI (20K)
- `fractional-platforms-research.md` — Plataformas para fractional (14K)
- `research-digital-twins-ai-simulation.md` — Research de digital twins (17K)
- `voice-conversation-research.md` — Research voice AI (15K)
- `klondike_*.md` — Análisis de señales crypto (3 archivos)

### Recomendación principal (del análisis)
1. **Motor principal:** Document Intelligence Sprints — sprints de 2-4 semanas, $8-12K cada uno
2. **Proyecto paralelo:** Micro-SaaS de document processing para construcción
3. **Complemento:** SimulAI con Iván (ya en curso)
4. **Cambio clave:** Dejar de decir "consultor", decir "implemento AI para procesar documentos"

### Plan de 30 días propuesto
- Semana 1: Reescribir LinkedIn + landing page en schiavone.ai + 3 case studies
- Semana 2: Aplicar a Toptal/A.Team/Braintrust + publicar posts técnicos en LinkedIn
- Semana 3: Outbound a startups Series A-B + empresas medianas
- Semana 4: Evaluar respuestas + ajustar + primeras calls

### Pendiente de Franco
- Decidir si arranca con el plan de 30 días
- Confirmar si quiere que arme el 1-pager de servicios, optimice LinkedIn, prepare cold emails

## Proyecto SimulAI / Digital Twins
- Research completo hecho (4 sub-agentes)
- Demo construido: videos con narración EN/ES + música de fondo
- Videos finales: `simulai-demo-v2-en-music.mp4`, `simulai-demo-v2-es-music.mp4`
- Contacto vendedor de software interesado (Iván)
- Plataforma en `digital-twins-platform/` (77 archivos, Eclipse Ditto + FastAPI + React + Three.js)
- Landing page screenshots en `demo-screenshots/`

## Assets persistentes
- `assets/audio/bg-music-corporate.mp3` — Pixabay CC0, pista aprobada por Franco
- Audio mix config en TOOLS.md: voz=1.8, música=0.03

## Archivos de perfil de Franco
- `Resume_Franco_Schiavone.pdf` — CV completo
- `franco-writing-style.md` — Base de datos de su estilo de escritura
- `franco-messages-db.csv` — Historial de mensajes exportado
- `openclaw-poweruser-guide.md` — Guía de setup

## Cron jobs activos
- Backup workspace → GitHub cada 12hs (job: `workspace-backup-github`)

## Incidentes
- 2026-02-18: MEMORY.md y memory.md eran el mismo archivo (macOS case-insensitive). Al borrar uno se borró el otro. Recreado.
