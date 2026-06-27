# PX4 Module Architecture: `muorb`

- Source: `src/modules/muorb`
- Build target: `muorb`
- Runtime main: `muorb`
- Build kind: `directory`
- Mermaid palette: `graphite` grey tone

Source-derived architecture notes for this PX4 module directory.

## Description of Module

Contains multi-uORB transport support code and nested module targets.

### Primary Responsibilities

- Translate between PX4 uORB data and an external transport or companion-computer interface.
- Operate without directly detected uORB topic dependencies in this source inventory.
- Do not publish directly detected uORB outputs from this module directory.
- Implement the main behavior in classes such as `Aggregator`, `AppsProtobufChannel`, `uORB`, `ProtobufChannel`, `uORB`.
- Organize nested module targets: `apps`, `slpi`.

### Runtime Behavior

- Creates a dedicated PX4 task/thread with `px4_task_spawn_cmd()`.

## Background Theory

No dedicated mathematical model was identified in the generated source scan. This module is best understood through its PX4 state handling, uORB message flow, scheduling, and configuration surfaces described below.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | none detected |
| Primary outputs | none detected |
| Referenced topics | none detected |
| Parameters/config | none detected |
| Key classes | `Aggregator`, `AppsProtobufChannel`, `uORB`, `ProtobufChannel`, `uORB` |

### Files

| File | Why it matters |
| --- | --- |
| apps/muorb_main.cpp | Entry point, start command, or module lifecycle code |
| apps/uORBAppsProtobufChannel.cpp | Entry point, start command, or module lifecycle code |
| slpi/muorb_main.cpp | Entry point, start command, or module lifecycle code |
| slpi/uORBProtobufChannel.cpp | Entry point, start command, or module lifecycle code |
| apps/CMakeLists.txt | Build, parameter, or module configuration |
| slpi/CMakeLists.txt | Build, parameter, or module configuration |
| aggregator/mUORBAggregator.hpp | Defines `Aggregator` class |
| apps/uORBAppsProtobufChannel.hpp | Defines `AppsProtobufChannel` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["muorb"]:::module
  Build["directory: muorb"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  In0["no input topics detected"]:::io
  Out0["no output topics detected"]:::io
  In0 -.-> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module -.-> Out0
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/muorb |
| Build kind | directory |
| Build target | muorb |
| Runtime main | muorb |
| Stack main | Not specified |
| Module config | Not specified |
| Detected sources | 5 |
| Detected headers | 3 |
| Detected configs | 2 |

### CMake Dependencies

- No explicit CMake dependencies detected.

### Nested Module Targets

- `apps`
- `slpi`

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["muorb logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| None detected. | None detected. |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 muorb start"]:::exec
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
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

The common PX4 module lifecycle is command entry, object construction or task spawn, parameter loading, topic setup, scheduled execution, publication, status reporting, and stop/cleanup. Modules that use `ModuleBase`, `ScheduledWorkItem`, polling loops, or bridge callbacks still fit this lifecycle with different scheduling triggers.

## State Machine

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as muorb
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start muorb
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
classDiagram
  class Aggregator
  Aggregator : aggregator/mUORBAggregator.hpp
  class AppsProtobufChannel
  AppsProtobufChannel : apps/uORBAppsProtobufChannel.hpp
  class uORB
  uORB : apps/uORBAppsProtobufChannel.hpp
  class ProtobufChannel
  ProtobufChannel : slpi/uORBProtobufChannel.hpp
  class uORB_4
  uORB_4 : slpi/uORBProtobufChannel.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| Aggregator |  | aggregator/mUORBAggregator.hpp |
| AppsProtobufChannel |  | apps/uORBAppsProtobufChannel.hpp |
| uORB |  | apps/uORBAppsProtobufChannel.hpp |
| ProtobufChannel |  | slpi/uORBProtobufChannel.hpp |
| uORB |  | slpi/uORBProtobufChannel.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| aggregator/mUORBAggregator.cpp | source |
| aggregator/mUORBAggregator.hpp | header |
| apps/CMakeLists.txt | build |
| apps/muorb_main.cpp | source |
| apps/uORBAppsProtobufChannel.cpp | source |
| apps/uORBAppsProtobufChannel.hpp | header |
| slpi/CMakeLists.txt | build |
| slpi/muorb_main.cpp | source |
| slpi/uORBProtobufChannel.cpp | source |
| slpi/uORBProtobufChannel.hpp | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
