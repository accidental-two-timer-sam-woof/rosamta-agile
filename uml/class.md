# Class diagram

Domain model for rosamta v1, from the accepted stories. Names are placeholders for the design, not final code names.

```mermaid
classDiagram
  direction LR
  class Module {
    +name: String
    +values: Map
  }
  class Template {
    +name: String
    +builtIn: bool
    +render(values) String
  }
  class Manifest {
    +outputs: List~Output~
    +validate() List~Problem~
  }
  class Output {
    +name: String
    +targetPaths: Map~OS, Path~
    +allowTakeOver: bool
    +requiredPrograms: List~String~
  }
  class Profile {
    +name: String
    +os: List~OS~
    +hostIds: List~String~
    +tags: List~String~
    +matches(machine) bool
  }
  class LocalSettings {
    +hostId: String
    +tags: List~String~
    +configFolder: Path
  }
  class Planner {
    +buildPlan(machine) ApplyPlan
  }
  class ApplyPlan {
    +changes: List~PlannedChange~
  }
  class PlannedChange {
    +output: Output
    +action: Write | Unchanged | Skip | Remove
    +reason: String
    +diff: String
  }
  class Preflight {
    +check(plan) List~Problem~
  }
  class Applier {
    +apply(plan) Result
    -rollback()
  }
  class StateRecord {
    +lastWritten: Map~Path, Hash~
    +isDrifted(path) bool
  }
  class BackupStore {
    +save(path) Path
    +restore(path)
  }
  class Result {
    +exitCode: 0 | 1 | 2 | 3
    +items: List~PlannedChange~
    +toJson() String
  }

  Output --> Template : rendered with
  Template ..> Module : reads values
  Manifest "1" *-- "many" Output
  Profile --> "many" Output : enables
  Profile ..> LocalSettings : matches host ID and tags
  Planner --> Manifest
  Planner --> Profile
  Planner --> StateRecord : checks drift
  Planner --> ApplyPlan : creates
  ApplyPlan "1" *-- "many" PlannedChange
  Preflight --> ApplyPlan : checks
  Applier --> ApplyPlan : executes
  Applier --> BackupStore : backs up and restores
  Applier --> StateRecord : updates
  Applier --> Result : returns
```

## Notes

- `StateRecord` stores only a hash of each written file, never its content, because outputs may contain secrets.
- `LocalSettings` lives on each machine and is not part of the shared config folder (S08, S18).
- `Profile.hostIds` uses a fixed Host ID instead of the system hostname (change request on S07, #12).
