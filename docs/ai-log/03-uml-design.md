# 03 Class, sequence and activity diagrams

- Date: 2026-11-10
- Who: Stanley (drafted with AI); review by SamWang (design lead)
- Tool and model: Claude (Opus 5.5), in the project chat
- Purpose: draft the class diagram and the apply sequence and activity diagrams from the accepted stories

## Prompt

Draft Mermaid class, sequence and activity diagrams for `rosamta apply` from the accepted stories S01 to S23. Tag each step with the story it comes from. Render each diagram to check it displays.

## AI output (verbatim)

The first commit of each file in this PR is the AI draft.

## What reviewing the diagrams found

- **Gap in the stories:** S10 says a failed preflight writes nothing, but S20 gives no exit code for it. Found while drawing the activity diagram. Left as an open question for the PO. Decided at the start of Sprint 2 (2026-11-11): exit code 1.
- **Change request from another team:** the AI-agent team's design (their ADR-0011) uses a fixed Host ID instead of the system hostname, because macOS can rename a host (for example adding `-2`). That would silently break S07. The PO changed S07 (#12) and the class diagram uses `hostIds`.

## Accepted and rejected

| Item | Decision | Reason | Approved by |
| --- | --- | --- | --- |
|  |  |  | SamWang |

## Where the AI was wrong

(SamWang: fill in after review.)

## Time saved or lost

(fill in after review)
