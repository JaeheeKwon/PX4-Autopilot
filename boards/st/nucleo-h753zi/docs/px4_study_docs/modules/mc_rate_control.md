# PX4 Module Architecture: `mc_rate_control`

- Source: `src/modules/mc_rate_control`
- Build target: `modules__mc_rate_control`
- Runtime main: `mc_rate_control`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

This implements the multicopter rate controller. It takes rate setpoints (in acro mode via `manual_control_setpoint` topic) as inputs and outputs actuator control messages. The controller has a PID loop for angular rate error.

## Description of Module

Runs the high-rate multicopter body-rate controller and publishes torque and thrust setpoints.

### Primary Responsibilities

- Convert selected state estimates and setpoints into downstream control or actuator-facing setpoints.
- Consume runtime inputs from uORB topics such as `battery_status`, `control_allocator_status`, `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_control_mode`, `vehicle_land_detected`, `vehicle_rates_setpoint`, ... 1 more.
- Publish outputs or status topics such as `actuator_controls_status_0`, `rate_ctrl_status`, `vehicle_rates_setpoint`, `vehicle_thrust_setpoint`, `vehicle_thrust_setpoint_virtual_mc`, `vehicle_torque_setpoint`, `vehicle_torque_setpoint_virtual_mc`.
- Use module configuration from `mc_acro_params.yaml`.
- Implement the main behavior in classes such as `MulticopterRateControl`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `rate_ctrl`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

Multicopter rate control is a high-rate PID loop on body angular velocity. It outputs body torque setpoints.

```text
e_rate = rate_sp - rate_body
I[k] = constrain(I[k-1] + e_rate*dt, -I_max, I_max)
D = -gyro_rate_derivative
torque_sp = K * (P*e_rate + I_gain*I + D_gain*D) + FF*rate_sp
torque_sp = constrain(torque_sp, torque_min, torque_max)
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `battery_status`, `control_allocator_status`, `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_control_mode`, `vehicle_land_detected`, `vehicle_rates_setpoint`, `vehicle_status` |
| Primary outputs | `actuator_controls_status_0`, `rate_ctrl_status`, `vehicle_rates_setpoint`, `vehicle_thrust_setpoint`, `vehicle_thrust_setpoint_virtual_mc`, `vehicle_torque_setpoint`, `vehicle_torque_setpoint_virtual_mc` |
| Referenced topics | `actuator_controls_status`, `actuator_controls_status_0`, `battery_status`, `control_allocator_status`, `manual_control_setpoint`, `parameter_update`, `rate_ctrl_status`, `vehicle_angular_velocity`, `vehicle_control_mode`, `vehicle_land_detected`, ... 6 more |
| Parameters/config | mc_acro_params.yaml |
| Key classes | `MulticopterRateControl` |

### Files

| File | Why it matters |
| --- | --- |
| MulticopterRateControl.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| mc_acro_params.yaml | Build, parameter, or module configuration |
| mc_rate_control_params.yaml | Build, parameter, or module configuration |
| MulticopterRateControl.hpp | Defines `MulticopterRateControl` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["mc_rate_control"]:::module
  Build["px4 module: modules__mc_rate_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["battery_status"]:::io
    In1["control_allocator_status"]:::io
    In2["manual_control_setpoint"]:::io
    In3["parameter_update"]:::io
    In4["vehicle_angular_velocity"]:::io
    In5["vehicle_control_mode"]:::io
  end
  subgraph Outputs
    Out0["actuator_controls_status_0"]:::io
    Out1["rate_ctrl_status"]:::io
    Out2["vehicle_rates_setpoint"]:::io
    Out3["vehicle_thrust_setpoint"]:::io
    Out4["vehicle_thrust_setpoint_virtual_mc"]:::io
    Out5["vehicle_torque_setpoint"]:::io
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
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/mc_rate_control |
| Build kind | px4 module |
| Build target | modules__mc_rate_control |
| Runtime main | mc_rate_control |
| Stack main | Not specified |
| Module config | mc_acro_params.yaml |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 3 |

### CMake Dependencies

- `circuit_breaker`
- `mathlib`
- `RateControl`
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
  Logic["mc_rate_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["battery_status"]:::io --> UORBIn
  Sub1["control_allocator_status"]:::io --> UORBIn
  Sub2["manual_control_setpoint"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["vehicle_angular_velocity"]:::io --> UORBIn
  UORBOut --> Pub0["actuator_controls_status_0"]:::io
  UORBOut --> Pub1["rate_ctrl_status"]:::io
  UORBOut --> Pub2["vehicle_rates_setpoint"]:::io
  UORBOut --> Pub3["vehicle_thrust_setpoint"]:::io
  UORBOut --> Pub4["vehicle_thrust_setpoint_virtual_mc"]:::io
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_controls_status | referenced |
| actuator_controls_status_0 | published |
| battery_status | subscribed |
| control_allocator_status | subscribed |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| rate_ctrl_status | published |
| vehicle_angular_velocity | subscribed |
| vehicle_control_mode | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_rates_setpoint | subscribed, published |
| vehicle_status | subscribed |
| vehicle_thrust_setpoint | published |
| vehicle_thrust_setpoint_virtual_mc | published |
| vehicle_torque_setpoint | published |
| vehicle_torque_setpoint_virtual_mc | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 mc_rate_control start"]:::exec
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
  participant M as mc_rate_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start mc_rate_control
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
  class MulticopterRateControl
  MulticopterRateControl : MulticopterRateControl.hpp
  class ModuleBase
  ModuleBase <|-- MulticopterRateControl
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| MulticopterRateControl | ModuleBase | MulticopterRateControl.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| MulticopterRateControl.cpp | source |
| MulticopterRateControl.hpp | header |
| mc_acro_params.yaml | config |
| mc_rate_control_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
