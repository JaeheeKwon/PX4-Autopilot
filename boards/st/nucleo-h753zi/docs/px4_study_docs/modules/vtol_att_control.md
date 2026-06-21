# PX4 Module Architecture: `vtol_att_control`

- Source: `src/modules/vtol_att_control`
- Build target: `modules__vtol_att_control`
- Runtime main: `vtol_att_control`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["vtol_att_control"]:::module
  Build["px4 module: modules__vtol_att_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["action_request"]:::io
    In1["airspeed_validated"]:::io
    In2["fw_virtual_attitude_setpoint"]:::io
    In3["home_position"]:::io
    In4["mc_virtual_attitude_setpoint"]:::io
    In5["parameter_update"]:::io
  end
  subgraph Outputs
    Out0["flaps_setpoint"]:::io
    Out1["spoilers_setpoint"]:::io
    Out2["tiltrotor_extra_controls"]:::io
    Out3["vehicle_attitude_setpoint"]:::io
    Out4["vehicle_command_ack"]:::io
    Out5["vehicle_thrust_setpoint"]:::io
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
| Module path | src/modules/vtol_att_control |
| Build kind | px4 module |
| Build target | modules__vtol_att_control |
| Runtime main | vtol_att_control |
| Stack main | Not specified |
| Module config | standard_params.yaml |
| Detected sources | 5 |
| Detected headers | 5 |
| Detected configs | 4 |

### CMake Dependencies

- No explicit CMake dependencies detected.

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["vtol_att_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["action_request"]:::io --> UORBIn
  Sub1["airspeed_validated"]:::io --> UORBIn
  Sub2["fw_virtual_attitude_setpoint"]:::io --> UORBIn
  Sub3["home_position"]:::io --> UORBIn
  Sub4["mc_virtual_attitude_setpoint"]:::io --> UORBIn
  UORBOut --> Pub0["flaps_setpoint"]:::io
  UORBOut --> Pub1["spoilers_setpoint"]:::io
  UORBOut --> Pub2["tiltrotor_extra_controls"]:::io
  UORBOut --> Pub3["vehicle_attitude_setpoint"]:::io
  UORBOut --> Pub4["vehicle_command_ack"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| action_request | subscribed |
| airspeed_validated | subscribed |
| flaps_setpoint | published |
| fw_virtual_attitude_setpoint | subscribed |
| home_position | subscribed |
| mc_virtual_attitude_setpoint | subscribed |
| normalized_unsigned_setpoint | referenced |
| parameter_update | subscribed |
| position_setpoint_triplet | subscribed |
| spoilers_setpoint | published |
| tecs_status | subscribed |
| tiltrotor_extra_controls | published |
| vehicle_air_data | subscribed |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | published |
| vehicle_command | subscribed |
| vehicle_command_ack | published |
| vehicle_control_mode | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_local_position_setpoint | subscribed |
| vehicle_status | subscribed |
| vehicle_thrust_setpoint | published |
| vehicle_thrust_setpoint_virtual_fw | subscribed |
| vehicle_thrust_setpoint_virtual_mc | subscribed |
| vehicle_torque_setpoint | published |
| vehicle_torque_setpoint_virtual_fw | subscribed |
| vehicle_torque_setpoint_virtual_mc | subscribed |
| vtol_vehicle_status | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 vtol_att_control start"]:::exec
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
  S0: ENABLE_ALL_MODES
  Initialized --> S0: detected state path
  S1: FW_MODE
  S0 --> S1: detected state path
  S2: MC_MODE
  S1 --> S2: detected state path
  S3: NAVIGATION_STATE_AUTO_LAND
  S2 --> S3: detected state path
  S4: NAVIGATION_STATE_AUTO_RTL
  S3 --> S4: detected state path
  S5: NAVIGATION_STATE_AUTO_TAK...
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ENABLE_ALL_MODES`
- `FW_MODE`
- `MC_MODE`
- `NAVIGATION_STATE_AUTO_LAND`
- `NAVIGATION_STATE_AUTO_RTL`
- `NAVIGATION_STATE_AUTO_TAKEOFF`
- `NAVIGATION_STATE_DESCEND`
- `NAVIGATION_STATE_ORBIT`
- `VEHICLE_VTOL_STATE_FW`
- `VEHICLE_VTOL_STATE_MC`
- `VEHICLE_VTOL_STATE_TRANSITION_TO_FW`
- `VEHICLE_VTOL_STATE_TRANSITION_TO_MC`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as vtol_att_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start vtol_att_control
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
  class Standard
  Standard : standard.h
  class VtolType
  VtolType <|-- Standard
  class vtol_mode
  vtol_mode : standard.h
  class Tailsitter
  Tailsitter : tailsitter.h
  class VtolType
  VtolType <|-- Tailsitter
  class vtol_mode_3
  vtol_mode_3 : tailsitter.h
  class Tiltrotor
  Tiltrotor : tiltrotor.h
  class VtolType
  VtolType <|-- Tiltrotor
  class vtol_mode_5
  vtol_mode_5 : tiltrotor.h
  class VtolAttitudeControl
  VtolAttitudeControl : vtol_att_control_main.h
  class ModuleBase
  ModuleBase <|-- VtolAttitudeControl
  class mode
  mode : vtol_type.h
  class vtol_type
  vtol_type : vtol_type.h
  class VtFwDifthrEnBits
  VtFwDifthrEnBits : vtol_type.h
  class QuadchuteReason
  QuadchuteReason : vtol_type.h
  class VtolAttitudeControl_11
  VtolAttitudeControl_11 : vtol_type.h
  class VtolType
  VtolType : vtol_type.h
  class ModuleParams
  ModuleParams <|-- VtolType
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| Standard | VtolType | standard.h |
| vtol_mode |  | standard.h |
| Tailsitter | VtolType | tailsitter.h |
| vtol_mode |  | tailsitter.h |
| Tiltrotor | VtolType | tiltrotor.h |
| vtol_mode |  | tiltrotor.h |
| VtolAttitudeControl | ModuleBase | vtol_att_control_main.h |
| mode |  | vtol_type.h |
| vtol_type |  | vtol_type.h |
| VtFwDifthrEnBits |  | vtol_type.h |
| QuadchuteReason |  | vtol_type.h |
| VtolAttitudeControl |  | vtol_type.h |
| VtolType | ModuleParams | vtol_type.h |

### Detected Enums

- `QuadchuteReason`
- `VtFwDifthrEnBits`
- `VtolForwardActuationMode`
- `for`
- `mode`
- `vtol_mode`
- `vtol_type`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| standard.cpp | source |
| standard.h | header |
| standard_params.yaml | config |
| tailsitter.cpp | source |
| tailsitter.h | header |
| tiltrotor.cpp | source |
| tiltrotor.h | header |
| tiltrotor_params.yaml | config |
| vtol_att_control_main.cpp | source |
| vtol_att_control_main.h | header |
| vtol_att_control_params.yaml | config |
| vtol_type.cpp | source |
| vtol_type.h | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
