# PX4 Module Architecture: `rover_differential`

- Source: `src/modules/rover_differential`
- Build target: `modules__rover_differential`
- Runtime main: `rover_differential`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Architecture notes for the Rover Differential module.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["rover_differential"]:::module
  Build["px4 module: modules__rover_differential"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_motors"]:::io
    In1["manual_control_setpoint"]:::io
    In2["offboard_control_mode"]:::io
    In3["parameter_update"]:::io
    In4["position_setpoint_triplet"]:::io
    In5["rover_attitude_setpoint"]:::io
  end
  subgraph Outputs
    Out0["actuator_motors"]:::io
    Out1["pure_pursuit_status"]:::io
    Out2["rover_attitude_setpoint"]:::io
    Out3["rover_attitude_status"]:::io
    Out4["rover_position_setpoint"]:::io
    Out5["rover_rate_setpoint"]:::io
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
| Module path | src/modules/rover_differential |
| Build kind | px4 module |
| Build target | modules__rover_differential |
| Runtime main | rover_differential |
| Stack main | Not specified |
| Module config | module.yaml |
| Detected sources | 9 |
| Detected headers | 9 |
| Detected configs | 11 |

### CMake Dependencies

- `DifferentialActControl`
- `DifferentialRateControl`
- `DifferentialAttControl`
- `DifferentialSpeedControl`
- `DifferentialPosControl`
- `DifferentialAutoMode`
- `DifferentialManualMode`
- `DifferentialOffboardMode`
- `px4_work_queue`
- `rover_control`
- `pure_pursuit`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["rover_differential logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_motors"]:::io --> UORBIn
  Sub1["manual_control_setpoint"]:::io --> UORBIn
  Sub2["offboard_control_mode"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["position_setpoint_triplet"]:::io --> UORBIn
  UORBOut --> Pub0["actuator_motors"]:::io
  UORBOut --> Pub1["pure_pursuit_status"]:::io
  UORBOut --> Pub2["rover_attitude_setpoint"]:::io
  UORBOut --> Pub3["rover_attitude_status"]:::io
  UORBOut --> Pub4["rover_position_setpoint"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_motors | subscribed, published |
| manual_control_setpoint | subscribed |
| offboard_control_mode | subscribed |
| parameter_update | subscribed |
| position_setpoint_triplet | subscribed |
| pure_pursuit_status | published |
| rover_attitude_setpoint | subscribed, published |
| rover_attitude_status | published |
| rover_position_setpoint | subscribed, published |
| rover_rate_setpoint | subscribed, published |
| rover_rate_status | published |
| rover_speed_setpoint | subscribed, published |
| rover_speed_status | published |
| rover_steering_setpoint | subscribed, published |
| rover_throttle_setpoint | subscribed, published |
| trajectory_setpoint | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_control_mode | subscribed |
| vehicle_local_position | subscribed |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 rover_differential start"]:::exec
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
  S0: NAVIGATION_STATE_ACRO
  Initialized --> S0: detected state path
  S1: NAVIGATION_STATE_AUTO_LOITER
  S0 --> S1: detected state path
  S2: NAVIGATION_STATE_AUTO_MIS...
  S1 --> S2: detected state path
  S3: NAVIGATION_STATE_AUTO_RTL
  S2 --> S3: detected state path
  S4: NAVIGATION_STATE_MANUAL
  S3 --> S4: detected state path
  S5: NAVIGATION_STATE_OFFBOARD
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `NAVIGATION_STATE_ACRO`
- `NAVIGATION_STATE_AUTO_LOITER`
- `NAVIGATION_STATE_AUTO_MISSION`
- `NAVIGATION_STATE_AUTO_RTL`
- `NAVIGATION_STATE_MANUAL`
- `NAVIGATION_STATE_OFFBOARD`
- `NAVIGATION_STATE_POSCTL`
- `NAVIGATION_STATE_STAB`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as rover_differential
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start rover_differential
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
  class DifferentialActControl
  DifferentialActControl : DifferentialActControl/DifferentialActControl.hpp
  class ModuleParams
  ModuleParams <|-- DifferentialActControl
  class DifferentialAttControl
  DifferentialAttControl : DifferentialAttControl/DifferentialAttControl.hpp
  class ModuleParams
  ModuleParams <|-- DifferentialAttControl
  class DifferentialAutoMode
  DifferentialAutoMode : DifferentialDriveModes/DifferentialAutoMode/Differe...
  class ModuleParams
  ModuleParams <|-- DifferentialAutoMode
  class DifferentialManualMode
  DifferentialManualMode : DifferentialDriveModes/DifferentialManualMode/Diffe...
  class ModuleParams
  ModuleParams <|-- DifferentialManualMode
  class DifferentialOffboardMode
  DifferentialOffboardMode : DifferentialDriveModes/DifferentialOffboardMode/Dif...
  class ModuleParams
  ModuleParams <|-- DifferentialOffboardMode
  class DrivingState
  DrivingState : DifferentialPosControl/DifferentialPosControl.hpp
  class DifferentialPosControl
  DifferentialPosControl : DifferentialPosControl/DifferentialPosControl.hpp
  class ModuleParams
  ModuleParams <|-- DifferentialPosControl
  class DifferentialRateControl
  DifferentialRateControl : DifferentialRateControl/DifferentialRateControl.hpp
  class ModuleParams
  ModuleParams <|-- DifferentialRateControl
  class DifferentialSpeedControl
  DifferentialSpeedControl : DifferentialSpeedControl/DifferentialSpeedControl.hpp
  class ModuleParams
  ModuleParams <|-- DifferentialSpeedControl
  class RoverDifferential
  RoverDifferential : RoverDifferential.hpp
  class ModuleBase
  ModuleBase <|-- RoverDifferential
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| DifferentialActControl | ModuleParams | DifferentialActControl/DifferentialActControl.hpp |
| DifferentialAttControl | ModuleParams | DifferentialAttControl/DifferentialAttControl.hpp |
| DifferentialAutoMode | ModuleParams | DifferentialDriveModes/DifferentialAutoMode/DifferentialAutoMode.hpp |
| DifferentialManualMode | ModuleParams | DifferentialDriveModes/DifferentialManualMode/DifferentialManualMode.hpp |
| DifferentialOffboardMode | ModuleParams | DifferentialDriveModes/DifferentialOffboardMode/DifferentialOffboardMode.hpp |
| DrivingState |  | DifferentialPosControl/DifferentialPosControl.hpp |
| DifferentialPosControl | ModuleParams | DifferentialPosControl/DifferentialPosControl.hpp |
| DifferentialRateControl | ModuleParams | DifferentialRateControl/DifferentialRateControl.hpp |
| DifferentialSpeedControl | ModuleParams | DifferentialSpeedControl/DifferentialSpeedControl.hpp |
| RoverDifferential | ModuleBase | RoverDifferential.hpp |

### Detected Enums

- `DrivingState`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| DifferentialActControl/CMakeLists.txt | build |
| DifferentialActControl/DifferentialActControl.cpp | source |
| DifferentialActControl/DifferentialActControl.hpp | header |
| DifferentialAttControl/CMakeLists.txt | build |
| DifferentialAttControl/DifferentialAttControl.cpp | source |
| DifferentialAttControl/DifferentialAttControl.hpp | header |
| DifferentialDriveModes/CMakeLists.txt | build |
| DifferentialDriveModes/DifferentialAutoMode/CMakeLists.txt | build |
| DifferentialDriveModes/DifferentialAutoMode/DifferentialAutoMode.cpp | source |
| DifferentialDriveModes/DifferentialAutoMode/DifferentialAutoMode.hpp | header |
| DifferentialDriveModes/DifferentialManualMode/CMakeLists.txt | build |
| DifferentialDriveModes/DifferentialManualMode/DifferentialManualMode.cpp | source |
| DifferentialDriveModes/DifferentialManualMode/DifferentialManualMode.hpp | header |
| DifferentialDriveModes/DifferentialOffboardMode/CMakeLists.txt | build |
| DifferentialDriveModes/DifferentialOffboardMode/DifferentialOffboardMode.cpp | source |
| DifferentialDriveModes/DifferentialOffboardMode/DifferentialOffboardMode.hpp | header |
| DifferentialPosControl/CMakeLists.txt | build |
| DifferentialPosControl/DifferentialPosControl.cpp | source |
| DifferentialPosControl/DifferentialPosControl.hpp | header |
| DifferentialRateControl/CMakeLists.txt | build |
| DifferentialRateControl/DifferentialRateControl.cpp | source |
| DifferentialRateControl/DifferentialRateControl.hpp | header |
| DifferentialSpeedControl/CMakeLists.txt | build |
| DifferentialSpeedControl/DifferentialSpeedControl.cpp | source |
| DifferentialSpeedControl/DifferentialSpeedControl.hpp | header |
| RoverDifferential.cpp | source |
| RoverDifferential.hpp | header |
| module.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
