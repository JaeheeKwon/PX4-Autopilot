# PX4 Module Architecture: `fw_att_control`

- Source: `src/modules/fw_att_control`
- Build target: `modules__fw_att_control`
- Runtime main: `fw_att_control`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["fw_att_control"]:::module
  Build["px4 module: modules__fw_att_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["airspeed_validated"]:::io
    In1["autotune_attitude_control_status"]:::io
    In2["fixed_wing_runway_control"]:::io
    In3["manual_control_setpoint"]:::io
    In4["parameter_update"]:::io
    In5["vehicle_angular_velocity"]:::io
  end
  subgraph Outputs
    Out0["fw_virtual_attitude_setpoint"]:::io
    Out1["landing_gear_wheel"]:::io
    Out2["vehicle_attitude_setpoint"]:::io
    Out3["vehicle_rates_setpoint"]:::io
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
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/fw_att_control |
| Build kind | px4 module |
| Build target | modules__fw_att_control |
| Runtime main | fw_att_control |
| Stack main | Not specified |
| Module config | fw_att_control_params.yaml |
| Detected sources | 3 |
| Detected headers | 2 |
| Detected configs | 2 |

### CMake Dependencies

- `px4_work_queue`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["fw_att_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["airspeed_validated"]:::io --> UORBIn
  Sub1["autotune_attitude_control_status"]:::io --> UORBIn
  Sub2["fixed_wing_runway_control"]:::io --> UORBIn
  Sub3["manual_control_setpoint"]:::io --> UORBIn
  Sub4["parameter_update"]:::io --> UORBIn
  UORBOut --> Pub0["fw_virtual_attitude_setpoint"]:::io
  UORBOut --> Pub1["landing_gear_wheel"]:::io
  UORBOut --> Pub2["vehicle_attitude_setpoint"]:::io
  UORBOut --> Pub3["vehicle_rates_setpoint"]:::io
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| airspeed_validated | subscribed |
| autotune_attitude_control_status | subscribed |
| fixed_wing_runway_control | subscribed |
| fw_virtual_attitude_setpoint | published |
| landing_gear_wheel | published |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | subscribed, published |
| vehicle_control_mode | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_rates_setpoint | published |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 fw_att_control start"]:::exec
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as fw_att_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start fw_att_control
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
  class FixedwingAttitudeControl
  FixedwingAttitudeControl : FixedwingAttitudeControl.hpp
  class WheelController
  WheelController : fw_wheel_controller.h
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| FixedwingAttitudeControl |  | FixedwingAttitudeControl.hpp |
| WheelController |  | fw_wheel_controller.h |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| FixedwingAttitudeControl.cpp | source |
| FixedwingAttitudeControl.hpp | header |
| FixedwingAttitudeControlTest.cpp | source |
| fw_att_control_params.yaml | config |
| fw_wheel_controller.cpp | source |
| fw_wheel_controller.h | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
