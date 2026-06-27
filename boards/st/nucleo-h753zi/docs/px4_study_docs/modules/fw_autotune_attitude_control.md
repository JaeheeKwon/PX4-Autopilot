# PX4 Module Architecture: `fw_autotune_attitude_control`

- Source: `src/modules/fw_autotune_attitude_control`
- Build target: `fw_autotune_attitude_control`
- Runtime main: `fw_autotune_attitude_control`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Source-derived architecture notes for this PX4 module directory.

## Description of Module

Injects and evaluates fixed-wing attitude-control excitation to support automatic gain tuning.

### Primary Responsibilities

- Convert selected state estimates and setpoints into downstream control or actuator-facing setpoints.
- Consume runtime inputs from uORB topics such as `actuator_controls_status_0`, `actuator_controls_status_1`, `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_command`, `vehicle_status`, `vehicle_torque_setpoint`.
- Publish outputs or status topics such as `autotune_attitude_control_status`.
- Use module configuration from `fw_autotune_attitude_control_params.yaml`.
- Implement the main behavior in classes such as `SignalType`, `FwAutotuneAttitudeControl`, `state`, `amplitudeDetectionState`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `hp_default`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

Autotune injects controlled excitation, estimates the axis frequency response, then derives gains from target bandwidth and phase-margin constraints.

```text
For excitation u(t) and measured response y(t):
G(jw) = FFT(y) / FFT(u)
phase_margin = pi + angle(G(jw_c))
|K(jw_c) * G(jw_c)| ~= 1

PID form:
u = Kp*e + Ki*integral(e) + Kd*de/dt
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `actuator_controls_status_0`, `actuator_controls_status_1`, `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_command`, `vehicle_status`, `vehicle_torque_setpoint` |
| Primary outputs | `autotune_attitude_control_status` |
| Referenced topics | `actuator_controls_status`, `actuator_controls_status_0`, `actuator_controls_status_1`, `autotune_attitude_control_status`, `manual_control_setpoint`, `parameter_update`, `vehicle_angular_velocity`, `vehicle_command`, `vehicle_status`, `vehicle_torque_setpoint` |
| Parameters/config | fw_autotune_attitude_control_params.yaml |
| Key classes | `SignalType`, `FwAutotuneAttitudeControl`, `state`, `amplitudeDetectionState` |

### Files

| File | Why it matters |
| --- | --- |
| fw_autotune_attitude_control.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| fw_autotune_attitude_control_params.yaml | Build, parameter, or module configuration |
| fw_autotune_attitude_control.hpp | Defines `SignalType` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["fw_autotune_attitude_control"]:::module
  Build["px4 module: fw_autotune_attitude_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_controls_status_0"]:::io
    In1["actuator_controls_status_1"]:::io
    In2["manual_control_setpoint"]:::io
    In3["parameter_update"]:::io
    In4["vehicle_angular_velocity"]:::io
    In5["vehicle_command"]:::io
  end
  subgraph Outputs
    Out0["autotune_attitude_control_status"]:::io
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
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/fw_autotune_attitude_control |
| Build kind | px4 module |
| Build target | fw_autotune_attitude_control |
| Runtime main | fw_autotune_attitude_control |
| Stack main | Not specified |
| Module config | fw_autotune_attitude_control_params.yaml |
| Detected sources | 1 |
| Detected headers | 1 |
| Detected configs | 2 |

### CMake Dependencies

- `hysteresis`
- `mathlib`
- `px4_work_queue`
- `SystemIdentification`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["fw_autotune_attitude_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_controls_status_0"]:::io --> UORBIn
  Sub1["actuator_controls_status_1"]:::io --> UORBIn
  Sub2["manual_control_setpoint"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["vehicle_angular_velocity"]:::io --> UORBIn
  UORBOut --> Pub0["autotune_attitude_control_status"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_controls_status | referenced |
| actuator_controls_status_0 | subscribed |
| actuator_controls_status_1 | subscribed |
| autotune_attitude_control_status | published |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_command | subscribed |
| vehicle_status | subscribed |
| vehicle_torque_setpoint | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 fw_autotune_attitude_control start"]:::exec
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
  S1: STATE_WAIT_FOR_DISARM
  S0 --> S1: detected state path
  S1 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `STATE_WAIT_FOR_DISARM`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as fw_autotune_attitude_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start fw_autotune_attitude_control
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
  class SignalType
  SignalType : fw_autotune_attitude_control.hpp
  class FwAutotuneAttitudeControl
  FwAutotuneAttitudeControl : fw_autotune_attitude_control.hpp
  class ModuleBase
  ModuleBase <|-- FwAutotuneAttitudeControl
  class state
  state : fw_autotune_attitude_control.hpp
  class amplitudeDetectionState
  amplitudeDetectionState : fw_autotune_attitude_control.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| SignalType |  | fw_autotune_attitude_control.hpp |
| FwAutotuneAttitudeControl | ModuleBase | fw_autotune_attitude_control.hpp |
| state |  | fw_autotune_attitude_control.hpp |
| amplitudeDetectionState |  | fw_autotune_attitude_control.hpp |

### Detected Enums

- `Axes`
- `SignalType`
- `amplitudeDetectionState`
- `state`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| fw_autotune_attitude_control.cpp | source |
| fw_autotune_attitude_control.hpp | header |
| fw_autotune_attitude_control_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
