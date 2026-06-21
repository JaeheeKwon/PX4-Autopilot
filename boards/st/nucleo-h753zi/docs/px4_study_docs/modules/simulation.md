# PX4 Module Architecture: `simulation`

- Source: `src/modules/simulation`
- Build target: `simulation`
- Runtime main: `simulation`
- Build kind: `directory`
- Mermaid palette: `graphite` grey tone

Source-derived architecture notes for this PX4 module directory.

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["simulation"]:::module
  Build["directory: simulation"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_outputs"]:::io
    In1["actuator_outputs_sim"]:::io
    In2["battery_status"]:::io
    In3["gimbal_controls"]:::io
    In4["gimbal_device_set_attitude"]:::io
    In5["parameter_update"]:::io
  end
  subgraph Outputs
    Out0["actuator_outputs_sim"]:::io
    Out1["airspeed"]:::io
    Out2["aux_global_position"]:::io
    Out3["differential_pressure"]:::io
    Out4["distance_sensor"]:::io
    Out5["esc_status"]:::io
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
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/simulation |
| Build kind | directory |
| Build target | simulation |
| Runtime main | simulation |
| Stack main | Not specified |
| Module config | Not specified |
| Detected sources | 31 |
| Detected headers | 31 |
| Detected configs | 35 |

### CMake Dependencies

- No explicit CMake dependencies detected.

### Nested Module Targets

- `battery_simulator`
- `gz_bridge`
- `pwm_out_sim`
- `sensor_agp_sim`
- `sensor_airspeed_sim`
- `sensor_baro_sim`
- `sensor_gps_sim`
- `sensor_mag_sim`
- `simulator_mavlink`
- `simulator_sih`
- `system_power_simulator`

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["simulation logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_outputs"]:::io --> UORBIn
  Sub1["actuator_outputs_sim"]:::io --> UORBIn
  Sub2["battery_status"]:::io --> UORBIn
  Sub3["gimbal_controls"]:::io --> UORBIn
  Sub4["gimbal_device_set_attitude"]:::io --> UORBIn
  UORBOut --> Pub0["actuator_outputs_sim"]:::io
  UORBOut --> Pub1["airspeed"]:::io
  UORBOut --> Pub2["aux_global_position"]:::io
  UORBOut --> Pub3["differential_pressure"]:::io
  UORBOut --> Pub4["distance_sensor"]:::io
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_outputs | subscribed |
| actuator_outputs_sim | subscribed, published |
| airspeed | published |
| aux_global_position | published |
| battery_status | subscribed |
| differential_pressure | published |
| distance_sensor | published |
| esc_report | referenced |
| esc_status | published |
| fiducial_marker_pos_report | published |
| fiducial_marker_yaw_report | published |
| gimbal_controls | subscribed |
| gimbal_device_attitude_status | published |
| gimbal_device_information | published |
| gimbal_device_set_attitude | subscribed |
| input_rc | published |
| irlock_report | published |
| landing_target_pose | published |
| manual_control_setpoint | referenced |
| obstacle_distance | published |
| parameter_update | subscribed |
| ranging_beacon | published |
| rpm | published |
| sensor_gps | published |
| sensor_optical_flow | published |
| system_power | published |
| target_gnss | published |
| vehicle_angular_velocity | referenced |
| vehicle_angular_velocity_groundtruth | published |
| vehicle_attitude | subscribed |
| vehicle_attitude_groundtruth | subscribed, published |
| vehicle_command | subscribed |
| vehicle_command_ack | published |
| vehicle_global_position | referenced |
| vehicle_global_position_groundtruth | subscribed, published |
| vehicle_local_position | subscribed |
| vehicle_local_position_groundtruth | subscribed, published |
| vehicle_mocap_odometry | published |
| vehicle_odometry | referenced |
| vehicle_status | subscribed |
| vehicle_visual_odometry | published |
| wheel_encoders | published |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 simulation start"]:::exec
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
classDef module fill:#edf2f4,stroke:#2f3437,color:#1f2326;
classDef io fill:#d9dee2,stroke:#5c636a,color:#1f2326;
classDef data fill:#f7f9fa,stroke:#5c636a,color:#1f2326;
classDef exec fill:#cfd4d8,stroke:#2f3437,color:#1f2326;
```

The common PX4 module lifecycle is command entry, object construction or task spawn, parameter loading, topic setup, scheduled execution, publication, status reporting, and stop/cleanup. Modules that use `ModuleBase`, `ScheduledWorkItem`, polling loops, or bridge callbacks still fit this lifecycle with different scheduling triggers.

## State Machine

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
stateDiagram-v2
  [*] --> Created
  Created --> Initialized: start
  S0: ARMING_STATE_ARMED
  Initialized --> S0: detected state path
  S1: GST_STATE_CHANGE_FAILURE
  S0 --> S1: detected state path
  S2: GST_STATE_NULL
  S1 --> S2: detected state path
  S3: GST_STATE_PLAYING
  S2 --> S3: detected state path
  S4: GZ_SIM_SYSTEMS_GENERICMOT...
  S3 --> S4: detected state path
  S5: GZ_SIM_SYSTEMS_SPACECRAFT...
  S4 --> S5: detected state path
  S5 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `GST_STATE_CHANGE_FAILURE`
- `GST_STATE_NULL`
- `GST_STATE_PLAYING`
- `GZ_SIM_SYSTEMS_GENERICMOTORMODEL_HPP_`
- `GZ_SIM_SYSTEMS_SPACECRAFTTHRUSTERMODEL_HH_`
- `HIL_STATE_QUATERNION`
- `MAVLINK_MSG_ID_HIL_STATE_QUATERNION`
- `MNT_MODE_OUT`
- `PWM_SIM_DISARMED_MAGIC`
- `PWM_SIM_FAILSAFE_MAGIC`
- `PX4_GZ_MODEL_NAME`
- `PX4_MODEL`
- `PX4_SIM_MODEL`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as simulation
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start simulation
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
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf2f4","secondaryColor":"#d9dee2","tertiaryColor":"#f7f9fa","primaryBorderColor":"#5c636a","primaryTextColor":"#1f2326","lineColor":"#5c636a","fontFamily":"Inter, Arial, sans-serif"}}}%%
classDiagram
  class BatterySimulator
  BatterySimulator : battery_simulator/BatterySimulator.hpp
  class ModuleBase
  ModuleBase <|-- BatterySimulator
  class GZBridge
  GZBridge : gz_bridge/GZBridge.hpp
  class ModuleBase
  ModuleBase <|-- GZBridge
  class GZGimbal
  GZGimbal : gz_bridge/GZGimbal.hpp
  class ScheduledWorkItem
  ScheduledWorkItem <|-- GZGimbal
  class GZBridge_3
  GZBridge_3 : gz_bridge/GZGimbal.hpp
  class GZMixingInterfaceESC
  GZMixingInterfaceESC : gz_bridge/GZMixingInterfaceESC.hpp
  class OutputModuleInterface
  OutputModuleInterface <|-- GZMixingInterfaceESC
  class GZBridge_5
  GZBridge_5 : gz_bridge/GZMixingInterfaceESC.hpp
  class GZMixingInterfaceServo
  GZMixingInterfaceServo : gz_bridge/GZMixingInterfaceServo.hpp
  class OutputModuleInterface
  OutputModuleInterface <|-- GZMixingInterfaceServo
  class GZBridge_7
  GZBridge_7 : gz_bridge/GZMixingInterfaceServo.hpp
  class GZMixingInterfaceWheel
  GZMixingInterfaceWheel : gz_bridge/GZMixingInterfaceWheel.hpp
  class OutputModuleInterface
  OutputModuleInterface <|-- GZMixingInterfaceWheel
  class GZBridge_9
  GZBridge_9 : gz_bridge/GZMixingInterfaceWheel.hpp
  class AirSpeed
  AirSpeed : gz_plugins/airspeed/AirSpeed.hpp
  class System
  System <|-- AirSpeed
  class gz
  gz : gz_plugins/buoyancy/BuoyancySystem.cpp
  class BuoyancyPrivate
  BuoyancyPrivate : gz_plugins/buoyancy/BuoyancySystem.hpp
  class Buoyancy
  Buoyancy : gz_plugins/buoyancy/BuoyancySystem.hpp
  class System
  System <|-- Buoyancy
  class can
  can : gz_plugins/generic_motor/GenericMotorModel.cpp
  class FirstOrderFilter
  FirstOrderFilter : gz_plugins/generic_motor/GenericMotorModel.cpp
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| BatterySimulator | ModuleBase | battery_simulator/BatterySimulator.hpp |
| GZBridge | ModuleBase | gz_bridge/GZBridge.hpp |
| GZGimbal | ScheduledWorkItem | gz_bridge/GZGimbal.hpp |
| GZBridge |  | gz_bridge/GZGimbal.hpp |
| GZMixingInterfaceESC | OutputModuleInterface | gz_bridge/GZMixingInterfaceESC.hpp |
| GZBridge |  | gz_bridge/GZMixingInterfaceESC.hpp |
| GZMixingInterfaceServo | OutputModuleInterface | gz_bridge/GZMixingInterfaceServo.hpp |
| GZBridge |  | gz_bridge/GZMixingInterfaceServo.hpp |
| GZMixingInterfaceWheel | OutputModuleInterface | gz_bridge/GZMixingInterfaceWheel.hpp |
| GZBridge |  | gz_bridge/GZMixingInterfaceWheel.hpp |
| AirSpeed | System | gz_plugins/airspeed/AirSpeed.hpp |
| gz |  | gz_plugins/buoyancy/BuoyancySystem.cpp |
| BuoyancyPrivate |  | gz_plugins/buoyancy/BuoyancySystem.hpp |
| Buoyancy | System | gz_plugins/buoyancy/BuoyancySystem.hpp |
| can |  | gz_plugins/generic_motor/GenericMotorModel.cpp |
| FirstOrderFilter |  | gz_plugins/generic_motor/GenericMotorModel.cpp |
| MotorType |  | gz_plugins/generic_motor/GenericMotorModel.cpp |
| ControlMethod |  | gz_plugins/generic_motor/GenericMotorModel.cpp |
| gz |  | gz_plugins/generic_motor/GenericMotorModel.cpp |
| GenericMotorModelPrivate |  | gz_plugins/generic_motor/GenericMotorModel.hpp |
| GenericMotorModel | System | gz_plugins/generic_motor/GenericMotorModel.hpp |
| CameraStream |  | gz_plugins/gstreamer/GstCameraSystem.hpp |
| GstCameraSystem | System | gz_plugins/gstreamer/GstCameraSystem.hpp |
| MotorFailureSystem | System | gz_plugins/motor_failure/MotorFailureSystem.hpp |
| ... 29 more |  |  |

### Detected Enums

- `BuoyancyType`
- `ControlMethod`
- `FailureMode`
- `InternetProtocol`
- `MotorType`
- `SensorSource`
- `TargetAbsoluteSensorCapability`
- `VehicleType`
- `type`

## Parameters and Configuration

- No parameters detected.

## Source Map

| File | Kind |
| --- | --- |
| battery_simulator/BatterySimulator.cpp | source |
| battery_simulator/BatterySimulator.hpp | header |
| battery_simulator/CMakeLists.txt | build |
| battery_simulator/battery_simulator_params.yaml | config |
| gz_bridge/CMakeLists.txt | build |
| gz_bridge/GZBridge.cpp | source |
| gz_bridge/GZBridge.hpp | header |
| gz_bridge/GZGimbal.cpp | source |
| gz_bridge/GZGimbal.hpp | header |
| gz_bridge/GZMixingInterfaceESC.cpp | source |
| gz_bridge/GZMixingInterfaceESC.hpp | header |
| gz_bridge/GZMixingInterfaceServo.cpp | source |
| gz_bridge/GZMixingInterfaceServo.hpp | header |
| gz_bridge/GZMixingInterfaceWheel.cpp | source |
| gz_bridge/GZMixingInterfaceWheel.hpp | header |
| gz_bridge/module.yaml | config |
| gz_bridge/parameters.yaml | config |
| gz_msgs/CMakeLists.txt | build |
| gz_plugins/CMakeLists.txt | build |
| gz_plugins/airspeed/AirSpeed.cpp | source |
| gz_plugins/airspeed/AirSpeed.hpp | header |
| gz_plugins/airspeed/CMakeLists.txt | build |
| gz_plugins/buoyancy/BuoyancySystem.cpp | source |
| gz_plugins/buoyancy/BuoyancySystem.hpp | header |
| gz_plugins/buoyancy/CMakeLists.txt | build |
| gz_plugins/generic_motor/CMakeLists.txt | build |
| gz_plugins/generic_motor/GenericMotorModel.cpp | source |
| gz_plugins/generic_motor/GenericMotorModel.hpp | header |
| gz_plugins/gstreamer/CMakeLists.txt | build |
| gz_plugins/gstreamer/GstCameraSystem.cpp | source |
| gz_plugins/gstreamer/GstCameraSystem.hpp | header |
| gz_plugins/gstreamer/README.md | readme |
| gz_plugins/motor_failure/CMakeLists.txt | build |
| gz_plugins/motor_failure/MotorFailureSystem.cpp | source |
| gz_plugins/motor_failure/MotorFailureSystem.hpp | header |
| gz_plugins/motor_failure/README.md | readme |
| gz_plugins/moving_platform_controller/CMakeLists.txt | build |
| gz_plugins/moving_platform_controller/MovingPlatformController.cpp | source |
| gz_plugins/moving_platform_controller/MovingPlatformController.hpp | header |
| gz_plugins/moving_platform_controller/README.md | readme |
| ... 63 more files | omitted |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
