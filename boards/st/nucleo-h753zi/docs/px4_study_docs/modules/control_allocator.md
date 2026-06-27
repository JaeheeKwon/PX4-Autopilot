# PX4 Module Architecture: `control_allocator`

- Source: `src/modules/control_allocator`
- Build target: `modules__control_allocator`
- Runtime main: `control_allocator`
- Build kind: `px4 module`
- Mermaid palette: `slate` grey tone

Architecture notes for the Control Allocation module.

## Description of Module

Maps normalized torque and thrust requests into actuator motor and servo setpoints using the configured vehicle geometry.

### Primary Responsibilities

- Convert selected state estimates and setpoints into downstream control or actuator-facing setpoints.
- Consume runtime inputs from uORB topics such as `actuator_armed`, `failure_detector_status`, `flaps_setpoint`, `launch_detection_status`, `manual_control_switches`, `parameter_update`, `rpm`, `spoilers_setpoint`, ... 7 more.
- Publish outputs or status topics such as `actuator_motors`, `actuator_servos`, `actuator_servos_trim`, `control_allocator_status`, `vehicle_command_ack`.
- Use parameters or module configuration entries such as `CA_AIRFRAME`, `CA_CS_LAUN_LK`, `CA_FAILURE_MODE`, `CA_HELI_RPM_I`, `CA_HELI_RPM_P`, `CA_HELI_RPM_SP`, ... 17 more.
- Implement the main behavior in classes such as `ActuatorGroupPreflightCheck`, `ControlAllocator`, `EffectivenessSource`, `FailureMode`, `providing`, `ActuatorEffectivenessControlSurfaces`, ... 19 more.

### Runtime Behavior

- Runs work-queue callbacks on queue configurations such as `rate_ctrl`.
- Uses uORB callback registration so new topic data can schedule execution.
- Uses explicit work-item scheduling through immediate, delayed, or interval scheduling calls.

## Background Theory

Control allocation solves an actuator mixing problem: find actuator commands that best realize requested body forces and moments under actuator limits.

```text
Given effectiveness matrix B and requested wrench tau:
u* = argmin_u ||W * (B*u - tau)||^2 + lambda ||u - u_trim||^2
subject to u_min <= u <= u_max

Unconstrained form:
u = B_plus * tau
B_plus = W_u^-1 * B^T * inverse(B * W_u^-1 * B^T)
```

These equations are the study-level form of the algorithm. The implementation applies PX4-specific saturation, validity checks, parameter updates, and frame conventions around these core relationships.

### Main Interfaces

| Area | Details |
| --- | --- |
| Primary inputs | `actuator_armed`, `failure_detector_status`, `flaps_setpoint`, `launch_detection_status`, `manual_control_switches`, `parameter_update`, `rpm`, `spoilers_setpoint`, `tiltrotor_extra_controls`, `vehicle_command`, ... 5 more |
| Primary outputs | `actuator_motors`, `actuator_servos`, `actuator_servos_trim`, `control_allocator_status`, `vehicle_command_ack` |
| Referenced topics | `actuator_armed`, `actuator_motors`, `actuator_servos`, `actuator_servos_trim`, `control_allocator_status`, `failure_detector_status`, `flaps_setpoint`, `launch_detection_status`, `manual_control_switches`, `normalized_unsigned_setpoint`, ... 11 more |
| Parameters/config | `CA_AIRFRAME`, `CA_CS_LAUN_LK`, `CA_FAILURE_MODE`, `CA_HELI_RPM_I`, `CA_HELI_RPM_P`, `CA_HELI_RPM_SP`, `CA_HELI_YAW_CCW`, `CA_HELI_YAW_CP_O`, `CA_HELI_YAW_CP_S`, `CA_HELI_YAW_TH_S`, ... 13 more |
| Key classes | `ActuatorGroupPreflightCheck`, `ControlAllocator`, `EffectivenessSource`, `FailureMode`, `providing`, `ActuatorEffectivenessControlSurfaces`, `Type`, `ActuatorEffectivenessCustom`, `ActuatorEffectivenessFixedWing`, `ActuatorEffectivenessHelicopter`, ... 15 more |

### Files

| File | Why it matters |
| --- | --- |
| ControlAllocator.cpp | Entry point, start command, or module lifecycle code |
| CMakeLists.txt | Build, parameter, or module configuration |
| VehicleActuatorEffectiveness/CMakeLists.txt | Build, parameter, or module configuration |
| module.yaml | Build, parameter, or module configuration |
| ActuatorGroupPreflightCheck.hpp | Defines `ActuatorGroupPreflightCheck` class |
| ControlAllocator.hpp | Defines `ControlAllocator` class |

## Architecture Overview

This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  Module["control_allocator"]:::module
  Build["px4 module: modules__control_allocator"]:::data
  Params["parameters / module.yaml"]:::data
  Schedule["task, work queue, or callback"]:::exec
  subgraph Inputs
    In0["actuator_armed"]:::io
    In1["failure_detector_status"]:::io
    In2["flaps_setpoint"]:::io
    In3["launch_detection_status"]:::io
    In4["manual_control_switches"]:::io
    In5["parameter_update"]:::io
  end
  subgraph Outputs
    Out0["actuator_motors"]:::io
    Out1["actuator_servos"]:::io
    Out2["actuator_servos_trim"]:::io
    Out3["control_allocator_status"]:::io
    Out4["vehicle_command_ack"]:::io
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
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

## Build and Entry Points

| Field | Value |
| --- | --- |
| Module path | src/modules/control_allocator |
| Build kind | px4 module |
| Build target | modules__control_allocator |
| Runtime main | control_allocator |
| Stack main | 3000 |
| Module config | module.yaml |
| Detected sources | 19 |
| Detected headers | 17 |
| Detected configs | 3 |

### CMake Dependencies

- `mathlib`
- `ActuatorEffectiveness`
- `VehicleActuatorEffectiveness`
- `ControlAllocation`
- `px4_work_queue`
- `SlewRate`

### Nested Module Targets

- No nested module targets detected.

## Data Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart LR
  UORBIn["uORB subscriptions"]:::io
  Params["parameter cache"]:::data
  Update["input update / polling"]:::exec
  Logic["control_allocator logic"]:::module
  UORBOut["uORB publications"]:::io
  Status["status, events, perf counters"]:::data
  UORBIn --> Update
  Params --> Logic
  Update --> Logic
  Logic --> UORBOut
  Logic --> Status
  Sub0["actuator_armed"]:::io --> UORBIn
  Sub1["failure_detector_status"]:::io --> UORBIn
  Sub2["flaps_setpoint"]:::io --> UORBIn
  Sub3["launch_detection_status"]:::io --> UORBIn
  Sub4["manual_control_switches"]:::io --> UORBIn
  UORBOut --> Pub0["actuator_motors"]:::io
  UORBOut --> Pub1["actuator_servos"]:::io
  UORBOut --> Pub2["actuator_servos_trim"]:::io
  UORBOut --> Pub3["control_allocator_status"]:::io
  UORBOut --> Pub4["vehicle_command_ack"]:::io
classDef module fill:#eef0f2,stroke:#30363d,color:#202428;
classDef io fill:#e1e5e8,stroke:#59636e,color:#202428;
classDef data fill:#fafafa,stroke:#59636e,color:#202428;
classDef exec fill:#d5dade,stroke:#30363d,color:#202428;
```

### uORB Topics

| Topic | Detected direction |
| --- | --- |
| actuator_armed | subscribed |
| actuator_motors | published |
| actuator_servos | published |
| actuator_servos_trim | published |
| control_allocator_status | published |
| failure_detector_status | subscribed |
| flaps_setpoint | subscribed |
| launch_detection_status | subscribed |
| manual_control_switches | subscribed |
| normalized_unsigned_setpoint | referenced |
| parameter_update | subscribed |
| rpm | subscribed |
| spoilers_setpoint | subscribed |
| tiltrotor_extra_controls | subscribed |
| vehicle_command | subscribed |
| vehicle_command_ack | published |
| vehicle_control_mode | subscribed |
| vehicle_land_detected | subscribed |
| vehicle_status | subscribed |
| vehicle_thrust_setpoint | subscribed |
| vehicle_torque_setpoint | subscribed |

## Execution Flow

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
flowchart TD
  Start["px4 control_allocator start"]:::exec
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
  S1: CA_FAILURE_MODE
  S0 --> S1: detected state path
  S2: CA_SP0_ARM_L
  S1 --> S2: detected state path
  S2 --> Running: normal execution
  Running --> Stopped: stop
  Stopped --> [*]
```

### Detected State-Like Symbols

- `ARMING_STATE_ARMED`
- `CA_FAILURE_MODE`
- `CA_SP0_ARM_L`

## Sequence Diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef0f2","secondaryColor":"#e1e5e8","tertiaryColor":"#fafafa","primaryBorderColor":"#59636e","primaryTextColor":"#202428","lineColor":"#59636e","fontFamily":"Inter, Arial, sans-serif"}}}%%
sequenceDiagram
  participant CLI as px4 shell
  participant M as control_allocator
  participant P as Parameters
  participant U as uORB
  participant W as Scheduler
  CLI->>M: start control_allocator
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
  class ActuatorGroupPreflightCheck
  ActuatorGroupPreflightCheck : ActuatorGroupPreflightCheck.hpp
  class ControlAllocator
  ControlAllocator : ControlAllocator.hpp
  class ModuleBase
  ModuleBase <|-- ControlAllocator
  class EffectivenessSource
  EffectivenessSource : ControlAllocator.hpp
  class FailureMode
  FailureMode : ControlAllocator.hpp
  class providing
  providing : ControlAllocator.hpp
  class ActuatorEffectivenessControlSurfaces
  ActuatorEffectivenessControlSurfaces : VehicleActuatorEffectiveness/ActuatorEffectivenessC...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessControlSurfaces
  class Type
  Type : VehicleActuatorEffectiveness/ActuatorEffectivenessC...
  class ActuatorEffectivenessCustom
  ActuatorEffectivenessCustom : VehicleActuatorEffectiveness/ActuatorEffectivenessC...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessCustom
  class ActuatorEffectivenessFixedWing
  ActuatorEffectivenessFixedWing : VehicleActuatorEffectiveness/ActuatorEffectivenessF...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessFixedWing
  class ActuatorEffectivenessHelicopter
  ActuatorEffectivenessHelicopter : VehicleActuatorEffectiveness/ActuatorEffectivenessH...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessHelicopter
  class ActuatorEffectivenessHelicopterCoaxial
  ActuatorEffectivenessHelicopterCoaxial : VehicleActuatorEffectiveness/ActuatorEffectivenessH...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessHelicopterCoaxial
  class ActuatorEffectivenessMCTilt
  ActuatorEffectivenessMCTilt : VehicleActuatorEffectiveness/ActuatorEffectivenessM...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessMCTilt
  class ActuatorEffectivenessMultirotor
  ActuatorEffectivenessMultirotor : VehicleActuatorEffectiveness/ActuatorEffectivenessM...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessMultirotor
  class ActuatorEffectivenessTilts
  ActuatorEffectivenessTilts : VehicleActuatorEffectiveness/ActuatorEffectivenessR...
  class ActuatorEffectivenessRotors
  ActuatorEffectivenessRotors : VehicleActuatorEffectiveness/ActuatorEffectivenessR...
  class ModuleParams
  ModuleParams <|-- ActuatorEffectivenessRotors
  class AxisConfiguration
  AxisConfiguration : VehicleActuatorEffectiveness/ActuatorEffectivenessR...
```

### Detected Classes

| Class | Base | File |
| --- | --- | --- |
| ActuatorGroupPreflightCheck |  | ActuatorGroupPreflightCheck.hpp |
| ControlAllocator | ModuleBase | ControlAllocator.hpp |
| EffectivenessSource |  | ControlAllocator.hpp |
| FailureMode |  | ControlAllocator.hpp |
| providing |  | ControlAllocator.hpp |
| ActuatorEffectivenessControlSurfaces | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessControlSurfaces.hpp |
| Type |  | VehicleActuatorEffectiveness/ActuatorEffectivenessControlSurfaces.hpp |
| ActuatorEffectivenessCustom | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessCustom.hpp |
| ActuatorEffectivenessFixedWing | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessFixedWing.hpp |
| ActuatorEffectivenessHelicopter | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessHelicopter.hpp |
| ActuatorEffectivenessHelicopterCoaxial | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessHelicopterCoaxial.hpp |
| ActuatorEffectivenessMCTilt | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessMCTilt.hpp |
| ActuatorEffectivenessMultirotor | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessMultirotor.hpp |
| ActuatorEffectivenessTilts |  | VehicleActuatorEffectiveness/ActuatorEffectivenessRotors.hpp |
| ActuatorEffectivenessRotors | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessRotors.hpp |
| AxisConfiguration |  | VehicleActuatorEffectiveness/ActuatorEffectivenessRotors.hpp |
| ActuatorEffectivenessSpacecraft | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessSpacecraft.hpp |
| ActuatorEffectivenessStandardVTOL | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessStandardVTOL.hpp |
| ActuatorEffectivenessTailsitterVTOL | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessTailsitterVTOL.hpp |
| ActuatorEffectivenessTiltrotorVTOL | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessTiltrotorVTOL.hpp |
| ActuatorEffectivenessTilts | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessTilts.hpp |
| Control |  | VehicleActuatorEffectiveness/ActuatorEffectivenessTilts.hpp |
| TiltDirection |  | VehicleActuatorEffectiveness/ActuatorEffectivenessTilts.hpp |
| ActuatorEffectivenessUUV | ModuleParams | VehicleActuatorEffectiveness/ActuatorEffectivenessUUV.hpp |
| ... 1 more |  |  |

### Detected Enums

- `AxisConfiguration`
- `Control`
- `EffectivenessSource`
- `FailureMode`
- `TiltDirection`
- `Type`

## Parameters and Configuration

- `CA_AIRFRAME`
- `CA_CS_LAUN_LK`
- `CA_FAILURE_MODE`
- `CA_HELI_RPM_I`
- `CA_HELI_RPM_P`
- `CA_HELI_RPM_SP`
- `CA_HELI_YAW_CCW`
- `CA_HELI_YAW_CP_O`
- `CA_HELI_YAW_CP_S`
- `CA_HELI_YAW_TH_S`
- `CA_ICE_PERIOD`
- `CA_MAX_SVO_THROW`
- `CA_METHOD`
- `CA_ROTOR_COUNT`
- `CA_R_REV`
- `CA_SP0_COUNT`
- `CA_SV_CS_COUNT`
- `CA_SV_FLAP_SLEW`
- `CA_SV_TL_COUNT`
- `COM_SPOOLUP_TIME`
- `DEFAULT`
- `NOTE`
- `VT_ELEV_MC_LOCK`

## Source Map

| File | Kind |
| --- | --- |
| ActuatorGroupPreflightCheck.cpp | source |
| ActuatorGroupPreflightCheck.hpp | header |
| CMakeLists.txt | build |
| ControlAllocator.cpp | source |
| ControlAllocator.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessControlSurfaces.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessControlSurfaces.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessCustom.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessCustom.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessFixedWing.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessFixedWing.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessHelicopter.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessHelicopter.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessHelicopterCoaxial.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessHelicopterCoaxial.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessHelicopterTest.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessMCTilt.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessMCTilt.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessMultirotor.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessMultirotor.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessRotors.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessRotors.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessRotorsTest.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessSpacecraft.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessSpacecraft.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessStandardVTOL.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessStandardVTOL.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessTailsitterVTOL.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessTailsitterVTOL.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessTiltrotorVTOL.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessTiltrotorVTOL.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessTilts.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessTilts.hpp | header |
| VehicleActuatorEffectiveness/ActuatorEffectivenessUUV.cpp | source |
| VehicleActuatorEffectiveness/ActuatorEffectivenessUUV.hpp | header |
| VehicleActuatorEffectiveness/CMakeLists.txt | build |
| VehicleActuatorEffectiveness/RpmControl.cpp | source |
| VehicleActuatorEffectiveness/RpmControl.hpp | header |
| module.yaml | config |

## Review Notes

- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.
- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.
- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.
