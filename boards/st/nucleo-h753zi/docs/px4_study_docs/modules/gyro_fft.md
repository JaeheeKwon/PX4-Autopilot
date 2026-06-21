# PX4 Module Architecture: `gyro_fft`

- Source: `src/modules/gyro_fft`
- Build target: `modules__gyro_fft`
- Runtime main: `gyro_fft`
- Build kind: `px4 module`
- Mermaid palette: `ash` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["gyro_fft"]:::module
  Build["px4 module: modules__gyro_fft"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["parameter_update"]:::io
    In1["sensor_gyro"]:::io
    In2["sensor_gyro_fifo"]:::io
    In3["sensor_selection"]:::io
    In4["vehicle_imu_status"]:::io
  end
  subgraph Outputs
    Out0["sensor_gyro_fft"]:::io
  end
  In0 --> Module
  In1 --> Module
  In2 --> Module
  In3 --> Module
  In4 --> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module --> Out0
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/gyro_fft |
| Build kind | px4 module |
| Build target | modules__gyro_fft |
| Runtime main | gyro_fft |
| Stack main | 4096 |
| Module config | parameters.yaml |
| Detected sources | 10 |
| Detected headers | 6 |
| Detected configs | 2 |

### CMake Dependencies

- `px4_work_queue`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["gyro_fft logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["parameter_update"]:::io --> UORBIn
  Sub1["sensor_gyro"]:::io --> UORBIn
  Sub2["sensor_gyro_fifo"]:::io --> UORBIn
  Sub3["sensor_selection"]:::io --> UORBIn
  Sub4["vehicle_imu_status"]:::io --> UORBIn
  UORBOut --> Pub0["sensor_gyro_fft"]:::io
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| parameter_update | subscribed |
| sensor_gyro | subscribed |
| sensor_gyro_fft | published |
| sensor_gyro_fifo | subscribed |
| sensor_selection | subscribed |
| vehicle_imu_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 gyro_fft start"]:::exec
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as gyro_fft
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start gyro_fft
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
  class classification
  classification : CMSIS_5/CMSIS/DSP/Include/arm_math.h
  class GyroFFT
  GyroFFT : GyroFFT.hpp
  class ModuleBase
  ModuleBase <|-- GyroFFT
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| classification |  | CMSIS_5/CMSIS/DSP/Include/arm_math.h |
| GyroFFT | ModuleBase | GyroFFT.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMSIS_5/CMSIS/Core/Include/cmsis_compiler.h | header |
| CMSIS_5/CMSIS/Core/Include/cmsis_gcc.h | header |
| CMSIS_5/CMSIS/DSP/Include/arm_common_tables.h | header |
| CMSIS_5/CMSIS/DSP/Include/arm_const_structs.h | header |
| CMSIS_5/CMSIS/DSP/Include/arm_math.h | header |
| CMSIS_5/CMSIS/DSP/Source/BasicMathFunctions/arm_mult_q15.c | source |
| CMSIS_5/CMSIS/DSP/Source/CommonTables/arm_common_tables.c | source |
| CMSIS_5/CMSIS/DSP/Source/CommonTables/arm_const_structs.c | source |
| CMSIS_5/CMSIS/DSP/Source/SupportFunctions/arm_float_to_q15.c | source |
| CMSIS_5/CMSIS/DSP/Source/TransformFunctions/arm_bitreversal2.c | source |
| CMSIS_5/CMSIS/DSP/Source/TransformFunctions/arm_cfft_q15.c | source |
| CMSIS_5/CMSIS/DSP/Source/TransformFunctions/arm_cfft_radix4_q15.c | source |
| CMSIS_5/CMSIS/DSP/Source/TransformFunctions/arm_rfft_init_q15.c | source |
| CMSIS_5/CMSIS/DSP/Source/TransformFunctions/arm_rfft_q15.c | source |
| CMakeLists.txt | build |
| GyroFFT.cpp | source |
| GyroFFT.hpp | header |
| parameters.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
