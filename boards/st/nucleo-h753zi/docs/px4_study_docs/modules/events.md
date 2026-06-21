# PX4 Module Architecture: `events`

- Source: `src/modules/events`
- Build target: `modules__events`
- Runtime main: `send_event`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["events"]:::module
  Build["px4 module: modules__events"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["battery_status"]:::io
    In1["cpuload"]:::io
    In2["failsafe_flags"]:::io
    In3["vehicle_command"]:::io
    In4["vehicle_status"]:::io
  end
  subgraph Outputs
    Out0["led_control"]:::io
    Out1["tune_control"]:::io
    Out2["vehicle_command_ack"]:::io
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
| Module path | src/modules/events |
| Build kind | px4 module |
| Build target | modules__events |
| Runtime main | send_event |
| Stack main | Not specified |
| Module config | events_params.yaml |
| Detected sources | 4 |
| Detected headers | 3 |
| Detected configs | 2 |

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
  Logic["send_event logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["battery_status"]:::io --> UORBIn
  Sub1["cpuload"]:::io --> UORBIn
  Sub2["failsafe_flags"]:::io --> UORBIn
  Sub3["vehicle_command"]:::io --> UORBIn
  Sub4["vehicle_status"]:::io --> UORBIn
  UORBOut --> Pub0["led_control"]:::io
  UORBOut --> Pub1["tune_control"]:::io
  UORBOut --> Pub2["vehicle_command_ack"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| battery_status | subscribed |
| cpuload | subscribed |
| failsafe_flags | subscribed |
| led_control | published |
| tune_control | published |
| vehicle_command | subscribed |
| vehicle_command_ack | published |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 send_event start"]:::exec
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
  S1: NAVIGATION_STATE_ALTCTL
  S0 --> S1: detected state path
  S2: NAVIGATION_STATE_AUTO_LAND
  S1 --> S2: detected state path
  S3: NAVIGATION_STATE_AUTO_MIS...
  S2 --> S3: detected state path
  S4: NAVIGATION_STATE_AUTO_RTL
  S3 --> S4: detected state path
  S4 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `NAVIGATION_STATE_ALTCTL`
- `NAVIGATION_STATE_AUTO_LAND`
- `NAVIGATION_STATE_AUTO_MISSION`
- `NAVIGATION_STATE_AUTO_RTL`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as send_event
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start send_event
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
  class RC_Loss_Alarm
  RC_Loss_Alarm : rc_loss_alarm.h
  class SendEvent
  SendEvent : send_event.h
  class manages
  manages : send_event.h
  class in
  in : send_event.h
  class StatusDisplay
  StatusDisplay : status_display.h
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| RC_Loss_Alarm |  | rc_loss_alarm.h |
| SendEvent |  | send_event.h |
| manages |  | send_event.h |
| in |  | send_event.h |
| StatusDisplay |  | status_display.h |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| events_params.yaml | config |
| rc_loss_alarm.cpp | source |
| rc_loss_alarm.h | header |
| send_event.cpp | source |
| send_event.h | header |
| set_leds.cpp | source |
| status_display.cpp | source |
| status_display.h | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
