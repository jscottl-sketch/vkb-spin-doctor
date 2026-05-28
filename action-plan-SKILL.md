---
name: action-plan
description: Show the project action plan, prioritized todo list, and next steps. Trigger on "action plan", "what's next", "todo list", "next move", "what should I do", "where are we", "next steps", "next priorities". Also trigger when Scott seems lost or unsure what to do next.
---

# Action Plan Skill

When triggered, read STATUS.md PENDING section and output the current prioritized action plan. Split into what CLAC (Claude Code) can automate vs what Scott must do manually.

## Rules
- **DSP IS ALWAYS YES — never ask. Every CLAC block output must be preceded by: Box 1 cd path, Box 2 claude --dangerously-skip-permissions, Box 3 CLAC block. Three boxes. Always. No exceptions. Never combine.**
- ALP (Allowance Preservation) is Rule No.1 — always flag cheapest path
- One step at a time — never stack steps
- Number everything so Scott can reply with just a number
- Mark each item: 🤖 CLAC (automatable) or 👤 MANUAL (Scott does it)
- Show blockers — if Job B depends on Job A, say so
- Always check STATUS.md PENDING table first — that's the source of truth
- If something on the list is done, say so and suggest removing it from PENDING

## Output format

```
## ACTION PLAN — [today's date]

### 🔴 DO NOW (unblocks everything else)
1. 🤖/👤 [task] — [one line why it matters]

### 🟡 NEXT SESSION
2. 🤖/👤 [task] — [one line]

### 🔵 QUEUED (after above done)
3. 🤖/👤 [task] — [one line]

### ⚪ PARKED (after benchmark)
4. [task]

---
**Cheapest next move:** [shortest ALP path to progress]
**CLAC block ready?** Yes/No — reply 1 to get it

**If CLAC block requested, ALWAYS output three boxes:**
Box 1: cd C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor
Box 2: claude --dangerously-skip-permissions
Box 3: [the CLAC instruction block]
```

## ALP note
Keep output under 30 lines. No waffle. Scott picks a number, gets the CLAC block or manual steps.
