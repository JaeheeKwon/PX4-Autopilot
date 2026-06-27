# PX4 Module Architecture: `rc_update`

- Source: `src/modules/rc_update`
- Build target: `modules__rc_update`
- Runtime main: `rc_update`
- Build kind: `px4 module`
- Mermaid palette: `ash` grey tone

The rc_update module handles RC channel mapping: read the raw input channels (`input_rc`), then apply the calibration, map the RC channels to the configured channels & mode switches and then publish as `rc_channels` and `manual_control_input`. To reduce control latency, the module is scheduled on input_rc publications.

## Description of Module

Converts raw RC input into calibrated manual-control input topics.

### Primary Responsibilities

- Consume runtime inputs from uORB topics such as `input_rc`, `manual_control_switches`, `parameter_update`, `rc_parameter_map`.
- Publish outputs or status topics such as `manual_control_input`, `manual_control_switches`, `rc_channels`.
- Use module configuration from `params.yaml`.
- Implement the main behavior in classes such as `TestRCUpdate`, `RCUpdateTest`, `RCUpdate`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `hp_default`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

No dedicated mathematical model was identified in the generated source scan. This module is best understood through its PX4 state handling, uORB message flow, scheduling, and configuration surfaces described below.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `input_rc`, `manual_control_switches`, `parameter_update`, `rc_parameter_map` |
| Primary outputs | `manual_control_input`, `manual_control_switches`, `rc_channels` |
| Referenced topics | `input_rc`, `manual_control_input`, `manual_control_setpoint`, `manual_control_switches`, `parameter_update`, `rc_channels`, `rc_parameter_map` |
| Parameters/config | params.yaml |
| Key classes | `TestRCUpdate`, `RCUpdateTest`, `RCUpdate` |

### Files

| File | Why it matters |
| --- | --- |
| rc_update.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| params.yaml | Build, parameter, or module configuration |
| params_deprecated.yaml | Build, parameter, or module configuration |
| RCUpdateTest.cpp | Defines `TestRCUpdate` class |
| rc_update.h | Defines `RCUpdate` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["rc_update"]:::module
  Build["px4 module: modules__rc_update"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["input_rc"]:::io
    In1["manual_control_switches"]:::io
    In2["parameter_update"]:::io
    In3["rc_parameter_map"]:::io
  end
  subgraph Outputs
    Out0["manual_control_input"]:::io
    Out1["manual_control_switches"]:::io
    Out2["rc_channels"]:::io
  end
  In0 --> Module
  In1 --> Module
  In2 --> Module
  In3 --> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module --> Out0
  Module --> Out1
  Module --> Out2
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/rc_update |
| Build kind | px4 module |
| Build target | modules__rc_update |
| Runtime main | rc_update |
| Stack main | Not specified |
| Module config | params.yaml |
| Detected sources | 2 |
| Detected headers | 1 |
| Detected configs | 3 |

### CMake Dependencies

- `hysteresis`
- `mathlib`
- `px4_work_queue`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["rc_update logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["input_rc"]:::io --> UORBIn
  Sub1["manual_control_switches"]:::io --> UORBIn
  Sub2["parameter_update"]:::io --> UORBIn
  Sub3["rc_parameter_map"]:::io --> UORBIn
  UORBOut --> Pub0["manual_control_input"]:::io
  UORBOut --> Pub1["manual_control_switches"]:::io
  UORBOut --> Pub2["rc_channels"]:::io
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| input_rc | subscribed |
| manual_control_input | published |
| manual_control_setpoint | referenced |
| manual_control_switches | subscribed, published |
| parameter_update | subscribed |
| rc_channels | published |
| rc_parameter_map | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 rc_update start"]:::exec
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
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

The common PX4 module lifecycle is command entry, object construction or task spawn, parameter loading, topic setup, scheduled execution, publication, status reporting, and stop/cleanup. Modules that use `ModuleBase`, `ScheduledWorkItem`, polling loops, or bridge callbacks still fit this lifecycle with different scheduling triggers.

## State Machine

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
stateDiagram-v2
  [*] --> Created
  Created --> Initialized: start
  S0: FUNCTION_ARMSWITCH
  Initialized --> S0: detected state path
  S1: RC_ARMSWITCH_TH
  S0 --> S1: detected state path
  S2: RC_MAP_ARM_SW
  S1 --> S2: detected state path
  S3: RC_MAP_FAILSAFE
  S2 --> S3: detected state path
  S4: RC_MAP_FLTMODE
  S3 --> S4: detected state path
  S5: RC_MAP_MODE_SW
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `FUNCTION_ARMSWITCH`
- `RC_ARMSWITCH_TH`
- `RC_MAP_ARM_SW`
- `RC_MAP_FAILSAFE`
- `RC_MAP_FLTMODE`
- `RC_MAP_MODE_SW`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as rc_update
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start rc_update
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
classDiagram
  class TestRCUpdate
  TestRCUpdate : RCUpdateTest.cpp
  class RCUpdate
  RCUpdate <|-- TestRCUpdate
  class RCUpdateTest
  RCUpdateTest : RCUpdateTest.cpp
  class RCUpdate
  RCUpdate : rc_update.h
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| TestRCUpdate | RCUpdate | RCUpdateTest.cpp |
| RCUpdateTest |  | RCUpdateTest.cpp |
| RCUpdate |  | rc_update.h |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| RCUpdateTest.cpp | source |
| params.yaml | config |
| params_deprecated.yaml | config |
| rc_update.cpp | source |
| rc_update.h | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
