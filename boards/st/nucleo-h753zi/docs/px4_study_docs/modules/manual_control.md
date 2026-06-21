# PX4 Module Architecture: `manual_control`

- Source: `src/modules/manual_control`
- Build target: `modules__manual_control`
- Runtime main: `manual_control`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["manual_control"]:::module
  Build["px4 module: modules__manual_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["action_request"]:::io
    In1["manual_control_setpoint"]:::io
    In2["manual_control_switches"]:::io
    In3["parameter_update"]:::io
    In4["vehicle_status"]:::io
  end
  subgraph Outputs
    Out0["action_request"]:::io
    Out1["landing_gear"]:::io
    Out2["manual_control_input"]:::io
    Out3["manual_control_setpoint"]:::io
    Out4["manual_control_switches"]:::io
    Out5["vehicle_command"]:::io
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
  Module --> Out2
  Module --> Out3
  Module --> Out4
  Module --> Out5
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/manual_control |
| Build kind | px4 module |
| Build target | modules__manual_control |
| Runtime main | manual_control |
| Stack main | Not specified |
| Module config | manual_control_params.yaml |
| Detected sources | 5 |
| Detected headers | 3 |
| Detected configs | 2 |

### CMake Dependencies

- `hysteresis`
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
  Logic["manual_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["action_request"]:::io --> UORBIn
  Sub1["manual_control_setpoint"]:::io --> UORBIn
  Sub2["manual_control_switches"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["vehicle_status"]:::io --> UORBIn
  UORBOut --> Pub0["action_request"]:::io
  UORBOut --> Pub1["landing_gear"]:::io
  UORBOut --> Pub2["manual_control_input"]:::io
  UORBOut --> Pub3["manual_control_setpoint"]:::io
  UORBOut --> Pub4["manual_control_switches"]:::io
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| action_request | subscribed, published |
| landing_gear | published |
| manual_control_input | published |
| manual_control_setpoint | subscribed, published |
| manual_control_switches | subscribed, published |
| parameter_update | subscribed |
| vehicle_command | published |
| vehicle_status | subscribed, published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 manual_control start"]:::exec
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
  S0: ACTION_ARM
  Initialized --> S0: detected state path
  S1: ACTION_DISARM
  S0 --> S1: detected state path
  S2: ACTION_SWITCH_MODE
  S1 --> S2: detected state path
  S3: ACTION_TOGGLE_ARMING
  S2 --> S3: detected state path
  S4: ARMING_STATE_ARMED
  S3 --> S4: detected state path
  S5: COM_ARM_SWISBTN
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ACTION_ARM`
- `ACTION_DISARM`
- `ACTION_SWITCH_MODE`
- `ACTION_TOGGLE_ARMING`
- `ARMING_STATE_ARMED`
- `COM_ARM_SWISBTN`
- `COM_FLTMODE`
- `COM_FLTMODE1`
- `COM_FLTMODE2`
- `COM_FLTMODE3`
- `COM_FLTMODE4`
- `COM_FLTMODE5`
- `COM_FLTMODE6`
- `COM_RC_IN_MODE`
- `MAN_ARM_GESTURE`
- `MC_AIRMODE`
- `NAVIGATION_STATE_ACRO`
- `NAVIGATION_STATE_ALTCTL`
- `NAVIGATION_STATE_ALTITUDE_CRUISE`
- `NAVIGATION_STATE_AUTO_FOLLOW_TARGET`
- `NAVIGATION_STATE_AUTO_LAND`
- `NAVIGATION_STATE_AUTO_LOITER`
- `NAVIGATION_STATE_AUTO_MISSION`
- `NAVIGATION_STATE_AUTO_PRECLAND`
- `NAVIGATION_STATE_AUTO_RTL`
- `NAVIGATION_STATE_AUTO_TAKEOFF`
- `NAVIGATION_STATE_AUTO_VTOL_TAKEOFF`
- `NAVIGATION_STATE_EXTERNAL1`
- `NAVIGATION_STATE_EXTERNAL2`
- `NAVIGATION_STATE_EXTERNAL3`
- `NAVIGATION_STATE_EXTERNAL4`
- `NAVIGATION_STATE_EXTERNAL5`
- `NAVIGATION_STATE_EXTERNAL6`
- `NAVIGATION_STATE_EXTERNAL7`
- `NAVIGATION_STATE_EXTERNAL8`
- `NAVIGATION_STATE_MANUAL`
- `NAVIGATION_STATE_OFFBOARD`
- `NAVIGATION_STATE_ORBIT`
- `NAVIGATION_STATE_POSCTL`
- `NAVIGATION_STATE_POSITION_SLOW`
- ... 4 more

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as manual_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start manual_control
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
  class ManualControl
  ManualControl : ManualControl.hpp
  class ModuleBase
  ModuleBase <|-- ManualControl
  class CameraMode
  CameraMode : ManualControl.hpp
  class ManualControlSelector
  ManualControlSelector : ManualControlSelector.hpp
  class RcInMode
  RcInMode : ManualControlSelector.hpp
  class TestManualControl
  TestManualControl : ManualControlTest.cpp
  class ManualControl
  ManualControl <|-- TestManualControl
  class SwitchTest
  SwitchTest : ManualControlTest.cpp
  class MovingDiff
  MovingDiff : MovingDiff.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| ManualControl | ModuleBase | ManualControl.hpp |
| CameraMode |  | ManualControl.hpp |
| ManualControlSelector |  | ManualControlSelector.hpp |
| RcInMode |  | ManualControlSelector.hpp |
| TestManualControl | ManualControl | ManualControlTest.cpp |
| SwitchTest |  | ManualControlTest.cpp |
| MovingDiff |  | MovingDiff.hpp |

### Detected Enums

- `CameraMode`
- `RcInMode`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| ManualControl.cpp | source |
| ManualControl.hpp | header |
| ManualControlSelector.cpp | source |
| ManualControlSelector.hpp | header |
| ManualControlSelectorTest.cpp | source |
| ManualControlTest.cpp | source |
| MovingDiff.hpp | header |
| MovingDiffTest.cpp | source |
| manual_control_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
