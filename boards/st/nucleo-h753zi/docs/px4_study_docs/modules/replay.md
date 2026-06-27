# PX4 Module Architecture: `replay`

- Source: `src/modules/replay`
- Build target: `modules__replay`
- Runtime main: `replay`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

This module is used to replay ULog files. There are 2 environment variables used for configuration: `replay`, which must be set to an ULog file name - it's the log file to be replayed. The second is the mode, specified via `replay_mode`: - `replay_mode=ekf2`: specific EKF2 replay mode. It can only be used with the ekf2 module, but allows the replay to run as fast as possible. - Generic otherwise: this can be used to replay any module(s), but the replay will be done with the same speed as the log was recorded. The m

## Description of Module

Replays logged sensor and uORB data through PX4 modules for estimator and analysis workflows.

### Primary Responsibilities

- Provide persistence, replay, or data-recording services used by other PX4 modules.
- Reference uORB topics such as `airspeed`, `airspeed_validated`, `aux_global_position`, `distance_sensor`, `ekf2_timestamps`, `landing_target_pose`, `ranging_beacon`, `sensor_combined`, ... 16 more.
- Do not publish directly detected uORB outputs from this module directory.
- Implement the main behavior in classes such as `Replay`, `Compatibility`, `to`, `CompatBase`, `CompatSensorCombinedDtType`, `ReadAndAndAddSubResult`, ... 1 more.

### Runtime Behavior

- Creates a dedicated PX4 task/thread with `px4_task_spawn_cmd()`.
- Uses a `run()` loop style module body for repeated execution.

## Background Theory

No dedicated mathematical model was identified in the generated source scan. This module is best understood through its PX4 state handling, uORB message flow, scheduling, and configuration surfaces described below.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | none detected |
| Primary outputs | none detected |
| Referenced topics | `airspeed`, `airspeed_validated`, `aux_global_position`, `distance_sensor`, `ekf2_timestamps`, `landing_target_pose`, `ranging_beacon`, `sensor_combined`, `sensor_gps`, `uORBTopics`, ... 14 more |
| Parameters/config | none detected |
| Key classes | `Replay`, `Compatibility`, `to`, `CompatBase`, `CompatSensorCombinedDtType`, `ReadAndAndAddSubResult`, `ReplayEkf2` |

### Files

| File | Why it matters |
| --- | --- |
| Replay.cpp | Entry point, start command, or module lifecycle code |
| replay_main.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| Replay.hpp | Defines `Replay` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["replay"]:::module
  Build["px4 module: modules__replay"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["airspeed"]:::io
    In1["airspeed_validated"]:::io
    In2["aux_global_position"]:::io
    In3["distance_sensor"]:::io
    In4["ekf2_timestamps"]:::io
    In5["landing_target_pose"]:::io
  end
  Out0["no output topics detected"]:::io
  In0 --> Module
  In1 --> Module
  In2 --> Module
  In3 --> Module
  In4 --> Module
  In5 --> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module -.-> Out0
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/replay |
| Build kind | px4 module |
| Build target | modules__replay |
| Runtime main | replay |
| Stack main | Not specified |
| Module config | Not specified |
| Detected sources | 3 |
| Detected headers | 3 |
| Detected configs | 1 |

### CMake Dependencies

- No explicit CMake dependencies detected.

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["replay logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| airspeed | referenced |
| airspeed_validated | referenced |
| aux_global_position | referenced |
| distance_sensor | referenced |
| ekf2_timestamps | referenced |
| landing_target_pose | referenced |
| ranging_beacon | referenced |
| sensor_combined | referenced |
| sensor_gps | referenced |
| uORBTopics | referenced |
| vehicle_air_data | referenced |
| vehicle_attitude | referenced |
| vehicle_attitude_groundtruth | referenced |
| vehicle_global_position | referenced |
| vehicle_global_position_groundtruth | referenced |
| vehicle_gps_position | referenced |
| vehicle_land_detected | referenced |
| vehicle_local_position | referenced |
| vehicle_local_position_groundtruth | referenced |
| vehicle_magnetometer | referenced |
| vehicle_odometry | referenced |
| vehicle_optical_flow | referenced |
| vehicle_status | referenced |
| vehicle_visual_odometry | referenced |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 replay start"]:::exec
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
  S0: ENV_MODE
  Initialized --> S0: detected state path
  S0 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ENV_MODE`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as replay
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start replay
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
  class Replay
  Replay : Replay.hpp
  class Compatibility
  Compatibility : Replay.hpp
  class to
  to : Replay.hpp
  class CompatBase
  CompatBase : Replay.hpp
  class CompatSensorCombinedDtType
  CompatSensorCombinedDtType : Replay.hpp
  class CompatBase
  CompatBase <|-- CompatSensorCombinedDtType
  class ReadAndAndAddSubResult
  ReadAndAndAddSubResult : Replay.hpp
  class ReplayEkf2
  ReplayEkf2 : ReplayEkf2.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| Replay |  | Replay.hpp |
| Compatibility |  | Replay.hpp |
| to |  | Replay.hpp |
| CompatBase |  | Replay.hpp |
| CompatSensorCombinedDtType | CompatBase | Replay.hpp |
| ReadAndAndAddSubResult |  | Replay.hpp |
| ReplayEkf2 |  | ReplayEkf2.hpp |

### Detected Enums

- `ReadAndAndAddSubResult`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| Replay.cpp | source |
| Replay.hpp | header |
| ReplayEkf2.cpp | source |
| ReplayEkf2.hpp | header |
| definitions.hpp | header |
| replay_main.cpp | source |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
