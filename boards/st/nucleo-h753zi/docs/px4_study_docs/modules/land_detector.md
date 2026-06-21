# PX4 Module Architecture: `land_detector`

- Source: `src/modules/land_detector`
- Build target: `modules__land_detector`
- Runtime main: `land_detector`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["land_detector"]:::module
  Build["px4 module: modules__land_detector"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_armed"]:::io
    In1["airspeed_validated"]:::io
    In2["fixed_wing_runway_control"]:::io
    In3["hover_thrust_estimate"]:::io
    In4["launch_detection_status"]:::io
    In5["parameter_update"]:::io
  end
  subgraph Outputs
    Out0["vehicle_land_detected"]:::io
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
| Module path | src/modules/land_detector |
| Build kind | px4 module |
| Build target | modules__land_detector |
| Runtime main | land_detector |
| Stack main | Not specified |
| Module config | land_detector_params.yaml |
| Detected sources | 7 |
| Detected headers | 6 |
| Detected configs | 4 |

### CMake Dependencies

- `hysteresis`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["land_detector logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_armed"]:::io --> UORBIn
  Sub1["airspeed_validated"]:::io --> UORBIn
  Sub2["fixed_wing_runway_control"]:::io --> UORBIn
  Sub3["hover_thrust_estimate"]:::io --> UORBIn
  Sub4["launch_detection_status"]:::io --> UORBIn
  UORBOut --> Pub0["vehicle_land_detected"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_armed | subscribed |
| airspeed_validated | subscribed |
| fixed_wing_runway_control | subscribed |
| hover_thrust_estimate | subscribed |
| launch_detection_status | subscribed |
| parameter_update | subscribed |
| position_setpoint_triplet | subscribed |
| sensor_selection | subscribed |
| takeoff_status | subscribed |
| trajectory_setpoint | subscribed |
| vehicle_acceleration | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_control_mode | subscribed |
| vehicle_global_position | subscribed |
| vehicle_imu_status | subscribed |
| vehicle_land_detected | published |
| vehicle_local_position | subscribed |
| vehicle_status | subscribed |
| vehicle_thrust_setpoint | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 land_detector start"]:::exec
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
  S0: NAVIGATION_STATE_AUTO_LAND
  Initialized --> S0: detected state path
  S1: NAVIGATION_STATE_AUTO_RTL
  S0 --> S1: detected state path
  S2: NAVIGATION_STATE_DESCEND
  S1 --> S2: detected state path
  S3: TAKEOFF_STATE_DISARMED
  S2 --> S3: detected state path
  S4: TAKEOFF_STATE_FLIGHT
  S3 --> S4: detected state path
  S5: TAKEOFF_STATE_RAMPUP
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `NAVIGATION_STATE_AUTO_LAND`
- `NAVIGATION_STATE_AUTO_RTL`
- `NAVIGATION_STATE_DESCEND`
- `TAKEOFF_STATE_DISARMED`
- `TAKEOFF_STATE_FLIGHT`
- `TAKEOFF_STATE_RAMPUP`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as land_detector
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start land_detector
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
  class AirshipLandDetector
  AirshipLandDetector : AirshipLandDetector.h
  class LandDetector
  LandDetector <|-- AirshipLandDetector
  class FixedwingLandDetector
  FixedwingLandDetector : FixedwingLandDetector.h
  class LandDetector
  LandDetector : LandDetector.h
  class ModuleBase
  ModuleBase <|-- LandDetector
  class MulticopterLandDetector
  MulticopterLandDetector : MulticopterLandDetector.h
  class LandDetector
  LandDetector <|-- MulticopterLandDetector
  class RoverLandDetector
  RoverLandDetector : RoverLandDetector.h
  class LandDetector
  LandDetector <|-- RoverLandDetector
  class VtolLandDetector
  VtolLandDetector : VtolLandDetector.h
  class MulticopterLandDetector
  MulticopterLandDetector <|-- VtolLandDetector
  class with
  with : land_detector_main.cpp
  class maintains
  maintains : land_detector_main.cpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| AirshipLandDetector | LandDetector | AirshipLandDetector.h |
| FixedwingLandDetector |  | FixedwingLandDetector.h |
| LandDetector | ModuleBase | LandDetector.h |
| MulticopterLandDetector | LandDetector | MulticopterLandDetector.h |
| RoverLandDetector | LandDetector | RoverLandDetector.h |
| VtolLandDetector | MulticopterLandDetector | VtolLandDetector.h |
| with |  | land_detector_main.cpp |
| maintains |  | land_detector_main.cpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| AirshipLandDetector.cpp | source |
| AirshipLandDetector.h | header |
| CMakeLists.txt | build |
| FixedwingLandDetector.cpp | source |
| FixedwingLandDetector.h | header |
| LandDetector.cpp | source |
| LandDetector.h | header |
| MulticopterLandDetector.cpp | source |
| MulticopterLandDetector.h | header |
| RoverLandDetector.cpp | source |
| RoverLandDetector.h | header |
| VtolLandDetector.cpp | source |
| VtolLandDetector.h | header |
| land_detector_main.cpp | source |
| land_detector_params.yaml | config |
| land_detector_params_fw.yaml | config |
| land_detector_params_mc.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
