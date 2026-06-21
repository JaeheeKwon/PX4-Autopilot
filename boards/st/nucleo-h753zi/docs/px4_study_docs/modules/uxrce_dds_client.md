# PX4 Module Architecture: `uxrce_dds_client`

- Source: `src/modules/uxrce_dds_client`
- Build target: `modules__uxrce_dds_client`
- Runtime main: `uxrce_dds_client`
- Build kind: `px4 module`
- Mermaid palette: `ash` grey tone

Architecture notes for the UXRCE-DDS Client module.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["uxrce_dds_client"]:::module
  Build["px4 module: modules__uxrce_dds_client"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["message_format_request"]:::io
    In1["vehicle_command_ack"]:::io
  end
  subgraph Outputs
    Out0["message_format_response"]:::io
    Out1["vehicle_command"]:::io
  end
  In0 --> Module
  In1 --> Module
  Build --> Module
  Params --> Module
  Schedule --> Module
  Module --> Out0
  Module --> Out1
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/uxrce_dds_client |
| Build kind | px4 module |
| Build target | modules__uxrce_dds_client |
| Runtime main | uxrce_dds_client |
| Stack main | 9000 |
| Module config | module.yaml |
| Detected sources | 3 |
| Detected headers | 4 |
| Detected configs | 3 |

### CMake Dependencies

- `git_micro_xrce_dds_client`
- `libmicroxrceddsclient_project`
- `microxrceddsclient`
- `libmicroxrceddsclient`
- `libmicrocdr`
- `timesync`
- `topic_bridge_files`
- `uorb_ucdr_headers`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["uxrce_dds_client logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["message_format_request"]:::io --> UORBIn
  Sub1["vehicle_command_ack"]:::io --> UORBIn
  UORBOut --> Pub0["message_format_response"]:::io
  UORBOut --> Pub1["vehicle_command"]:::io
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| message_format_request | subscribed |
| message_format_response | published |
| uORBTopics | referenced |
| vehicle_command | published |
| vehicle_command_ack | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 uxrce_dds_client start"]:::exec
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
  S0: PARMRK
  Initialized --> S0: detected state path
  S0 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `PARMRK`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as uxrce_dds_client
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start uxrce_dds_client
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
  class SrvBase
  SrvBase : srv_base.h
  class defines
  defines : srv_base.h
  class UxrceddsClient
  UxrceddsClient : uxrce_dds_client.h
  class ModuleBase
  ModuleBase <|-- UxrceddsClient
  class Transport
  Transport : uxrce_dds_client.h
  class ParticipantConfig
  ParticipantConfig : uxrce_dds_client.h
  class VehicleCommandSrv
  VehicleCommandSrv : vehicle_command_srv.h
  class implement
  implement : vehicle_command_srv.h
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| SrvBase |  | srv_base.h |
| defines |  | srv_base.h |
| UxrceddsClient | ModuleBase | uxrce_dds_client.h |
| Transport |  | uxrce_dds_client.h |
| ParticipantConfig |  | uxrce_dds_client.h |
| VehicleCommandSrv |  | vehicle_command_srv.h |
| implement |  | vehicle_command_srv.h |

### Detected Enums

- `ParticipantConfig`
- `Transport`

## Parameters and Configuration

- `UXRCE_DDS_AG_IP`
- `UXRCE_DDS_CFG`
- `UXRCE_DDS_DOM_ID`
- `UXRCE_DDS_FLCTRL`
- `UXRCE_DDS_KEY`
- `UXRCE_DDS_NS_IDX`
- `UXRCE_DDS_PRT`
- `UXRCE_DDS_PTCFG`
- `UXRCE_DDS_RX_TO`
- `UXRCE_DDS_SYNCC`
- `UXRCE_DDS_SYNCT`
- `UXRCE_DDS_TX_TO`

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| dds_topics.yaml | config |
| module.yaml | config |
| srv_base.cpp | source |
| srv_base.h | header |
| utilities.hpp | header |
| uxrce_dds_client.cpp | source |
| uxrce_dds_client.h | header |
| vehicle_command_srv.cpp | source |
| vehicle_command_srv.h | header |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
