# PX4 Module Architecture: `internal_combustion_engine_control`

- Source: `src/modules/internal_combustion_engine_control`
- Build target: `modules__internal_combustion_engine_control`
- Runtime main: `internal_combustion_engine_control`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Architecture notes for the Internal Combustion Engine Control module.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["internal_combustion_engine_control"]:::module
  Build["px4 module: modules__internal_combustio..."]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_motors"]:::io
    In1["manual_control_setpoint"]:::io
    In2["parameter_update"]:::io
    In3["rpm"]:::io
    In4["vehicle_status"]:::io
  end
  subgraph Outputs
    Out0["internal_combustion_engine_control"]:::io
    Out1["internal_combustion_engine_status"]:::io
  end
  In0 --> Module
  In1 --> Module
  In2 --> Module
  In3 --> Module
  In4 --> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module --> Out0
  Module --> Out1
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/internal_combustion_engine_control |
| Build kind | px4 module |
| Build target | modules__internal_combustion_engine_control |
| Runtime main | internal_combustion_engine_control |
| Stack main | Not specified |
| Module config | module.yaml |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 2 |

### CMake Dependencies

- `px4_work_queue`
- `SlewRate`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["internal_combustion_engine_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_motors"]:::io --> UORBIn
  Sub1["manual_control_setpoint"]:::io --> UORBIn
  Sub2["parameter_update"]:::io --> UORBIn
  Sub3["rpm"]:::io --> UORBIn
  Sub4["vehicle_status"]:::io --> UORBIn
  UORBOut --> Pub0["internal_combustion_engine_control"]:::io
  UORBOut --> Pub1["internal_combustion_engine_status"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_motors | subscribed |
| internal_combustion_engine_control | published |
| internal_combustion_engine_status | published |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| rpm | subscribed |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 internal_combustion_engine_control start"]:::exec
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
  S0: ARMING_STATE_ARMED
  Initialized --> S0: detected state path
  S1: DISARMED
  S0 --> S1: detected state path
  S1 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `DISARMED`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as internal_combustion_engine_...
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start internal_combustion_engin...
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
  class InternalCombustionEngineControl
  InternalCombustionEngineControl : InternalCombustionEngineControl.hpp
  class ModuleBase
  ModuleBase <|-- InternalCombustionEngineControl
  class State
  State : InternalCombustionEngineControl.hpp
  class SubState
  SubState : InternalCombustionEngineControl.hpp
  class UserOnOffRequest
  UserOnOffRequest : InternalCombustionEngineControl.hpp
  class ICESource
  ICESource : InternalCombustionEngineControl.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| InternalCombustionEngineControl | ModuleBase | InternalCombustionEngineControl.hpp |
| State |  | InternalCombustionEngineControl.hpp |
| SubState |  | InternalCombustionEngineControl.hpp |
| UserOnOffRequest |  | InternalCombustionEngineControl.hpp |
| ICESource |  | InternalCombustionEngineControl.hpp |

### Detected Enums

- `ICESource`
- `State`
- `SubState`
- `UserOnOffRequest`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| InternalCombustionEngineControl.cpp | source |
| InternalCombustionEngineControl.hpp | header |
| module.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
