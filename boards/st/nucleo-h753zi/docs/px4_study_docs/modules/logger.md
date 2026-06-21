# PX4 Module Architecture: `logger`

- Source: `src/modules/logger`
- Build target: `modules__logger`
- Runtime main: `logger`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Architecture notes for the logger module.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["logger"]:::module
  Build["px4 module: modules__logger"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["battery_status"]:::io
    In1["log_message"]:::io
    In2["manual_control_setpoint"]:::io
    In3["parameter_update"]:::io
    In4["ulog_stream_ack"]:::io
    In5["vehicle_command"]:::io
  end
  subgraph Outputs
    Out0["logger_status"]:::io
    Out1["ulog_stream"]:::io
    Out2["vehicle_command_ack"]:::io
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
| Module path | src/modules/logger |
| Build kind | px4 module |
| Build target | modules__logger |
| Runtime main | logger |
| Stack main | 2500 |
| Module config | module.yaml |
| Detected sources | 10 |
| Detected headers | 9 |
| Detected configs | 3 |

### CMake Dependencies

- `version`
- `component_general_json`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["logger logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["battery_status"]:::io --> UORBIn
  Sub1["log_message"]:::io --> UORBIn
  Sub2["manual_control_setpoint"]:::io --> UORBIn
  Sub3["parameter_update"]:::io --> UORBIn
  Sub4["ulog_stream_ack"]:::io --> UORBIn
  UORBOut --> Pub0["logger_status"]:::io
  UORBOut --> Pub1["ulog_stream"]:::io
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
| log_message | subscribed |
| logger_status | published |
| manual_control_setpoint | subscribed |
| parameter_update | subscribed |
| uORBTopics | referenced |
| ulog_stream | published |
| ulog_stream_ack | subscribed |
| vehicle_command | subscribed |
| vehicle_command_ack | published |
| vehicle_status | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 logger start"]:::exec
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
  S1: PX4_O_MODE_666
  S0 --> S1: detected state path
  S2: TSTATE_TASK_INVALID
  S1 --> S2: detected state path
  S3: TSTATE_TASK_READYTORUN
  S2 --> S3: detected state path
  S3 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `PX4_O_MODE_666`
- `TSTATE_TASK_INVALID`
- `TSTATE_TASK_READYTORUN`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as logger
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start logger
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
  class LogWriter
  LogWriter : log_writer.h
  class LogType
  LogType : log_writer_file.h
  class LogWriterFile
  LogWriterFile : log_writer_file.h
  class LogFileBuffer
  LogFileBuffer : log_writer_file.h
  class LogWriterMavlink
  LogWriterMavlink : log_writer_mavlink.h
  class SDLogProfileMask
  SDLogProfileMask : logged_topics.h
  class MissionLogType
  MissionLogType : logged_topics.h
  class LoggedTopics
  LoggedTopics : logged_topics.h
  class Logger
  Logger : logger.h
  class ModuleBase
  ModuleBase <|-- Logger
  class LogMode
  LogMode : logger.h
  class PrintLoadReason
  PrintLoadReason : logger.h
  class ULogMessageType
  ULogMessageType : messages.h
  class ulog_parameter_default_type_t
  ulog_parameter_default_type_t : messages.h
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| LogWriter |  | log_writer.h |
| LogType |  | log_writer_file.h |
| LogWriterFile |  | log_writer_file.h |
| LogFileBuffer |  | log_writer_file.h |
| LogWriterMavlink |  | log_writer_mavlink.h |
| SDLogProfileMask |  | logged_topics.h |
| MissionLogType |  | logged_topics.h |
| LoggedTopics |  | logged_topics.h |
| Logger | ModuleBase | logger.h |
| LogMode |  | logger.h |
| PrintLoadReason |  | logger.h |
| ULogMessageType |  | messages.h |
| ulog_parameter_default_type_t |  | messages.h |

### Detected Enums

- `LogMode`
- `LogType`
- `MissionLogType`
- `PrintLoadReason`
- `SDLogProfileMask`
- `ULogMessageType`
- `ulog_parameter_default_type_t`
- `values`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| ULogMessagesTest.cpp | source |
| log_writer.cpp | source |
| log_writer.h | header |
| log_writer_file.cpp | source |
| log_writer_file.h | header |
| log_writer_mavlink.cpp | source |
| log_writer_mavlink.h | header |
| logged_topics.cpp | source |
| logged_topics.h | header |
| logger.cpp | source |
| logger.h | header |
| loggerUtilTest.cpp | source |
| messages.h | header |
| module.yaml | config |
| module_params_crypto.yaml | config |
| util.cpp | source |
| util.h | header |
| util_parse.cpp | source |
| util_parse.h | header |
| watchdog.cpp | source |
| watchdog.h | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
