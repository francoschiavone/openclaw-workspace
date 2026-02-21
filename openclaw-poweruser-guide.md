# 🦞 OpenClaw Power User Setup Guide

*Guide to make the introduction interview as good as possible.*

---

## Key Workspace Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Orchestration protocol, when/how to delegate, channel rules |
| `SOUL.md` | Personality, values, tone, boundaries — **who** the AI is |
| `IDENTITY.md` | AI info: name, creature, vibe, emoji |
| `USER.md` | Human info: name, timezone, context, preferences |
| `TOOLS.md` | Environment-specific notes (cameras, SSH hosts, etc.) |
| `MEMORY.md` | Long-term memory: projects, decisions, people |

---

## What to Define in the Interview

### 1. AI Identity (IDENTITY.md)
- **Name** — something you like, doesn't have to be generic
- **Creature** — AI? familiar? ghost in the machine?
- **Vibe** — sharp? warm? chaotic? calm?
- **Emoji** — signature emoji
- **Avatar** — optional, image

### 2. Personality (SOUL.md)
Power users recommend defining:
- **Hierarchical values** — e.g.: honesty > being helpful
- **Communication style** — direct, technical, no formalities
- **Boundaries** — what to NEVER do
- **Relationship** — tool? collaborator? friend?

### 3. Orchestration Protocol (AGENTS.md)
- Main model vs sub-agents
- When to delegate vs do it directly
- Per-channel rules (WhatsApp, Telegram)
- Security rules

### 4. Memory (MEMORY.md)
- Active projects with status
- Key people and context
- Important decisions made
- Recurring tasks
- Open questions

---

## Features Power Users Leverage

### Chat Commands
| Command | Use |
|---------|-----|
| `/status` | Session status (model, tokens, cost) |
| `/mesh <goal>` | Auto-plan + execute multi-step workflow |
| `/new` or `/reset` | Session reset |
| `/compact` | Compact context (summary) |
| `/think <level>` | Thinking level |
| `/usage tokens` | Show token usage |

### Memory System
- SQLite + vector search over workspace Markdown and transcripts
- Embedding: OpenAI text-embedding-3-small
- Hybrid search: 70% vector similarity + 30% BM25 keyword
- Chunking: 400 tokens with 80 overlap

### Multi-Agent Routing
- Different agents for different channels
- Separate workspaces by context (work vs personal)

### Security
- DM pairing for unknown senders
- Sandboxing for groups
- Tool policies per profile (minimal, coding, messaging, full)

---

## Interview Tips

1. **Don't be robotic** — it's a conversation, not a questionnaire
2. **Define values > define rules** — values guide better than rigid rules
3. **Be specific** — "direct, technical, no formalities" > "be nice"
4. **Include personal context** — the AI works better when it knows you
5. **Define boundaries explicitly** — what it should NOT do
6. **Think about the relationship** — what kind of interaction do you want?
7. **Save everything** — every decision in the corresponding files

---

## Post-Interview Checklist

- [ ] IDENTITY.md — AI name, creature, vibe, emoji
- [ ] SOUL.md — personality, values, boundaries
- [ ] USER.md — complete human info ✅ (already done)
- [ ] AGENTS.md — orchestration protocol ✅ (already done)
- [ ] TOOLS.md — environment notes
- [ ] MEMORY.md — create with active projects
- [ ] Delete BOOTSTRAP.md — no longer needed post-interview
