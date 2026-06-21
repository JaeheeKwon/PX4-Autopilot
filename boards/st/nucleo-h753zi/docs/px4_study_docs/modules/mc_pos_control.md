# PX4 Module Architecture: `mc_pos_control`

- Source: `src/modules/mc_pos_control`
- Build target: `modules__mc_pos_control`
- Runtime main: `mc_pos_control`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["mc_pos_control"]:::module
  Build["px4 module: modules__mc_pos_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["goto_setpoint"]:::io
    In1["hover_thrust_estimate"]:::io
    In2["parameter_update"]:::io
    In3["trajectory_setpoint"]:::io
    In4["vehicle_constraints"]:::io
    In5["vehicle_control_mode"]:::io
  end
  subgraph Outputs
    Out0["mc_virtual_attitude_setpoint"]:::io
    Out1["takeoff_status"]:::io
    Out2["trajectory_setpoint"]:::io
    Out3["vehicle_attitude_setpoint"]:::io
    Out4["vehicle_constraints"]:::io
    Out5["vehicle_local_position_setpoint"]:::io
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
  Module --> Out2
  Module --> Out3
  Module --> Out4
  Module --> Out5
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/mc_pos_control |
| Build kind | px4 module |
| Build target | modules__mc_pos_control |
| Runtime main | mc_pos_control |
| Stack main | Not specified |
| Module config | multicopter_altitude_mode_params.yaml |
| Detected sources | 8 |
| Detected headers | 5 |
| Detected configs | 14 |

### CMake Dependencies

- `GotoControl`
- `PositionControl`
- `Takeoff`
- `controllib`
- `geo`
- `SlewRate`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["mc_pos_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["goto_setpoint"]:::io --> UORBIn
  Sub1["hover_thrust_estimate"]:::io --> UORBIn
  Sub2["parameter_update"]:::io --> UORBIn
  Sub3["trajectory_setpoint"]:::io --> UORBIn
  Sub4["vehicle_constraints"]:::io --> UORBIn
  UORBOut --> Pub0["mc_virtual_attitude_setpoint"]:::io
  UORBOut --> Pub1["takeoff_status"]:::io
  UORBOut --> Pub2["trajectory_setpoint"]:::io
  UORBOut --> Pub3["vehicle_attitude_setpoint"]:::io
  UORBOut --> Pub4["vehicle_constraints"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| goto_setpoint | subscribed |
| hover_thrust_estimate | subscribed |
| mc_virtual_attitude_setpoint | published |
| parameter_update | subscribed |
| takeoff_status | published |
| trajectory_setpoint | subscribed, published |
| vehicle_attitude_setpoint | published |
| vehicle_constraints | subscribed, published |
| vehicle_control_mode | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_local_position_setpoint | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 mc_pos_control start"]:::exec
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
  S0: MPC_ALT_MODE
  Initialized --> S0: detected state path
  S1: TAKEOFF_STATE_DISARMED
  S0 --> S1: detected state path
  S2: TAKEOFF_STATE_FLIGHT
  S1 --> S2: detected state path
  S3: TAKEOFF_STATE_RAMPUP
  S2 --> S3: detected state path
  S4: TAKEOFF_STATE_READY_FOR_T...
  S3 --> S4: detected state path
  S5: TAKEOFF_STATE_SPOOLUP
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `MPC_ALT_MODE`
- `TAKEOFF_STATE_DISARMED`
- `TAKEOFF_STATE_FLIGHT`
- `TAKEOFF_STATE_RAMPUP`
- `TAKEOFF_STATE_READY_FOR_TAKEOFF`
- `TAKEOFF_STATE_SPOOLUP`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as mc_pos_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start mc_pos_control
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
  class which
  which : GotoControl/GotoControl.hpp
  class GotoControl
  GotoControl : GotoControl/GotoControl.hpp
  class MulticopterPositionControl
  MulticopterPositionControl : MulticopterPositionControl.hpp
  class ModuleBase
  ModuleBase <|-- MulticopterPositionControl
  class contains
  contains : PositionControl/PositionControl.hpp
  class PositionControl
  PositionControl : PositionControl/PositionControl.hpp
  class PositionControlBasicTest
  PositionControlBasicTest : PositionControl/PositionControlTest.cpp
  class PositionControlBasicDirectionTest
  PositionControlBasicDirectionTest : PositionControl/PositionControlTest.cpp
  class PositionControlBasicTest
  PositionControlBasicTest <|-- PositionControlBasicDirectionTest
  class handling
  handling : Takeoff/Takeoff.hpp
  class TakeoffState
  TakeoffState : Takeoff/Takeoff.hpp
  class TakeoffHandling
  TakeoffHandling : Takeoff/Takeoff.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| which |  | GotoControl/GotoControl.hpp |
| GotoControl |  | GotoControl/GotoControl.hpp |
| MulticopterPositionControl | ModuleBase | MulticopterPositionControl.hpp |
| contains |  | PositionControl/PositionControl.hpp |
| PositionControl |  | PositionControl/PositionControl.hpp |
| PositionControlBasicTest |  | PositionControl/PositionControlTest.cpp |
| PositionControlBasicDirectionTest | PositionControlBasicTest | PositionControl/PositionControlTest.cpp |
| handling |  | Takeoff/Takeoff.hpp |
| TakeoffState |  | Takeoff/Takeoff.hpp |
| TakeoffHandling |  | Takeoff/Takeoff.hpp |

### Detected Enums

- `TakeoffState`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| GotoControl/CMakeLists.txt | build |
| GotoControl/GotoControl.cpp | source |
| GotoControl/GotoControl.hpp | header |
| MulticopterPositionControl.cpp | source |
| MulticopterPositionControl.hpp | header |
| PositionControl/CMakeLists.txt | build |
| PositionControl/ControlMath.cpp | source |
| PositionControl/ControlMath.hpp | header |
| PositionControl/ControlMathTest.cpp | source |
| PositionControl/PositionControl.cpp | source |
| PositionControl/PositionControl.hpp | header |
| PositionControl/PositionControlTest.cpp | source |
| Takeoff/CMakeLists.txt | build |
| Takeoff/Takeoff.cpp | source |
| Takeoff/Takeoff.hpp | header |
| Takeoff/TakeoffTest.cpp | source |
| multicopter_altitude_mode_params.yaml | config |
| multicopter_autonomous_params.yaml | config |
| multicopter_nudging_params.yaml | config |
| multicopter_position_control_gain_params.yaml | config |
| multicopter_position_control_limits_params.yaml | config |
| multicopter_position_control_params.yaml | config |
| multicopter_position_mode_params.yaml | config |
| multicopter_responsiveness_params.yaml | config |
| multicopter_stabilized_mode_params.yaml | config |
| multicopter_takeoff_land_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
