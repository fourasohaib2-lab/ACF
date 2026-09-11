---
name: acf-status-sync
description: Keep docs/STATUS.md and the relevant closure report (AWCI_IMPLEMENTATION_STATUS.md, future-improvements.md, or a new ACF-RECONCILIATION-*.md-style report) consistent with a just-completed module change. Use after finishing a non-trivial change to any acf.* module, before considering the task done — not for typo fixes or single-line changes.
---

# ACF status/doc sync

`docs/STATUS.md` states its own rule explicitly: a module is only checked
`[x]` if it satisfies `ARCHITECTURE.md` §3's 4 criteria (an `audit(module)`
commit, green tests, no docstring over-claim, declared dependencies). This
project's own history shows real drift between code and status docs when
this step is skipped (see `docs/STATUS.md`'s own entries documenting
fabricated self-certifications later found and corrected). This skill is a
mechanical checklist to avoid repeating that drift — it does not replace
`awci-review` (use both when the change is AWCI-specific).

## When a change is done, check:

1. **Does `docs/STATUS.md` still describe this module accurately?**
   - A module newly reaching all 4 `ARCHITECTURE.md` §3 criteria → mark
     `[x]`, one line, factual (no adjectives like "complete"/"production
     ready" unless literally verified).
   - A module with real work done but not fully audited → `[~]`, and say
     what's still open.
   - Never silently leave a stale claim (e.g. a module marked `[x]` that
     a change just made partially true again) — update it in the same
     change.

2. **Is there a per-feature closure doc that needs updating?** For AWCI:
   `docs/awci/future-improvements.md` (if this closes/narrows a disclosed
   gap) and `docs/awci/AWCI_IMPLEMENTATION_STATUS.md`. For other modules,
   check `docs/` and `reports/` for an existing equivalent before creating
   a new one — this repo already has many
   (`ACF-RECONCILIATION-*.md`, `reports/ACF_MASTER_AUDIT_v2.md`,
   `reports/architecture/*.md`). Prefer extending an existing doc's own
   "Update <date>" convention over creating a parallel one.

3. **Does the change leave any doc claiming something no longer true?**
   Grep the docstring/doc language for words like "not built", "proxy",
   "TODO", "not yet" near the code just changed — if the change closed
   that gap, the doc must say so; if it didn't, leave the disclosure
   alone rather than deleting a still-true caveat.

4. **CHANGELOG.md** — add an entry if the change is user-visible or
   changes a documented output (not for internal refactors with no
   behavior change).

## What this skill does NOT do

It does not decide whether a module *should* be marked `[x]` — that
judgment (the 4 real criteria) is yours to make honestly, not to assume
because a task felt complete. When in doubt, `[~]` and say what's missing
is more honest than a premature `[x]`.
