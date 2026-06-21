# PX4 Module Architecture: `uuv_pos_control`

- Source: `src/modules/uuv_pos_control`
- Build target: `modules__uuv_pos_control`
- Runtime main: `uuv_pos_control`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["uuv_pos_control"]:::module
  Build["px4 module: modules__uuv_pos_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["manual_control_setpoint"]:::io
    In1["parameter_update"]:::io
    In2["trajectory_setpoint6dof"]:::io
    In3["vehicle_attitude"]:::io
    In4["vehicle_control_mode"]:::io
    In5["vehicle_local_position"]:::io
  end
  subgraph Outputs
    Out0["vehicle_attitude_setpoint"]:::io
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
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/uuv_pos_control |
| Build kind | px4 module |
| Build target | modules__uuv_pos_control |
| Runtime main | uuv_pos_control |
| Stack main | 1200 |
| Module config | uuv_pos_control_params.yaml |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 2 |

### CMake Dependencies

- No explicit CMake dependencies detected.

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["uuv_pos_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["manual_control_setpoint"]:::io --> UORBIn
  Sub1["parameter_update"]:::io --> UORBIn
  Sub2["trajectory_setpoint6dof"]:::io --> UORBIn
  Sub3["vehicle_attitude"]:::io --> UORBIn
  Sub4["vehicle_control_mode"]:::io --> UORBIn
  UORBOut --> Pub0["vehicle_attitude_setpoint"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| trajectory_setpoint6dof | subscribed |
| vehicle_angular_velocity | referenced |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | published |
| vehicle_control_mode | subscribed |
| vehicle_local_position | subscribed |
| vehicle_rates_setpoint | referenced |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 uuv_pos_control start"]:::exec
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
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

The common PX4 module lifecycle is command entry, object construction or task spawn, parameter loading, topic setup, scheduled execution, publication, status reporting, and stop/cleanup. Modules that use `ModuleBase`, `ScheduledWorkItem`, polling loops, or bridge callbacks still fit this lifecycle with different scheduling triggers.

## State Machine

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
stateDiagram-v2
  [*] --> Created
  Created --> Initialized: start
  S0: UUV_POS_MODE
  Initialized --> S0: detected state path
  S1: UUV_STAB_MODE
  S0 --> S1: detected state path
  S1 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `UUV_POS_MODE`
- `UUV_STAB_MODE`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as uuv_pos_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start uuv_pos_control
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
classDiagram
  class UUVPOSControl
  UUVPOSControl : uuv_pos_control.hpp
  class ModuleBase
  ModuleBase <|-- UUVPOSControl
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| UUVPOSControl | ModuleBase | uuv_pos_control.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| uuv_pos_control.cpp | source |
| uuv_pos_control.hpp | header |
| uuv_pos_control_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
