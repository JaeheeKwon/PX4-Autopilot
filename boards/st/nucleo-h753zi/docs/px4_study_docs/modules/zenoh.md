# PX4 Module Architecture: `zenoh`

- Source: `src/modules/zenoh`
- Build target: `modules__zenoh`
- Runtime main: `zenoh`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Architecture notes for the Zenoh bridge module.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["zenoh"]:::module
  Build["px4 module: modules__zenoh"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_outputs"]:::io
    In1["input_rc"]:::io
    In2["parameter_update"]:::io
    In3["uORBTopics"]:::io
  end
  Out0["no output topics detected"]:::io
  In0 --> Module
  In1 --> Module
  In2 --> Module
  In3 --> Module
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
| Module path | src/modules/zenoh |
| Build kind | px4 module |
| Build target | modules__zenoh |
| Runtime main | zenoh |
| Stack main | Not specified |
| Module config | module.yaml |
| Detected sources | 4 |
| Detected headers | 7 |
| Detected configs | 4 |

### CMake Dependencies

- `cdr`
- `uorb_msgs`
- `px4_work_queue`
- `zenohpico_static`
- `zenoh_topics`
- `git_zenoh-pico`
- `default_topics_config`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["zenoh logic"]:::module
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
| actuator_outputs | referenced |
| input_rc | referenced |
| parameter_update | referenced |
| uORBTopics | referenced |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 zenoh start"]:::exec
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
  S0: NET_MODE_SIZE
  Initialized --> S0: detected state path
  S1: Z_CONFIG_MODE_DEFAULT
  S0 --> S1: detected state path
  S2: Z_CONFIG_MODE_KEY
  S1 --> S2: detected state path
  S3: Z_CONFIG_MODE_PEER
  S2 --> S3: detected state path
  S3 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `NET_MODE_SIZE`
- `Z_CONFIG_MODE_DEFAULT`
- `Z_CONFIG_MODE_KEY`
- `Z_CONFIG_MODE_PEER`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as zenoh
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start zenoh
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
  class uORB_Zenoh_Publisher
  uORB_Zenoh_Publisher : publishers/uorb_publisher.hpp
  class Zenoh_Publisher
  Zenoh_Publisher <|-- uORB_Zenoh_Publisher
  class Zenoh_Publisher
  Zenoh_Publisher : publishers/zenoh_publisher.hpp
  class ListNode
  ListNode <|-- Zenoh_Publisher
  class uORB_Zenoh_Subscriber
  uORB_Zenoh_Subscriber : subscribers/uorb_subscriber.hpp
  class Zenoh_Subscriber
  Zenoh_Subscriber <|-- uORB_Zenoh_Subscriber
  class size_t
  size_t : subscribers/uorb_subscriber.hpp
  class Zenoh_Subscriber
  Zenoh_Subscriber : subscribers/zenoh_subscriber.hpp
  class ListNode
  ListNode <|-- Zenoh_Subscriber
  class ZENOH
  ZENOH : zenoh.h
  class ModuleBase
  ModuleBase <|-- ZENOH
  class Zenoh_Config
  Zenoh_Config : zenoh_config.hpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| uORB_Zenoh_Publisher | Zenoh_Publisher | publishers/uorb_publisher.hpp |
| Zenoh_Publisher | ListNode | publishers/zenoh_publisher.hpp |
| uORB_Zenoh_Subscriber | Zenoh_Subscriber | subscribers/uorb_subscriber.hpp |
| size_t |  | subscribers/uorb_subscriber.hpp |
| Zenoh_Subscriber | ListNode | subscribers/zenoh_subscriber.hpp |
| ZENOH | ModuleBase | zenoh.h |
| Zenoh_Config |  | zenoh_config.hpp |

### Detected Enums

- No enums detected.

## Parameters and Configuration

- `ZENOH_ENABLE`

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| dds_topics.yaml | config |
| module.yaml | config |
| publishers/uorb_publisher.hpp | header |
| publishers/zenoh_publisher.cpp | source |
| publishers/zenoh_publisher.hpp | header |
| rmw_attachment.h | header |
| subscribers/uorb_subscriber.hpp | header |
| subscribers/zenoh_subscriber.cpp | source |
| subscribers/zenoh_subscriber.hpp | header |
| zenoh.cpp | source |
| zenoh.h | header |
| zenoh_config.cpp | source |
| zenoh_config.hpp | header |
| zenoh_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
