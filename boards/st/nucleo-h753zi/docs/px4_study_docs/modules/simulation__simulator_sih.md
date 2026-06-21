# PX4 Module Architecture: `simulation/simulator_sih`

- Source: `src/modules/simulation/simulator_sih`
- Build target: `modules__simulation__simulator_sih`
- Runtime main: `simulator_sih`
- Build kind: `px4 module`
- Mermaid palette: `ash` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["simulation/simulator_sih"]:::module
  Build["px4 module: modules__simulation__simula..."]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_outputs_sim"]:::io
    In1["parameter_update"]:::io
  end
  subgraph Outputs
    Out0["airspeed"]:::io
    Out1["esc_status"]:::io
    Out2["ranging_beacon"]:::io
    Out3["vehicle_angular_velocity_groundtruth"]:::io
    Out4["vehicle_attitude_groundtruth"]:::io
    Out5["vehicle_global_position_groundtruth"]:::io
  end
  In0 --> Module
  In1 --> Module
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
| Module path | src/modules/simulation/simulator_sih |
| Build kind | px4 module |
| Build target | modules__simulation__simulator_sih |
| Runtime main | simulator_sih |
| Stack main | Not specified |
| Module config | sih_params.yaml |
| Detected sources | 1 |
| Detected headers | 2 |
| Detected configs | 2 |

### CMake Dependencies

- `mathlib`
- `drivers_accelerometer`
- `drivers_gyroscope`
- `drivers_rangefinder`
- `geo`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["simulator_sih logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_outputs_sim"]:::io --> UORBIn
  Sub1["parameter_update"]:::io --> UORBIn
  UORBOut --> Pub0["airspeed"]:::io
  UORBOut --> Pub1["esc_status"]:::io
  UORBOut --> Pub2["ranging_beacon"]:::io
  UORBOut --> Pub3["vehicle_angular_velocity_groundtruth"]:::io
  UORBOut --> Pub4["vehicle_attitude_groundtruth"]:::io
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_outputs | referenced |
| actuator_outputs_sim | subscribed |
| airspeed | published |
| distance_sensor | referenced |
| esc_status | published |
| parameter_update | subscribed |
| ranging_beacon | published |
| vehicle_angular_velocity | referenced |
| vehicle_angular_velocity_groundtruth | published |
| vehicle_attitude | referenced |
| vehicle_attitude_groundtruth | published |
| vehicle_global_position | referenced |
| vehicle_global_position_groundtruth | published |
| vehicle_local_position | referenced |
| vehicle_local_position_groundtruth | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 simulator_sih start"]:::exec
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as simulator_sih
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start simulator_sih
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
  class can
  can : aero.hpp
  class Thruster
  Thruster : aero.hpp
  class Aerodynamic
  Aerodynamic : aero.hpp
  class AeroSeg
  AeroSeg : aero.hpp
  class Sih
  Sih : sih.hpp
  class ModuleBase
  ModuleBase <|-- Sih
  class VehicleType
  VehicleType : sih.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| can |  | aero.hpp |
| Thruster |  | aero.hpp |
| Aerodynamic |  | aero.hpp |
| AeroSeg |  | aero.hpp |
| Sih | ModuleBase | sih.hpp |
| VehicleType |  | sih.hpp |

### Detected Enums

- `VehicleType`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| aero.hpp | header |
| sih.cpp | source |
| sih.hpp | header |
| sih_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
