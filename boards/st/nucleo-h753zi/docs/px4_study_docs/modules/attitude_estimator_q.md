# PX4 Module Architecture: `attitude_estimator_q`

- Source: `src/modules/attitude_estimator_q`
- Build target: `modules__attitude_estimator_q`
- Runtime main: `attitude_estimator_q`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Attitude estimator q.

## Description of Module

Provides a lightweight quaternion attitude estimator using IMU and aiding data.

### Primary Responsibilities

- Fuse, filter, or validate measurements into estimated state outputs for other modules.
- Consume runtime inputs from uORB topics such as `parameter_update`, `sensor_combined`, `vehicle_attitude`, `vehicle_gps_position`, `vehicle_local_position`, `vehicle_magnetometer`, `vehicle_mocap_odometry`, `vehicle_visual_odometry`.
- Publish outputs or status topics such as `vehicle_attitude`.
- Use module configuration from `attitude_estimator_q_params.yaml`.
- Implement the main behavior in classes such as `AttitudeEstimatorQ`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `nav_and_controllers`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

This module is a quaternion complementary attitude estimator. Gyro integration predicts attitude, while accelerometer, magnetometer, or external heading corrections slowly pull the quaternion back to observed gravity/heading.

```text
q_pred = q[k-1] * exp(0.5 * (omega - bias) * dt)
e_acc = normalize(accel_body) x gravity_body_pred
e_mag = heading_measured - heading_pred
omega_corr = omega + w_acc*e_acc + w_mag*e_mag
bias[k] = bias[k-1] - w_bias * e_acc * dt
q[k] = normalize(q[k-1] * exp(0.5 * omega_corr * dt))
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `parameter_update`, `sensor_combined`, `vehicle_attitude`, `vehicle_gps_position`, `vehicle_local_position`, `vehicle_magnetometer`, `vehicle_mocap_odometry`, `vehicle_visual_odometry` |
| Primary outputs | `vehicle_attitude` |
| Referenced topics | `parameter_update`, `sensor_combined`, `sensor_gps`, `vehicle_attitude`, `vehicle_gps_position`, `vehicle_local_position`, `vehicle_magnetometer`, `vehicle_mocap_odometry`, `vehicle_odometry`, `vehicle_visual_odometry` |
| Parameters/config | attitude_estimator_q_params.yaml |
| Key classes | `AttitudeEstimatorQ` |

### Files

| File | Why it matters |
| --- | --- |
| attitude_estimator_q_main.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| attitude_estimator_q_params.yaml | Build, parameter, or module configuration |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["attitude_estimator_q"]:::module
  Build["px4 module: modules__attitude_estimator_q"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["parameter_update"]:::io
    In1["sensor_combined"]:::io
    In2["vehicle_attitude"]:::io
    In3["vehicle_gps_position"]:::io
    In4["vehicle_local_position"]:::io
    In5["vehicle_magnetometer"]:::io
  end
  subgraph Outputs
    Out0["vehicle_attitude"]:::io
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
| Module path | src/modules/attitude_estimator_q |
| Build kind | px4 module |
| Build target | modules__attitude_estimator_q |
| Runtime main | attitude_estimator_q |
| Stack main | Not specified |
| Module config | attitude_estimator_q_params.yaml |
| Detected sources | 1 |
| Detected headers | 0 |
| Detected configs | 2 |

### CMake Dependencies

- `world_magnetic_model`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["attitude_estimator_q logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["parameter_update"]:::io --> UORBIn
  Sub1["sensor_combined"]:::io --> UORBIn
  Sub2["vehicle_attitude"]:::io --> UORBIn
  Sub3["vehicle_gps_position"]:::io --> UORBIn
  Sub4["vehicle_local_position"]:::io --> UORBIn
  UORBOut --> Pub0["vehicle_attitude"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| parameter_update | subscribed |
| sensor_combined | subscribed |
| sensor_gps | referenced |
| vehicle_attitude | subscribed, published |
| vehicle_gps_position | subscribed |
| vehicle_local_position | subscribed |
| vehicle_magnetometer | subscribed |
| vehicle_mocap_odometry | subscribed |
| vehicle_odometry | referenced |
| vehicle_visual_odometry | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 attitude_estimator_q start"]:::exec
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
  Initialized --> Running: init complete
  Running --> Updating: new data or timer
  Updating --> Publishing: output ready
  Publishing --> Running: wait next cycle
  Running --> Error: health or IO failure
  Error --> Running: recovered
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- No state-like symbols detected.

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as attitude_estimator_q
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start attitude_estimator_q
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
  class AttitudeEstimatorQ
  AttitudeEstimatorQ : attitude_estimator_q_main.cpp
  class ModuleBase
  ModuleBase <|-- AttitudeEstimatorQ
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| AttitudeEstimatorQ | ModuleBase | attitude_estimator_q_main.cpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| attitude_estimator_q_main.cpp | source |
| attitude_estimator_q_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
