# QBank Review UI — Design System

Generated for: Internal Data Annotation Tool / Exam Question Review Dashboard
UI UX Pro Max style category: Data-Dense Dashboard (Dark)

---

## COLORS

| Role | Hex | Usage |
|---|---|---|
| Background | #0D1117 | Page background |
| Surface | #161B22 | Cards, panels, sidebar |
| Border | #30363D | Dividers, input borders |
| Text Primary | #E6EDF3 | Body text, question stems |
| Text Secondary | #8B949E | Meta info, labels, placeholders |
| Approve / Correct | #3FB950 | Approve button, correct answer highlight |
| Reject | #F85149 | Reject button |
| Edit / Action | #58A6FF | Edit button, focus rings, links |
| High Confidence | #3FB950 | Confidence >= 0.90 |
| Mid Confidence | #E3B341 | Confidence 0.70–0.89 |
| Low Confidence | #F85149 | Confidence < 0.70 |
| Progress Fill | #238636 | Progress bar fill |

---

## TYPOGRAPHY

| Element | Font | Size | Weight |
|---|---|---|---|
| Body / stems | -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif | 15px | 400 |
| Question options | same sans-serif | 14px | 400 |
| Data: IDs, confidence, page numbers, source book | 'SF Mono', 'Fira Code', 'Cascadia Code', monospace | 12px | 400 |
| Stats counts | monospace | 20px | 600 |
| Keyboard shortcuts | monospace | 11px | 500 |
| Section labels | sans-serif | 11px | 600, uppercase, tracked |

---

## STYLE

- Dark mode only. No light mode toggle.
- High information density — no decorative whitespace.
- Flat design — no box shadows, no gradients on primary surfaces.
- Borders instead of shadows for panel separation.
- Icons: SVG only. No emoji, no icon fonts.
- Correct answer: solid green left-border + green background tint on the option row.
- Hover states on options: subtle surface lift (#1C2128).
- Focus rings: 2px solid #58A6FF, offset 2px. Visible on all interactive elements.
- Keyboard shortcut labels: monospace chip displayed in action bar.

---

## ANTI-PATTERNS

- NO purple (#8B5CF6 / #A78BFA range) background or gradient anywhere.
- NO pink gradients.
- NO AI aesthetic (no gradient hero, no glassmorphism on primary surfaces).
- NO emoji used as icons (checkmark emoji, cross emoji, etc.).
- NO font-size below 11px (WCAG readability).
- NO placeholder text as the only label.
- NO hover-only affordances — all interactive elements have visible labels.
- NO auto-advancing without keyboard confirmation in edit mode.

---

## LAYOUT

```
┌────────────┬────────────────────────────────────────┐
│  SIDEBAR   │  QUESTION PANEL                        │
│  180px     │  flex-1                                │
│            │  [figure if present]                   │
│  Stats     │  [stem]                                │
│  ────────  │  [A] option                            │
│  Subjects  │  [B] option  ← correct: green          │
│            │  [C] option                            │
│            │  [D] option                            │
│            │  [explanation]                         │
│            │  [meta: book / page / confidence]      │
│            │                                        │
│            │  ─────────────────────────────────     │
│            │  [A Approve] [R Reject] [E Edit]       │
│            │  [← Prev]              [Next →]        │
│            │                                        │
│            │  ████████░░░░  10 / 60 reviewed        │
└────────────┴────────────────────────────────────────┘
```

---

## COMPONENT CHECKLIST

- [ ] Stats sidebar: approved / rejected / edited / pending counts in monospace
- [ ] Subject filter: clickable pills, active state with #58A6FF border
- [ ] Figure: `<img>` above stem, max-height 320px, only when has_figure=true
- [ ] Option rows: A/B/C/D with keyboard letter prefix, correct-answer class on right option
- [ ] Action bar: A / R / E shortcut chips + prev/next navigation
- [ ] Progress bar: `<progress>` or div with width%, aria-label, updates live
- [ ] Confidence badge: monospace, color-coded dot
- [ ] Edit mode: stem + options become editable, Save/Cancel replace action bar
- [ ] Focus rings: visible on tab navigation for all interactive elements
- [ ] WCAG AA contrast verified for primary and secondary text
