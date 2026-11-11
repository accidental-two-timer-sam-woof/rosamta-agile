# Product decisions

Changes to the product or its stories after the backlog was accepted. Each entry gives the date, what changed, why, and who approved it. The story's GitHub issue has the same entry in its change log.

| Date | Decision | Stories | Reason | Approved by |
| --- | --- | --- | --- | --- |
| 2026-11-10 | The system hostname is replaced by a fixed Host ID, chosen once during init and stored in local settings | S07 (#12), S18 (#24) | The system hostname can change (macOS adds `-2` on name conflicts), which would silently stop profiles from matching. Learned from the AI-agent team's design (their ADR-0011) | Stanley (PO) |
| 2026-11-11 | A failed preflight exits with code 1 and writes nothing | S20 (#26), S10 (#15) | S20 did not give a code for it. Found while drawing the activity diagram | Stanley (PO) |
