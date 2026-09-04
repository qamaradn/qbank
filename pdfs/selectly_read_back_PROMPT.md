# SELECTLY TASK 1 — let a caller read back what qbank pushed

Small, and it closes a hole that has already bitten this project once.

## The problem

qbank sends `formId`, `formPosition` and `formKind` with every question. Selectly's
`questions` table has all three columns and `/api/questions/import` writes all three.
**But nothing returns them**, so there is no way to check they arrived.

That is not a theoretical worry. In August those same three fields were being silently
dropped by zod on every push. Everything looked fine — `inserted=N errors=0` — and it
was found weeks later by reading the app's source, not by a check. The fix shipped, but
the blind spot did not.

`/api/admin/questions-dump` already returns `qbankId` for exactly this reason. Its own
comment says it is there "so a caller can see which questions are still unaddressable
from qbank". Form membership needs the same treatment: on 2026-09-04 qbank pushed 4,500
VIC questions across 153 forms and **cannot prove any of them landed in a form.**

If the fields were dropped again, the questions would go live with no form, every drill
paper would be empty, and the first person to find out would be a reviewer.

## What to change

**1. `src/app/api/admin/questions-dump/route.ts` — add three fields to the select.**

Already written and committed on branch `feature/dump-form-fields` (commit `f07215e`).
It type-checks and changes nothing for existing callers. Review it, merge it, deploy it.

```ts
qbankId: questions.qbankId,
formId: questions.formId,
formPosition: questions.formPosition,
formKind: questions.formKind,
stem: questions.stem,
```

**2. `src/app/api/admin/flagged-questions/export/route.ts` — add `form_id` to the CSV.**

The CSV reviewers send back is the whole correction loop, and its columns are currently
`qbank_id, question_id, category, stem_snippet, reviewer_email, note, flagged_at`. There
is no form. qbank can look the form up from `qbank_id`, so this is not blocking — but
with the column present the CSV describes itself, and qbank can check that Selectly and
qbank agree about which form a flagged question is in. Add `form_id` after `category`.

## How to know it worked

qbank has the checker already: `tools/verify_pushed_forms.py`. Today it refuses to run
and says so:

> questions-dump does not return formId yet, so this cannot be checked. Deploy Selectly
> branch feature/dump-form-fields first — an absent field is not an empty one, and
> reporting a pass here would be a lie.

After deploying, that command compares every approved qbank question against Selectly and
reports three things separately: not live, live with no form, and form differs from qbank.
**Tell qbank when it is deployed and it will run.**

## Please don't

Do not filter `active` out of the dump, and do not add a `form` query parameter to
replace reading the whole category. The dump's value is that it returns everything,
including rows that have been switched off — that is what makes an audit possible.
