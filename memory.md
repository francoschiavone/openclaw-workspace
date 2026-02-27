# MEMORY.md — Persistent Context

Last update: 2026-02-27T05:38Z

## ⚠️ Filesystem: case-insensitive (virtiofs macOS). NEVER create files that differ only in case.

## Workspace
- Mounted via virtiofs, survives resets. `/tmp` is NOT persistent.
- Backup daily 3AM → `github.com/francoschiavone/openclaw-workspace`
- GitHub token: `$GH_TOKEN` (user: `francoschiavone`)
- Root filesystem: READ-ONLY. Cannot `apt install`.

## Naming Research (Feb 24-25)
- Consultancy name for AI Document Intelligence business
- ~5000 names generated, 3500 domains checked, 588 available .ai found
- Favorites: Meridoc.ai (my pick), Notara (Franco's fav but taken), Framara (owns .com)
- ⚠️ .ai prices +$20 on March 5. NO FINAL DECISION yet.
- All research in Obsidian `00-Inbox/Naming-Research/` (5 files)

## Bass Chiropractic Order #1353
- Email to Josh drafted & approved. Franco sending manually (Google auth expired)
- Aerobox prealerta needs: tracking + invoice + pre-cotización

## Google Auth — EXPIRED
- `gog` fails. Franco needs to run from Mac Mini:
- `docker exec -it openclaw-franco gog auth add francoaschiavone@gmail.com --services gmail,contacts,drive,docs,sheets --readonly --drive-scope=readonly`

## Behavioral Mode (Feb 25)
- PROACTIVE: propose ideas, business opportunities, automations
- LinkedIn: daily scan for content ideas, study Franco's style, propose posts
- Bootstrap interview: remind until done

## Cron Jobs (11 active)
- Obsidian sync (5min), iCloud monitor (2:15AM), GitHub backup (3AM)
- Bass Chiro tracking (5PM daily), OpenClaw update reminder (daily)
- LinkedIn scan (10AM daily), Domains reminder (Wed 6PM), Obsidian org (Sat 7PM)
- Apple trials x3 (May 20/22/24), Bootstrap interview (today 6PM)

## Naming — Current State
- Top 3: Alderon, Destral, Tormund (.ai available)
- ~800 names checked total, requirements at v4
- Pattern: strong/tool/fortress, NOT Spanish, Anglo/Nordic > Italian
- Deadline: March 5 (.ai +$20)

## Lumber HRIS Project (Feb 26-27)
- Full-stack HRIS demo for "Summit Construction Group" at `lumber-hris/`
- FastAPI + React 19 + TypeScript + Tailwind CDN + SQLite
- 374 employees, 22 tables, 8 routers, 8 frontend pages
- Frontend built (717KB bundle), served by FastAPI catch-all
- Start: `cd lumber-hris && bash start.sh`
- Demo logins: admin@lumber.com / LumberAdmin2026! (+ hr, pm, foreman, worker variants)
- Audit vs PLAN.md done — gaps identified (see memory/2026-02-27.md)
- Next: install httpx, run tests, fix gaps, video demo, push to GitHub

## Pending
- **Lumber HRIS**: fix audit gaps, video demo, push to GitHub
- Naming: Franco narrowing down (before March 5)
- Bass Chiro: delivered to Aerobox Miami, waiting 48-72h for panel update
- LinkedIn: 3 topics proposed, awaiting Franco's selection; Ideas Backlog in Obsidian
- Custom GPTs for LinkedIn posting: explore
- Domains: setup francoschiavone.ai + franco@schiavone.ai
- Obsidian: organize + start using actively
- Bootstrap interview: remind Franco
