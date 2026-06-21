# PX4 Module Architecture: `fw_lateral_longitudinal_control`

- Source: `src/modules/fw_lateral_longitudinal_control`
- Build target: `modules__fw_lateral_longitudinal_control`
- Runtime main: `fw_lat_lon_control`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["fw_lateral_longitudinal_control"]:::module
  Build["px4 module: modules__fw_lateral_longitu..."]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["airspeed_validated"]:::io
    In1["fixed_wing_lateral_setpoint"]:::io
    In2["fixed_wing_longitudinal_setpoint"]:::io
    In3["flaps_setpoint"]:::io
    In4["lateral_control_configuration"]:::io
    In5["longitudinal_control_configuration"]:::io
  end
  subgraph Outputs
    Out0["fixed_wing_lateral_status"]:::io
    Out1["flight_phase_estimation"]:::io
    Out2["fw_virtual_attitude_setpoint"]:::io
    Out3["tecs_status"]:::io
    Out4["vehicle_attitude_setpoint"]:::io
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
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/fw_lateral_longitudinal_control |
| Build kind | px4 module |
| Build target | modules__fw_lateral_longitudinal_control |
| Runtime main | fw_lat_lon_control |
| Stack main | Not specified |
| Module config | fw_lat_long_params.yaml |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 2 |

### CMake Dependencies

- `${CONTROL_DEPENDENCIES}`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["fw_lat_lon_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["airspeed_validated"]:::io --> UORBIn
  Sub1["fixed_wing_lateral_setpoint"]:::io --> UORBIn
  Sub2["fixed_wing_longitudinal_setpoint"]:::io --> UORBIn
  Sub3["flaps_setpoint"]:::io --> UORBIn
  Sub4["lateral_control_configuration"]:::io --> UORBIn
  UORBOut --> Pub0["fixed_wing_lateral_status"]:::io
  UORBOut --> Pub1["flight_phase_estimation"]:::io
  UORBOut --> Pub2["fw_virtual_attitude_setpoint"]:::io
  UORBOut --> Pub3["tecs_status"]:::io
  UORBOut --> Pub4["vehicle_attitude_setpoint"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| airspeed_validated | subscribed |
| fixed_wing_lateral_setpoint | subscribed |
| fixed_wing_lateral_status | published |
| fixed_wing_longitudinal_setpoint | subscribed |
| flaps_setpoint | subscribed |
| flight_phase_estimation | published |
| fw_virtual_attitude_setpoint | published |
| lateral_control_configuration | subscribed |
| longitudinal_control_configuration | subscribed |
| normalized_unsigned_setpoint | referenced |
| parameter_update | subscribed |
| tecs_status | published |
| vehicle_air_data | subscribed |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | published |
| vehicle_control_mode | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_status | subscribed |
| wind | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 fw_lat_lon_control start"]:::exec
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
  participant M as fw_lat_lon_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start fw_lat_lon_control
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
  class FwLateralLongitudinalControl
  FwLateralLongitudinalControl : FwLateralLongitudinalControl.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| FwLateralLongitudinalControl |  | FwLateralLongitudinalControl.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| FwLateralLongitudinalControl.cpp | source |
| FwLateralLongitudinalControl.hpp | header |
| fw_lat_long_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
