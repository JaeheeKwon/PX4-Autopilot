# PX4 Module Architecture: `airspeed_selector`

- Source: `src/modules/airspeed_selector`
- Build target: `modules__airspeed_selector`
- Runtime main: `airspeed_selector`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["airspeed_selector"]:::module
  Build["px4 module: modules__airspeed_selector"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["estimator_selector_status"]:::io
    In1["estimator_status"]:::io
    In2["flight_phase_estimation"]:::io
    In3["launch_detection_status"]:::io
    In4["parameter_update"]:::io
    In5["position_setpoint"]:::io
  end
  subgraph Outputs
    Out0["airspeed_validated"]:::io
    Out1["airspeed_wind"]:::io
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
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/airspeed_selector |
| Build kind | px4 module |
| Build target | modules__airspeed_selector |
| Runtime main | airspeed_selector |
| Stack main | Not specified |
| Module config | airspeed_selector_params.yaml |
| Detected sources | 2 |
| Detected headers | 1 |
| Detected configs | 2 |

### CMake Dependencies

- `wind_estimator`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["airspeed_selector logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["estimator_selector_status"]:::io --> UORBIn
  Sub1["estimator_status"]:::io --> UORBIn
  Sub2["flight_phase_estimation"]:::io --> UORBIn
  Sub3["launch_detection_status"]:::io --> UORBIn
  Sub4["parameter_update"]:::io --> UORBIn
  UORBOut --> Pub0["airspeed_validated"]:::io
  UORBOut --> Pub1["airspeed_wind"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| airspeed | referenced |
| airspeed_validated | published |
| airspeed_wind | published |
| estimator_selector_status | subscribed |
| estimator_status | subscribed |
| flight_phase_estimation | subscribed |
| launch_detection_status | subscribed |
| mavlink_log | referenced |
| parameter_update | subscribed |
| position_setpoint | subscribed |
| tecs_status | subscribed |
| vehicle_acceleration | subscribed |
| vehicle_air_data | subscribed |
| vehicle_attitude | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_rates_setpoint | subscribed |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 airspeed_selector start"]:::exec
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
  S0: ARMING_STATE_ARMED
  Initialized --> S0: detected state path
  S0 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as airspeed_selector
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start airspeed_selector
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
  class AirspeedValidator
  AirspeedValidator : AirspeedValidator.hpp
  class AirspeedModule
  AirspeedModule : airspeed_selector_main.cpp
  class ModuleBase
  ModuleBase <|-- AirspeedModule
  class AirspeedSource
  AirspeedSource : airspeed_selector_main.cpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| AirspeedValidator |  | AirspeedValidator.hpp |
| AirspeedModule | ModuleBase | airspeed_selector_main.cpp |
| AirspeedSource |  | airspeed_selector_main.cpp |

### Detected Enums

- `AirspeedSource`
- `CheckTypeBits`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| AirspeedValidator.cpp | source |
| AirspeedValidator.hpp | header |
| CMakeLists.txt | build |
| airspeed_selector_main.cpp | source |
| airspeed_selector_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
