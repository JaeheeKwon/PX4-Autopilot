# PX4 Module Architecture: `mc_hover_thrust_estimator`

- Source: `src/modules/mc_hover_thrust_estimator`
- Build target: `modules__mc_hover_thrust_estimator`
- Runtime main: `mc_hover_thrust_estimator`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["mc_hover_thrust_estimator"]:::module
  Build["px4 module: modules__mc_hover_thrust_es..."]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["control_allocator_status"]:::io
    In1["hover_thrust_estimate"]:::io
    In2["parameter_update"]:::io
    In3["vehicle_attitude"]:::io
    In4["vehicle_land_detected"]:::io
    In5["vehicle_local_position"]:::io
  end
  subgraph Outputs
    Out0["hover_thrust_estimate"]:::io
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
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/mc_hover_thrust_estimator |
| Build kind | px4 module |
| Build target | modules__mc_hover_thrust_estimator |
| Runtime main | mc_hover_thrust_estimator |
| Stack main | Not specified |
| Module config | hover_thrust_estimator_params.yaml |
| Detected sources | 3 |
| Detected headers | 2 |
| Detected configs | 2 |

### CMake Dependencies

- `hysteresis`
- `mathlib`
- `px4_work_queue`
- `zero_order_hover_thrust_ekf`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["mc_hover_thrust_estimator logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["control_allocator_status"]:::io --> UORBIn
  Sub1["hover_thrust_estimate"]:::io --> UORBIn
  Sub2["parameter_update"]:::io --> UORBIn
  Sub3["vehicle_attitude"]:::io --> UORBIn
  Sub4["vehicle_land_detected"]:::io --> UORBIn
  UORBOut --> Pub0["hover_thrust_estimate"]:::io
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| control_allocator_status | subscribed |
| hover_thrust_estimate | subscribed, published |
| parameter_update | subscribed |
| vehicle_attitude | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_status | subscribed |
| vehicle_thrust_setpoint | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 mc_hover_thrust_estimator start"]:::exec
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
  participant M as mc_hover_thrust_estimator
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start mc_hover_thrust_estimator
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
  class MulticopterHoverThrustEstimator
  MulticopterHoverThrustEstimator : MulticopterHoverThrustEstimator.hpp
  class ModuleBase
  ModuleBase <|-- MulticopterHoverThrustEstimator
  class ZeroOrderHoverThrustEkf
  ZeroOrderHoverThrustEkf : zero_order_hover_thrust_ekf.hpp
  class ZeroOrderHoverThrustEkfTest
  ZeroOrderHoverThrustEkfTest : zero_order_hover_thrust_ekf_test.cpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| MulticopterHoverThrustEstimator | ModuleBase | MulticopterHoverThrustEstimator.hpp |
| ZeroOrderHoverThrustEkf |  | zero_order_hover_thrust_ekf.hpp |
| ZeroOrderHoverThrustEkfTest |  | zero_order_hover_thrust_ekf_test.cpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| MulticopterHoverThrustEstimator.cpp | source |
| MulticopterHoverThrustEstimator.hpp | header |
| hover_thrust_estimator_params.yaml | config |
| zero_order_hover_thrust_ekf.cpp | source |
| zero_order_hover_thrust_ekf.hpp | header |
| zero_order_hover_thrust_ekf_test.cpp | source |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
