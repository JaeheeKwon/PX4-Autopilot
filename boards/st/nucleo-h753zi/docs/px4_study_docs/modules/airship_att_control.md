# PX4 Module Architecture: `airship_att_control`

- Source: `src/modules/airship_att_control`
- Build target: `modules__airship_att_control`
- Runtime main: `airship_att_control`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

This implements the airship attitude and rate controller. Ideally it would take attitude setpoints (`vehicle_attitude_setpoint`) or rate setpoints (in acro mode via `manual_control_setpoint` topic) as inputs and outputs actuator control messages. Currently it is feeding the `manual_control_setpoint` topic directly to the actuators. To reduce control latency, the module directly polls on the gyro topic published by the IMU driver.

## Description of Module

Controls airship attitude and converts attitude or rate demands into actuator-facing control outputs.

### Primary Responsibilities

- Convert selected state estimates and setpoints into downstream control or actuator-facing setpoints.
- Consume runtime inputs from uORB topics such as `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_status`.
- Publish outputs or status topics such as `vehicle_thrust_setpoint`, `vehicle_torque_setpoint`.
- Implement the main behavior in classes such as `AirshipAttitudeControl`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `rate_ctrl`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

Airship attitude control is represented as attitude-error feedback that maps the desired orientation into body-rate or torque-style setpoints.

```text
q_err = inverse(q_body) * q_sp
e_att = sign(q_err.w) * q_err.xyz
rate_sp = K_att * e_att + rate_ff
torque_sp = K_rate * (rate_sp - rate_body) + D * (d/dt)(rate_sp - rate_body)
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_status` |
| Primary outputs | `vehicle_thrust_setpoint`, `vehicle_torque_setpoint` |
| Referenced topics | `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_status`, `vehicle_thrust_setpoint`, `vehicle_torque_setpoint` |
| Parameters/config | none detected |
| Key classes | `AirshipAttitudeControl` |

### Files

| File | Why it matters |
| --- | --- |
| airship_att_control_main.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| airship_att_control.hpp | Defines `AirshipAttitudeControl` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["airship_att_control"]:::module
  Build["px4 module: modules__airship_att_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["manual_control_setpoint"]:::io
    In1["parameter_update"]:::io
    In2["vehicle_angular_velocity"]:::io
    In3["vehicle_status"]:::io
  end
  subgraph Outputs
    Out0["vehicle_thrust_setpoint"]:::io
    Out1["vehicle_torque_setpoint"]:::io
  end
  In0 --> Module
  In1 --> Module
  In2 --> Module
  In3 --> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module --> Out0
  Module --> Out1
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/airship_att_control |
| Build kind | px4 module |
| Build target | modules__airship_att_control |
| Runtime main | airship_att_control |
| Stack main | Not specified |
| Module config | Not specified |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 1 |

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
  Logic["airship_att_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["manual_control_setpoint"]:::io --> UORBIn
  Sub1["parameter_update"]:::io --> UORBIn
  Sub2["vehicle_angular_velocity"]:::io --> UORBIn
  Sub3["vehicle_status"]:::io --> UORBIn
  UORBOut --> Pub0["vehicle_thrust_setpoint"]:::io
  UORBOut --> Pub1["vehicle_torque_setpoint"]:::io
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_status | subscribed |
| vehicle_thrust_setpoint | published |
| vehicle_torque_setpoint | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 airship_att_control start"]:::exec
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as airship_att_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start airship_att_control
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
  class AirshipAttitudeControl
  AirshipAttitudeControl : airship_att_control.hpp
  class ModuleBase
  ModuleBase <|-- AirshipAttitudeControl
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| AirshipAttitudeControl | ModuleBase | airship_att_control.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| airship_att_control.hpp | header |
| airship_att_control_main.cpp | source |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
