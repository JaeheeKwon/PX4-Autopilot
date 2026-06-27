# PX4 Module Architecture: `mc_nn_control`

- Source: `src/modules/mc_nn_control`
- Build target: `mc_nn_control`
- Runtime main: `mc_nn_control`
- Build kind: `px4 module`
- Mermaid palette: `graphite` grey tone

Multicopter Neural Network Control module. This module is an end-to-end neural network control system for multicopters. It takes in 15 input values and outputs 4 control actions. Inputs: [pos_err(3), att(6), vel(3), ang_vel(3)] Outputs: [Actuator motors(4)]

## Description of Module

Runs an experimental neural-network multicopter control path.

### Primary Responsibilities

- Convert selected state estimates and setpoints into downstream control or actuator-facing setpoints.
- Consume runtime inputs from uORB topics such as `arming_check_request`, `manual_control_setpoint`, `parameter_update`, `register_ext_component_reply`, `trajectory_setpoint`, `vehicle_angular_velocity`, `vehicle_attitude`, `vehicle_local_position`, ... 1 more.
- Publish outputs or status topics such as `actuator_motors`, `arming_check_reply`, `config_control_setpoints`, `neural_control`, `register_ext_component_request`, `unregister_ext_component`.
- Use module configuration from `mc_nn_control_params.yaml`.
- Implement the main behavior in classes such as `MulticopterNeuralNetworkControl`.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `nav_and_controllers`.
- Uses uORB callback registration so new topic data can schedule execution.

## Background Theory

The neural-network controller evaluates a learned policy. Its math is feed-forward inference from normalized state features to actuator or setpoint outputs.

```text
a_0 = normalize(observation)
for layer l:
  a_l = activation(W_l * a_{l-1} + b_l)
output = denormalize(a_L)
command = constrain(output, command_min, command_max)
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `arming_check_request`, `manual_control_setpoint`, `parameter_update`, `register_ext_component_reply`, `trajectory_setpoint`, `vehicle_angular_velocity`, `vehicle_attitude`, `vehicle_local_position`, `vehicle_status` |
| Primary outputs | `actuator_motors`, `arming_check_reply`, `config_control_setpoints`, `neural_control`, `register_ext_component_request`, `unregister_ext_component` |
| Referenced topics | `actuator_motors`, `arming_check_reply`, `arming_check_request`, `config_control_setpoints`, `manual_control_setpoint`, `neural_control`, `parameter_update`, `register_ext_component_reply`, `register_ext_component_request`, `trajectory_setpoint`, ... 6 more |
| Parameters/config | mc_nn_control_params.yaml |
| Key classes | `MulticopterNeuralNetworkControl` |

### Files

| File | Why it matters |
| --- | --- |
| mc_nn_control.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| mc_nn_control_params.yaml | Build, parameter, or module configuration |
| mc_nn_control.hpp | Defines `MulticopterNeuralNetworkControl` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["mc_nn_control"]:::module
  Build["px4 module: mc_nn_control"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["arming_check_request"]:::io
    In1["manual_control_setpoint"]:::io
    In2["parameter_update"]:::io
    In3["register_ext_component_reply"]:::io
    In4["trajectory_setpoint"]:::io
    In5["vehicle_angular_velocity"]:::io
  end
  subgraph Outputs
    Out0["actuator_motors"]:::io
    Out1["arming_check_reply"]:::io
    Out2["config_control_setpoints"]:::io
    Out3["neural_control"]:::io
    Out4["register_ext_component_request"]:::io
    Out5["unregister_ext_component"]:::io
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
| Module path | src/modules/mc_nn_control |
| Build kind | px4 module |
| Build target | mc_nn_control |
| Runtime main | mc_nn_control |
| Stack main | Not specified |
| Module config | mc_nn_control_params.yaml |
| Detected sources | 2 |
| Detected headers | 2 |
| Detected configs | 2 |

### CMake Dependencies

- `tensorflow_lite_micro`
- `px4_work_queue`
- `mathlib`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["mc_nn_control logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["arming_check_request"]:::io --> UORBIn
  Sub1["manual_control_setpoint"]:::io --> UORBIn
  Sub2["parameter_update"]:::io --> UORBIn
  Sub3["register_ext_component_reply"]:::io --> UORBIn
  Sub4["trajectory_setpoint"]:::io --> UORBIn
  UORBOut --> Pub0["actuator_motors"]:::io
  UORBOut --> Pub1["arming_check_reply"]:::io
  UORBOut --> Pub2["config_control_setpoints"]:::io
  UORBOut --> Pub3["neural_control"]:::io
  UORBOut --> Pub4["register_ext_component_request"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_motors | published |
| arming_check_reply | published |
| arming_check_request | subscribed |
| config_control_setpoints | published |
| manual_control_setpoint | subscribed |
| neural_control | published |
| parameter_update | subscribed |
| register_ext_component_reply | subscribed |
| register_ext_component_request | published |
| trajectory_setpoint | subscribed |
| unregister_ext_component | published |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_control_mode | referenced |
| vehicle_local_position | subscribed |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 mc_nn_control start"]:::exec
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as mc_nn_control
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start mc_nn_control
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
  class MulticopterNeuralNetworkControl
  MulticopterNeuralNetworkControl : mc_nn_control.hpp
  class ModuleBase
  ModuleBase <|-- MulticopterNeuralNetworkControl
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| MulticopterNeuralNetworkControl | ModuleBase | mc_nn_control.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| control_net.cpp | source |
| control_net.hpp | header |
| mc_nn_control.cpp | source |
| mc_nn_control.hpp | header |
| mc_nn_control_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
