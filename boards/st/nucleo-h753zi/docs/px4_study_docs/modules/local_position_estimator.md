# PX4 Module Architecture: `local_position_estimator`

- Source: `src/modules/local_position_estimator`
- Build target: `modules__local_position_estimator`
- Runtime main: `local_position_estimator`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["local_position_estimator"]:::module
  Build["px4 module: modules__local_position_est..."]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_armed"]:::io
    In1["distance_sensor"]:::io
    In2["landing_target_pose"]:::io
    In3["parameter_update"]:::io
    In4["sensor_combined"]:::io
    In5["vehicle_air_data"]:::io
  end
  subgraph Outputs
    Out0["estimator_innovation_variances"]:::io
    Out1["estimator_innovations"]:::io
    Out2["estimator_states"]:::io
    Out3["estimator_status"]:::io
    Out4["vehicle_global_position"]:::io
    Out5["vehicle_local_position"]:::io
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
| Module path | src/modules/local_position_estimator |
| Build kind | px4 module |
| Build target | modules__local_position_estimator |
| Runtime main | local_position_estimator |
| Stack main | 5700 |
| Module config | params.yaml |
| Detected sources | 10 |
| Detected headers | 1 |
| Detected configs | 2 |

### CMake Dependencies

- `controllib`
- `geo`
- `px4_work_queue`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["local_position_estimator logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_armed"]:::io --> UORBIn
  Sub1["distance_sensor"]:::io --> UORBIn
  Sub2["landing_target_pose"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["sensor_combined"]:::io --> UORBIn
  UORBOut --> Pub0["estimator_innovation_variances"]:::io
  UORBOut --> Pub1["estimator_innovations"]:::io
  UORBOut --> Pub2["estimator_states"]:::io
  UORBOut --> Pub3["estimator_status"]:::io
  UORBOut --> Pub4["vehicle_global_position"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_armed | subscribed |
| distance_sensor | subscribed |
| estimator_innovation_variances | published |
| estimator_innovations | published |
| estimator_states | published |
| estimator_status | published |
| landing_target_pose | subscribed |
| parameter_update | subscribed |
| sensor_combined | subscribed |
| sensor_gps | referenced |
| vehicle_air_data | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | referenced |
| vehicle_command | subscribed |
| vehicle_control_mode | referenced |
| vehicle_global_position | published |
| vehicle_gps_position | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed, published |
| vehicle_mocap_odometry | subscribed |
| vehicle_odometry | published |
| vehicle_optical_flow | subscribed |
| vehicle_status | referenced |
| vehicle_visual_odometry | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 local_position_estimator start"]:::exec
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as local_position_estimator
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start local_position_estimator
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
  class BlockLocalPositionEstimator
  BlockLocalPositionEstimator : BlockLocalPositionEstimator.hpp
  class ModuleBase
  ModuleBase <|-- BlockLocalPositionEstimator
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| BlockLocalPositionEstimator | ModuleBase | BlockLocalPositionEstimator.hpp |

### Detected Enums

- `estimate_t`
- `sensor_t`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| BlockLocalPositionEstimator.cpp | source |
| BlockLocalPositionEstimator.hpp | header |
| CMakeLists.txt | build |
| params.yaml | config |
| sensors/baro.cpp | source |
| sensors/flow.cpp | source |
| sensors/gps.cpp | source |
| sensors/land.cpp | source |
| sensors/landing_target.cpp | source |
| sensors/lidar.cpp | source |
| sensors/mocap.cpp | source |
| sensors/sonar.cpp | source |
| sensors/vision.cpp | source |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
