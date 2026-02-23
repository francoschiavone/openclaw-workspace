# Obsidian Vault — AI Content Rules

*Decision date: 2026-02-22*
*Approved by Franco*

## Directory Structure

All AI-generated content goes under `AI-Drafts/` subdirectory in the vault, mirroring the root structure:

```
obsidian/
├── AI-Drafts/                   ← All AI-generated content lives here (pending review)
│   ├── 00-Inbox/                ← Quick captures, unsorted AI notes
│   ├── 02-LumberFi/             ← Work-related AI notes
│   ├── 03-Career/               ← Career, side projects, research
│   ├── 04-Personal/             ← Personal AI notes (purchases, etc.)
│   ├── 05-Resources/            ← Knowledge base additions
│   └── 06-Archive/              ← Archived AI content
├── 00-Inbox/                    ← Franco's inbox (DO NOT touch)
├── 01-Journal/                  ← Franco's journals
│   └── Daily/                   ← Dreams go HERE (not in AI-Drafts/)
├── 02-LumberFi/                 ← Franco's work notes
├── ...                          ← All root folders remain untouched
```

## Rules

### 1. All AI content → `AI-Drafts/` subfolder
- Every note I create goes under `AI-Drafts/` in the matching subfolder
- Example: research about business opportunities → `AI-Drafts/03-Career/Research/`
- Example: purchase tracking → `AI-Drafts/04-Personal/Compras/`
- Example: work notes → `AI-Drafts/02-LumberFi/`

### 2. Exception: Dreams → `01-Journal/Daily/`
- Dreams are part of Franco's daily journal, not AI content
- Add dreams to the daily note under a `## Sueños` section
- Daily notes live at `01-Journal/Daily/YYYY-MM-DD.md`

### 3. Required frontmatter on ALL AI-generated notes
```yaml
---
source: claw
created: YYYY-MM-DD
tags: [claw, <topic-tags>]
---
```
- `source: claw` — marks the note as AI-generated (permanent, even after migration)
- `tags` — always include `claw` + relevant topic tags
- This metadata persists even if the note is moved to root folders

### 4. Migration workflow
- Franco reviews content in `AI/` at his pace
- If he likes a note, he asks me to migrate it to the corresponding root folder
- Migration = move file from `AI-Drafts/XX-Folder/` to `XX-Folder/` (same relative path)
- The `source: claw` frontmatter stays — so it's always clear the note originated from AI
- Wikilinks and tags are preserved during migration

### 5. DO NOT modify Franco's existing notes
- Never edit files outside `AI-Drafts/` without explicit permission
- Never create files in root folders (except dreams in Daily Journal)
- The root vault structure is Franco's personal space

### 6. Naming conventions
- Use descriptive kebab-case filenames: `research-data-products-2026.md`
- No prefixes needed (the `AI/` folder already separates content)
- Use Spanish or English depending on the content language

### 7. Sync after changes
```bash
cd /home/node/.openclaw/workspace/obsidian
git pull origin main
git add .
git commit -m "AI: description of changes"
git push origin main
```
- Commit messages for AI content prefixed with "AI:" for easy filtering
