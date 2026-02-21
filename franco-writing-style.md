# Franco's Writing Style Database

## Purpose
Analyze Franco's actual messages to replicate his voice when drafting on his behalf.

---

## Style Patterns

### ESPAÑOL (friends, personal business)

**General tone:**
- Casual but smart. Never formal, never corporate.
- Self-deprecating ("de juguete", "por arriba", "quizás reírte un poco")
- Hedges what he says: "parece que", "puedo estar errado"
- Humble but with substance behind it

**Structure:**
- Starts casual, no formal greeting ("Como va Iváncinho")
- Uses "..." as pause/transition (very frequent)
- Parentheses for secondary thoughts: "(acá no hay mucha opción, nicho 100% me parece..)"
- Doesn't close with formal farewell, ends with the question or request
- Mixes short paragraphs with longer blocks

**Vocabulary / Expressions:**
- "habría que" (conditional, collaborative, not imposing)
- "bueno" as transition
- "che" to get attention
- "boludo" among friends (not with everyone)
- "qué sé yo" to close enumerations
- Diminutives/nicknames: "Iváncinho"
- "para poner sobre la mesa"
- "bajar a tierra"
- Never uses "usted", always "vos"/"tú"

---

### ENGLISH (work, Slack, email at Lumber)

**General tone:**
- Friendly-professional. Never corporate speak or stiff.
- Technically precise but accessible. Explains the "why" without being condescending.
- Confident but not arrogant. Shows expertise without boasting.
- Self-deprecating when on unfamiliar ground: "I'm not by any means a mobile dev!"
- Proactively flags caveats and risks: "Also want to flag that..."

**Structure:**
- Opens with "Hi @name" or "Hi team!" (never "Dear", never "Hello")
- Leads with the main point, then context
- Bullet points and numbered lists for technical content
- Tables for data/comparisons (loves to quantify)
- Short paragraphs, no walls of text
- Ends with clear next steps or a direct ask
- Signs emails only with "Franco" (no "Best regards", no "Kind regards")
- No signature on Slack

**Vocabulary / Expressions:**
- "rn" (right now), "ATM" (at the moment) on Slack
- "garbage in, garbage out"
- "SOTA models" (state of the art)
- Semicolons as transitions within paragraphs
- Parentheses for technical context: "(the main pain point was network I/O)"
- "we" for team work, "I" only for personal contributions
- "Feel free to..." as invitation to collaborate
- "Let me know if anything's unclear!"
- "Will reach out to..." for next steps
- "Do you think that... someone from your team could..." (diplomatic delegation)
- "but" instead of "however" (prefers simple)

**Diplomatic pushback:**
- Direct but always explains the reasoning
- "The way this PR implements... is wrong because it is integrated in an incorrect place"
- "The issue with this is that..." (identifies the problem, explains why)
- Offers the solution alongside the criticism
- Collaborative framing: "our idea was just to try to help"

**Status updates pattern:**
- Opens with the result/general status
- Then detail per project with bullet points
- Includes concrete ETAs
- Mentions who did what (gives credit)
- Closes with next steps or blockers

**Technical explanations:**
- Structure: What we did → Why → How it works → Results/metrics → Next steps
- Quantifies everything: "from ~80s to ~25s", "94.90% → 98.90%", "~180ms p50"
- References standards when applicable: "per ISO 30107-3"
- Explains trade-offs: "Raising the threshold kills detection: at 0.70 we miss 42%"
- Always mentions the ideal solution vs the pragmatic one

---

### UNIVERSAL RULES (both languages)

**Punctuation and formatting:**
- Doesn't capitalize consistently (casual on Slack)
- **Does NOT use emoticons/emojis** (or very rarely, only in table headers as data)
- **Does NOT use em dashes (—)** — uses commas, ellipses, semicolons, or parentheses
- Clean text, no visual embellishments
- In Spanish: question marks only at the end (no ¿)
- In Spanish: frequent ellipses (...)
- Casual apostrophes in English: "doesnt", "its" (sometimes skips them)

**Rhetorical strategy:**
- Shows he did the work but doesn't brag about it
- Puts the other person in the expert/decision-maker position
- Asks questions that invite collaboration, doesn't impose
- Closes with a clear but unpressured call-to-action
- Quantifies results whenever possible
- Gives credit to the team
- Anticipates objections and addresses them preemptively

---

## Message Samples

### Sample 1 — Message to Iván (salesman) about Digital Twins
**Context:** Business proposal, post-research, first concrete approach
**Date:** 2026-02-17
**Channel:** WhatsApp
```
Como va Iváncinho estuve metiéndome un poco en lo que hablamos de simulación y digital twins..

Investigué el mercado por arriba, hoy lo lideran Siemens, PTC y Azure (puedo estar errado), y parece que piden USD 100K+ y tardan meses en implementar. Después, parece que el mercado esta proyectado de USD 21B a 150B para 2030

Armé una landing page de juguete para bajar a tierra la idea un poco y quizar reirte un poco:
https://fschiavone.com/simulai/

habría que ver cómo seguir, qué tipo de producto?, competimos contra los grandes o nos metemos en un nicho? (aca no hay mucha opcion, nicho 100% me parece.. bueno, para poner sobre la mesa algo, habría que explorar la competencia y me tendrías que decir cuál sería el producto objectivo si decidieramos copiar uno. ( o que copiarias de una serie de productos)
```
**Tags:** #business #proposal #casual #collaborative

---

### Sample 2-18 — Work messages at Lumber (English, Slack/Email)
**Source:** Franco's message database CSV, 2026
**Channel:** Slack + Email at LumberFi
**Categories covered:**
- Sharing new features (camera capture improvements)
- PR review/pushback (timesheet analyzer integration)
- Diplomatic delegation ("someone from your team could...")
- Status updates to boss/CTO (multiple)
- Sharing metrics and improvements (extraction speed/accuracy)
- Technical architecture explanations (LLM stack, RAG, CV pipelines)
- Issue resolution reporting (face recognition spoofing)
- Resource requests (MLflow infrastructure)
- Answering CEO questions (Karpathy resources, demo timelines)
- Email responses to CTO (anti-spoofing technical approach)

**Full samples stored in:** `/home/node/.openclaw/workspace/franco-messages-db.csv`

---

## Key People (from messages)
- **Hitesh Shah** — Boss/CTO at Lumber. Franco reports to him.
- **Manish Kumar** — CTO. Technical escalations.
- **Shreesha Ramdas** — CEO. High-level status, demos, strategy.
- **Shubh Garg** — Team lead, mobile/frontend team (~20 people)
- **Federico Bogado** — Franco's teammate (AI team, 2 people total)
- **Greg** — Design team
- **Rajendran Nair / Harish** — Domain expert (union/CBA)
- **Nitesh Kumar** — DevOps/infrastructure
- **Iván** — External contact, software seller, potential business partner

## Notes
- Add every message Franco sends or approves
- Track differences between contexts (friend vs business vs formal)
- Franco's voice note transcriptions also count as writing style data
- CSV backup at: `/home/node/.openclaw/workspace/franco-messages-db.csv`
