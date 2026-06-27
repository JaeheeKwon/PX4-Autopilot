# PX4 Module Architecture: `simulation/simulator_mavlink`

- Source: `src/modules/simulation/simulator_mavlink`
- Build target: `modules__simulation__simulator_mavlink`
- Runtime main: `simulator_mavlink`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Source-derived architecture notes for this PX4 module directory.

## Description of Module

Connects PX4 to a MAVLink-based simulator backend.

### Primary Responsibilities

- Generate simulator-facing or simulated sensor/actuator data for non-flight-hardware runs.
- Translate between PX4 uORB data and an external transport or companion-computer interface.
- Consume runtime inputs from uORB topics such as `actuator_outputs`, `actuator_outputs_sim`, `battery_status`, `parameter_update`, `vehicle_attitude`, `vehicle_command`, `vehicle_local_position`, `vehicle_status`.
- Publish outputs or status topics such as `differential_pressure`, `distance_sensor`, `esc_status`, `fiducial_marker_pos_report`, `fiducial_marker_yaw_report`, `input_rc`, `irlock_report`, `landing_target_pose`, ... 11 more.
- Implement the main behavior in classes such as `SensorSource`, `TargetAbsoluteSensorCapability`, `SimulatorMavlink`, `InternetProtocol`.

### Runtime Behavior

- Creates a dedicated PX4 task/thread with `px4_task_spawn_cmd()`.
- Uses a `run()` loop style module body for repeated execution.
- Waits on file descriptors or uORB subscriptions with `px4_poll()`.
- Creates an additional pthread helper context.

## Background Theory

No dedicated mathematical model was identified in the generated source scan. This module is best understood through its PX4 state handling, uORB message flow, scheduling, and configuration surfaces described below.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `actuator_outputs`, `actuator_outputs_sim`, `battery_status`, `parameter_update`, `vehicle_attitude`, `vehicle_command`, `vehicle_local_position`, `vehicle_status` |
| Primary outputs | `differential_pressure`, `distance_sensor`, `esc_status`, `fiducial_marker_pos_report`, `fiducial_marker_yaw_report`, `input_rc`, `irlock_report`, `landing_target_pose`, `rpm`, `sensor_gps`, ... 9 more |
| Referenced topics | `actuator_outputs`, `actuator_outputs_sim`, `battery_status`, `differential_pressure`, `distance_sensor`, `esc_report`, `esc_status`, `fiducial_marker_pos_report`, `fiducial_marker_yaw_report`, `input_rc`, ... 22 more |
| Parameters/config | none detected |
| Key classes | `SensorSource`, `TargetAbsoluteSensorCapability`, `SimulatorMavlink`, `InternetProtocol` |

### Files

| File | Why it matters |
| --- | --- |
| SimulatorMavlink.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| SimulatorMavlink.hpp | Defines `SensorSource` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["simulation/simulator_mavlink"]:::module
  Build["px4 module: modules__simulation__simula..."]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_outputs"]:::io
    In1["actuator_outputs_sim"]:::io
    In2["battery_status"]:::io
    In3["parameter_update"]:::io
    In4["vehicle_attitude"]:::io
    In5["vehicle_command"]:::io
  end
  subgraph Outputs
    Out0["differential_pressure"]:::io
    Out1["distance_sensor"]:::io
    Out2["esc_status"]:::io
    Out3["fiducial_marker_pos_report"]:::io
    Out4["fiducial_marker_yaw_report"]:::io
    Out5["input_rc"]:::io
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
| Module path | src/modules/simulation/simulator_mavlink |
| Build kind | px4 module |
| Build target | modules__simulation__simulator_mavlink |
| Runtime main | simulator_mavlink |
| Stack main | Not specified |
| Module config | Not specified |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 1 |

### CMake Dependencies

- `mavlink_c_generate`
- `conversion`
- `geo`
- `drivers_accelerometer`
- `drivers_barometer`
- `drivers_gyroscope`
- `drivers_magnetometer`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["simulator_mavlink logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_outputs"]:::io --> UORBIn
  Sub1["actuator_outputs_sim"]:::io --> UORBIn
  Sub2["battery_status"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["vehicle_attitude"]:::io --> UORBIn
  UORBOut --> Pub0["differential_pressure"]:::io
  UORBOut --> Pub1["distance_sensor"]:::io
  UORBOut --> Pub2["esc_status"]:::io
  UORBOut --> Pub3["fiducial_marker_pos_report"]:::io
  UORBOut --> Pub4["fiducial_marker_yaw_report"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_outputs | subscribed |
| actuator_outputs_sim | subscribed |
| battery_status | subscribed |
| differential_pressure | published |
| distance_sensor | published |
| esc_report | referenced |
| esc_status | published |
| fiducial_marker_pos_report | published |
| fiducial_marker_yaw_report | published |
| input_rc | published |
| irlock_report | published |
| landing_target_pose | published |
| manual_control_setpoint | referenced |
| parameter_update | subscribed |
| rpm | published |
| sensor_gps | published |
| sensor_optical_flow | published |
| target_gnss | published |
| vehicle_angular_velocity | referenced |
| vehicle_angular_velocity_groundtruth | published |
| vehicle_attitude | subscribed |
| vehicle_attitude_groundtruth | published |
| vehicle_command | subscribed |
| vehicle_command_ack | published |
| vehicle_global_position | referenced |
| vehicle_global_position_groundtruth | published |
| vehicle_local_position | subscribed |
| vehicle_local_position_groundtruth | published |
| vehicle_mocap_odometry | published |
| vehicle_odometry | referenced |
| vehicle_status | subscribed |
| vehicle_visual_odometry | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 simulator_mavlink start"]:::exec
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
  S0: ARMING_STATE_ARMED
  Initialized --> S0: detected state path
  S1: HIL_STATE_QUATERNION
  S0 --> S1: detected state path
  S2: MAVLINK_MSG_ID_HIL_STATE_...
  S1 --> S2: detected state path
  S2 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `HIL_STATE_QUATERNION`
- `MAVLINK_MSG_ID_HIL_STATE_QUATERNION`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as simulator_mavlink
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start simulator_mavlink
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
  class SensorSource
  SensorSource : SimulatorMavlink.hpp
  class TargetAbsoluteSensorCapability
  TargetAbsoluteSensorCapability : SimulatorMavlink.hpp
  class SimulatorMavlink
  SimulatorMavlink : SimulatorMavlink.hpp
  class ModuleParams
  ModuleParams <|-- SimulatorMavlink
  class InternetProtocol
  InternetProtocol : SimulatorMavlink.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| SensorSource |  | SimulatorMavlink.hpp |
| TargetAbsoluteSensorCapability |  | SimulatorMavlink.hpp |
| SimulatorMavlink | ModuleParams | SimulatorMavlink.hpp |
| InternetProtocol |  | SimulatorMavlink.hpp |

### Detected Enums

- `InternetProtocol`
- `SensorSource`
- `TargetAbsoluteSensorCapability`
- `type`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| SimulatorMavlink.cpp | source |
| SimulatorMavlink.hpp | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
