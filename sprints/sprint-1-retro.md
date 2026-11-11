# Sprint 1 retrospective

- Date: 2026-11-11
- Facilitator: Jonas (Scrum Master)
- Attendees: Stanley (Product Owner), Jonas, SamWang

## What went well

- Every change went through a pull request and a review.
- The AI logs record each use of AI.
- Planning poker changed 7 of the AI's 12 estimates.
- We caught the S07 problem from another team's work: Stanley, using AI, saw that the AI-agent team's ADR-0011 (a fixed Host ID, because macOS can rename a host) would break S07's hostname profiles.

## What did not go well

- S13: the votes ranged from 3 to 8, but we skipped the re-vote our rule asks for and took the median.
- #33 and #34 were approved with only "LGTM", so the reviews do not show what was checked.
- When S07 changed to Host ID, `docs/vision.md` and S18 (#24) were not updated and still say hostname.
- It was hard to find a time when all three of us were free.

## Why S06 and S13 were rated higher than the AI

The sprint plan said we would ask about these here.

- S06 (AI 2, final 3): the votes were within one step of each other. We agreed the difference was small and did not need discussion.
- S13 (AI 3, final 5): Jonas voted 8 because he read the story as needing a three-way merge, which the acceptance criteria do not ask for. It was a wrong estimate. The recorded votes are not changed.

## What AI helped with

- Drafted the 22 stories in about 5 minutes.
- Drawing the activity diagram showed that S20 gives no exit code for a failed preflight (S10).
- PR review took about 30 minutes instead of about 1 hour.

## What AI got wrong

- It missed S23: no story covered a file that already exists at a target path, so apply could overwrite a user's own config. The PO added the story.
- S18 contradicted the vision: the drafted init only recorded the machine and wrote nothing, but the vision promises one-command initialization.

## What we change in Sprint 2

| Change | Owner |
| --- | --- |
| When votes are more than one step apart, the highest and lowest voters explain their reasons and we vote again before taking the median | Jonas |
| An approval says what the reviewer checked, not only "LGTM" | Everyone |
