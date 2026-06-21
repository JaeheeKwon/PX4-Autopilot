# PX4 Module Architecture: `navigator`

- Source: `src/modules/navigator`
- Build target: `modules__navigator`
- Runtime main: `navigator`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["navigator"]:::module
  Build["px4 module: modules__navigator"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["fixed_wing_lateral_guidance_status"]:::io
    In1["geofence_status"]:::io
    In2["home_position"]:::io
    In3["landing_target_pose"]:::io
    In4["mission"]:::io
    In5["parameter_update"]:::io
  end
  subgraph Outputs
    Out0["distance_sensor_mode_change_request"]:::io
    Out1["geofence_result"]:::io
    Out2["geofence_status"]:::io
    Out3["home_position"]:::io
    Out4["mission"]:::io
    Out5["mission_result"]:::io
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
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/navigator |
| Build kind | px4 module |
| Build target | modules__navigator |
| Runtime main | navigator |
| Stack main | Not specified |
| Module config | geofence_params.yaml |
| Detected sources | 20 |
| Detected headers | 23 |
| Detected configs | 8 |

### CMake Dependencies

- `dataman_client`
- `geo`
- `adsb`
- `motion_planning`
- `mission_feasibility_checker`
- `rtl_time_estimator`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["navigator logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["fixed_wing_lateral_guidance_status"]:::io --> UORBIn
  Sub1["geofence_status"]:::io --> UORBIn
  Sub2["home_position"]:::io --> UORBIn
  Sub3["landing_target_pose"]:::io --> UORBIn
  Sub4["mission"]:::io --> UORBIn
  UORBOut --> Pub0["distance_sensor_mode_change_request"]:::io
  UORBOut --> Pub1["geofence_result"]:::io
  UORBOut --> Pub2["geofence_status"]:::io
  UORBOut --> Pub3["home_position"]:::io
  UORBOut --> Pub4["mission"]:::io
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| distance_sensor_mode_change_request | published |
| fixed_wing_lateral_guidance_status | subscribed |
| geofence_result | published |
| geofence_status | subscribed, published |
| gimbal_manager_set_attitude | referenced |
| home_position | subscribed, published |
| landing_target_pose | subscribed |
| mission | subscribed, published |
| mission_result | published |
| mode_completed | published |
| navigator_mission_item | referenced |
| navigator_status | published |
| parameter_update | subscribed |
| position_controller_landing_status | subscribed |
| position_controller_status | subscribed |
| position_setpoint | referenced |
| position_setpoint_triplet | published |
| prec_land_status | published |
| rtl_status | subscribed, published |
| rtl_time_estimate | published |
| sensor_gps | referenced |
| telemetry_status | referenced |
| transponder_report | subscribed |
| vehicle_command | subscribed, published |
| vehicle_command_ack | published |
| vehicle_global_position | subscribed, published |
| vehicle_gps_position | subscribed |
| vehicle_land_detected | subscribed, published |
| vehicle_local_position | subscribed |
| vehicle_roi | published |
| vehicle_status | subscribed, published |
| vte_orientation | subscribed |
| vtol_vehicle_status | referenced |
| wind | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 navigator start"]:::exec
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
  S1: CHANGE_MODE
  S0 --> S1: detected state path
  S2: CONFIG_MODE_NAVIGATOR_VTO...
  S1 --> S2: detected state path
  S3: DM_KEY_FENCE_POINTS_STATE
  S2 --> S3: detected state path
  S4: DM_KEY_MISSION_STATE
  S3 --> S4: detected state path
  S5: DM_KEY_SAFE_POINTS_STATE
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `CHANGE_MODE`
- `CONFIG_MODE_NAVIGATOR_VTOL_TAKEOFF`
- `DM_KEY_FENCE_POINTS_STATE`
- `DM_KEY_MISSION_STATE`
- `DM_KEY_SAFE_POINTS_STATE`
- `FW_POSCTRL_MODE_AUTO`
- `MAV_CMD_DO_SET_MODE`
- `NAVIGATION_STATE_ACRO`
- `NAVIGATION_STATE_ALTCTL`
- `NAVIGATION_STATE_ALTITUDE_CRUISE`
- `NAVIGATION_STATE_AUTO_LAND`
- `NAVIGATION_STATE_AUTO_LOITER`
- `NAVIGATION_STATE_AUTO_MISSION`
- `NAVIGATION_STATE_AUTO_PRECLAND`
- `NAVIGATION_STATE_AUTO_RTL`
- `NAVIGATION_STATE_AUTO_TAKEOFF`
- `NAVIGATION_STATE_AUTO_VTOL_TAKEOFF`
- `NAVIGATION_STATE_DESCEND`
- `NAVIGATION_STATE_GUIDED_COURSE`
- `NAVIGATION_STATE_MANUAL`
- `NAVIGATION_STATE_OFFBOARD`
- `NAVIGATION_STATE_POSCTL`
- `NAVIGATION_STATE_STAB`
- `NAVIGATION_STATE_TERMINATION`
- `NAVIGATOR_MODE_ARRAY_SIZE`
- `NAV_CMD_COMPONENT_ARM_DISARM`
- `NAV_CMD_SET_CAMERA_MODE`
- `PREC_LAND_STATE_DESCEND`
- `PREC_LAND_STATE_DONE`
- `PREC_LAND_STATE_FALLBACK`
- `PREC_LAND_STATE_FINAL`
- `PREC_LAND_STATE_HORIZONTAL`
- `PREC_LAND_STATE_SEARCH`
- `PREC_LAND_STATE_START`
- `PREC_LAND_STATE_STOPPED`
- `VEHICLE_VTOL_STATE_FW`
- `VEHICLE_VTOL_STATE_MC`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as navigator
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start navigator
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
  class FeasibilityChecker
  FeasibilityChecker : MissionFeasibility/FeasibilityChecker.hpp
  class ModuleParams
  ModuleParams <|-- FeasibilityChecker
  class VehicleType
  VehicleType : MissionFeasibility/FeasibilityChecker.hpp
  class FeasibilityCheckerTest
  FeasibilityCheckerTest : MissionFeasibility/FeasibilityCheckerTest.cpp
  class TestFeasibilityChecker
  TestFeasibilityChecker : MissionFeasibility/FeasibilityCheckerTest.cpp
  class FeasibilityChecker
  FeasibilityChecker <|-- TestFeasibilityChecker
  class Course
  Course : course.h
  class MissionBlock
  MissionBlock <|-- Course
  class Navigator
  Navigator : geofence.h
  class Geofence
  Geofence : geofence.h
  class ModuleParams
  ModuleParams <|-- Geofence
  class DatamanState
  DatamanState : geofence.h
  class to
  to : geofence.h
  class to_9
  to_9 : land.cpp
  class to_10
  to_10 : land.h
  class Land
  Land : land.h
  class MissionBlock
  MissionBlock <|-- Land
  class to_12
  to_12 : loiter.cpp
  class to_13
  to_13 : loiter.h
  class Loiter
  Loiter : loiter.h
  class MissionBlock
  MissionBlock <|-- Loiter
  class to_15
  to_15 : mission.cpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| FeasibilityChecker | ModuleParams | MissionFeasibility/FeasibilityChecker.hpp |
| VehicleType |  | MissionFeasibility/FeasibilityChecker.hpp |
| FeasibilityCheckerTest |  | MissionFeasibility/FeasibilityCheckerTest.cpp |
| TestFeasibilityChecker | FeasibilityChecker | MissionFeasibility/FeasibilityCheckerTest.cpp |
| Course | MissionBlock | course.h |
| Navigator |  | geofence.h |
| Geofence | ModuleParams | geofence.h |
| DatamanState |  | geofence.h |
| to |  | geofence.h |
| to |  | land.cpp |
| to |  | land.h |
| Land | MissionBlock | land.h |
| to |  | loiter.cpp |
| to |  | loiter.h |
| Loiter | MissionBlock | loiter.h |
| to |  | mission.cpp |
| that |  | mission.h |
| gets |  | mission.h |
| Navigator |  | mission.h |
| Mission | MissionBase | mission.h |
| that |  | mission_base.cpp |
| attributes |  | mission_base.cpp |
| that |  | mission_base.h |
| Navigator |  | mission_base.h |
| ... 49 more |  |  |

### Detected Enums

- `DatamanState`
- `DestinationType`
- `HeadingMode`
- `MissionTraversalType`
- `MissionType`
- `NAV_CMD`
- `NAV_FRAME`
- `ORIGIN`
- `PrecLandMode`
- `PrecLandState`
- `RTLState`
- `RtlType`
- `VehicleType`
- `WorkItemType`
- `definitions`
- `fw_takeoff_state`
- `values`
- `vtol_takeoff_state`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| MissionFeasibility/CMakeLists.txt | build |
| MissionFeasibility/FeasibilityChecker.cpp | source |
| MissionFeasibility/FeasibilityChecker.hpp | header |
| MissionFeasibility/FeasibilityCheckerTest.cpp | source |
| course.cpp | source |
| course.h | header |
| geofence.cpp | source |
| geofence.h | header |
| geofence_params.yaml | config |
| land.cpp | source |
| land.h | header |
| loiter.cpp | source |
| loiter.h | header |
| mission.cpp | source |
| mission.h | header |
| mission_base.cpp | source |
| mission_base.h | header |
| mission_block.cpp | source |
| mission_block.h | header |
| mission_feasibility_checker.cpp | source |
| mission_feasibility_checker.h | header |
| mission_item_utils.h | header |
| mission_params.yaml | config |
| navigation.h | header |
| navigator.h | header |
| navigator_main.cpp | source |
| navigator_mode.cpp | source |
| navigator_mode.h | header |
| navigator_params.yaml | config |
| precland.cpp | source |
| precland.h | header |
| precland_params.yaml | config |
| rtl.cpp | source |
| rtl.h | header |
| rtl_base.h | header |
| rtl_direct.cpp | source |
| rtl_direct.h | header |
| rtl_direct_mission_land.cpp | source |
| rtl_direct_mission_land.h | header |
| ... 11 more files | omitted |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
