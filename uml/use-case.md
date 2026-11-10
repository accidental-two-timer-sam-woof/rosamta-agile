# Use case diagram

Actors and the main use cases of rosamta v1. Each use case lists the stories it comes from. Dotted arrows show `include` (always happens as part of the use case) and `extend` (happens only in some cases).

```mermaid
flowchart LR
  regular["Actor: Regular user"]
  advanced["Actor: Advanced user"]
  script["Actor: Script (no terminal)"]
  assistant["Actor: AI assistant"]

  subgraph rosamta["rosamta"]
    direction TB
    edit(["Edit module values<br/>S01"])
    templates(["Use built-in templates<br/>S02"])
    override(["Override or add a template<br/>S03, S04"])
    manifest(["Declare outputs and target paths<br/>S05, S06"])
    profiles(["Configure profiles and tags<br/>S07, S08"])
    preview(["Preview changes<br/>S09"])
    apply(["Apply outputs<br/>S11, S20"])
    preflight(["Run preflight checks<br/>S10"])
    drift(["Keep hand-edited files<br/>S13"])
    backup(["Back up existing files<br/>S23"])
    cleanup(["Clean up old outputs<br/>S15"])
    rollback(["Roll back a failed apply<br/>S12"])
    overwrite(["Overwrite a drifted file<br/>S14"])
    query(["Query modules and outputs<br/>S16, S17"])
    init(["Initialize a new machine<br/>S18"])
    json(["Read results as JSON<br/>S21, S22"])
  end

  regular --- edit
  regular --- templates
  regular --- manifest
  regular --- profiles
  regular --- preview
  regular --- apply
  regular --- query
  regular --- init
  advanced --- override
  advanced --- query
  script --- apply
  script --- preview
  assistant --- json
  assistant --- apply

  apply -. include .-> preflight
  apply -. include .-> drift
  apply -. include .-> cleanup
  apply -. include .-> backup
  rollback -. extend .-> apply
  overwrite -. extend .-> apply
  init -. include .-> apply
  json -. extend .-> preview
  json -. extend .-> query
```

## Notes

- The script actor covers S19 (never wait for input) and S20 (exit codes): every use case it touches must run without prompts and report through exit codes.
- Use cases come from the accepted stories (#6 to #28). Use cases for Should and Could stories are included so the diagram shows the whole v1 scope.
