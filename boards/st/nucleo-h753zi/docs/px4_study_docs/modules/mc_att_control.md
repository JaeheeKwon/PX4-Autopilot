# PX4 Module Architecture: `mc_att_control`

- Source: `src/modules/mc_att_control`
- Build target: `modules__mc_att_control`
- Runtime main: `mc_att_control`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

This implements the multicopter attitude controller. It takes attitude setpoints (`vehicle_attitude_setpoint`) as inputs and outputs a rate setpoint. The controller has a P loop for angular error Publication documenting the implemented Quaternion Attitude Control: Nonlinear Quadrocopter Attitude Control (2013) by Dario Brescianini, Markus Hehn and Raffaello D'Andrea Institute for Dynamic Systems and Control (IDSC), ETH Zurich https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/154099/eth-7387-01.p

## Description of Module

Runs multicopter attitude control and converts attitude setpoints into body-rate setpoints.

### Primary Responsibilities

- Convert selected state estimates and setpoints into downstream control or actuator-facing setpoints.
- Consume runtime inputs from uORB topics such as `autotune_attitude_control_status`, `hover_thrust_estimate`, `manual_control_setpoint`, `parameter_update`, `vehicle_attitude`, `vehicle_attitude_setpoint`, `vehicle_control_mode`, `vehicle_land_detected`, ... 2 more.
- Publish outputs or status topics such as `mc_virtual_attitude_setpoint`, `vehicle_attitude_setpoint`, `vehicle_rates_setpoint`.
- Use module configuration from `mc_att_control_params.yaml`.
- Implement the main behavior in classes such as `AttitudeControl`, `AttitudeControlConvergenceTest`, `MulticopterAttitudeControl`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `nav_and_controllers`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

Multicopter attitude control is quaternion based. The reduced attitude error is converted to a body-rate setpoint; yaw can be weighted lower than roll/pitch.

```text
q_err = inverse(q_body) * q_sp
e_q = sign(q_err.w) * q_err.xyz
rate_sp = 2 * K_att * e_q + yaw_feedforward
rate_sp.xy = limit_tilt_priority(rate_sp.xy)
rate_sp.z = yaw_weight * rate_sp.z
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `autotune_attitude_control_status`, `hover_thrust_estimate`, `manual_control_setpoint`, `parameter_update`, `vehicle_attitude`, `vehicle_attitude_setpoint`, `vehicle_control_mode`, `vehicle_land_detected`, `vehicle_local_position`, `vehicle_status` |
| Primary outputs | `mc_virtual_attitude_setpoint`, `vehicle_attitude_setpoint`, `vehicle_rates_setpoint` |
| Referenced topics | `autotune_attitude_control_status`, `hover_thrust_estimate`, `manual_control_setpoint`, `mc_virtual_attitude_setpoint`, `parameter_update`, `vehicle_attitude`, `vehicle_attitude_setpoint`, `vehicle_control_mode`, `vehicle_land_detected`, `vehicle_local_position`, ... 2 more |
| Parameters/config | mc_att_control_params.yaml |
| Key classes | `AttitudeControl`, `AttitudeControlConvergenceTest`, `MulticopterAttitudeControl` |

### Files

| File | Why it matters |
| --- | --- |
| mc_att_control_main.cpp | Entry point, start command, or module lifecycle code |
| AttitudeControl/CMakeLists.txt | Build, parameter, or module configuration |
| CMakeLists.txt | Build, parameter, or module configuration |
| mc_att_control_params.yaml | Build, parameter, or module configuration |
| AttitudeControl/AttitudeControl.hpp | Defines `AttitudeControl` class |
| AttitudeControl/AttitudeControlTest.cpp | Defines `AttitudeControlConvergenceTest` class |
| mc_att_control.hpp | Defines `MulticopterAttitudeControl` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["mc_att_control"]:::module
  Build["px4 module: modules__mc_att_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["autotune_attitude_control_status"]:::io
    In1["hover_thrust_estimate"]:::io
    In2["manual_control_setpoint"]:::io
    In3["parameter_update"]:::io
    In4["vehicle_attitude"]:::io
    In5["vehicle_attitude_setpoint"]:::io
  end
  subgraph Outputs
    Out0["mc_virtual_attitude_setpoint"]:::io
    Out1["vehicle_attitude_setpoint"]:::io
    Out2["vehicle_rates_setpoint"]:::io
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
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/mc_att_control |
| Build kind | px4 module |
| Build target | modules__mc_att_control |
| Runtime main | mc_att_control |
| Stack main | Not specified |
| Module config | mc_att_control_params.yaml |
| Detected sources | 4 |
| Detected headers | 3 |
| Detected configs | 3 |

### CMake Dependencies

- `AttitudeControl`
- `mathlib`
- `px4_work_queue`
- `Sticks`
- `StickYaw`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["mc_att_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["autotune_attitude_control_status"]:::io --> UORBIn
  Sub1["hover_thrust_estimate"]:::io --> UORBIn
  Sub2["manual_control_setpoint"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["vehicle_attitude"]:::io --> UORBIn
  UORBOut --> Pub0["mc_virtual_attitude_setpoint"]:::io
  UORBOut --> Pub1["vehicle_attitude_setpoint"]:::io
  UORBOut --> Pub2["vehicle_rates_setpoint"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| autotune_attitude_control_status | subscribed |
| hover_thrust_estimate | subscribed |
| manual_control_setpoint | subscribed |
| mc_virtual_attitude_setpoint | published |
| parameter_update | subscribed |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | subscribed, published |
| vehicle_control_mode | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_rates_setpoint | published |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 mc_att_control start"]:::exec
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
  S0: ARMING_STATE_ARMED
  Initialized --> S0: detected state path
  S1: MC_AIRMODE
  S0 --> S1: detected state path
  S1 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `MC_AIRMODE`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as mc_att_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start mc_att_control
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
  class AttitudeControl
  AttitudeControl : AttitudeControl/AttitudeControl.hpp
  class AttitudeControlConvergenceTest
  AttitudeControlConvergenceTest : AttitudeControl/AttitudeControlTest.cpp
  class MulticopterAttitudeControl
  MulticopterAttitudeControl : mc_att_control.hpp
  class ModuleBase
  ModuleBase <|-- MulticopterAttitudeControl
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| AttitudeControl |  | AttitudeControl/AttitudeControl.hpp |
| AttitudeControlConvergenceTest |  | AttitudeControl/AttitudeControlTest.cpp |
| MulticopterAttitudeControl | ModuleBase | mc_att_control.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| AttitudeControl/AttitudeControl.cpp | source |
| AttitudeControl/AttitudeControl.hpp | header |
| AttitudeControl/AttitudeControlMath.hpp | header |
| AttitudeControl/AttitudeControlMathTest.cpp | source |
| AttitudeControl/AttitudeControlTest.cpp | source |
| AttitudeControl/CMakeLists.txt | build |
| CMakeLists.txt | build |
| mc_att_control.hpp | header |
| mc_att_control_main.cpp | source |
| mc_att_control_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
