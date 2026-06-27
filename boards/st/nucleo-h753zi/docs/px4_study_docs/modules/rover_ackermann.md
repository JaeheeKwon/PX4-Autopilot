# PX4 Module Architecture: `rover_ackermann`

- Source: `src/modules/rover_ackermann`
- Build target: `modules__rover_ackermann`
- Runtime main: `rover_ackermann`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Architecture notes for the Rover Ackermann module.

## Description of Module

Controls Ackermann-steered rover motion from rover setpoints to actuator commands.

### Primary Responsibilities

- Consume runtime inputs from uORB topics such as `actuator_motors`, `actuator_servos`, `manual_control_setpoint`, `offboard_control_mode`, `parameter_update`, `position_controller_status`, `position_setpoint_triplet`, `rover_attitude_setpoint`, ... 11 more.
- Publish outputs or status topics such as `actuator_motors`, `actuator_servos`, `position_controller_status`, `pure_pursuit_status`, `rover_attitude_setpoint`, `rover_attitude_status`, `rover_position_setpoint`, `rover_rate_setpoint`, ... 5 more.
- Use module configuration from `module.yaml`.
- Implement the main behavior in classes such as `AckermannActControl`, `AckermannAttControl`, `AckermannAutoMode`, `AckermannManualMode`, `AckermannOffboardMode`, `AckermannPosControl`, ... 3 more.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `rate_ctrl`.
- Uses explicit work-item scheduling through immediate, delayed, or interval scheduling calls.

## Background Theory

Ackermann rover control uses car-like planar kinematics. Steering angle is related to path curvature and yaw rate by the wheelbase.

```text
curvature = yaw_rate_sp / max(speed_sp, epsilon)
steering_angle = atan(wheelbase * curvature)
yaw_rate = speed / wheelbase * tan(steering_angle)
throttle = K_speed * (speed_sp - speed) + feedforward(speed_sp)
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `actuator_motors`, `actuator_servos`, `manual_control_setpoint`, `offboard_control_mode`, `parameter_update`, `position_controller_status`, `position_setpoint_triplet`, `rover_attitude_setpoint`, `rover_position_setpoint`, `rover_rate_setpoint`, ... 9 more |
| Primary outputs | `actuator_motors`, `actuator_servos`, `position_controller_status`, `pure_pursuit_status`, `rover_attitude_setpoint`, `rover_attitude_status`, `rover_position_setpoint`, `rover_rate_setpoint`, `rover_rate_status`, `rover_speed_setpoint`, ... 3 more |
| Referenced topics | `actuator_motors`, `actuator_servos`, `manual_control_setpoint`, `offboard_control_mode`, `parameter_update`, `position_controller_status`, `position_setpoint_triplet`, `pure_pursuit_status`, `rover_attitude_setpoint`, `rover_attitude_status`, ... 13 more |
| Parameters/config | module.yaml |
| Key classes | `AckermannActControl`, `AckermannAttControl`, `AckermannAutoMode`, `AckermannManualMode`, `AckermannOffboardMode`, `AckermannPosControl`, `AckermannRateControl`, `AckermannSpeedControl`, `RoverAckermann` |

### Files

| File | Why it matters |
| --- | --- |
| RoverAckermann.cpp | Entry point, start command, or module lifecycle code |
| AckermannActControl/CMakeLists.txt | Build, parameter, or module configuration |
| AckermannAttControl/CMakeLists.txt | Build, parameter, or module configuration |
| AckermannDriveModes/AckermannAutoMode/CMakeLists.txt | Build, parameter, or module configuration |
| AckermannDriveModes/AckermannManualMode/CMakeLists.txt | Build, parameter, or module configuration |
| AckermannDriveModes/AckermannOffboardMode/CMakeLists.txt | Build, parameter, or module configuration |
| AckermannDriveModes/CMakeLists.txt | Build, parameter, or module configuration |
| AckermannActControl/AckermannActControl.hpp | Defines `AckermannActControl` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["rover_ackermann"]:::module
  Build["px4 module: modules__rover_ackermann"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_motors"]:::io
    In1["actuator_servos"]:::io
    In2["manual_control_setpoint"]:::io
    In3["offboard_control_mode"]:::io
    In4["parameter_update"]:::io
    In5["position_controller_status"]:::io
  end
  subgraph Outputs
    Out0["actuator_motors"]:::io
    Out1["actuator_servos"]:::io
    Out2["position_controller_status"]:::io
    Out3["pure_pursuit_status"]:::io
    Out4["rover_attitude_setpoint"]:::io
    Out5["rover_attitude_status"]:::io
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
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/rover_ackermann |
| Build kind | px4 module |
| Build target | modules__rover_ackermann |
| Runtime main | rover_ackermann |
| Stack main | Not specified |
| Module config | module.yaml |
| Detected sources | 9 |
| Detected headers | 9 |
| Detected configs | 11 |

### CMake Dependencies

- `AckermannActControl`
- `AckermannRateControl`
- `AckermannAttControl`
- `AckermannSpeedControl`
- `AckermannPosControl`
- `AckermannAutoMode`
- `AckermannManualMode`
- `AckermannOffboardMode`
- `px4_work_queue`
- `rover_control`
- `pure_pursuit`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["rover_ackermann logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_motors"]:::io --> UORBIn
  Sub1["actuator_servos"]:::io --> UORBIn
  Sub2["manual_control_setpoint"]:::io --> UORBIn
  Sub3["offboard_control_mode"]:::io --> UORBIn
  Sub4["parameter_update"]:::io --> UORBIn
  UORBOut --> Pub0["actuator_motors"]:::io
  UORBOut --> Pub1["actuator_servos"]:::io
  UORBOut --> Pub2["position_controller_status"]:::io
  UORBOut --> Pub3["pure_pursuit_status"]:::io
  UORBOut --> Pub4["rover_attitude_setpoint"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_motors | subscribed, published |
| actuator_servos | subscribed, published |
| manual_control_setpoint | subscribed |
| offboard_control_mode | subscribed |
| parameter_update | subscribed |
| position_controller_status | subscribed, published |
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 rover_ackermann start"]:::exec
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as rover_ackermann
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start rover_ackermann
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
  class AckermannActControl
  AckermannActControl : AckermannActControl/AckermannActControl.hpp
  class ModuleParams
  ModuleParams <|-- AckermannActControl
  class AckermannAttControl
  AckermannAttControl : AckermannAttControl/AckermannAttControl.hpp
  class ModuleParams
  ModuleParams <|-- AckermannAttControl
  class AckermannAutoMode
  AckermannAutoMode : AckermannDriveModes/AckermannAutoMode/AckermannAuto...
  class ModuleParams
  ModuleParams <|-- AckermannAutoMode
  class AckermannManualMode
  AckermannManualMode : AckermannDriveModes/AckermannManualMode/AckermannMa...
  class ModuleParams
  ModuleParams <|-- AckermannManualMode
  class AckermannOffboardMode
  AckermannOffboardMode : AckermannDriveModes/AckermannOffboardMode/Ackermann...
  class ModuleParams
  ModuleParams <|-- AckermannOffboardMode
  class AckermannPosControl
  AckermannPosControl : AckermannPosControl/AckermannPosControl.hpp
  class ModuleParams
  ModuleParams <|-- AckermannPosControl
  class AckermannRateControl
  AckermannRateControl : AckermannRateControl/AckermannRateControl.hpp
  class ModuleParams
  ModuleParams <|-- AckermannRateControl
  class AckermannSpeedControl
  AckermannSpeedControl : AckermannSpeedControl/AckermannSpeedControl.hpp
  class ModuleParams
  ModuleParams <|-- AckermannSpeedControl
  class RoverAckermann
  RoverAckermann : RoverAckermann.hpp
  class ModuleBase
  ModuleBase <|-- RoverAckermann
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| AckermannActControl | ModuleParams | AckermannActControl/AckermannActControl.hpp |
| AckermannAttControl | ModuleParams | AckermannAttControl/AckermannAttControl.hpp |
| AckermannAutoMode | ModuleParams | AckermannDriveModes/AckermannAutoMode/AckermannAutoMode.hpp |
| AckermannManualMode | ModuleParams | AckermannDriveModes/AckermannManualMode/AckermannManualMode.hpp |
| AckermannOffboardMode | ModuleParams | AckermannDriveModes/AckermannOffboardMode/AckermannOffboardMode.hpp |
| AckermannPosControl | ModuleParams | AckermannPosControl/AckermannPosControl.hpp |
| AckermannRateControl | ModuleParams | AckermannRateControl/AckermannRateControl.hpp |
| AckermannSpeedControl | ModuleParams | AckermannSpeedControl/AckermannSpeedControl.hpp |
| RoverAckermann | ModuleBase | RoverAckermann.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| AckermannActControl/AckermannActControl.cpp | source |
| AckermannActControl/AckermannActControl.hpp | header |
| AckermannActControl/CMakeLists.txt | build |
| AckermannAttControl/AckermannAttControl.cpp | source |
| AckermannAttControl/AckermannAttControl.hpp | header |
| AckermannAttControl/CMakeLists.txt | build |
| AckermannDriveModes/AckermannAutoMode/AckermannAutoMode.cpp | source |
| AckermannDriveModes/AckermannAutoMode/AckermannAutoMode.hpp | header |
| AckermannDriveModes/AckermannAutoMode/CMakeLists.txt | build |
| AckermannDriveModes/AckermannManualMode/AckermannManualMode.cpp | source |
| AckermannDriveModes/AckermannManualMode/AckermannManualMode.hpp | header |
| AckermannDriveModes/AckermannManualMode/CMakeLists.txt | build |
| AckermannDriveModes/AckermannOffboardMode/AckermannOffboardMode.cpp | source |
| AckermannDriveModes/AckermannOffboardMode/AckermannOffboardMode.hpp | header |
| AckermannDriveModes/AckermannOffboardMode/CMakeLists.txt | build |
| AckermannDriveModes/CMakeLists.txt | build |
| AckermannPosControl/AckermannPosControl.cpp | source |
| AckermannPosControl/AckermannPosControl.hpp | header |
| AckermannPosControl/CMakeLists.txt | build |
| AckermannRateControl/AckermannRateControl.cpp | source |
| AckermannRateControl/AckermannRateControl.hpp | header |
| AckermannRateControl/CMakeLists.txt | build |
| AckermannSpeedControl/AckermannSpeedControl.cpp | source |
| AckermannSpeedControl/AckermannSpeedControl.hpp | header |
| AckermannSpeedControl/CMakeLists.txt | build |
| CMakeLists.txt | build |
| RoverAckermann.cpp | source |
| RoverAckermann.hpp | header |
| module.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
