# PX4 Module Architecture: `vision_target_estimator`

- Source: `src/modules/vision_target_estimator`
- Build target: `modules__vision_target_estimator`
- Runtime main: `vision_target_estimator`
- Build kind: `px4 module`
- Mermaid palette: `mist` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["vision_target_estimator"]:::module
  Build["px4 module: modules__vision_target_esti..."]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["fiducial_marker_pos_report"]:::io
    In1["fiducial_marker_yaw_report"]:::io
    In2["home_position"]:::io
    In3["navigator_mission_item"]:::io
    In4["parameter_update"]:::io
    In5["position_setpoint_triplet"]:::io
  end
  subgraph Outputs
    Out0["landing_target_pose"]:::io
    Out1["vte_aid_ev_yaw"]:::io
    Out2["vte_aid_fiducial_marker"]:::io
    Out3["vte_aid_gps_pos_mission"]:::io
    Out4["vte_aid_gps_pos_target"]:::io
    Out5["vte_aid_gps_vel_target"]:::io
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
| Module path | src/modules/vision_target_estimator |
| Build kind | px4 module |
| Build target | modules__vision_target_estimator |
| Runtime main | vision_target_estimator |
| Stack main | Not specified |
| Module config | vision_target_estimator_params.yaml |
| Detected sources | 6 |
| Detected headers | 24 |
| Detected configs | 2 |

### CMake Dependencies

- `mathlib`
- `px4_work_queue`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["vision_target_estimator logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["fiducial_marker_pos_report"]:::io --> UORBIn
  Sub1["fiducial_marker_yaw_report"]:::io --> UORBIn
  Sub2["home_position"]:::io --> UORBIn
  Sub3["navigator_mission_item"]:::io --> UORBIn
  Sub4["parameter_update"]:::io --> UORBIn
  UORBOut --> Pub0["landing_target_pose"]:::io
  UORBOut --> Pub1["vte_aid_ev_yaw"]:::io
  UORBOut --> Pub2["vte_aid_fiducial_marker"]:::io
  UORBOut --> Pub3["vte_aid_gps_pos_mission"]:::io
  UORBOut --> Pub4["vte_aid_gps_pos_target"]:::io
classDef module fill:#f1f3f5,stroke:#343a40,color:#212529;
classDef io fill:#e9ecef,stroke:#6c757d,color:#212529;
classDef data fill:#f8f9fa,stroke:#6c757d,color:#212529;
classDef exec fill:#dee2e6,stroke:#343a40,color:#212529;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| fiducial_marker_pos_report | subscribed |
| fiducial_marker_yaw_report | subscribed |
| home_position | subscribed |
| landing_target_pose | published |
| navigator_mission_item | subscribed |
| parameter_update | subscribed |
| position_setpoint_triplet | subscribed |
| prec_land_status | subscribed |
| sensor_gps | referenced |
| target_gnss | subscribed |
| vehicle_acceleration | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_gps_position | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vte_aid_ev_yaw | published |
| vte_aid_fiducial_marker | published |
| vte_aid_gps_pos_mission | published |
| vte_aid_gps_pos_target | published |
| vte_aid_gps_vel_target | published |
| vte_aid_gps_vel_uav | published |
| vte_aid_source1d | referenced |
| vte_aid_source3d | referenced |
| vte_bias_init_status | published |
| vte_input | published |
| vte_orientation | published |
| vte_position | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 vision_target_estimator start"]:::exec
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
  S0: EKF_STATE_H
  Initialized --> S0: detected state path
  S1: PREC_LAND_STATE_DONE
  S0 --> S1: detected state path
  S2: PREC_LAND_STATE_STOPPED
  S1 --> S2: detected state path
  S2 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `EKF_STATE_H`
- `PREC_LAND_STATE_DONE`
- `PREC_LAND_STATE_STOPPED`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f1f3f5","secondaryColor":"#e9ecef","tertiaryColor":"#f8f9fa","primaryBorderColor":"#6c757d","primaryTextColor":"#212529","lineColor":"#6c757d","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as vision_target_estimator
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start vision_target_estimator
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
  class KF_orientation
  KF_orientation : Orientation/KF_orientation.h
  class OOSMManager
  OOSMManager : Orientation/KF_orientation.h
  class VTEOrientation
  VTEOrientation : Orientation/VTEOrientation.h
  class ModuleParams
  ModuleParams <|-- VTEOrientation
  class KF_position
  KF_position : Position/KF_position.h
  class OOSMManager_4
  OOSMManager_4 : Position/KF_position.h
  class VTEPosition
  VTEPosition : Position/VTEPosition.h
  class ModuleParams
  ModuleParams <|-- VTEPosition
  class ObsType
  ObsType : Position/VTEPosition.h
  class PreBiasReference
  PreBiasReference : Position/VTEPosition.h
  class OOSMManager_8
  OOSMManager_8 : VTEOosm.h
  class VisionTargetEstTest
  VisionTargetEstTest : VisionTargetEst.h
  class VisionTargetEstTestable
  VisionTargetEstTestable : VisionTargetEst.h
  class VisionTargetEst
  VisionTargetEst : VisionTargetEst.h
  class ModuleBase
  ModuleBase <|-- VisionTargetEst
  class TimeSourceProvider
  TimeSourceProvider : common.h
  class VisionTargetEstTest_13
  VisionTargetEstTest_13 : tasks/PrecLandTask.h
  class VisionTargetEstTestable_14
  VisionTargetEstTestable_14 : tasks/PrecLandTask.h
  class VTEPosition_15
  VTEPosition_15 : tasks/PrecLandTask.h
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| KF_orientation |  | Orientation/KF_orientation.h |
| OOSMManager |  | Orientation/KF_orientation.h |
| VTEOrientation | ModuleParams | Orientation/VTEOrientation.h |
| KF_position |  | Position/KF_position.h |
| OOSMManager |  | Position/KF_position.h |
| VTEPosition | ModuleParams | Position/VTEPosition.h |
| ObsType |  | Position/VTEPosition.h |
| PreBiasReference |  | Position/VTEPosition.h |
| OOSMManager |  | VTEOosm.h |
| VisionTargetEstTest |  | VisionTargetEst.h |
| VisionTargetEstTestable |  | VisionTargetEst.h |
| VisionTargetEst | ModuleBase | VisionTargetEst.h |
| TimeSourceProvider |  | common.h |
| VisionTargetEstTest |  | tasks/PrecLandTask.h |
| VisionTargetEstTestable |  | tasks/PrecLandTask.h |
| VTEPosition |  | tasks/PrecLandTask.h |
| PrecLandTask |  | tasks/PrecLandTask.h |
| VTEPosition |  | tasks/VteTask.h |
| VteTask |  | tasks/VteTask.h |
| DebugTask |  | tasks/VteTask.h |

### Detected Enums

- `ObsType`
- `PreBiasReference`
- `State`
- `values`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| Orientation/KF_orientation.cpp | source |
| Orientation/KF_orientation.h | header |
| Orientation/VTEOrientation.cpp | source |
| Orientation/VTEOrientation.h | header |
| Orientation/vtest_derivation/generated/getTransitionMatrix.h | header |
| Orientation/vtest_derivation/generated/predictCov.h | header |
| Orientation/vtest_derivation/generated/predictState.h | header |
| Position/KF_position.cpp | source |
| Position/KF_position.h | header |
| Position/VTEPosition.cpp | source |
| Position/VTEPosition.h | header |
| Position/vtest_derivation/generated/applyCorrection.h | header |
| Position/vtest_derivation/generated/computeInnovCov.h | header |
| Position/vtest_derivation/generated/getTransitionMatrix.h | header |
| Position/vtest_derivation/generated/predictCov.h | header |
| Position/vtest_derivation/generated/predictState.h | header |
| Position/vtest_derivation/generated/state.h | header |
| Position/vtest_derivation/generated_moving/applyCorrection.h | header |
| Position/vtest_derivation/generated_moving/computeInnovCov.h | header |
| Position/vtest_derivation/generated_moving/getTransitionMatrix.h | header |
| Position/vtest_derivation/generated_moving/predictCov.h | header |
| Position/vtest_derivation/generated_moving/predictState.h | header |
| Position/vtest_derivation/generated_moving/state.h | header |
| VTEOosm.h | header |
| VisionTargetEst.cpp | source |
| VisionTargetEst.h | header |
| common.h | header |
| tasks/PrecLandTask.cpp | source |
| tasks/PrecLandTask.h | header |
| tasks/VteTask.h | header |
| vision_target_estimator_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
