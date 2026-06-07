# MCC WMBW Report — Per-Element Scrutiny
Generated: 2026-06-07 11:47:33

WMBW = What Makes it Better? (3 improvements + web best-practice + WENTO score)

---

## Tab Navigation — Score: 7/10  

**Current implementation:** Tab bar with data-tab buttons, CSS active state, JS switchTab()

**3 ways it could be better:**
1. Keyboard arrow-key navigation between tabs (WCAG 2.1 §4.1.3)
2. aria-selected and role='tab' + role='tabpanel' for screen readers
3. Tab state persisted to localStorage so refresh returns to last tab

**Recommendation:** Add aria-selected/role=tab attributes; persist active tab to localStorage

---

## Button Save — Score: 7/10  

**Current implementation:** btn-save-lg with disabled state during run

**3 ways it could be better:**
1. Loading spinner replaces button label during async op (not just disabled)
2. Success/fail toast with undo action within 5s (Nielsen: error recovery)
3. Keyboard shortcut (Ctrl+S) wired to save trigger

**Recommendation:** Add inline spinner to save button; wire Ctrl+S shortcut

---

## Textarea Chat — Score: 6/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** Plain textarea with fixed height, Consolas font

**3 ways it could be better:**
1. Auto-resize textarea (css: field-sizing: content or JS resize observer)
2. Character count indicator with soft/hard limits clearly marked
3. Paste-to-save keyboard shortcut (Ctrl+Enter) clearly labelled

**Recommendation:** Auto-resize + char counter + Ctrl+Enter shortcut label

---

## Polling Dashboard — Score: 6/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** setInterval polling every 5-10s on multiple tabs simultaneously

**3 ways it could be better:**
1. Exponential backoff when server is unreachable (not constant polling)
2. Pause polling when tab is hidden (document.visibilityState check)
3. Show 'Last updated X seconds ago' staleness indicator

**Recommendation:** Implement visibility-aware polling + backoff on failure

---

## Toast Notifications — Score: 7/10  

**Current implementation:** Bottom-right toast with ok/error colour coding, 3s auto-dismiss

**3 ways it could be better:**
1. Stack multiple toasts vertically (currently may overlap)
2. Manual dismiss X button for error toasts (shouldn't auto-dismiss errors)
3. ARIA live region (role=alert) so screen readers announce them

**Recommendation:** Add role=alert to toast container; keep error toasts until dismissed

---

## Error Display — Score: 5/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** Inline .error-msg class shown in panels on failure

**3 ways it could be better:**
1. Errors should include actionable text: what failed + what user can do
2. Error messages should be distinguishable from empty/loading states
3. Retry button inline with error for recoverable failures

**Recommendation:** Add actionable error text + inline retry buttons

---

## Theme Toggle — Score: 7/10  

**Current implementation:** Dark/light theme stored in prefs, CSS body.theme-light class swap

**3 ways it could be better:**
1. Respect prefers-color-scheme media query as default before user pref
2. Theme persists across sessions (localStorage or server pref)
3. System-level contrast check — light theme may not meet WCAG AA

**Recommendation:** Add prefers-color-scheme auto-detection as fallback

---

## Data Tables — Score: 6/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** data-table class with th/td, no pagination, loads all rows

**3 ways it could be better:**
1. Virtual scrolling or pagination for tables >50 rows
2. Sortable columns — click th to sort ascending/descending
3. Column resize handles for wide content

**Recommendation:** Add client-side sort on th click; cap row render at 50 with load-more

---

## Confirm Dialog — Score: 7/10  

**Current implementation:** Custom overlay confirm-box for destructive actions

**3 ways it could be better:**
1. Focus trap inside dialog (Tab cycles within modal, not to background)
2. Esc key closes dialog
3. Default focus on Cancel (not Confirm) for destructive actions

**Recommendation:** Implement focus trap + Escape key handler in confirm dialog

---

## Endpoint Error Handling — Score: 5/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** Most endpoints catch Exception and return {error: str(exc)}

**3 ways it could be better:**
1. Distinguish client errors (4xx) from server errors (5xx) consistently
2. Never expose raw exception messages to client (security + UX)
3. Structured error codes (e.g. {error_code: 'E_QUEUE_FULL'}) for machine parsing

**Recommendation:** Add error_code field to all error responses; sanitize exception text

---

## Performance Polling — Score: 5/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** Multiple setInterval timers across tabs, all polling even when not visible

**3 ways it could be better:**
1. Consolidate to single polling loop that distributes to subscribers
2. Reduce polling rate to 30s when window loses focus
3. Request coalescing: batch multiple endpoint reads into one cycle

**Recommendation:** Implement central poller with visibility-aware rate reduction

---

## Accessibility Contrast — Score: 5/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** #888 text on #0d0d0d background — ratio ~4.5:1 (borderline AA)

**3 ways it could be better:**
1. WCAG AA requires 4.5:1 for normal text, 3:1 for large text
2. Secondary text (#555, #444, #333) on dark backgrounds likely fails AA
3. Run automated contrast checker on all colour pairs

**Recommendation:** Audit and lighten secondary text colours (#555->#777 minimum)

---

## Keyboard Shortcuts — Score: 6/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** Number key 1-9 for tab switching, some VKB profile shortcuts

**3 ways it could be better:**
1. All shortcuts visible in a help overlay (? key)
2. Shortcuts should not conflict with browser defaults
3. Shortcut hints should appear in tooltips (e.g. 'Save (Ctrl+S)')

**Recommendation:** Add shortcut hints to button tooltips; verify no browser conflicts

---

## Form Validation — Score: 5/10  🚩 FLAGGED FOR UPGRADE

**Current implementation:** Client-side empty-check before fetch; server returns 400 for empty

**3 ways it could be better:**
1. Inline validation feedback before submit (not just on empty check)
2. Max-length enforcement visible to user (not just truncated server-side)
3. Input sanitization visible — show what characters are stripped

**Recommendation:** Add maxlength attributes to inputs; show character remaining

---

## Summary

Average score: **6.0/10**
Elements flagged for upgrade: **9**

### Top Upgrade Targets:
- textarea_chat: Auto-resize + char counter + Ctrl+Enter shortcut label
- polling_dashboard: Implement visibility-aware polling + backoff on failure
- error_display: Add actionable error text + inline retry buttons
- data_tables: Add client-side sort on th click; cap row render at 50 with load-more
- endpoint_error_handling: Add error_code field to all error responses; sanitize exception text