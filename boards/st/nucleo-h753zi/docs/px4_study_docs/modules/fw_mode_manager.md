# PX4 Module Architecture: `fw_mode_manager`

- Source: `src/modules/fw_mode_manager`
- Build target: `modules__fw_mode_manager`
- Runtime main: `fw_mode_manager`
- Build kind: `px4 module`
- Mermaid palette: `ash` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["fw_mode_manager"]:::module
  Build["px4 module: modules__fw_mode_manager"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["airspeed_validated"]:::io
    In1["parameter_update"]:::io
    In2["position_setpoint_triplet"]:::io
    In3["trajectory_setpoint"]:::io
    In4["vehicle_angular_velocity"]:::io
    In5["vehicle_attitude"]:::io
  end
  subgraph Outputs
    Out0["figure_eight_status"]:::io
    Out1["fixed_wing_lateral_guidance_status"]:::io
    Out2["fixed_wing_lateral_setpoint"]:::io
    Out3["fixed_wing_longitudinal_setpoint"]:::io
    Out4["fixed_wing_runway_control"]:::io
    Out5["flaps_setpoint"]:::io
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
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/fw_mode_manager |
| Build kind | px4 module |
| Build target | modules__fw_mode_manager |
| Runtime main | fw_mode_manager |
| Stack main | Not specified |
| Module config | fw_mode_manager_params.yaml |
| Detected sources | 5 |
| Detected headers | 5 |
| Detected configs | 7 |

### CMake Dependencies

- `${POSCONTROL_DEPENDENCIES}`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["fw_mode_manager logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["airspeed_validated"]:::io --> UORBIn
  Sub1["parameter_update"]:::io --> UORBIn
  Sub2["position_setpoint_triplet"]:::io --> UORBIn
  Sub3["trajectory_setpoint"]:::io --> UORBIn
  Sub4["vehicle_angular_velocity"]:::io --> UORBIn
  UORBOut --> Pub0["figure_eight_status"]:::io
  UORBOut --> Pub1["fixed_wing_lateral_guidance_status"]:::io
  UORBOut --> Pub2["fixed_wing_lateral_setpoint"]:::io
  UORBOut --> Pub3["fixed_wing_longitudinal_setpoint"]:::io
  UORBOut --> Pub4["fixed_wing_runway_control"]:::io
classDef module fill:#f2f2f2,stroke:#3d3d3d,color:#222222;
classDef io fill:#e6e6e6,stroke:#707070,color:#222222;
classDef data fill:#fbfbfb,stroke:#707070,color:#222222;
classDef exec fill:#d7d7d7,stroke:#3d3d3d,color:#222222;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| airspeed_validated | subscribed |
| figure_eight_status | published |
| fixed_wing_lateral_guidance_status | published |
| fixed_wing_lateral_setpoint | published |
| fixed_wing_longitudinal_setpoint | published |
| fixed_wing_runway_control | published |
| flaps_setpoint | published |
| landing_gear | published |
| lateral_control_configuration | published |
| launch_detection_status | published |
| longitudinal_control_configuration | published |
| normalized_unsigned_setpoint | referenced |
| orbit_status | published |
| parameter_update | subscribed |
| position_controller_landing_status | published |
| position_setpoint_triplet | subscribed |
| spoilers_setpoint | published |
| trajectory_setpoint | subscribed |
| vehicle_angular_velocity | subscribed |
| vehicle_attitude | subscribed |
| vehicle_attitude_setpoint | subscribed |
| vehicle_command | subscribed |
| vehicle_control_mode | subscribed |
| vehicle_global_position | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_local_position | subscribed |
| vehicle_local_position_setpoint | published |
| vehicle_status | subscribed |
| wind | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 fw_mode_manager start"]:::exec
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
  S0: FIXEDWINGMODEMANAGER_HPP_
  Initialized --> S0: detected state path
  S1: FW_POSCTRL_MODE
  S0 --> S1: detected state path
  S2: FW_POSCTRL_MODE_AUTO
  S1 --> S2: detected state path
  S3: FW_POSCTRL_MODE_AUTO_ALTI...
  S2 --> S3: detected state path
  S4: FW_POSCTRL_MODE_AUTO_CLIM...
  S3 --> S4: detected state path
  S5: FW_POSCTRL_MODE_AUTO_LAND...
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `FIXEDWINGMODEMANAGER_HPP_`
- `FW_POSCTRL_MODE`
- `FW_POSCTRL_MODE_AUTO`
- `FW_POSCTRL_MODE_AUTO_ALTITUDE`
- `FW_POSCTRL_MODE_AUTO_CLIMBRATE`
- `FW_POSCTRL_MODE_AUTO_LANDING_CIRCULAR`
- `FW_POSCTRL_MODE_AUTO_LANDING_STRAIGHT`
- `FW_POSCTRL_MODE_AUTO_PATH`
- `FW_POSCTRL_MODE_AUTO_TAKEOFF`
- `FW_POSCTRL_MODE_AUTO_TAKEOFF_NO_NAV`
- `FW_POSCTRL_MODE_MANUAL_ALTITUDE`
- `FW_POSCTRL_MODE_MANUAL_POSITION`
- `FW_POSCTRL_MODE_OTHER`
- `FW_POSCTRL_MODE_TRANSITION_TO_HOVER_HEADING_HOLD`
- `FW_POSCTRL_MODE_TRANSITION_TO_HOVER_LINE_FOLLOW`
- `NAVIGATION_STATE_AUTO_MISSION`
- `NAVIGATION_STATE_EXTERNAL1`
- `NAVIGATION_STATE_EXTERNAL8`
- `NAVIGATION_STATE_GUIDED_COURSE`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f2f2f2","secondaryColor":"#e6e6e6","tertiaryColor":"#fbfbfb","primaryBorderColor":"#707070","primaryTextColor":"#222222","lineColor":"#707070","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as fw_mode_manager
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start fw_mode_manager
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
  class CombinedControllerConfigurationHandler
  CombinedControllerConfigurationHandler : ControllerConfigurationHandler.hpp
  class FixedWingModeManager
  FixedWingModeManager : FixedWingModeManager.hpp
  class handling
  handling : FixedWingModeManager.hpp
  class at
  at : FixedWingModeManager.hpp
  class FigureEight
  FigureEight : figure_eight/FigureEight.hpp
  class ModuleParams
  ModuleParams <|-- FigureEight
  class FigureEightSegment
  FigureEightSegment : figure_eight/FigureEight.hpp
  class __EXPORT
  __EXPORT : launchdetection/LaunchDetector.h
  class __EXPORT_7
  __EXPORT_7 : runway_takeoff/RunwayTakeoff.h
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| CombinedControllerConfigurationHandler |  | ControllerConfigurationHandler.hpp |
| FixedWingModeManager |  | FixedWingModeManager.hpp |
| handling |  | FixedWingModeManager.hpp |
| at |  | FixedWingModeManager.hpp |
| FigureEight | ModuleParams | figure_eight/FigureEight.hpp |
| FigureEightSegment |  | figure_eight/FigureEight.hpp |
| __EXPORT |  | launchdetection/LaunchDetector.h |
| __EXPORT |  | runway_takeoff/RunwayTakeoff.h |

### Detected Enums

- `FW_POSCTRL_MODE`
- `FigureEightSegment`
- `LandingNudgingOption`
- `RunwayTakeoffState`
- `StickConfig`
- `TerrainEstimateUseOnLanding`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| CMakeLists.txt | build |
| ControllerConfigurationHandler.cpp | source |
| ControllerConfigurationHandler.hpp | header |
| FixedWingModeManager.cpp | source |
| FixedWingModeManager.hpp | header |
| figure_eight/CMakeLists.txt | build |
| figure_eight/FigureEight.cpp | source |
| figure_eight/FigureEight.hpp | header |
| fw_mode_manager_params.yaml | config |
| launchdetection/CMakeLists.txt | build |
| launchdetection/LaunchDetector.cpp | source |
| launchdetection/LaunchDetector.h | header |
| launchdetection/launchdetection_params.yaml | config |
| runway_takeoff/CMakeLists.txt | build |
| runway_takeoff/RunwayTakeoff.cpp | source |
| runway_takeoff/RunwayTakeoff.h | header |
| runway_takeoff/runway_takeoff_params.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
