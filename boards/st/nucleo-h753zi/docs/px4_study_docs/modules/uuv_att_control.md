# PX4 Module Architecture: `uuv_att_control`

- Source: `src/modules/uuv_att_control`
- Build target: `modules__uuv_att_control`
- Runtime main: `uuv_att_control`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["uuv_att_control"]:::module
  Build["px4 module: modules__uuv_att_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["manual_control_setpoint"]:::io
    In1["parameter_update"]:::io
    In2["vehicle_angular_velocity"]:::io
    In3["vehicle_attitude"]:::io
    In4["vehicle_attitude_setpoint"]:::io
    In5["vehicle_control_mode"]:::io
  end
  subgraph Outputs
    Out0["vehicle_thrust_setpoint"]:::io
    Out1["vehicle_torque_setpoint"]:::io
  end
  In0 --> Module
  In1 --> Module
  In2 --> Module
  In3 --> Module
  In4 --> Module
  In5 --> Module
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
| Module path | src/modules/uuv_att_control |
| Build kind | px4 module |
| Build target | modules__uuv_att_control |
| Runtime main | uuv_att_control |
| Stack main | 1200 |
| Module config | uuv_att_control_params.yaml |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 2 |

### CMake Dependencies

- No explicit CMake dependencies detected.

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["uuv_att_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["manual_control_setpoint"]:::io --> UORBIn
  Sub1["parameter_update"]:::io --> UORBIn
  Sub2["vehicle_angular_velocity"]:::io --> UORBIn
  Sub3["vehicle_attitude"]:::io --> UORBIn
  Sub4["vehicle_attitude_setpoint"]:::io --> UORBIn
  UORBOut --> Pub0["vehicle_thrust_setpoint"]:::io
  UORBOut --> Pub1["vehicle_torque_setpoint"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | subscribed |
| vehicle_control_mode | subscribed |
| vehicle_rates_setpoint | subscribed |
| vehicle_thrust_setpoint | published |
| vehicle_torque_setpoint | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 uuv_att_control start"]:::exec
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
  S0: UUV_STICK_MODE
  Initialized --> S0: detected state path
  S0 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `UUV_STICK_MODE`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as uuv_att_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start uuv_att_control
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
  class UUVAttitudeControl
  UUVAttitudeControl : uuv_att_control.hpp
  class ModuleBase
  ModuleBase <|-- UUVAttitudeControl
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| UUVAttitudeControl | ModuleBase | uuv_att_control.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| uuv_att_control.cpp | source |
| uuv_att_control.hpp | header |
| uuv_att_control_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
