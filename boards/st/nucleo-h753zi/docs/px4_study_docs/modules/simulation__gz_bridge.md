# PX4 Module Architecture: `simulation/gz_bridge`

- Source: `src/modules/simulation/gz_bridge`
- Build target: `modules__simulation__gz_bridge`
- Runtime main: `gz_bridge`
- Build kind: `px4 module`
- Mermaid palette: `ash` grey tone

Architecture notes for the SIM_GZ module.

## Description of Module

Bridges PX4 uORB data with Gazebo transport for simulation.

### Primary Responsibilities

- Generate simulator-facing or simulated sensor/actuator data for non-flight-hardware runs.
- Translate between PX4 uORB data and an external transport or companion-computer interface.
- Consume runtime inputs from uORB topics such as `gimbal_controls`, `gimbal_device_set_attitude`, `parameter_update`, `vehicle_command`.
- Publish outputs or status topics such as `differential_pressure`, `esc_status`, `gimbal_device_attitude_status`, `gimbal_device_information`, `obstacle_distance`, `sensor_gps`, `sensor_optical_flow`, `vehicle_angular_velocity_groundtruth`, ... 6 more.
- Use module configuration from `module.yaml`.
- Implement the main behavior in classes such as `GZBridge`, `GZGimbal`, `GZBridge`, `GZMixingInterfaceESC`, `GZBridge`, `GZMixingInterfaceServo`, ... 3 more.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `rate_ctrl`.
- Uses uORB callback registration so new topic data can schedule execution.
- Uses explicit work-item scheduling through immediate, delayed, or interval scheduling calls.

## Background Theory

No dedicated mathematical model was identified in the generated source scan. This module is best understood through its PX4 state handling, uORB message flow, scheduling, and configuration surfaces described below.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `gimbal_controls`, `gimbal_device_set_attitude`, `parameter_update`, `vehicle_command` |
| Primary outputs | `differential_pressure`, `esc_status`, `gimbal_device_attitude_status`, `gimbal_device_information`, `obstacle_distance`, `sensor_gps`, `sensor_optical_flow`, `vehicle_angular_velocity_groundtruth`, `vehicle_attitude_groundtruth`, `vehicle_command_ack`, ... 4 more |
| Referenced topics | `differential_pressure`, `esc_status`, `gimbal_controls`, `gimbal_device_attitude_status`, `gimbal_device_information`, `gimbal_device_set_attitude`, `obstacle_distance`, `parameter_update`, `sensor_gps`, `sensor_optical_flow`, ... 13 more |
| Parameters/config | module.yaml |
| Key classes | `GZBridge`, `GZGimbal`, `GZBridge`, `GZMixingInterfaceESC`, `GZBridge`, `GZMixingInterfaceServo`, `GZBridge`, `GZMixingInterfaceWheel`, `GZBridge` |

### Files

| File | Why it matters |
| --- | --- |
| GZBridge.cpp | Entry point, start command, or module lifecycle code |
| GZGimbal.cpp | Work-item callback or main runtime update path |
| GZMixingInterfaceESC.cpp | Work-item callback or main runtime update path |
| GZMixingInterfaceServo.cpp | Work-item callback or main runtime update path |
| GZMixingInterfaceWheel.cpp | Work-item callback or main runtime update path |
| CMakeLists.txt | Build, parameter, or module configuration |
| module.yaml | Build, parameter, or module configuration |
| GZBridge.hpp | Defines `GZBridge` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["simulation/gz_bridge"]:::module
  Build["px4 module: modules__simulation__gz_bridge"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["gimbal_controls"]:::io
    In1["gimbal_device_set_attitude"]:::io
    In2["parameter_update"]:::io
    In3["vehicle_command"]:::io
  end
  subgraph Outputs
    Out0["differential_pressure"]:::io
    Out1["esc_status"]:::io
    Out2["gimbal_device_attitude_status"]:::io
    Out3["gimbal_device_information"]:::io
    Out4["obstacle_distance"]:::io
    Out5["sensor_gps"]:::io
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
  Module --> Out3
  Module --> Out4
  Module --> Out5
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/simulation/gz_bridge |
| Build kind | px4 module |
| Build target | modules__simulation__gz_bridge |
| Runtime main | gz_bridge |
| Stack main | Not specified |
| Module config | module.yaml |
| Detected sources | 5 |
| Detected headers | 5 |
| Detected configs | 3 |

### CMake Dependencies

- `drivers_accelerometer`
- `drivers_gyroscope`
- `drivers_magnetometer`
- `drivers_rangefinder`
- `drivers_barometer`
- `mixer_module`
- `px4_work_queue`
- `${GZ_TRANSPORT_TARGET}`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["gz_bridge logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["gimbal_controls"]:::io --> UORBIn
  Sub1["gimbal_device_set_attitude"]:::io --> UORBIn
  Sub2["parameter_update"]:::io --> UORBIn
  Sub3["vehicle_command"]:::io --> UORBIn
  UORBOut --> Pub0["differential_pressure"]:::io
  UORBOut --> Pub1["esc_status"]:::io
  UORBOut --> Pub2["gimbal_device_attitude_status"]:::io
  UORBOut --> Pub3["gimbal_device_information"]:::io
  UORBOut --> Pub4["obstacle_distance"]:::io
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| differential_pressure | published |
| esc_status | published |
| gimbal_controls | subscribed |
| gimbal_device_attitude_status | published |
| gimbal_device_information | published |
| gimbal_device_set_attitude | subscribed |
| obstacle_distance | published |
| parameter_update | subscribed |
| sensor_gps | published |
| sensor_optical_flow | published |
| vehicle_angular_velocity | referenced |
| vehicle_angular_velocity_groundtruth | published |
| vehicle_attitude | referenced |
| vehicle_attitude_groundtruth | published |
| vehicle_command | subscribed |
| vehicle_command_ack | published |
| vehicle_global_position | referenced |
| vehicle_global_position_groundtruth | published |
| vehicle_local_position | referenced |
| vehicle_local_position_groundtruth | published |
| vehicle_odometry | referenced |
| vehicle_visual_odometry | published |
| wheel_encoders | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 gz_bridge start"]:::exec
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
  S0: MNT_MODE_OUT
  Initialized --> S0: detected state path
  S0 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `MNT_MODE_OUT`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as gz_bridge
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start gz_bridge
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
  class GZBridge
  GZBridge : GZBridge.hpp
  class ModuleBase
  ModuleBase <|-- GZBridge
  class GZGimbal
  GZGimbal : GZGimbal.hpp
  class ScheduledWorkItem
  ScheduledWorkItem <|-- GZGimbal
  class GZBridge_2
  GZBridge_2 : GZGimbal.hpp
  class GZMixingInterfaceESC
  GZMixingInterfaceESC : GZMixingInterfaceESC.hpp
  class OutputModuleInterface
  OutputModuleInterface <|-- GZMixingInterfaceESC
  class GZBridge_4
  GZBridge_4 : GZMixingInterfaceESC.hpp
  class GZMixingInterfaceServo
  GZMixingInterfaceServo : GZMixingInterfaceServo.hpp
  class OutputModuleInterface
  OutputModuleInterface <|-- GZMixingInterfaceServo
  class GZBridge_6
  GZBridge_6 : GZMixingInterfaceServo.hpp
  class GZMixingInterfaceWheel
  GZMixingInterfaceWheel : GZMixingInterfaceWheel.hpp
  class OutputModuleInterface
  OutputModuleInterface <|-- GZMixingInterfaceWheel
  class GZBridge_8
  GZBridge_8 : GZMixingInterfaceWheel.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| GZBridge | ModuleBase | GZBridge.hpp |
| GZGimbal | ScheduledWorkItem | GZGimbal.hpp |
| GZBridge |  | GZGimbal.hpp |
| GZMixingInterfaceESC | OutputModuleInterface | GZMixingInterfaceESC.hpp |
| GZBridge |  | GZMixingInterfaceESC.hpp |
| GZMixingInterfaceServo | OutputModuleInterface | GZMixingInterfaceServo.hpp |
| GZBridge |  | GZMixingInterfaceServo.hpp |
| GZMixingInterfaceWheel | OutputModuleInterface | GZMixingInterfaceWheel.hpp |
| GZBridge |  | GZMixingInterfaceWheel.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| GZBridge.cpp | source |
| GZBridge.hpp | header |
| GZGimbal.cpp | source |
| GZGimbal.hpp | header |
| GZMixingInterfaceESC.cpp | source |
| GZMixingInterfaceESC.hpp | header |
| GZMixingInterfaceServo.cpp | source |
| GZMixingInterfaceServo.hpp | header |
| GZMixingInterfaceWheel.cpp | source |
| GZMixingInterfaceWheel.hpp | header |
| module.yaml | config |
| parameters.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
