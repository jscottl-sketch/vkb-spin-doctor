---
name: mcc-instructions-keeper
description: Keep MCC instructions_db.json in sync with mission_control.html. Trigger when: new OCB session adds elements, user says "update instructions", "instructions out of date", "add help text", or after any build that adds MCC elements. Also trigger if Self-Health flags missing instruction entries.
---

# MCC Instructions Keeper

## Purpose
data/instructions_db.json is the live help database for MCC.
Every element in data/element_registry.json must have an entry.
This skill tells Claude how to keep them in sync.

## When to trigger
- After any OCB that adds new MCC elements
- When user says "update instructions" or "missing help text"
- When self_health.py flags element_id with no instruction entry
- At start of any session where new elements were added last session

## What to do
1. Read data/element_registry.json — get all element_ids
2. Read data/instructions_db.json — get all existing entries
3. Find any element_id in registry that has NO entry in instructions_db
4. Write entries for missing ones (plain English, BI-friendly, no jargon)
5. Atomic write back to instructions_db.json
6. Report: "X new entries added. Total: Y entries."

## Entry format
{
  "short_description": "One line — what it does",
  "full_explanation": "2-3 sentences — how to use it",
  "nested_topics": [{"title": "...", "content": "...", "nested_topics": []}]
}

## Rules
- Plain English always — Scott has BI, no unexplained jargon
- Never delete existing entries — only add or update
- Nested topics max 3 levels deep
- short_description max 10 words
- Atomic write always — verify after save
