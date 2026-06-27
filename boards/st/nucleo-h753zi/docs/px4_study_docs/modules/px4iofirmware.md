# PX4 Module Architecture: `px4iofirmware`

- Source: `src/modules/px4iofirmware`
- Build target: `px4iofirmware`
- Runtime main: `px4iofirmware`
- Build kind: `library`
- Mermaid palette: `slate` grey tone

Source-derived architecture notes for this PX4 module directory.

## Description of Module

Builds PX4IO firmware support code for the IO co-processor path.

### Primary Responsibilities

- Reference uORB topics such as `input_rc`.
- Do not publish directly detected uORB outputs from this module directory.
- Implement behavior mostly in C/C++ source functions rather than detected C++ classes.

### Runtime Behavior

- Scheduling style was not explicit in the detected source inventory; inspect the entry source for runtime details.

## Background Theory

No dedicated mathematical model was identified in the generated source scan. This module is best understood through its PX4 state handling, uORB message flow, scheduling, and configuration surfaces described below.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | none detected |
| Primary outputs | none detected |
| Referenced topics | `input_rc` |
| Parameters/config | none detected |
| Key classes | none detected |

### Files

| File | Why it matters |
| --- | --- |
| CMakeLists.txt | Build, parameter, or module configuration |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["px4iofirmware"]:::module
  Build["library: px4iofirmware"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["input_rc"]:::io
  end
  Out0["no output topics detected"]:::io
  In0 --> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module -.-> Out0
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/px4iofirmware |
| Build kind | library |
| Build target | px4iofirmware |
| Runtime main | px4iofirmware |
| Stack main | Not specified |
| Module config | Not specified |
| Detected sources | 7 |
| Detected headers | 2 |
| Detected configs | 1 |

### CMake Dependencies

- No explicit CMake dependencies detected.

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["px4iofirmware logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| input_rc | referenced |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 px4iofirmware start"]:::exec
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
  S0: LED_PATTERN_FMU_ARMED
  Initialized --> S0: detected state path
  S1: LED_PATTERN_FMU_OK_TO_ARM
  S0 --> S1: detected state path
  S2: LED_PATTERN_FMU_REFUSE_TO...
  S1 --> S2: detected state path
  S3: LED_PATTERN_IO_ARMED
  S2 --> S3: detected state path
  S4: LED_PATTERN_IO_FMU_ARMED
  S3 --> S4: detected state path
  S5: MIX_DISARMED
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `LED_PATTERN_FMU_ARMED`
- `LED_PATTERN_FMU_OK_TO_ARM`
- `LED_PATTERN_FMU_REFUSE_TO_ARM`
- `LED_PATTERN_IO_ARMED`
- `LED_PATTERN_IO_FMU_ARMED`
- `MIX_DISARMED`
- `MIX_FAILSAFE`
- `PX4IO_PAGE_DISARMED_PWM`
- `PX4IO_PAGE_FAILSAFE_PWM`
- `PX4IO_P_RAW_RC_FLAGS_FAILSAFE`
- `PX4IO_P_SETUP_ARMING`
- `PX4IO_P_SETUP_ARMING_FAILSAFE_CUSTOM`
- `PX4IO_P_SETUP_ARMING_FMU_ARMED`
- `PX4IO_P_SETUP_ARMING_FMU_PREARMED`
- `PX4IO_P_SETUP_ARMING_IO_ARM_OK`
- `PX4IO_P_SETUP_ARMING_LOCKDOWN`
- `PX4IO_P_SETUP_ARMING_TERMINATION`
- `PX4IO_P_SETUP_ARMING_TERMINATION_FAILSAFE`
- `PX4IO_P_SETUP_ARMING_VALID`
- `PX4IO_P_STATUS_ALARMS`
- `PX4IO_P_STATUS_ALARMS_PWM_ERROR`
- `PX4IO_P_STATUS_ALARMS_RC_LOST`
- `PX4IO_P_STATUS_FLAGS_ARM_SYNC`
- `PX4IO_P_STATUS_FLAGS_FAILSAFE`
- `PX4IO_P_STATUS_FLAGS_OUTPUTS_ARMED`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as px4iofirmware
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start px4iofirmware
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
  class px4iofirmware
  px4iofirmware : library
  px4iofirmware : classes not detected
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| None detected. | None detected. | None detected. |

### Detected Enums

- `mixer_source`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| adc.cpp | source |
| controls.cpp | source |
| mixer.cpp | source |
| protocol.h | header |
| px4io.cpp | source |
| px4io.h | header |
| registers.c | source |
| safety_button.cpp | source |
| serial.cpp | source |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
