# Activity diagram: apply

The decisions apply makes for each output, and which exit code each path ends with (S20).

```mermaid
flowchart TD
  start([Start: rosamta apply]) --> load[Load modules, manifest, profiles]
  load --> valid{Configuration valid?}
  valid -- No --> exit3([Report problem, exit 3])
  valid -- Yes --> plan[Build plan for this machine]
  plan --> pre{Preflight passes?}
  pre -- No --> stop([Report problem, write nothing, exit 1])
  pre -- Yes --> next{Next planned change?}
  next -- Drifted --> keep[Keep user's file, mark skipped] --> next
  next -- Existing file not written by rosamta --> allowed{Take-over allowed?}
  allowed -- No --> skip[Skip, mark with reason] --> next
  allowed -- Yes --> backup[Back up original] --> write
  next -- Write or remove --> write[Write or delete file]
  write --> ok{Succeeded?}
  ok -- No --> rollback[Restore every changed file] --> exit1([Exit 1])
  ok -- Yes --> next
  next -- None left --> record[Record what was written]
  record --> skipped{Anything skipped?}
  skipped -- Yes --> exit2([Summary, exit 2])
  skipped -- No --> exit0([Summary, exit 0])
```

## Decision

A failed preflight writes nothing and exits with code 1. This was an open question from drawing this diagram, because S20 gave no code for it. Decided by Stanley (PO) at the start of Sprint 2 (2026-11-11). See `docs/decisions.md`.
