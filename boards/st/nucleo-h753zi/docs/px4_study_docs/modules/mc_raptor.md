# PX4 Module Architecture: `mc_raptor`

- Source: `src/modules/mc_raptor`
- Build target: `modules__mc_raptor`
- Runtime main: `mc_raptor`
- Build kind: `px4 module`
- Mermaid palette: `ash` grey tone

Architecture notes for the mc_raptor module.

## Description of Module

Runs an experimental multicopter Raptor control path for advanced setpoint generation.

### Primary Responsibilities

- Consume runtime inputs from uORB topics such as `arming_check_request`, `register_ext_component_reply`, `trajectory_setpoint`, `vehicle_angular_velocity`, `vehicle_attitude`, `vehicle_local_position`, `vehicle_status`.
- Publish outputs or status topics such as `actuator_motors`, `arming_check_reply`, `config_control_setpoints`, `raptor_input`, `raptor_status`, `register_ext_component_request`, `tune_control`, `unregister_ext_component`.
- Use parameters or module configuration entries such as `MC_RAPTOR_ENABLE`, `MC_RAPTOR_INTREF`, `MC_RAPTOR_OFFB`, `MC_RAPTOR_VERBOS`.
- Implement the main behavior in classes such as `Raptor`, `FlightModeState`, `InternalReference`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `rate_ctrl`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

Raptor runs learned policy inference for multicopter control. The controller is a parameterized neural policy, optionally with recurrent state.

```text
o_t = normalize(sensor_state_t, setpoint_t, previous_action_t)
h_t = f_theta(h_{t-1}, o_t)
a_t = pi_theta(o_t, h_t)
a_t = constrain(a_t, action_min, action_max)
actuator_output = action_scale * a_t + action_offset
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `arming_check_request`, `register_ext_component_reply`, `trajectory_setpoint`, `vehicle_angular_velocity`, `vehicle_attitude`, `vehicle_local_position`, `vehicle_status` |
| Primary outputs | `actuator_motors`, `arming_check_reply`, `config_control_setpoints`, `raptor_input`, `raptor_status`, `register_ext_component_request`, `tune_control`, `unregister_ext_component` |
| Referenced topics | `actuator_motors`, `arming_check_reply`, `arming_check_request`, `config_control_setpoints`, `raptor_input`, `raptor_status`, `register_ext_component_reply`, `register_ext_component_request`, `trajectory_setpoint`, `tune_control`, ... 7 more |
| Parameters/config | `MC_RAPTOR_ENABLE`, `MC_RAPTOR_INTREF`, `MC_RAPTOR_OFFB`, `MC_RAPTOR_VERBOS` |
| Key classes | `Raptor`, `FlightModeState`, `InternalReference` |

### Files

| File | Why it matters |
| --- | --- |
| mc_raptor.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| module.yaml | Build, parameter, or module configuration |
| mc_raptor.hpp | Defines `Raptor` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["mc_raptor"]:::module
  Build["px4 module: modules__mc_raptor"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["arming_check_request"]:::io
    In1["register_ext_component_reply"]:::io
    In2["trajectory_setpoint"]:::io
    In3["vehicle_angular_velocity"]:::io
    In4["vehicle_attitude"]:::io
    In5["vehicle_local_position"]:::io
  end
  subgraph Outputs
    Out0["actuator_motors"]:::io
    Out1["arming_check_reply"]:::io
    Out2["config_control_setpoints"]:::io
    Out3["raptor_input"]:::io
    Out4["raptor_status"]:::io
    Out5["register_ext_component_request"]:::io
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
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/mc_raptor |
| Build kind | px4 module |
| Build target | modules__mc_raptor |
| Runtime main | mc_raptor |
| Stack main | 4000 |
| Module config | module.yaml |
| Detected sources | 1 |
| Detected headers | 5 |
| Detected configs | 2 |

### CMake Dependencies

- `px4_work_queue`
- `rl_tools`
- `git_raptor_blob`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["mc_raptor logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["arming_check_request"]:::io --> UORBIn
  Sub1["register_ext_component_reply"]:::io --> UORBIn
  Sub2["trajectory_setpoint"]:::io --> UORBIn
  Sub3["vehicle_angular_velocity"]:::io --> UORBIn
  Sub4["vehicle_attitude"]:::io --> UORBIn
  UORBOut --> Pub0["actuator_motors"]:::io
  UORBOut --> Pub1["arming_check_reply"]:::io
  UORBOut --> Pub2["config_control_setpoints"]:::io
  UORBOut --> Pub3["raptor_input"]:::io
  UORBOut --> Pub4["raptor_status"]:::io
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_motors | published |
| arming_check_reply | published |
| arming_check_request | subscribed |
| config_control_setpoints | published |
| raptor_input | published |
| raptor_status | published |
| register_ext_component_reply | subscribed |
| register_ext_component_request | published |
| trajectory_setpoint | subscribed |
| tune_control | published |
| unregister_ext_component | published |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_control_mode | referenced |
| vehicle_local_position | subscribed |
| vehicle_odometry | referenced |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 mc_raptor start"]:::exec
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
  S0: NAVIGATION_STATE_OFFBOARD
  Initialized --> S0: detected state path
  S0 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `NAVIGATION_STATE_OFFBOARD`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as mc_raptor
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start mc_raptor
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
  class Raptor
  Raptor : mc_raptor.hpp
  class ModuleBase
  ModuleBase <|-- Raptor
  class FlightModeState
  FlightModeState : mc_raptor.hpp
  class InternalReference
  InternalReference : mc_raptor.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| Raptor | ModuleBase | mc_raptor.hpp |
| FlightModeState |  | mc_raptor.hpp |
| InternalReference |  | mc_raptor.hpp |

### Detected Enums

- `FlightModeState`
- `InternalReference`
- `values`

## Parameters and Configuration

- `MC_RAPTOR_ENABLE`
- `MC_RAPTOR_INTREF`
- `MC_RAPTOR_OFFB`
- `MC_RAPTOR_VERBOS`

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| README.md | readme |
| blob/benchmark.h | header |
| blob/policy.h | header |
| mc_raptor.cpp | source |
| mc_raptor.hpp | header |
| module.yaml | config |
| trajectories/lissajous.hpp | header |
| trajectories/trajectory.hpp | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
