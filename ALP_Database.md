# ALP Superhero Database — Living Document

**ALP = Allowance Preservation. Rule No. 1 of this project.**
Every session: Claude Code reads this file and adds any new savings found. Grow it, never delete entries.

---

| # | Saving | Impact | Found |
|---|---|---|---|
| 1 | **Sonnet not Opus** — Sonnet gives 3-5x more messages for same allowance. Use Opus only for complex reasoning. Switch via model selector (bottom right of chat). | Massive — 3-5x more messages immediately | 15 May 2026 |
| 2 | **New chat for new topics** — Long chats cost more per message because the whole conversation re-reads on each turn. Start a fresh chat when switching subjects. | High — exponential cost creep in long chats | 15 May 2026 |
| 3 | **Max 1-2 screenshots per message** — Each image eats thousands of tokens. Describe the rest in words. Send images only when the visual is essential. | High — 1 screenshot session can burn 10-20% daily allowance | 15 May 2026 |
| 4 | **Remove old handover versions from Project Files** — Only the latest .md should be pinned. v17, v18, v19… all load on every message and burn tokens silently. | Medium — tokens wasted every message | 15 May 2026 |
| 5 | **Extended Thinking off for simple tasks** — Toggle in the model selector. Only turn on for architecture, complex debugging, or strategic decisions. | Medium — burns extra per message when unnecessary | 15 May 2026 |
| 6 | **Combine questions into one message** — 3 short messages cost more than 1 longer combined message. Batch everything. | Medium — easy daily saving | 15 May 2026 |
| 7 | **Run /status before heavy Claude Code sessions** — Shows remaining allowance. Don't start a 6-task build at 10% budget. | Medium — prevents wasted sessions | 15 May 2026 |
| 8 | **Session logs not full handover rewrites** — WCCS now writes 30-line session_logs/ entries instead of rewriting 200-line handover every time. Weekly merge to master. | Medium — saves allowance every session end | 15 May 2026 |
| 9 | **Chat and Claude Code share the SAME allowance pool** — Claude Code is £0 money but burns the same message quota as Chat. One big task beats six small tasks. | Critical — previously misunderstood as "free" | 15 May 2026 |
| 10 | **n8n self-hosted could replace manual Python builds** — Free, visual workflow builder, 400+ integrations, AI nodes built in. Could reduce Claude Code hours spent hand-coding the AAFL loop. | Potential — not yet tested | 15 May 2026 |
| 11 | **Use SFL only for genuinely visual things** — Reading a chat via screenshot (text → image → text via AI) adds two error-prone steps. Export chat as text instead. SFL is for terminal errors, UI bugs, game configs. | Medium — avoids unnecessary complexity | 15 May 2026 |
| 12 | **AAFL free providers (Gemini/Mistral/Cerebras) don't touch Claude allowance** — Once AAFL is reliable, route all coding/file tasks through it. Claude Chat only for decisions it can't make. | High — long-term strategy | 15 May 2026 |
| 13 | **Research Anthropic docs FIRST for any platform or UI question** — Guessing UI paths costs multiple messages and often fails. One doc search costs less than 5 wrong guesses. Applies to skills upload, settings, API behaviour, model names. | Medium — prevents wasted message chains | 17 May 2026 |
| 14 | **New ACCA code system works without overhead** — Using short codes (SIB, WRS, MCC etc.) in messages costs zero tokens and enables batch instructions. Build the code table once in the handover, reference it every session. No explanation needed per message. | Low per message, High cumulative — saves explanation tokens every session | 18 May 2026 |
| 15 | **Mobile projects share same memory — no Obsidian needed** — OneDrive sync means mission_control.html works on phone via browser. No separate note-taking app, no sync setup. One dashboard serves all devices. JSON is the single source of truth. | Medium — eliminates a tool and its token cost | 18 May 2026 |
| 16 | **5-project Claude split reduces context burn per message** — Splitting into 5 Claude Projects (AAFL Engine / VKB Spin Doctor / Mission Control / Promo+Business / ACCA Database) means each chat only loads its own pinned files. A chat about AAFL routing won't load the VKB GUI code. Smaller context = fewer tokens burned per message. | High — cumulative saving across all future sessions | 19 May 2026 |
| 17 | **Master project = weekly boardroom only, open max 2-3x/week** — Master project loads all cross-project context. Opening it daily burns tokens unnecessarily. Daily work stays in lean sub-project chats. Master reserved for big-picture strategy sessions only. Split barely affects benchmark (runs locally, not in Chat). | High — prevents context bleed from daily work bleeding into strategic sessions | 19 May 2026 |
| 2026-05-23 | Test ALP entry from automated test |
| 2026-05-23 | Phase 3 test ALP entry |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-24 | test ALP from mcc_test |
| 2026-05-25 | __medical ALP test entry__ |
| 2026-05-25 | __medical ALP test entry__ |
| 2026-05-25 | __medical ALP test entry__ |
| 2026-05-25 | __medical ALP test entry__ |
| 2026-05-25 | __medical ALP test entry__ |
| 2026-05-25 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-27 | __medical ALP test entry__ |
| 2026-05-28 | __medical ALP test entry__ |
| 2026-05-28 | __medical ALP test entry__ |
| 2026-05-28 | __medical ALP test entry__ |
| 2026-05-28 | __medical ALP test entry__ |
| 18 | **mcc-instructions-keeper saves future re-reading** — 132 plain-English help entries for every MCC element, served via API. Future sessions: instead of re-reading code or asking Claude "what does this button do?", click ? — instant answer, zero Claude tokens. 7 section ? buttons cover every major tab. | High — eliminates lookup cost for every future MCC session | 2026-05-28 |
| 2026-05-28 | __medical ALP test entry__ |
| 2026-05-28 | __medical ALP test entry__ |
