# PX4 Module Architecture: `time_persistor`

- Source: `src/modules/time_persistor`
- Build target: `modules__time_persistor`
- Runtime main: `time_persistor`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["time_persistor"]:::module
  Build["px4 module: modules__time_persistor"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  In0["no input topics detected"]:::io
  Out0["no output topics detected"]:::io
  In0 -.-> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module -.-> Out0
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/time_persistor |
| Build kind | px4 module |
| Build target | modules__time_persistor |
| Runtime main | time_persistor |
| Stack main | Not specified |
| Module config | Not specified |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 1 |

### CMake Dependencies

- `px4_work_queue`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["time_persistor logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| None detected. | None detected. |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 time_persistor start"]:::exec
  Spawn["task_spawn / instantiate"]:::exec
  Init["init subscriptions, publishers, parameters"]:::module
  Schedule["schedule work item or enter task loop"]:::exec
  Poll["poll, callback, or interval tick"]:::exec
  Update["copy inputs and update parameters"]:::module
  Compute["run control, estimation, bridge, or service logic"]:::module
  Publish["publish outputs / events / status"]:::io
  Stop{"stop requested?"}:::data
  Exit["cleanup and exit"]:::exec
  Start --> Spawn --> Init --> Schedule --> Poll --> Update --> Compute --> Publish --> Stop
  Stop -- no --> Poll
  Stop -- yes --> Exit
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

The common PX4 module lifecycle is command entry, object construction or task spawn, parameter loading, topic setup, scheduled execution, publication, status reporting, and stop/cleanup. Modules that use `ModuleBase`, `ScheduledWorkItem`, polling loops, or bridge callbacks still fit this lifecycle with different scheduling triggers.

## State Machine

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
stateDiagram-v2
  [*] --> Created
  Created --> Initialized: start
  Initialized --> Running: init complete
  Running --> Updating: new data or timer
  Updating --> Publishing: output ready
  Publishing --> Running: wait next cycle
  Running --> Error: health or IO failure
  Error --> Running: recovered
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- No state-like symbols detected.

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as time_persistor
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start time_persistor
  M->>P: load cached parameter values
  M->>U: advertise and subscribe topics
  M->>W: schedule task or work item
  loop execution cycle
    W-->>M: timer, callback, or poll wakeup
    U-->>M: input topic samples
    M->>P: consume parameter updates
    M->>M: validate, compute, and update state
    M-->>U: publish outputs and status
  end
  CLI->>M: status / stop
```

## Class Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
classDiagram
  class TimePersistor
  TimePersistor : TimePersistor.hpp
  class ModuleBase
  ModuleBase <|-- TimePersistor
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| TimePersistor | ModuleBase | TimePersistor.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| TimePersistor.cpp | source |
| TimePersistor.hpp | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
